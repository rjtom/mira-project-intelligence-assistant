from fastapi import APIRouter
from services.langflow import query_mira
import uuid

router = APIRouter(prefix="/api/governance", tags=["Governance"])

@router.post("/query")
async def governance_query(project: str):
    question = f"What governance checkpoints were used in {project}?"
    session_id = str(uuid.uuid4())
    result = await query_mira(question, session_id)
    return {
        "project": project,
        "question": question,
        "response": result["response"],
        "response_time": result["time"]
    }

@router.post("/hil")
async def hil_query(project: str):
    question = f"What Human-in-the-Loop decisions are required for {project}?"
    session_id = str(uuid.uuid4())
    result = await query_mira(question, session_id)
    return {
        "project": project,
        "question": question,
        "response": result["response"],
        "response_time": result["time"]
    }
