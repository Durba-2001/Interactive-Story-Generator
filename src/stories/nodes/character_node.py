from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts/character_prompt.txt"

import json


async def character_node(state: StoryStateModel) -> StoryStateModel:
    # Read template
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    # Inject outline
    prompt_text = template.replace("{outline}", "\n".join(state.outline))

    # Call LLM
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    text = response.content

    # Parse JSON safely
    try:
        characters_json = json.loads(text)
        if isinstance(characters_json, list):
            state.characters = characters_json
        else:
            # fallback: treat as a single character name
            state.characters = [{"name": str(characters_json)}]
    except json.JSONDecodeError:
        # fallback: treat each line as a simple name
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        state.characters = [{"name": line} for line in lines]

    # Update history and move to next node
    state.history.append({"role": "assistant", "content": text})
    state.current_node = "scene_node"

    return state
