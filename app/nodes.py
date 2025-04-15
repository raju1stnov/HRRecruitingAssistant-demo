import httpx
import logging
from . import config

logger = logging.getLogger("hra_nodes")

async def a2a_call(agent_url: str, method: str, params: dict, id: int = 1):
    logger.info(f"Attempting A2A call to URL: {agent_url} for method: {method}")
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": id
    }
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Calling A2A method '{method}' on {agent_url} with: {params}")
            resp = await client.post(agent_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                logger.error(f"A2A error response: {data['error']}")
                raise Exception(data["error"])
            return data["result"]
    except Exception as e:
        logger.exception(f"A2A call to {agent_url} failed:")
        raise

async def authenticate_user(state):
    logger.info("Authenticating user...")
    result = await a2a_call(
        config.AUTH_AGENT_URL,
        method="login",
        params={"username": state.username, "password": state.password},
    )
    logger.info(f"Auth result: {result}")
    if isinstance(result, dict) and "token" in result:
        state.token = result["token"]
        return "search_candidates"
    raise Exception("Authentication failed or malformed response.")

async def search_candidates(state):
    logger.info("Searching for candidates...")
    result = await a2a_call(
        config.WEBSERVICE_AGENT_URL,
        method="search_candidates",
        params={"title": state.title, "skills": state.skills}
    )
    logger.info(f"Search result: {result}")
    if isinstance(result, list):
        state.candidates = result
        return "save_candidates"
    raise Exception("Search candidates failed or invalid result.")

async def save_candidates(state):
    logger.info("Saving candidates...")
    for c in state.candidates:
        params_to_send = {
            "name": c.get("name"),
            "title": c.get("title"),
            "skills": c.get("skills")
        }        
        logger.info(f"Attempting to save candidate. PARAMS: {params_to_send}")
        await a2a_call(
            config.DBSERVICE_AGENT_URL,
            method="create_record",
            params=params_to_send
        )
    return None
