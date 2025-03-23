from enum import Enum
from typing import Optional

from ai21.models.responses.conversational_rag_response import ConversationalRagResponse
from pydantic import BaseModel, Field


class Decision(str, Enum):
    APPEAL = "appeal"
    CODE_FOR_CHANGE = "code_for_change"
    SETTLEMENT = "settlement"


class SubmitAppealOutput(BaseModel):
    decision: Decision
    action_steps: list[str]
    appeal_letter: Optional[str] = None


class Output(BaseModel):
    message: str
    data: dict
    result: SubmitAppealOutput


class AskIn(BaseModel):
    question: str
    file_ids: list[str] = Field(default_factory=list)


class AskOut(BaseModel):
    message: str
    data: dict
    result: ConversationalRagResponse


if __name__ == "__main__":
    print(
        SubmitAppealOutput(
            decision=Decision.APPEAL,
            action_steps=["action1", "action2"],
            appeal_letter="appeal letter",
        ).model_json_schema()
    )
