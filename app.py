import streamlit as st
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
import os
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient

# =========================
# LOAD ENV
# =========================
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# =========================
# TAVILY SETUP
# =========================
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def search_web(query: str):
    """Web search using Tavily"""
    response = tavily.search(
        query=query,
        search_depth="basic",
        max_results=5
    )
    return response.get("results", [])

# =========================
# STATE
# =========================
class ChatState(TypedDict):
    message: str
    intent: str
    search_query: str
    search_results: Optional[List[dict]]
    context: str
    response: str
    conversation_history: List[dict]
    timestamp: str

# =========================
# 1. INTENT DETECTION
# =========================
def detect_intent(state: ChatState) -> dict:
    msg = state["message"].lower()

    if any(w in msg for w in ["hi", "hello", "hey"]):
        intent = "greeting"
    elif any(w in msg for w in ["what", "who", "how", "why", "find", "search"]):
        intent = "search"
    else:
        intent = "general"

    return {"intent": intent}

# =========================
# 2. GREETING
# =========================
def greeting_node(state: ChatState) -> dict:
    return {
        "response": "👋 Hello! I am your FREE AI chatbot (no OpenAI needed). Ask me anything!"
    }

# =========================
# 3. QUERY EXTRACTION
# =========================
def extract_query(state: ChatState) -> dict:
    return {"search_query": state["message"]}

# =========================
# 4. WEB SEARCH
# =========================
def web_search_node(state: ChatState) -> dict:
    query = state.get("search_query") or state["message"]

    results = search_web(query)

    context = ""
    formatted_results = []

    for r in results:
        title = r.get("title", "")
        content = r.get("content", r.get("snippet", ""))
        url = r.get("url", "")

        context += f"{title}\n{content}\n{url}\n\n"

        formatted_results.append({
            "title": title,
            "content": content,
            "url": url
        })

    return {
        "search_results": formatted_results,
        "context": context
    }

# =========================
# 5. FREE RESPONSE GENERATOR (NO OPENAI)
# =========================
def generate_response(state: ChatState) -> dict:
    """
    FREE fallback AI logic (no API cost)
    Uses search context to build answer
    """

    context = state.get("context", "")

    if context:
        response = f"""
🧠 **Answer based on web search:**

{context}

✨ This response was generated using real-time search data (FREE mode).
"""
    else:
        response = f"""
🤖 I couldn't find web results.

But here's a simple explanation for:
👉 {state['message']}

This is a free-mode response without AI model API.
"""

    return {"response": response}

# =========================
# 6. HISTORY
# =========================
def update_history(state: ChatState) -> dict:
    history = state.get("conversation_history", [])

    history.append({
        "user": state["message"],
        "bot": state.get("response", ""),
        "time": datetime.now().isoformat()
    })

    return {"conversation_history": history}

# =========================
# ROUTER
# =========================
def route(state: ChatState):
    return state["intent"]

# =========================
# LANGGRAPH BUILD
# =========================
graph = StateGraph(ChatState)

graph.add_node("detect_intent", detect_intent)
graph.add_node("greeting", greeting_node)
graph.add_node("extract_query", extract_query)
graph.add_node("search", web_search_node)
graph.add_node("generate", generate_response)
graph.add_node("history", update_history)

graph.set_entry_point("detect_intent")

graph.add_conditional_edges(
    "detect_intent",
    route,
    {
        "greeting": "greeting",
        "search": "extract_query",
        "general": "generate"
    }
)

graph.add_edge("extract_query", "search")
graph.add_edge("search", "generate")

graph.add_edge("greeting", "history")
graph.add_edge("generate", "history")
graph.add_edge("history", END)

app = graph.compile()

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="FREE LangGraph Chatbot", layout="wide")

st.title("🤖 FREE LangGraph Chatbot (No OpenAI)")

st.success("✅ Running in FREE MODE (Tavily + LangGraph)")

if "history" not in st.session_state:
    st.session_state.history = []

message = st.text_input("Ask something:")

if st.button("Send") and message:

    result = app.invoke({
        "message": message,
        "intent": "",
        "search_query": "",
        "search_results": [],
        "context": "",
        "response": "",
        "conversation_history": st.session_state.history,
        "timestamp": str(datetime.now())
    })

    st.session_state.history = result["conversation_history"]

    st.success("Response")
    st.markdown(result["response"])

    with st.expander("Details"):
        st.write("Intent:", result.get("intent"))
        st.write("Search Results:", result.get("search_results", []))