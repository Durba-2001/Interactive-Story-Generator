import json
from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts/character_prompt.txt"


async def character_node(state: StoryStateModel) -> StoryStateModel:
    # Read template
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    # Inject outline
    prompt_text = template.replace("{outline}", "\n".join(state.outline))

    # Call LLM
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    text = response.content.strip()

    # Parse JSON safely
    try:
        characters_json = json.loads(text)
        if isinstance(characters_json, list):
            state.characters = characters_json
        else:
            state.characters = [{"name": str(characters_json)}]
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        state.characters = [{"name": text}]

    # Clean only for history (avoid \n in JSON)
    history_text = text.replace("\n", " ").strip()

    state.history.append({"role": "assistant", "content": history_text})
    state.current_node = "scene_node"

    return state
