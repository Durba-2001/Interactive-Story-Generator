import json
from src.database.models import StoryStateModel
from src.stories.nodes.prompts import character_prompt
from src.stories.utils import run_llm

from loguru import logger
async def character_node(state: StoryStateModel, story_history: list) -> StoryStateModel:
    logger.info("Starting character_node for story with prompt: %s", state.prompt)
    
    state.current_node = "character_node"
    logger.debug("Set current_node to 'character_node'")

    # Inject outline into prompt
    prompt_text = character_prompt.replace("{outline}", "\n".join(state.outline))
    logger.debug("Formatted character prompt:\n%s", prompt_text)

    # Call LLM
    text = await run_llm(
        prompt_text,
        "You are a creative character designer.",
        story_history
    )
    logger.info("LLM returned text with %d characters", len(text))
    logger.debug("LLM output:\n%s", text)

    # Parse JSON safely
    try:
        characters_json = json.loads(text)
        if isinstance(characters_json, list):
            state.characters = characters_json
            logger.info("Parsed %d characters from LLM JSON", len(characters_json))
        else:
            state.characters = [{"name": str(characters_json)}]
            logger.warning("LLM JSON was not a list, wrapped in dict: %s", characters_json)
    except json.JSONDecodeError:
        # Fallback if JSON invalid
        state.characters = [{"name": text}]
        characters_json = [{"name": text}]
        logger.error("Failed to parse JSON from LLM output, fallback used")

    return state