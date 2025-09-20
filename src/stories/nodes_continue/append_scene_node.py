from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts/append_scene_prompt.txt"

async def append_scene_node(state: StoryStateModel, user_input: str) -> StoryStateModel:
  # Get the last scene
    if state.scenes:
        last_scene = state.scenes[-1]
    else:
        last_scene = ""

    # Build outline text
    outline_lines = []
    for event in state.outline:
     outline_lines.append(event)
    outline_text = "\n".join(outline_lines)

    # Build characters text
    character_names = []
    for character in state.characters:
        name = character.get("name", "")
        if name:
            character_names.append(name)
    characters_text = ", ".join(character_names)

    
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_text = f.read().format(
            last_scene=last_scene,
            input=user_input,
            outline=outline_text,
            characters=characters_text
        )
    
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    
    # Append new scene
    state.scenes.append(response.text.strip())
    state.history.append({"role": "assistant", "content": response.text})
    state.current_node = "done"  # end node for continuation
    
    return state
