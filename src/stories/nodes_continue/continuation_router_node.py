from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts_continue/continuation_router_prompt.txt"

async def continuation_router_node(state: StoryStateModel) -> StoryStateModel:
   
    # Read prompt
    with open(PROMPT_FILE, "r") as f:
        prompt_text = f.read().format(
            input=state.user_input,
            state_summary=" ".join(state.outline)
        )

    # Call LLM
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    assistant_text = response.content.strip()

# Clean only for history
    assistant_text_clean = " ".join(assistant_text.split())

# Update history
    state.history.append({"role": "user", "content": state.user_input})
    state.history.append({"role": "assistant", "content": assistant_text_clean})

    # Explicitly set route
    text = assistant_text.lower()
    if "append" in text:
        state.route = "append_scene"
    elif "extend" in text:
        state.route = "extend_plot"
    elif "character" in text:
        state.route = "develop_character"
    else:
        state.route = "append_scene"  # fallback

    return state
