"""LangGraph agent: analyze_query -> select_tool -> check_permission ->
execute_tool -> generate_response.

Runs fully deterministically with no API key. If OPENAI_API_KEY is set,
generate_response uses the LLM to phrase the final answer from the tool's
raw result; otherwise it formats the raw result directly.
"""
import os
from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.registry import get_tool
from app.router import route
from app.security import check_permission
from app.tracing import Trace, log_event


class AgentState(TypedDict, total=False):
    query: str
    role: str
    trace: Trace
    routing: dict
    selected_tool: str | None
    permission: dict
    tool_status: str
    tool_result: object
    answer: str


def analyze_query(state: AgentState) -> AgentState:
    state["trace"].step("analyze_query", query=state["query"])
    return state


def select_tool(state: AgentState) -> AgentState:
    routing = route(state["query"], state["role"])
    state["routing"] = routing
    state["selected_tool"] = routing["selected"]
    state["trace"].step("select_tool", selected=routing["selected"])
    return state


def check_permission_node(state: AgentState) -> AgentState:
    tool_name = state["selected_tool"]
    if tool_name is None:
        state["permission"] = {"granted": False, "reason": "No eligible tool for this role/query."}
    else:
        tool = get_tool(tool_name)
        state["permission"] = check_permission(state["role"], tool["meta"])
    state["trace"].step("check_permission", **state["permission"])
    return state


def execute_tool(state: AgentState) -> AgentState:
    if not state["permission"]["granted"]:
        state["tool_status"] = "rejected"
        state["tool_result"] = state["permission"]["reason"]
        state["trace"].step("execute_tool", status="rejected")
        return state

    tool_name = state["selected_tool"]
    tool = get_tool(tool_name)
    try:
        outcome = tool["run"](state["query"])
        state["tool_status"] = outcome.get("status", "success")
        state["tool_result"] = outcome.get("result")
    except Exception as exc:  # noqa: BLE001 — fallback path
        state["tool_status"] = "error"
        state["tool_result"] = f"Tool '{tool_name}' raised: {exc}"

    # Fallback: if the primary tool failed outright, retry via the generic
    # search tool so a broken/unavailable tool doesn't hard-fail the request.
    if state["tool_status"] == "error" and tool_name != "search":
        search_tool = get_tool("search")
        fallback_outcome = search_tool["run"](state["query"])
        state["tool_status"] = "fallback_success"
        state["tool_result"] = fallback_outcome.get("result")
        state["selected_tool"] = "search (fallback)"

    state["trace"].step("execute_tool", status=state["tool_status"])
    return state


def generate_response(state: AgentState) -> AgentState:
    raw = state["tool_result"]

    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        prompt = (
            f"User asked: {state['query']}\n"
            f"Tool '{state['selected_tool']}' returned: {raw}\n"
            "Write a short, direct answer for the user based only on this data."
        )
        state["answer"] = llm.invoke(prompt).content
    else:
        state["answer"] = str(raw)

    state["trace"].step("generate_response")

    log_event(
        {
            "user_role": state["role"],
            "query": state["query"],
            "selected_tool": state["selected_tool"],
            "permission_granted": state["permission"]["granted"],
            "status": state["tool_status"],
            "latency_ms": state["trace"].total_ms(),
        }
    )
    return state


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("analyze_query", analyze_query)
    workflow.add_node("select_tool", select_tool)
    workflow.add_node("check_permission", check_permission_node)
    workflow.add_node("execute_tool", execute_tool)
    workflow.add_node("generate_response", generate_response)

    workflow.set_entry_point("analyze_query")
    workflow.add_edge("analyze_query", "select_tool")
    workflow.add_edge("select_tool", "check_permission")
    workflow.add_edge("check_permission", "execute_tool")
    workflow.add_edge("execute_tool", "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile()


_GRAPH = build_graph()


def run_agent(query: str, role: str) -> AgentState:
    initial: AgentState = {"query": query, "role": role, "trace": Trace()}
    result = _GRAPH.invoke(initial)
    return result
