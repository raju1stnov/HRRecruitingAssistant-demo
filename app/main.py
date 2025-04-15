from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from .graph import get_graph, HRAState

logger = logging.getLogger("hra_main")
app = FastAPI(title="HRRecruitingAssistant")

class JSONRPCRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Optional[Dict[str, Any]] = {}
    id: Optional[int | str] = None

@app.post("/a2a")
async def handle_a2a(rpc_req: JSONRPCRequest):
    if rpc_req.jsonrpc != "2.0":
        raise HTTPException(status_code=400, detail="Invalid JSON-RPC version")

    if rpc_req.method != "start_recruiting_workflow":
        return {"jsonrpc": "2.0", "id": rpc_req.id, "error": {"code": -32601, "message": "Method not found"}}

    state = HRAState(**rpc_req.params)
    nodes, transitions, _ = get_graph()

    current = "authenticate_user"
    while current:
        node_func = nodes[current]
        current = await node_func(state)

    return {"jsonrpc": "2.0", "id": rpc_req.id, "result": {"candidates_saved": len(state.candidates)}}

@app.get("/run_workflow")
async def run_workflow(username: str, password: str, title: str, skills: str):
    state = HRAState(username=username, password=password, title=title, skills=skills)
    nodes, transitions, _ = get_graph()

    current = "authenticate_user"
    while current:
        node_func = nodes[current]
        current = await node_func(state)

    return {"message": f"Saved {len(state.candidates)} candidates", "candidates": state.candidates}