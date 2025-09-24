from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key
from src.stories.nodes_continue.prompts import continue_router_prompt
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)

async def continuation_router_node(state: StoryStateModel) -> StoryStateModel:
   
    # Read prompt
    prompt_text = continue_router_prompt.format(
            input=state.prompt,
            state_summary=" ".join(state.outline)
        )

    # Call LLM
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    assistant_text = response.content.strip()

# Clean only for history
    assistant_text_clean = " ".join(assistant_text.split())

# Update history
    state.history.append({"role": "user", "content": state.prompt})
    state.history.append({"role": "assistant", "content": assistant_text_clean})

    # Explicitly set route
    text = assistant_text.lower()
    if "append" in text:
        state.current_node = "append_scene"
    elif "extend" in text:
        state.current_node = "extend_plot"
    elif "character" in text:
        state.current_node = "develop_character"
    else:
        state.current_node = "append_scene"  

    return state
