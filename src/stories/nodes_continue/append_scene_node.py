from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts_continue/append_scene_prompt.txt"
async def append_scene_node(state: StoryStateModel, user_input: str) -> StoryStateModel:
    # Read and format prompt
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_text = f.read().format(
            input=user_input,
            last_scene=state.scenes[-1] if state.scenes else "N/A",
            outline="\n".join(state.outline),
            characters="\n".join([f"{c['name']} - {c['description']}" for c in state.characters])
        )
    
    # Generate scene continuation
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    
    # Update state
    state.scenes.append(response.text.strip())
    state.history.append({"role": "assistant", "content": response.text})
    state.current_node = "continuation_router_node"  # Loop back to router for further input
    
    return state