import json
from src.database.models import StoryStateModel
from src.stories.nodes.prompts import character_prompt
from src.stories.utils import run_llm
from loguru import logger

async def character_node(state: StoryStateModel, story_history: list) -> StoryStateModel:
    logger.info("Starting character_node for story with prompt: {}", state.prompt)
    
    state.current_node = "character_node"
    logger.debug("Set current_node to 'character_node'")

    outline_text = "\n".join(state.outline) if state.outline else "No outline provided."
    prompt_text = character_prompt.replace("{outline}", outline_text)
    logger.debug("Formatted character prompt:\n{}", prompt_text)

    text = await run_llm(
        prompt_text,
        "You are a creative character designer.",
        story_history
    )
    logger.info("LLM returned text with {} characters", len(text) if text else 0)
    logger.debug("LLM output:\n{}", text)

    # Parse JSON safely
    try:
        characters_json = json.loads(text)
        if isinstance(characters_json, list):
            state.characters = characters_json
            logger.info("Parsed {} characters from LLM JSON", len(characters_json))
        else:
            state.characters = [{"name": str(characters_json)}]
            logger.warning("LLM JSON was not a list, wrapped in dict: {}", characters_json)
    except json.JSONDecodeError:
        state.characters = [{"name": text.strip()}]
        logger.error("Failed to parse JSON from LLM output, fallback used")

    return state
