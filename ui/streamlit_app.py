"""Streamlit demo UI for ToolRouter.

Run with: streamlit run ui/streamlit_app.py
Talks to the FastAPI backend over HTTP, so start the API first:
    uvicorn app.main:app --reload
"""
import os

import requests
import streamlit as st

API_URL = os.getenv("TOOLROUTER_API_URL", "https://toolrouter.onrender.com")
st.set_page_config(page_title="ToolRouter", page_icon="🧭", layout="centered")
st.title("🧭 ToolRouter")
st.caption("Intelligent tool-selection framework — query → route → permission check → execute → answer")

with st.form("query_form"):
    query = st.text_input("Query", placeholder="e.g. What is the leave policy?")
    role = st.selectbox("Role", ["guest", "employee", "admin"], index=1)
    submitted = st.form_submit_button("Execute")

EXAMPLES = [
    "Calculate 125 * 48",
    "What is the leave policy?",
    "Find employee 105",
    "Search for information about Python",
]
st.caption("Try: " + " · ".join(f"`{q}`" for q in EXAMPLES))

if submitted:
    if not query.strip():
        st.warning("Enter a query first.")
    else:
        try:
            resp = requests.post(f"{API_URL}/chat", json={"query": query, "role": role}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            st.error(f"Can't reach the API at {API_URL}. Is `uvicorn app.main:app --reload` running?")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Request failed: {exc}")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Selected tool", data["tool"] or "none")
            col2.metric("Permission", "✅ Granted" if data["permission"]["granted"] else "🚫 Denied")
            col3.metric("Latency", f"{data['latency_ms']:.1f} ms")

            if not data["permission"]["granted"]:
                st.info(data["permission"]["reason"])

            st.subheader("Answer")
            st.write(data["answer"])

            with st.expander("Full routing scores (all candidate tools)"):
                st.json(data["candidates"])

st.divider()
st.caption("Roles: guest < employee < admin — permission is checked *after* routing, "
           "so a denied request still shows which tool it would have used.")
