from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Annotated # Use TypedDict for state
import operator # Needed for state updates

# Import node functions
from .nodes import authenticate_user, search_candidates, save_candidates

# Define the state structure using TypedDict (recommended for LangGraph)
class HRAState(TypedDict):
    username: str
    password: str
    title: str
    skills: str
    # Use Annotated types for state updates (merging dictionaries)
    token: Annotated[Optional[str], operator.add]
    candidates: Annotated[Optional[List[dict]], operator.add]   

# --- LangGraph Implementation ---
# Create a new graph
workflow = StateGraph(HRAState)

# Define the nodes
workflow.add_node("authenticate_user", authenticate_user)
workflow.add_node("search_candidates", search_candidates)
workflow.add_node("save_candidates", save_candidates)

# Build the graph connections (simple linear flow)
workflow.set_entry_point("authenticate_user")
workflow.add_edge("authenticate_user", "search_candidates")
workflow.add_edge("search_candidates", "save_candidates")
workflow.add_edge("save_candidates", END) # End after saving

# Compile the graph
app = workflow.compile()

# Function to easily get the compiled app (optional, main.py can import 'app')
def get_compiled_graph():
    return app