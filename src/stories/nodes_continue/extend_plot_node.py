from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts_continue/extend_plot_prompt.txt"
async def extend_plot_node(state: StoryStateModel, user_input: str) -> StoryStateModel:
    # Read and format prompt
    with open(PROMPT_FILE, "r") as f:
        prompt_text = f.read().format(input=user_input, outline="\n".join(state.outline))
    
    # Generate extended plot
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    
    # Split response into lines
    lines = response.text.splitlines()

    # Initialize cleaned list
    cleaned_lines = []

    # Strip each line and remove empty lines
    for line in lines:
        stripped = line.strip()
        if stripped:  # Only add non-empty lines
            cleaned_lines.append(stripped)

    # Assign to state
    state.outline = cleaned_lines
    
    # Update state
    state.history.append({"role": "assistant", "content": response.text})
    state.current_node = "continuation_router_node"  # Loop back to router for further input
    
    return state