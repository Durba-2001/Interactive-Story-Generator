from src.database.models import StoryStateModel
from src.stories.nodes.prompts import outline_prompt
from src.stories.utils import run_llm  # <-- use helper

async def outline_node(state: StoryStateModel, story_history: list) -> StoryStateModel:
    # Format the prompt
    prompt_text = outline_prompt.format(prompt=state.prompt)

    # Call LLM through shared helper
    text = await run_llm(
        prompt_text,
        "You are an expert story planner.",
        story_history
    )

    # Split and clean lines
    lines = []
    for line in text.splitlines():
        stripped_line = line.strip()
        if stripped_line:
            lines.append(stripped_line)

    # Update state
    state.outline = lines

    return state
