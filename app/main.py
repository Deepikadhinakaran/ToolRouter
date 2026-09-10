from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

from app.agent import run_agent  # noqa: E402  (must load .env first)
from app.registry import all_tools  # noqa: E402
from app.security import ROLE_RANK  # noqa: E402

app = FastAPI(title="ToolRouter", description="Intelligent tool selection framework", version="0.1.0")


class ChatRequest(BaseModel):
    query: str
    role: str = "employee"


class ChatResponse(BaseModel):
    answer: str
    tool: str | None
    status: str
    permission: dict
    latency_ms: float
    candidates: list[dict]


@app.get("/")
def root():
    return {"service": "ToolRouter", "status": "ok", "roles": list(ROLE_RANK), "tools": [t["name"] for t in all_tools()]}


@app.get("/tools")
def list_tools():
    return {"tools": all_tools()}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = run_agent(req.query, req.role)
    return ChatResponse(
        answer=result["answer"],
        tool=result["selected_tool"],
        status=result["tool_status"],
        permission=result["permission"],
        latency_ms=result["trace"].total_ms(),
        candidates=result["routing"]["candidates"],
    )
