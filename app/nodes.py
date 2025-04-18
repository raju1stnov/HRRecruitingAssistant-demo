import httpx
import logging
from typing import Dict, Any, List, Optional # Import Dict, Any, List, Optional
from . import config
# Assuming HRAState is defined elsewhere (e.g., imported from graph.py or a state.py)
# from .graph import HRAState # Or wherever HRAState lives

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
            # Add a timeout to prevent indefinite hangs
            resp = await client.post(agent_url, json=payload, timeout=15.0)
            resp.raise_for_status() # Raise HTTP errors
            data = resp.json()
            if "error" in data:
                logger.error(f"A2A error response: {data['error']}")
                # Propagate error details for better debugging
                raise Exception(f"A2A Error from {agent_url} calling {method}: {data['error']}")
            return data["result"]
    except httpx.TimeoutException as e:
         logger.exception(f"A2A call to {agent_url} timed out:")
         raise Exception(f"A2A Timeout calling {agent_url} for method {method}") from e
    except Exception as e:
        logger.exception(f"A2A call to {agent_url} failed:")
        # Re-raise with more context if it's not already an A2A Error Exception
        if "A2A Error" not in str(e):
             raise Exception(f"Failed A2A call to {agent_url} for method {method}") from e
        else:
             raise # Re-raise the specific A2A error exception

async def authenticate_user(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Authenticating user...")
    try:
        result = await a2a_call(
            config.AUTH_AGENT_URL,
            method="login",
            params={"username": state["username"], "password": state["password"]},
        )
        logger.info(f"Auth result: {result}")
        if isinstance(result, dict) and result.get("success") and "token" in result:
            # Return only the state update
            return {"token": result["token"]}
        else:
             # Include the reason for failure if available
             error_msg = result.get("error", "Authentication failed or malformed response.") if isinstance(result, dict) else "Authentication failed or malformed response."
             raise Exception(error_msg)
    except Exception as e:
         logger.error(f"Authentication Exception: {e}")
         # You might want specific error handling or state updates here
         # For now, just re-raising will stop the graph execution.
         raise Exception(f"Authentication failed: {e}") from e

async def search_candidates(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Searching for candidates...")
    if not state.get("token"):
         raise Exception("Cannot search candidates without authentication token.")
    try:
        result = await a2a_call(
            config.WEBSERVICE_AGENT_URL,
            method="search_candidates",
            params={"title": state["title"], "skills": state["skills"]}
        )
        logger.info(f"Search result: {result}")
        if isinstance(result, list):
            # Return only the state update
            return {"candidates": result}
        else:
             # Handle unexpected search result format
             logger.error(f"Search candidates returned non-list result: {result}")
             raise Exception("Search candidates failed or returned invalid result format.")
    except Exception as e:
         logger.error(f"Search Candidates Exception: {e}")
         raise Exception(f"Search candidates failed: {e}") from e

async def save_candidates(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Saving candidates...")
    candidates_to_save = state.get("candidates")
    if not candidates_to_save:
        logger.warning("No candidates found in state to save.")
        # Return None or empty dict to indicate no state change needed here
        return {} # No state change, just proceed

    saved_count = 0
    errors = []
    for c in candidates_to_save:
        params_to_send = {
            "name": c.get("name"),
            "title": c.get("title"),
            "skills": c.get("skills")
        }
        # Basic validation before sending
        if not params_to_send["name"] or not params_to_send["title"] or not params_to_send["skills"]:
             logger.warning(f"Skipping candidate due to missing data: {c}")
             errors.append(f"Missing data for candidate: {c.get('name', 'N/A')}")
             continue

        logger.info(f"Attempting to save candidate. PARAMS: {params_to_send}")
        try:
            await a2a_call(
                config.DBSERVICE_AGENT_URL,
                method="create_record",
                params=params_to_send
            )
            saved_count += 1
        except Exception as e:
             logger.error(f"Failed to save candidate {params_to_send.get('name', 'N/A')}: {e}")
             errors.append(f"Failed to save {params_to_send.get('name', 'N/A')}: {e}")            

    logger.info(f"Finished saving. Saved: {saved_count}, Errors: {len(errors)}")
    if errors:      
        pass    
    return {}