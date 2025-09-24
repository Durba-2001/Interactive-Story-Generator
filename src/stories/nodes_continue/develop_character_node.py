from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key
from src.stories.nodes_continue.prompts import develop_character
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)


async def develop_character_node(state: StoryStateModel) -> StoryStateModel:
    # Choose a target character from user_input or default to first
    if state.prompt:
        target = state.prompt
    else:
        if state.characters:
            target = state.characters[0]["name"]
        else:
            target = "Character"


    
    prompt_text = develop_character.format(
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
