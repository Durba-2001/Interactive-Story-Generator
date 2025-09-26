from src.database.models import StoryStateModel
from src.stories.nodes.prompts import scene_prompt
from src.stories.utils import run_llm
from loguru import logger

async def scene_node(state: StoryStateModel, story_history: list) -> StoryStateModel:
    logger.info("Starting scene_node for story with prompt: {}", state.prompt)

    state.current_node = "scene_node"
    logger.debug("Set current_node to 'scene_node'")

    # Build characters string
    characters_str = "\n".join(
        f"{c.get('name', 'Unknown')} - {c.get('background', '')}" for c in state.characters
    )
    logger.debug("Constructed characters string:\n{}", characters_str or "No characters provided")

    # Format prompt
    outline_text = "\n".join(state.outline) if state.outline else "No outline provided"
    prompt_text = scene_prompt.format(outline=outline_text, characters=characters_str)
    logger.debug("Formatted scene prompt:\n{}", prompt_text)

    # Call LLM
    text = await run_llm(
        prompt_text,
        "You are a professional novelist.",
        story_history
    )
    logger.info("LLM returned text with {} characters", len(text) if text else 0)
    logger.debug("LLM output:\n{}", text or "<empty output>")

    # Clean and split into lines
    cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()] if text else []
    logger.info("Processed {} scene lines", len(cleaned_lines))

    state.scenes = cleaned_lines

    return state
