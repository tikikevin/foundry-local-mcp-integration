# Integrating Foundry Local with Your Docker-Hosted MCP Servers

By default, Foundry Local is an OpenAI-compatible inference engine—it doesn’t natively “plug in” MCP servers the way Azure’s cloud Agent Service does. However, you can build a simple Python agent layer that:

- Uses Foundry Local for LLM inference  
- Calls your local `mcp-fetch` and `mcp-playwright` containers as external tools  

Below is a step-by-step guide, including all the Python code you need.

---

## 1. Verify Your Endpoints

1. Start Foundry Local (if not already running):  
   ```bash
   foundry service start
   ```  
   By default it listens on `http://localhost:8080/v1`.  

2. In Docker Desktop, confirm your MCP servers are up and note their ports:  
   ```bash
   docker ps
   # e.g., 
   #   mcp-fetch      → 0.0.0.0:7001
   #   mcp-playwright → 0.0.0.0:7002
   ```

---

## 2. Create & Activate a Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install openai langchain requests
```

---

## 3. Write Tool Wrappers (`tools.py`)

```python
import requests

# Update these URLs if your containers map to different ports:
FETCH_URL = "http://localhost:7001/fetch"
PLAY_URL  = "http://localhost:7002/run"

def fetch_resource(path: str) -> str:
    """
    Call mcp-fetch to retrieve file contents by path.
    Returns the raw content string.
    """
    resp = requests.post(FETCH_URL, json={"path": path})
    resp.raise_for_status()
    data = resp.json()
    return data.get("content", "")

def run_playwright(script: str) -> str:
    """
    Call mcp-playwright to execute a Playwright script.
    Returns the textual output.
    """
    resp = requests.post(PLAY_URL, json={"script": script})
    resp.raise_for_status()
    data = resp.json()
    return data.get("output", "")
```

---

## 4. Configure the Foundry Local Client

```python
from openai import OpenAI

foundry = OpenAI(
    api_base="http://localhost:8080/v1",
    api_key="unused"         # Foundry Local ignores the key
)
```

---

## 5. Assemble a LangChain Agent (`agent.py`)

```python
from langchain.agents import Tool, initialize_agent
from langchain.llms import OpenAI

from tools import fetch_resource, run_playwright

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
```

---

## 6. Run & Validate

```bash
python agent.py
```

You should see:

- The raw contents of `example.txt`  
- The Playwright-scraped `<h1>` heading from example.com  

---

## Next Steps & Tips

- If your MCP containers require auth, pass headers in the `requests.post()` calls.  
- For heavy usage, add error-retry logic and timeouts around your HTTP calls.  
- You can bypass LangChain and orchestrate manually:  
  1. Call `foundry.chat.completions.create(...)` to get model’s decision.  
  2. Inspect the JSON for tool calls.  
  3. Invoke corresponding MCP HTTP endpoints.  
  4. Send a follow-up LLM call with the tool outputs.  

This pattern effectively bridges Foundry Local’s inference with your local MCP servers—no cloud Agent Service needed. Let me know if you need deeper dives into authentication, streaming responses, or custom orchestration!
