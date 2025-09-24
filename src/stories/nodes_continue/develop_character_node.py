from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts_continue/develop_character_prompt.txt"

async def develop_character_node(state: StoryStateModel) -> StoryStateModel:
    # Choose a target character from user_input or default to first
    if state.prompt:
        target = state.prompt
    else:
        if state.characters:
            target = state.characters[0]["name"]
        else:
            target = "Character"


    with open(PROMPT_FILE, "r") as f:
        prompt_text = f.read().format(
            input=state.prompt,
            character=target
        )

    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    assistant_text = response.content.strip()

    # Update a character 
    for char in state.characters:
        if char.get("name") == target:
            char["background"] = char.get("background", "") + " " + assistant_text

    state.history.append({"role": "assistant", "content": assistant_text})
    state.current_node = "continuation_router_node"  # loop back
    return state
