from pydantic import BaseModel, Field
from typing import Optional,List,Dict
from datetime import datetime

class StoryCreate(BaseModel):
    prompt: str

class StoryContinue(BaseModel):
    prompt: str

# --- Story State (LangGraph checkpoint) ---
class StoryStateModel(BaseModel):
    current_node: Optional[str] = "outline_node"
    outline: List[str] = []
    characters: List[Dict] = []
    scenes: List[str] = []
    # history: List[Dict] = []  # internal workflow messages
    prompt:str


# --- Stories Collection ---
class StoryModel(BaseModel):
    story_id: str  
    user_id: str  
    prompt: str
    state: StoryStateModel
    history: List[Dict] = []  # full chat messages [{"role": "user", "content": str}, [{"role": "assistant", "content": str}...]
    created_at: datetime 
    updated_at: datetime 

class StoryResponse(BaseModel):
    story_id:str
    user_id: str  
    full_story: str
    created_at: datetime 
    updated_at: datetime 