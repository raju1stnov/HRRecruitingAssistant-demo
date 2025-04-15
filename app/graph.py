from pydantic import BaseModel
from typing import Optional, List
from .nodes import authenticate_user, search_candidates, save_candidates

class HRAState(BaseModel):
    username: str
    password: str
    title: str
    skills: str
    token: Optional[str] = None
    candidates: Optional[List[dict]] = []

nodes = {
    "authenticate_user": authenticate_user,
    "search_candidates": search_candidates,
    "save_candidates": save_candidates
}

transitions = {
    "authenticate_user": "search_candidates",
    "search_candidates": "save_candidates",
    "save_candidates": None
}

def get_graph():
    return nodes, transitions, HRAState
