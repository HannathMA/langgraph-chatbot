import streamlit as st
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from datetime import datetime
from dotenv import load_dotenv
import os

from tavily import TavilyClient

# =========================
# LOAD ENV
# =========================
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# =========================
# TAVILY
# =========================
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# =========================
# WEB SEARCH
# =========================
def search_web(query: str):
    try:
        response = tavily.search(
            query=query,
            search_depth="basic",
            max_results=5
        )
        return response.get("results", [])
    except Exception as e:
        print("Search Error:", e)
        return []

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
# INTENT DETECTION
# =========================
def detect_intent(state: ChatState):

    msg = state["message"].lower()

    if any(word in msg for word in ["hi", "hello", "hey"]):
        intent = "greeting"

    elif any(word in msg for word in [
        "what",
        "who",
        "how",
        "why",
        "when",
        "where",
        "find",
        "search",
        "latest",
        "news"
    ]):
        intent = "search"

    else:
        intent = "general"

    return {"intent": intent}

# =========================
# GREETING NODE
# =========================
def greeting_node(state: ChatState):
    return {
        "response":
        "👋 Hello! I'm your Gemini + LangGraph chatbot. How can I help you today?"
    }

# =========================
# QUERY EXTRACTION
# =========================
def extract_query(state: ChatState):
    return {
        "search_query": state["message"]
    }

# =========================
# WEB SEARCH NODE
# =========================
def web_search_node(state: ChatState):

    query = state.get("search_query") or state["message"]

    results = search_web(query)

    context = ""
    formatted_results = []

    for r in results:

        title = r.get("title", "")
        content = r.get("content", "")
        url = r.get("url", "")

        context += f"""
Title: {title}

Content:
{content}

URL:
{url}

------------------------
"""

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
# RESPONSE GENERATION
# =========================
def generate_response(state: ChatState):
    question = state["message"].strip()
    context = state.get("context", "").strip()
    lower = question.lower()

    if context:
        return {
            "response": (
                "🧠 Answer based on the latest search results:\n\n"
                f"{context}\n"
                "If the search results do not fully answer your question, please ask again with more detail."
            )
        }

    if any(word in lower for word in ["love", "like", "care", "miss", "happy", "sad", "angry", "thanks", "thank you"]):
        return {
            "response": (
                "🤖 I’m here to chat! Thank you for sharing.\n\n"
                "I’m a free chatbot that can help by talking through questions and ideas, even without search results."
            )
        }

    if any(lower.startswith(w) for w in ["what", "who", "how", "why", "when", "where"]) or "?" in question:
        return {
            "response": (
                "🤖 I don't have web search results available right now, but I can still help you think it through.\n\n"
                f"You asked: {question}\n\n"
                "Try asking for a definition, explanation, or recommendation."
            )
        }

    return {
        "response": (
            "🤖 I’m not sure how to answer that yet, but I’m happy to keep chatting.\n\n"
            "Ask a question, say hello, or try a different topic."
        )
    }

# =========================
# HISTORY
# =========================
def update_history(state: ChatState):

    history = state.get("conversation_history", [])

    history.append({
        "user": state["message"],
        "bot": state.get("response", ""),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return {
        "conversation_history": history
    }

# =========================
# ROUTER
# =========================
def route(state: ChatState):
    return state["intent"]

# =========================
# BUILD GRAPH
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
st.set_page_config(
    page_title="Gemini LangGraph Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Gemini + LangGraph + Tavily Chatbot")

st.success("✅ Gemini AI Connected")

if "history" not in st.session_state:
    st.session_state.history = []

if "response" not in st.session_state:
    st.session_state.response = ""

if "last_search_results" not in st.session_state:
    st.session_state.last_search_results = []

message = st.text_input("Ask anything", key="message_input")

if st.button("Send"):
    if message:
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
        st.session_state.response = result.get("response", "")
        st.session_state.last_search_results = result.get("search_results", [])

        if not st.session_state.response:
            st.session_state.response = "No response returned from the chatbot."
    else:
        st.warning("Please type a message before sending.")

if st.session_state.response:
    st.markdown("### Response")
    st.markdown(st.session_state.response)

    with st.expander("Search Results"):
        st.json(st.session_state.last_search_results or [])
