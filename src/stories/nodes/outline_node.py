from src.database.models import StoryStateModel
from src.stories.nodes.prompts import outline_prompt
from src.stories.utils import run_llm  
from loguru import logger

async def outline_node(state: StoryStateModel, story_history: list) -> StoryStateModel:
    logger.info("Starting outline_node for story with prompt: %s", state.prompt)

    # Format the prompt
    prompt_text = outline_prompt.format(prompt=state.prompt)
    logger.debug("Formatted outline prompt: %s", prompt_text)

    # Call LLM through shared helper
    text = await run_llm(
        prompt_text,
        "You are an expert story planner.",
        story_history
    )
    logger.info("LLM returned text with %d characters", len(text))

    # Split and clean lines
    lines = []
    for line in text.splitlines():
        stripped_line = line.strip()
        if stripped_line:
            lines.append(stripped_line)
    logger.debug("Processed outline lines: %s", lines)

    # Update state
    state.outline = lines
    logger.info("Outline updated in state with %d items", len(lines))

    return state
