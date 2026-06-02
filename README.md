# 🤖 Advanced LangGraph Chatbot with Google Search

A sophisticated, multi-node chatbot powered by LangGraph that integrates Google Search API for real-time information retrieval and OpenAI GPT for intelligent response generation.

## Features

✨ **Multi-Intent Detection**: Automatically detects user intents (greeting, search, support, general questions)

🔍 **Pluggable Web Search Integration**: Uses a `search_web(query)` helper (placeholder) so you can plug in Google Custom Search, Bing, DuckDuckGo, or any other search provider

🧠 **LLM-Powered Responses**: Uses OpenAI GPT to generate contextual, intelligent responses

📊 **Conversation History**: Maintains and displays chat history with reasoning

🔄 **Complex Workflow**: Multi-node LangGraph workflow with conditional routing

🎨 **Beautiful UI**: Built with Streamlit for an interactive web interface

## System Architecture

```
detect_intent
    ├── greeting → greeting_node
    ├── search → extract_query → search (web search node) → llm
    ├── support → support_node
    └── general_question → generate_response

High-level entry point: `search` → `llm` → END
All paths → update_history → END
```

## Prerequisites

- Python 3.9+
- Virtual environment (venv)
- Google Search API credentials
- OpenAI API key

## Setup Instructions

### 1. Install Dependencies

```bash
# Activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Keys

#### Google Search API Setup:
1. Go to [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Create a new search engine
3. Get your Search Engine ID
4. Enable Custom Search API in [Google Cloud Console](https://console.cloud.google.com/)
5. Create an API key

#### OpenAI API Setup:
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Generate a new API key
3. Keep it secure (never share)

#### Set Environment Variables:

**Option A: Create a `.env` file** (recommended for local development)
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
GOOGLE_API_KEY=your_key_here
GOOGLE_SEARCH_ENGINE_ID=your_id_here
OPENAI_API_KEY=your_key_here
```

**Option B: Use Streamlit Secrets** (recommended for deployed apps)
```bash
# Create ~/.streamlit/secrets.toml (Windows: %userprofile%\.streamlit\secrets.toml)
GOOGLE_API_KEY = "your_key_here"
GOOGLE_SEARCH_ENGINE_ID = "your_id_here"
OPENAI_API_KEY = "your_key_here"
```

### 3. Run the Application

```bash
streamlit run app.py
```

The chatbot will open at `http://localhost:8501`

## Usage Examples

### Greeting
- User: "Hello"
- Bot: Responds with a welcome message

### Web Search
- User: "Find information about artificial intelligence"
- Bot: Searches Google, fetches results, and provides a comprehensive answer

### Support Query
- User: "I need help"
- Bot: Provides available support options

### General Question
- User: "What is machine learning?"
- Bot: Uses LLM to generate an answer based on its knowledge

## State Structure

The chatbot maintains the following state:

```python
class ChatState(TypedDict):
    message: str                          # User input
    intent: str                          # Detected intent
    search_query: str                    # Extracted search query
    search_results: Optional[List[str]]  # Google search results
    context: str                         # Formatted search context
    reasoning: str                       # Explanation of reasoning
    response: str                        # Final response
    conversation_history: List[dict]     # Chat history
    timestamp: str                       # Timestamp
```

## Node Descriptions

| Node | Purpose |
|------|---------|
| `detect_intent` | Analyzes user message to determine intent type |
| `greeting` | Handles greeting intents |
| `extract_query` | Extracts search query from message |
| `search` / `google_search` | Performs web search using `search_web(query)` helper and retrieves results |
| `generate_response` | Uses LLM to generate response with context |
| `support` | Handles support-related queries |
| `update_history` | Updates conversation history |

## Environment Variables

- `GOOGLE_API_KEY`: Your Google Custom Search API key
# 🤖 FREE LangGraph Chatbot (Tavily + LangGraph)

This repository contains a lightweight chatbot built with LangGraph and Streamlit that performs real-time web searches using the Tavily API (no OpenAI required). It's a cost-free mode by design — search-powered responses are composed from retrieved web content.

## Key Changes

- Replaced OpenAI LLM usage with a free search-driven response generator.
- Uses the `tavily` Python client for web search results.
- LangGraph workflow updated to use `detect_intent -> extract_query -> search -> generate -> history`.

## Features

- Intent detection (greeting, search, general)
- Web search via Tavily (`tavily-python` client)
- Free-mode response generation (no external LLM costs)
- Conversation history stored in-session
- Streamlit UI for quick local usage

## System Architecture

```
detect_intent
    ├── greeting → greeting_node → history
    ├── search → extract_query → search (web_search_node) → generate → history
    └── general → generate → history
```

Entry point: `detect_intent` (configured in `app.py`).

## Prerequisites

- Python 3.9+
- Virtual environment (recommended)
- Tavily API key (set `TAVILY_API_KEY`)

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
# or
source venv/bin/activate    # macOS / Linux
```

2. Install dependencies (add `tavily` if not in `requirements.txt`):

```bash
pip install -r requirements.txt
pip install tavily-python
```

3. Set environment variables (create a `.env` file at repo root):

```
TAVILY_API_KEY=your_tavily_api_key_here
```

4. Run the app:

```bash
streamlit run app.py
```

App UI will be available at `http://localhost:8501`.

## File: `app.py` Overview

- `TavilyClient` is initialized with `TAVILY_API_KEY` from the environment.
- `search_web(query)` uses the `tavily` client and returns a list of results.
- Core LangGraph nodes:
  - `detect_intent` — decide intent from user message
  - `greeting` — returns a welcome message
  - `extract_query` — extracts query from the message
  - `search` (`web_search_node`) — performs the web search via Tavily
  - `generate` (`generate_response`) — builds a free-mode response using search context
  - `history` — appends conversation to session history

## State Structure

```python
class ChatState(TypedDict):
    message: str
    intent: str
    search_query: str
    search_results: Optional[List[dict]]
    context: str
    response: str
    conversation_history: List[dict]
    timestamp: str
```

## Usage Examples

- Greeting: "Hello" → bot replies with a friendly welcome message
- Search: "Find information about AI" → bot performs a Tavily web search and returns a response compiled from search results
- General question: Bot attempts a simple free-mode explanation when no web context is found

## Environment Variables

- `TAVILY_API_KEY`: API key for Tavily web search

## Troubleshooting

- If responses are empty: ensure `TAVILY_API_KEY` is set and valid in `.env`.
- If no search results: try different queries or increase `max_results` in `search_web`.

## Extensibility

- You can replace the `search_web` implementation with any search provider (Google/Bing/DuckDuckGo) — keep the return format `[{"title":..., "content":..., "url":...}, ...]`.
- If you want to reintroduce an LLM backend later, plug it into `generate_response`.

## Development Notes

- The app runs in "FREE MODE" by default — no OpenAI keys required.
- Conversation history is stored only in `st.session_state` and is not persisted.

## License

MIT

## Support

Open an issue or edit the code directly to customize behavior.
- [ ] Implement caching with Redis
