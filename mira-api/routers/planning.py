from fastapi import APIRouter
from services.langflow import query_mira
import uuid

router = APIRouter(prefix="/api/planning", tags=["Planning"])

PROJECTS = [
    "ForgeNova EV Battery Gigafactory Expansion",
    "ForgeNova Autonomous Driving Platform Development",
    "ForgeNova Electric SUV Launch Program",
    "ForgeNova DevOps Pipeline Transformation",
    "ForgeNova Digital Twin Factory Initiative",
    "ForgeNova Global ERP System Migration",
    "ForgeNova Multi-Cloud Infrastructure Modernization",
    "ForgeNova Software Defined Vehicle Platform",
    "ForgeNova Next-Generation Battery Technology Program",
    "ForgeNova Urban Air Mobility Initiative",
]

@router.get("/projects")
async def list_projects():
    return {"projects": PROJECTS}

@router.post("/query")
async def planning_query(project: str, question_type: str = "timeline"):
    templates = {
        "timeline": f"What is the timeline for {project}?",
        "objectives": f"What are the objectives for {project}?",
        "resources": f"What are the resource requirements for {project}?",
        "lessons": f"What lessons were learned from {project}?",
    }
    question = templates.get(question_type, templates["timeline"])
    session_id = str(uuid.uuid4())
    result = await query_mira(question, session_id)
    return {
        "project": project,
        "question_type": question_type,
        "question": question,
        "response": result["response"],
        "response_time": result["time"]
    }

@router.post("/full")
async def full_planning(project: str):
    session_id = str(uuid.uuid4())
    results = {}
    for qt, template in [
        ("timeline", f"What is the timeline for {project}?"),
        ("objectives", f"What are the objectives for {project}?"),
        ("resources", f"What are the resource requirements for {project}?"),
        ("lessons", f"What lessons were learned from {project}?"),
    ]:
        result = await query_mira(template, session_id)
        results[qt] = result["response"]
    return {"project": project, **results}
