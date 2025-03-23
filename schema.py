from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Decision(str, Enum):
    APPEAL = "appeal"
    CODE_FOR_CHANGE = "code_for_change"
    SETTLEMENT = "settlement"


class SubmitAppealOutput(BaseModel):
    decision: Decision
    action_steps: list[str]
    appeal_letter: Optional[str] = None


if __name__ == "__main__":
    print(
        SubmitAppealOutput(
            decision=Decision.APPEAL,
            action_steps=["action1", "action2"],
            appeal_letter="appeal letter",
        ).model_json_schema()
    )
