from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts_continue/develop_character_prompt.txt"

async def develop_character_node(state: StoryStateModel, user_input: str) -> StoryStateModel:
    # Read and format prompt
    with open(PROMPT_FILE, "r") as f:
        prompt_text = f.read().format(input=user_input, character=state.character)

    # Generate character development
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])

    # Update state
    state.character = response.text
    state.history.append({"role": "assistant", "content": response.text})
    state.current_node = "continuation_router_node"  # Loop back to router for further input

    return state