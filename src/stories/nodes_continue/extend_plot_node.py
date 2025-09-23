from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts_continue/extend_plot_prompt.txt"

async def extend_plot_node(state: StoryStateModel) -> StoryStateModel:
    with open(PROMPT_FILE, "r") as f:
        prompt_text = f.read().format(
            input=state.prompt,
            outline="\n".join(state.outline)
        )

    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    assistant_text = response.content.strip()

    # Clean lines and update outline
    lines = assistant_text.splitlines()  # Split the text into individual lines
    clean_lines = []

    for line in lines:
        stripped_line = line.strip()  # Remove leading/trailing whitespace
        if stripped_line:  # Only keep non-empty lines
            clean_lines.append(stripped_line)

    state.outline = clean_lines


    state.history.append({"role": "assistant", "content": assistant_text})
    state.current_node = "continuation_router_node"  # loop back
    return state
