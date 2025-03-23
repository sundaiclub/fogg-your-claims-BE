from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse, JSONResponse
from ai21 import AI21Client
from typing import Optional
from datetime import datetime
from ai21 import AI21Client
from dotenv import load_dotenv
import os
import uvicorn
import requests

load_dotenv()

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
def read_root():
    return "Hello, this is a simple FastAPI endpoint returning plain text!"


api_key = os.getenv("AI21_API_KEY")
client = AI21Client(api_key=api_key)

@app.post("/submit-appeal")
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


        return {
            "message": "Appeal submission received successfully",
            "data": {
                "name": name,
                "dob": dob,
                "denial_letter": denial_letter,
                "policy_doc_file_id": policy_doc_file_id,
                "additional_info": additional_info,
            }
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/get_steps")
async def get_steps(run_results_id: str):
    graph_url = f"https://api.ai21.com/studio/v1/execution/{run_results_id}/graph?filtered=true"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(graph_url, headers=headers)

    if response.status_code == 200:
        graph_data = response.json()
        return graph_data
    else:
        return JSONResponse(status_code=400, content={"error": "run_results_id not found"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
