from langchain.agents import Tool, initialize_agent
from langchain.llms import OpenAI
from openai import OpenAI

from tools import fetch_resource, run_playwright

foundry = OpenAI(
    api_base="http://localhost:8080/v1",
    api_key="unused"         # Foundry Local ignores the key
)

# Define tools for the agent
tools = [
    Tool(
        name="fetch",
        func=fetch_resource,
        description="Fetch the content of a local file given its path"
    ),
    Tool(
        name="playwright",
        func=run_playwright,
        description="Run a Playwright script and return its output"
    )
]

# LLM pointing to Foundry Local
llm = OpenAI(
    streaming=False,
    openai_api_key="x",     # dummy
    openai_api_base="http://localhost:8080/v1",
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

if __name__ == "__main__":
    prompt = """
    1. Use the fetch tool to read '/data/example.txt'.
    2. Based on its contents, write and run a Playwright script that
       navigates to example.com, grabs the first <h1> text, and returns it.
    Please show both the fetched file content and the scraped heading.
    """
    result = agent.run(prompt)
    print("\n===== Agent Output =====\n", result)