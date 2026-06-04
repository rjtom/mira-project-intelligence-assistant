from pydantic import BaseModel
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
