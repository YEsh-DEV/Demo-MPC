# Demo-MPC

A minimal MCP chat agent using Gemini and a Tavily web search tool.

## Requirements

- Python 3.14+
- Node.js (for MCP servers launched via `npx`)

## Setup

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_gemini_key
TAVILY_API_KEY=your_tavily_key
# Optional: override model
GEMINI_MODEL=gemini-1.5-flash
```

Install dependencies (pick one):

```powershell
python -m pip install -U langchain-google-genai mcp-use python-dotenv tavily-python
```

```powershell
uv add langchain-google-genai mcp-use python-dotenv tavily-python
```

## Run

```powershell
python main.py
```

## Notes

- If you see a model not found error, set `GEMINI_MODEL` to a model your key supports (e.g. `gemini-2.0-flash`).
- MCP servers are configured in `browseing.json`.

## Ouput 
<img width="999" height="806" alt="image" src="https://github.com/user-attachments/assets/46d7f37b-6606-4a4f-90bd-051859a8455e" />
