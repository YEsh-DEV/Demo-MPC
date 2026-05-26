import os
import sys
import asyncio
import warnings

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from mcp_use import MCPAgent, MCPClient
from tavily import TavilyClient

# Suppress resource warnings for cleaner CLI output
warnings.filterwarnings("ignore", category=ResourceWarning)

# Load environment variables from the local .env file
load_dotenv()


async def add_extra_tools(agent: MCPAgent, extra_tools: list) -> None:
    """Attach additional LangChain tools and rebuild the agent."""
    if not extra_tools:
        return
    agent._tools.extend(extra_tools)
    await agent._create_system_message_from_tools(agent._tools)
    agent._agent_executor = agent._create_agent()


async def run_memory_chat():
    """Simple chat example using MCP with built-in conversation memory."""
    print("Initializing Gemini...")

    gemini_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        sys.exit(1)

    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        print("Error: TAVILY_API_KEY not found in environment variables.")
        sys.exit(1)

    # Initialize the LLM (override with GEMINI_MODEL env var)
    model_name = "gemini-2.5-flash"
    print(f"Using Gemini model: {model_name}")

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=gemini_key,
        temperature=0,
    )

    tavily = TavilyClient(api_key=tavily_key)

    @tool("tavily_web_search")
    def tavily_web_search(query: str) -> str:
        """Search the live web for current information."""
        try:
            response = tavily.search(query=query, search_depth="basic")
            results = response.get("results", [])
            if not results:
                return "No results found."

            output = []
            for res in results:
                title = res.get("title", "")
                url = res.get("url", "")
                snippet = res.get("content", "")
                output.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}\n---")
            return "\n".join(output)
        except Exception as exc:
            return f"Error performing web search: {exc}"

    print("Loading MCP configuration from browseing.json...")
    client = MCPClient.from_config_file("browseing.json")

    try:
        print("Starting MCP Client and initializing agent...")
        agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=10,
            memory_enabled=True,
        )

        await agent.initialize()
        await add_extra_tools(agent, [tavily_web_search])
        print("Connecting to MCP servers...")
        print("\n=== MCP Chat Agent Started ===")
        print("Type 'exit' or 'quit' to end the session.")

        while True:
            try:
                user_input = input("\nYou: ")
            except (KeyboardInterrupt, EOFError):
                break

            if user_input.lower() in ["exit", "quit"]:
                break

            if not user_input.strip():
                continue

            print("\nAssistant: ", end="", flush=True)
            response = await agent.run(user_input)
            print(response)

    finally:
        print("\nClosing MCP client sessions...")
        await client.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(run_memory_chat())
