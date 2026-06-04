from fastapi import APIRouter, HTTPException
from models.schemas import MiraQuery, MiraResponse
from services.langflow import query_mira
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/mira", tags=["MIRA"])

@router.post("/query", response_model=MiraResponse)
async def mira_query(request: MiraQuery):
    session_id = request.session_id or str(uuid.uuid4())
    result = await query_mira(request.question, session_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["response"])
    return MiraResponse(
        question=request.question,
        response=result["response"],
        session_id=session_id,
        response_time=result["time"],
        timestamp=datetime.utcnow().isoformat()
    )

@router.get("/health")
async def health():
    return {"status": "ok", "service": "MIRA API"}
