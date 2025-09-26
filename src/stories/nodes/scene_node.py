from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key
from src.stories.nodes.prompts import scene_prompt
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)

async def scene_node(state: StoryStateModel,story_history: list) -> StoryStateModel:
    # Read prompt template
    state.current_node = "scene_node"
    characters_str = ""
    for c in state.characters:
        name = c.get("name", "Unknown")
        description = c.get("description", "")
        characters_str += f"{name} - {description}\n"

    # Remove the trailing newline if needed
    characters_str = characters_str.rstrip("\n")


    # Format prompt
    prompt_text = scene_prompt.format(
        outline="\n".join(state.outline),
        characters=characters_str
    )

    # Generate scenes
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    text = response.content  # use .content instead of .text

    # Clean lines
    cleaned_lines = []

    for line in text.splitlines():  # Split text into lines
        stripped_line = line.strip()  # Remove leading/trailing whitespace
        if stripped_line:  # Only keep non-empty lines
            cleaned_lines.append(stripped_line)

    history_text = text.replace("\n", " ").strip()
    # Update state
    state.scenes = cleaned_lines
    story_history.append({"role": "assistant", "content": history_text})
    

    return state
