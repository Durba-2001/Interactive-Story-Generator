import json
from src.database.models import StoryStateModel
from src.stories.nodes.prompts import character_prompt
from src.stories.utils import run_llm


async def character_node(state: StoryStateModel, story_history: list) -> StoryStateModel:
    state.current_node = "character_node"

    # Inject outline into prompt
    prompt_text = character_prompt.replace("{outline}", "\n".join(state.outline))

    # Call LLM
    text = await run_llm(
        prompt_text,
        "You are a creative character designer.",
        story_history
    )

    # Parse JSON safely
    try:
        characters_json = json.loads(text)
        if isinstance(characters_json, list):
            state.characters = characters_json
        else:
            state.characters = [{"name": str(characters_json)}]
    except json.JSONDecodeError:
        # Fallback if JSON invalid
        state.characters = [{"name": text}]
        characters_json = [{"name": text}]

    return state
