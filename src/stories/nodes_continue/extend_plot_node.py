from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key
from src.stories.nodes_continue.prompts import extended_plot_outline_prompt
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)

async def extend_plot_node(state: StoryStateModel,story_history:list) -> StoryStateModel:
    
    prompt_text = extended_plot_outline_prompt.format(
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


    story_history.append({"role": "assistant", "content": assistant_text})
    state.current_node = "continuation_router_node"  # loop back
    return state
