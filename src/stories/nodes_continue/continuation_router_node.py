from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key
from src.stories.nodes_continue.prompts import continue_router_prompt

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)

async def continuation_router_node(state: StoryStateModel,story_history:list) -> StoryStateModel:
    # Format prompt for LLM
    prompt_text = continue_router_prompt.format(
        input=state.prompt,
        state_summary=" ".join(state.outline)
    )

    # Call LLM
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    assistant_text = response.content.strip()

    # Clean text for history
    assistant_text_clean = " ".join(assistant_text.split())

    # Append to history
    # story_history.append({"role": "user", "content": state.prompt})
    story_history.append({"role": "assistant", "content": assistant_text_clean})

    # Directly set the node name returned by the model
    # This will match one of the conditional edges in LangGraph
    state.current_node = assistant_text_clean.lower().strip()

    return state
