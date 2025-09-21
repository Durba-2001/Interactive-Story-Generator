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
    characters_str = "\n".join([
        f"{c.get('name', 'Unknown')} - {c.get('description', '')}"
        for c in state.characters
    ])

    # Format prompt
    prompt_text = template.format(
        outline="\n".join(state.outline),
        characters=characters_str
    )

    # Generate scenes
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    text = response.content  # use .content instead of .text

    # Clean lines
    cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Update state
    state.scenes = cleaned_lines
    state.history.append({"role": "assistant", "content": text})
    state.current_node = "end_node"  # adjust as needed

    return state
