from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts/character_prompt.txt"
async def character_node(state: StoryStateModel) -> StoryStateModel:
    # Read and format prompt
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_text = f.read().format(outline="\n".join(state.outline))
    
    # Generate characters
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    
    # Parse response into character list
    lines = response.text.splitlines()
    characters = []
    for line in lines:
        line = line.strip()
        if line:
            parts = line.split(" - ")
            if len(parts) == 2:
                name, description = parts
                characters.append({"name": name.strip(), "description": description.strip()})
    
    # Update state
    state.characters = characters
    state.history.append({"role": "assistant", "content": response.text})
    state.current_node = "scene_node"
    
    return state