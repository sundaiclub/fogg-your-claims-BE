import os
from typing import Optional

from pydantic import BaseModel, Field
import requests
import uvicorn
from ai21 import AI21Client
from ai21.models.chat import ChatMessage
from ai21.models.responses.conversational_rag_response import ConversationalRagResponse
from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, PlainTextResponse

from schema import Output, SubmitAppealOutput

load_dotenv()

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
def read_root():
    return "Hello, this is a simple FastAPI endpoint returning plain text!"


api_key = os.getenv("AI21_API_KEY")
client = AI21Client(api_key=api_key)


@app.post("/submit-appeal", response_model=Output)
async def submit_appeal(
    name: str = Form(...),
    dob: Optional[str] = Form(None),
    denial_letter: str = Form(...),
    policy_doc_file_id: Optional[str] = Form(None),
    additional_info: Optional[str] = Form(None),
):
    try:
        # policy_doc_metadata = None
        # if policy_doc_file_id:
        #     policy_doc_metadata = client.library.files.get(policy_doc_file_id)

        # dob_parsed = None
        # if dob:
        #     try:
        #         dob_parsed = datetime.strptime(dob, "%Y-%m-%d").date()
        #     except ValueError:
        #         return JSONResponse(status_code=400, content={"error": "DOB must be in YYYY-MM-DD format"})

        run_result = client.beta.maestro.runs.create_and_poll(
            input="""
Objective:
You are an AI assistant tasked with handling a health insurance dispute. Given a case description, you must analyze the situation and decide on the best course of action:

Appeal to the health insurance provider – If the denial is unjustified and can be contested.

Code for change – If the issue is due to a coding error or claim submission mistake.

Settle with the provider – If appealing is not viable, and negotiation is the best option.

Once a decision is made, you must generate a structured output in JSON format following the provided schema.

Schema for Output Formatting:
{
  "$defs": {
    "Decision": {
      "enum": ["appeal", "code_for_change", "settlement"],
      "title": "Decision",
      "type": "string"
    }
  },
  "properties": {
    "decision": {
      "$ref": "#/$defs/Decision"
    },
    "action_steps": {
      "items": {
        "type": "string"
      },
      "title": "Action Steps",
      "type": "array"
    },
    "appeal_letter": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Appeal Letter"
    }
  },
  "required": ["decision", "action_steps"],
  "title": "SubmitAppealOutput",
  "type": "object"
}
Instructions for AI Response:
Determine the best course of action (decision)

Consider whether appealing, correcting a coding issue, or negotiating a settlement is the best option.

Choose one of the three options: "appeal", "code_for_change", or "settlement".

Provide a step-by-step action plan (action_steps)

List actionable steps in logical order that the user should take.

Ensure that steps are clear, concise, and relevant to the decision.

If the decision is "appeal", generate a formal appeal letter (appeal_letter)

Address the insurance provider.

Clearly state the claim details and reason for appeal.

Reference supporting medical documentation or policy details.

Keep the tone professional and persuasive.

If not an appeal, set "appeal_letter": null.

Few-Shot Examples:
Example 1: Appeal to Health Insurance Provider

{
  "decision": "appeal",
  "action_steps": [
    "Review the denial letter and identify the insurer's reason for denial.",
    "Gather medical records, a letter of medical necessity, and relevant insurance policy sections.",
    "Draft and submit an appeal letter with supporting documents.",
    "Follow up with the insurance provider for a decision update.",
    "Seek external assistance if the appeal is denied (e.g., state insurance department)."
  ],
  "appeal_letter": "Dear [Insurance Company],\n\nI am writing to formally appeal the denial of my claim [Claim Number] for [Service/Treatment], provided on [Date of Service] by [Healthcare Provider]. The denial reason stated was '[Denial Reason].'\n\nAccording to my physician, [Doctor Name], this treatment was medically necessary for my condition, as outlined in the attached supporting documentation. Additionally, per Section [Policy Section] of my insurance policy, this service should be covered.\n\nI kindly request a reconsideration of this decision based on the provided evidence. Please find enclosed medical records and a physician’s letter supporting my appeal.\n\nThank you for your time and attention to this matter. I look forward to your response.\n\nSincerely,\n[Your Name]\n[Your Contact Information]\n[Your Policy Number]"
}
Example 2: Code for Change (Claim Correction)

{
  "decision": "code_for_change",
  "action_steps": [
    "Contact the provider’s billing department to verify the claim details.",
    "Obtain the corrected procedure code from the healthcare provider.",
    "Request the provider to resubmit the corrected claim to the insurance company.",
    "Follow up with the insurance provider to confirm claim processing."
  ],
  "appeal_letter": null
}
Example 3: Settlement (Negotiation with Provider)

{
  "decision": "settlement",
  "action_steps": [
    "Confirm that the denial is final and not subject to appeal.",
    "Contact the healthcare provider’s billing department to negotiate a lower payment.",
    "Request financial assistance or a payment plan if applicable.",
    "Review third-party medical bill negotiation options."
  ],
  "appeal_letter": null
}
            """,
            tools=[{"type": "file_search"}],
        )

        run_result_json = run_result.model_dump()

        output = SubmitAppealOutput.model_validate_json(run_result_json["result"])

        return {
            "message": "Appeal submission received successfully",
            "data": {
                "name": name,
                "dob": dob,
                "denial_letter": denial_letter,
                "policy_doc_file_id": policy_doc_file_id,
                "additional_info": additional_info,
                "run_result_id": run_result.id
            },
            "result": output.model_dump()
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/get_steps")
async def get_steps(run_results_id: str):
    graph_url = (
        f"https://api.ai21.com/studio/v1/execution/{run_results_id}/graph?filtered=true"
    )
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(graph_url, headers=headers)

    if response.status_code == 200:
        graph_data = response.json()
        return graph_data
    else:
        return JSONResponse(
            status_code=400, content={"error": "run_results_id not found"}
        )


history = []


class AskIn(BaseModel):
    question: str
    file_ids: list[str] = Field(default_factory=list)


class AskOut(BaseModel):
    message: str
    data: dict
    result: ConversationalRagResponse


@app.post("/ask", response_model=AskOut)
async def ask(ask_in: AskIn):
    run_result: ConversationalRagResponse = client.beta.conversational_rag.create(
        messages=history + [ChatMessage(role="user", content=ask_in.question)],
        file_ids=ask_in.file_ids,
        max_segments=15,
        retrieval_strategy="segments",
        retrieval_similarity_threshold=0,
        max_neighbors=1,
        response_language="english",
    )
    history.append(
        ChatMessage(role="assistant", content=run_result.choices[0].message.content)
    )
    return AskOut(
        message="Question answered successfully",
        data={"question": ask_in.question, "file_ids": ask_in.file_ids},
        result=run_result,
    )


@app.delete("/clear_history")
async def clear_history():
    global history
    history = []
    return {"message": "History cleared"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
