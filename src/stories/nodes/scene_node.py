from src.database.models import StoryStateModel
from src.stories.nodes.prompts import scene_prompt
from src.stories.utils import run_llm

async def scene_node(state: StoryStateModel, story_history: list) -> StoryStateModel:
    state.current_node = "scene_node"

    # Build characters string
    characters_str = ""
    for c in state.characters:
        name = c.get("name", "Unknown")
        description = c.get("background", "")
        characters_str += f"{name} - {description}\n"

    characters_str = characters_str.rstrip("\n")  # Remove trailing newline

    # Format prompt
    prompt_text = scene_prompt.format(
        outline="\n".join(state.outline),
        characters=characters_str
    )

    # Call LLM
    text = await run_llm(
        prompt_text,
        "You are a professional novelist.",
        story_history
    )

    # Clean and split into lines
    cleaned_lines = []
    for line in text.splitlines():
        stripped_line = line.strip()
        if stripped_line:
            cleaned_lines.append(stripped_line)

    state.scenes = cleaned_lines

    return state
