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