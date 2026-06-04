from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers import mira, planning, risk, governance, email
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="MIRA API",
    description="Project Intelligence Assistant - Capstone Demo",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Budget tracking
BUDGET_FILE = "budget_tracker.json"
MAX_BUDGET = float(os.getenv("MAX_DEMO_BUDGET", "25.0"))
COST_PER_QUERY = 0.05

def load_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, 'r') as f:
            return json.load(f)
    return {"total_queries": 0, "total_cost": 0.0, "started": datetime.now().isoformat()}

def save_budget(data):
    with open(BUDGET_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def check_budget():
    data = load_budget()
    return data["total_cost"] < MAX_BUDGET, data

def increment_budget():
    data = load_budget()
    data["total_queries"] += 1
    data["total_cost"] = round(data["total_cost"] + COST_PER_QUERY, 4)
    data["last_query"] = datetime.now().isoformat()
    save_budget(data)
    return data

# Budget middleware
@app.middleware("http")
async def budget_check_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/") and request.method == "POST":
        within_budget, data = check_budget()
        if not within_budget:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Demo budget exceeded",
                    "message": "MIRA demo budget has been reached. Please contact Raju Thomas.",
                    "total_queries": data["total_queries"],
                    "total_cost": data["total_cost"]
                }
            )
        increment_budget()
    response = await call_next(request)
    return response

app.include_router(mira.router)
app.include_router(planning.router)
app.include_router(risk.router)
app.include_router(governance.router)
app.include_router(email.router)

@app.get("/")
async def root():
    within_budget, data = check_budget()
    return {
        "service": "MIRA API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "demo_budget": {
            "total_queries": data["total_queries"],
            "total_cost": f"${data['total_cost']}",
            "budget_remaining": f"${round(MAX_BUDGET - data['total_cost'], 2)}",
            "within_budget": within_budget
        }
    }

@app.get("/budget")
async def budget_status():
    within_budget, data = check_budget()
    return {
        "total_queries": data["total_queries"],
        "total_cost": f"${data['total_cost']}",
        "max_budget": f"${MAX_BUDGET}",
        "budget_remaining": f"${round(MAX_BUDGET - data['total_cost'], 2)}",
        "within_budget": within_budget,
        "started": data.get("started", "unknown"),
        "last_query": data.get("last_query", "none")
    }
