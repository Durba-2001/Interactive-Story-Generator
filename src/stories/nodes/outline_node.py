from src.database.models import StoryStateModel
from src.stories.nodes.prompts import outline_prompt
from src.stories.utils import run_llm  
from loguru import logger

async def outline_node(state: StoryStateModel, story_history: list) -> StoryStateModel:
    logger.info("Starting outline_node for story with prompt: {}", state.prompt)

    # Format the prompt safely
    prompt_text = outline_prompt.format(prompt=state.prompt or "No prompt provided")
    logger.debug("Formatted outline prompt: {}", prompt_text)

    # Call LLM through shared helper
    text = await run_llm(
        prompt_text,
        "You are an expert story planner.",
        story_history
    )
    logger.info("LLM returned text with {} characters", len(text) if text else 0)

    # Split and clean lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    logger.debug("Processed outline lines: {}", lines)

    # Update state
    state.outline = lines
    logger.info("Outline updated in state with {} items", len(lines))

    return state
