from src.database.models import StoryStateModel
from src.stories.nodes.prompts import scene_prompt
from src.stories.utils import run_llm
from loguru import logger
async def scene_node(state: StoryStateModel, story_history: list) -> StoryStateModel:
    logger.info("Starting scene_node for story with prompt: %s", state.prompt)
    
    state.current_node = "scene_node"
    logger.debug("Set current_node to 'scene_node'")

    # Build characters string
    characters_str = ""
    for c in state.characters:
        name = c.get("name", "Unknown")
        description = c.get("background", "")
        characters_str += f"{name} - {description}\n"
    characters_str = characters_str.rstrip("\n")
    logger.debug("Constructed characters string:\n%s", characters_str)

    # Format prompt
    prompt_text = scene_prompt.format(
        outline="\n".join(state.outline),
        characters=characters_str
    )
    logger.debug("Formatted scene prompt:\n%s", prompt_text)

    # Call LLM
    text = await run_llm(
        prompt_text,
        "You are a professional novelist.",
        story_history
    )
    logger.info("LLM returned text with %d characters", len(text))
    logger.debug("LLM output:\n%s", text)

    # Clean and split into lines
    cleaned_lines = []
    for line in text.splitlines():
        stripped_line = line.strip()
        if stripped_line:
            cleaned_lines.append(stripped_line)
    logger.info("Processed %d scene lines", len(cleaned_lines))

    state.scenes = cleaned_lines

    return state