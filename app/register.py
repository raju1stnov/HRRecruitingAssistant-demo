import httpx
import os

A2A_REGISTRY_URL = os.getenv("A2A_REGISTRY_URL", "http://a2a_registry:8000/a2a")
AGENT_CARD = {
    "jsonrpc": "2.0",
    "method": "register_agent",
    "params": {
        "name": "hr_recruiting_assistant",
        "url": "http://hr_recruiting_assistant:8005/a2a",
        "description": "LangGraph-powered agent for recruiting workflow",
        "methods": ["start_recruiting_workflow"]
    },
    "id": 1
}

if __name__ == "__main__":
    try:
        response = httpx.post(A2A_REGISTRY_URL, json=AGENT_CARD, timeout=5.0)
        print("Registered:", response.json())
    except Exception as e:
        print("Registration failed:", str(e))
