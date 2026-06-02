# 🤖 Free LangGraph Chatbot (Tavily + LangGraph)

A lightweight chatbot built with LangGraph and Streamlit that uses the Tavily API for web search responses. The app is designed to run locally with real-time search data and can optionally be extended to use Gemini for response generation.

## Features

- Intent detection: greeting, search, general chat
- Web search via the Tavily API (`tavily-python` client)
- Free response generation without OpenAI or Gemini by default
- Optional Gemini API support for richer LLM responses
- Conversation history persisted in Streamlit session state
- Simple Streamlit UI for quick local usage

## Architecture

The LangGraph flow in `app.py` is:

```
detect_intent
  ├─ greeting → greeting_node → history
  ├─ search → extract_query → search (web_search_node) → generate_response → history
  └─ general → generate_response → history
```

## Prerequisites

- Python 3.9 or newer
- `venv` virtual environment
- Tavily API key
- Optional Gemini API key for LLM-powered responses

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
# or
source venv/bin/activate    # macOS / Linux
```

2. Install dependencies:

```bash
pip install -r requirements.txt
pip install tavily-python
```

3. (Optional) Install Gemini integration packages if you want LLM responses:

```bash
pip install langchain-google-genai google-genai
```

4. Add your Tavily API key to a `.env` file in the repo root:

```bash
TAVILY_API_KEY=your_tavily_api_key_here
```

Optional Gemini environment variable:

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

If you prefer, you can also set the environment variable directly in your shell.

## Run the App

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

## Usage

- Ask a greeting: `Hello`
- Ask a web query: `What is LangGraph?`
- Ask a general question: `Tell me about free AI chatbots.`

If no search results are found, the app will return a friendly fallback response.

## File Overview

- `app.py`: main Streamlit application and LangGraph workflow
- `requirements.txt`: Python dependency list
- `README.md`: project documentation

## Environment Variables

- `TAVILY_API_KEY`: required for the Tavily search client

## Notes

- By default, this app uses Tavily for free search responses and does not require OpenAI/Gemini.
- Gemini API support can be enabled by installing `langchain-google-genai` and setting `GOOGLE_API_KEY`.
- The search result behavior is powered by the `tavily-python` package and `search_web()`.
- Use `streamlit run app.py` to launch the UI and test chat input.


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



