from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts_continue/continuation_router_prompt.txt"

async def continuation_router_node(state: StoryStateModel, user_input: str) -> str:
    """
    Determines which continuation node to route to:
    'extend_plot', 'develop_character', or 'append_scene'
    """
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_text = f.read().format(input=user_input, state_summary=" ".join(state.outline))
    
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    
    # Extract routing decision
    route = response.text.strip().lower()
    
    # Update state with user input
    state.history.append({"role": "user", "content": user_input})
    
    return route
