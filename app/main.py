from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

# Import the compiled LangGraph app
from .graph import app as langgraph_app # Rename to avoid conflict with FastAPI app
from .graph import HRAState # Import state definition if needed elsewhere

logger = logging.getLogger("hra_main")
# Configure logging if not done elsewhere
# logging.basicConfig(level=logging.INFO)

# FastAPI app instance
fastapi_app = FastAPI(title="HRRecruitingAssistant") 

# Model for JSON-RPC A2A calls (keep as is)
class JSONRPCRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Optional[Dict[str, Any]] = {}
    id: Optional[int | str] = None

# --- A2A Endpoint (Using LangGraph) ---
@fastapi_app.post("/a2a")
async def handle_a2a(rpc_req: JSONRPCRequest):
    if rpc_req.jsonrpc != "2.0":
        return JSONResponse( # Use JSONResponse for explicit error structure
             status_code=400,
             content={
                 "jsonrpc": "2.0",
                 "id": rpc_req.id,
                 "error": {"code": -32600, "message": "Invalid JSON-RPC version"}
             }
        )

    if rpc_req.method != "start_recruiting_workflow":
         return JSONResponse(
             status_code=404, # Method Not Found
             content={
                 "jsonrpc": "2.0",
                 "id": rpc_req.id,
                 "error": {"code": -32601, "message": "Method not found"}
             }
         )

    # Prepare the initial state for LangGraph
    initial_state = rpc_req.params

    try:
        # Invoke the compiled LangGraph app       
        final_state = await langgraph_app.ainvoke(initial_state)

        # Decide what result to return based on the final state.Example: return the number of candidates found or saved
        result_data = {
             "message": f"Workflow completed. Found {len(final_state.get('candidates', []))} candidates.",
             "final_token": final_state.get('token'), # Example data from state
             "candidates_found": final_state.get('candidates', []) # Example
        }

        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "result": result_data
        }

    except Exception as e:
        logger.exception(f"Error executing LangGraph workflow via A2A for ID {rpc_req.id}: {e}")
        # Return a JSON-RPC internal error
        return JSONResponse(
             status_code=500, # Internal Server Error for the workflow execution
             content={
                 "jsonrpc": "2.0",
                 "id": rpc_req.id,
                 "error": {
                     "code": -32603,
                     "message": "Internal workflow error",
                     "data": str(e) # Include error details
                 }
             }
        )


# --- GET Endpoint for Testing (Using LangGraph) ---
# Pydantic model for query parameters to make validation easier
class WorkflowParams(BaseModel):
    username: str
    password: str
    title: str
    skills: str

@fastapi_app.get("/run_workflow")
async def run_workflow(params: WorkflowParams = Depends()): 
    # Prepare the initial state dictionary from query parameters
    initial_state = params.dict()

    try:
        logger.info(f"Running workflow with params: {initial_state}")
        # Invoke the compiled LangGraph app
        final_state = await langgraph_app.ainvoke(initial_state)

        # Extract relevant info from the final state for the response
        candidates_found = final_state.get('candidates', [])
        message = f"Workflow completed. Found {len(candidates_found)} candidates."        

        logger.info(f"Workflow completed. Final state (partial): token={final_state.get('token')}, num_candidates={len(candidates_found)}")

        return {"message": message, "candidates": candidates_found}

    except Exception as e:
        logger.exception(f"Error executing LangGraph workflow via GET: {e}")        
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

app = fastapi_app