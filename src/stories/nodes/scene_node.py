from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts/scene_prompt.txt"

async def scene_node(state: StoryStateModel) -> StoryStateModel:
    # Read prompt template
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        template = f.read()

   # Safely format characters, defaulting missing description to empty string
    characters_str = ""
    for c in state.characters:
        name = c.get("name", "Unknown")
        description = c.get("description", "")
        characters_str += f"{name} - {description}\n"

    # Remove the trailing newline if needed
    characters_str = characters_str.rstrip("\n")


    # Format prompt
    prompt_text = template.format(
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
    state.history.append({"role": "assistant", "content": history_text})
    state.current_node = "end_node"  # adjust as needed

    return state
