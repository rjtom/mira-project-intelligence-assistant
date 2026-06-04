from fastapi import APIRouter
from services.langflow import query_mira
from services.sheets import get_risks_for_project, format_risks_for_display
import uuid

router = APIRouter(prefix="/api/risk", tags=["Risk"])

QUESTIONS = {
    "risks": "What are the major risks for {p}?",
    "mitigation": "What are the risk mitigation strategies for {p}?",
    "hil": "What Human-in-the-Loop checkpoints are required for {p}?",
    "score": "What are the risk scores and impact levels for {p}?",
    "likelihood": "What is the likelihood assessment for risks in {p}?",
}


@router.post("/query")
async def risk_query(project: str, question_type: str = "risks"):
    template = QUESTIONS.get(question_type, QUESTIONS["risks"])
    question = template.format(p=project)
    sheet_risks = get_risks_for_project(project)

    if sheet_risks:
        raw_data = format_risks_for_display(sheet_risks)
        grounded = (
            f"{question}\n\n"
            f"Use ONLY this data from our risk matrix:\n{raw_data}\n\n"
            f"Do not add any information not in the data above."
        )
        session_id = str(uuid.uuid4())
        result = await query_mira(grounded, session_id)
        return {
            "project": project,
            "question_type": question_type,
            "question": question,
            "response": result["response"],
            "response_time": result["time"],
            "data_source": "Google Sheets",
            "risk_count": len(sheet_risks)
        }

    session_id = str(uuid.uuid4())
    result = await query_mira(question, session_id)
    return {
        "project": project,
        "question_type": question_type,
        "question": question,
        "response": result["response"],
        "response_time": result["time"],
        "data_source": "MIRA RAG",
        "risk_count": 0
    }


@router.get("/raw")
async def raw_risks(project: str):
    risks = get_risks_for_project(project)
    return {
        "project": project,
        "risks": risks,
        "count": len(risks)
    }