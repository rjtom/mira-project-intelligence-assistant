from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services.langflow import query_mira
from services.email import send_project_report, send_context_report
import uuid

router = APIRouter(prefix="/api/email", tags=["Email"])

class EmailReportRequest(BaseModel):
    project: str
    recipient_email: str
    report_type: str = "full"

class EmailContextRequest(BaseModel):
    project: str
    recipient_email: str
    last_question: Optional[str] = None
    last_response: Optional[str] = None
    hil_lines: Optional[List[str]] = []
    sources: Optional[List[str]] = []
    response_time: Optional[float] = None

REPORT_QUESTIONS = {
    "timeline": "What is the timeline for {project}?",
    "objectives": "What are the objectives for {project}?",
    "risks": "What are the major risks for {project}?",
    "governance": "What governance checkpoints were used in {project}?",
    "lessons": "What lessons were learned from {project}?",
}

@router.post("/send-report")
async def send_report(request: EmailReportRequest):
    project = request.project
    data = {}
    for key, template in REPORT_QUESTIONS.items():
        question = template.format(project=project)
        session_id = f"email-{key}-{str(uuid.uuid4())[:8]}"
        result = await query_mira(question, session_id)
        data[key] = result["response"] if result["success"] else "Data not available"

    result = await send_project_report(
        project=project,
        recipient_email=request.recipient_email,
        data=data
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.post("/send-context-report")
async def send_context_report_endpoint(request: EmailContextRequest):
    project = request.project

    # Get a quick project summary for context
    session_id = f"email-summary-{str(uuid.uuid4())[:8]}"
    summary_result = await query_mira(
        f"Give a brief 3-sentence summary of {project} including status and key objectives.",
        session_id
    )
    summary = summary_result["response"] if summary_result["success"] else ""

    result = await send_context_report(
        project=project,
        recipient_email=request.recipient_email,
        last_question=request.last_question,
        last_response=request.last_response,
        hil_lines=request.hil_lines or [],
        sources=request.sources or [],
        response_time=request.response_time,
        summary=summary
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.post("/test")
async def test_email(recipient_email: str):
    result = await send_project_report(
        project="ForgeNova EV Battery Gigafactory Expansion",
        recipient_email=recipient_email,
        data={
            "timeline": "Q1 2024 to Q4 2024 — 4 phases completed successfully.",
            "objectives": "Double production capacity, integrate automation, ensure workforce wellbeing.",
            "risks": "Supply chain delays and welding defects — resolved with dual sourcing.",
            "governance": "Monthly leadership reviews, HIL checkpoints at every phase gate.",
            "lessons": "Antifragility comes from treating every delay as a signal to strengthen the system.",
        }
    )
    return result
