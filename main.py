from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse, JSONResponse
from ai21 import AI21Client
from typing import Optional
from datetime import datetime
from ai21 import AI21Client
from dotenv import load_dotenv
import os
import uvicorn

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
    denial_letter_file_id: str = Form(...),
    policy_doc_file_id: Optional[str] = Form(None),
    additional_info: Optional[str] = Form(None),
):
    try:
        denial_letter_metadata = client.library.files.get(denial_letter_file_id)

        policy_doc_metadata = None
        if policy_doc_file_id:
            policy_doc_metadata = client.library.files.get(policy_doc_file_id)

        dob_parsed = None
        if dob:
            try:
                dob_parsed = datetime.strptime(dob, "%Y-%m-%d").date()
            except ValueError:
                return JSONResponse(status_code=400, content={"error": "DOB must be in YYYY-MM-DD format"})


        return {
            "message": "Appeal submission received successfully",
            "data": {
                "name": name,
                "dob": dob_parsed,
                "denial_letter_file_id": denial_letter_file_id,
                "denial_letter_filename": denial_letter_metadata,
                "policy_doc_file_id": policy_doc_file_id,
                "policy_doc_filename": policy_doc_metadata.filename if policy_doc_metadata else None,
                "additional_info": additional_info,
            }
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
