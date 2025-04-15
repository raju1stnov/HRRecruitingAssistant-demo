import os

# URLs for all agents (using Docker DNS or ENV overrides)
AUTH_AGENT_URL = os.getenv("AUTH_AGENT_URL", "http://auth_agent:8000/a2a")
WEBSERVICE_AGENT_URL = os.getenv("WEBSERVICE_AGENT_URL", "http://webservice_agent:8000/a2a")
DBSERVICE_AGENT_URL = os.getenv("DBSERVICE_AGENT_URL", "http://dbservice_agent:8000/a2a")

# Optionally resolve from registry instead of hardcoding
USE_REGISTRY = os.getenv("USE_A2A_REGISTRY", "false").lower() == "true"
REGISTRY_URL = os.getenv("A2A_REGISTRY_URL", "http://a2a_registry:8000/a2a")