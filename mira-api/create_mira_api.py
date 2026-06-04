import os

files = {}

files['models/schemas.py'] = """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MiraQuery(BaseModel):
    question: str
    session_id: Optional[str] = None
    project: Optional[str] = None

class MiraResponse(BaseModel):
    question: str
    response: str
    session_id: str
    response_time: float
    timestamp: str

class PlanningResponse(BaseModel):
    project: str
    timeline: Optional[str] = None
    objectives: Optional[str] = None
    resources: Optional[str] = None
    lessons: Optional[str] = None

class EmailReportRequest(BaseModel):
    project: str
    recipient_email: str
    report_type: str = "full"
"""

files['services/langflow.py'] = """import httpx
import time
import os
from dotenv import load_dotenv
load_dotenv()

LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://127.0.0.1:7860")
FLOW_ID = os.getenv("FLOW_ID", "")
API_KEY = os.getenv("LANGFLOW_API_KEY", "")

async def query_mira(question: str, session_id: str) -> dict:
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY
                },
                json={
                    "input_value": question,
                    "output_type": "chat",
                    "input_type": "chat",
                    "session_id": session_id
                }
            )
            elapsed = round(time.time() - start, 2)
            if response.status_code == 200:
                data = response.json()
                try:
                    text = (data["outputs"][0]["outputs"][0]
                           ["results"]["message"]["data"]["text"])
                except Exception:
                    text = ""
                return {"success": True, "response": text, "time": elapsed}
            return {
                "success": False,
                "response": f"Error: HTTP {response.status_code}",
                "time": elapsed
            }
    except Exception as e:
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            "time": round(time.time() - start, 2)
        }
"""

files['routers/mira.py'] = """from fastapi import APIRouter, HTTPException
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
"""

files['routers/planning.py'] = """from fastapi import APIRouter
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
"""

files['routers/risk.py'] = """from fastapi import APIRouter
from services.langflow import query_mira
import uuid

router = APIRouter(prefix="/api/risk", tags=["Risk"])

@router.post("/query")
async def risk_query(project: str):
    question = f"What are the major risks for {project}?"
    session_id = str(uuid.uuid4())
    result = await query_mira(question, session_id)
    return {
        "project": project,
        "question": question,
        "response": result["response"],
        "response_time": result["time"]
    }
"""

files['routers/governance.py'] = """from fastapi import APIRouter
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
"""

files['routers/__init__.py'] = ""
files['models/__init__.py'] = ""
files['services/__init__.py'] = ""

files['main.py'] = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import mira, planning, risk, governance
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="MIRA API",
    description="Project Intelligence Assistant - inaibridge.ai",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mira.router)
app.include_router(planning.router)
app.include_router(risk.router)
app.include_router(governance.router)

@app.get("/")
async def root():
    return {
        "service": "MIRA API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }
"""

files['requirements.txt'] = """fastapi==0.124.4
uvicorn==0.33.0
httpx==0.28.1
python-dotenv==1.0.1
pydantic==2.10.6
"""

for filepath, content in files.items():
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Created: {filepath}")

print("\nAll files created!")
