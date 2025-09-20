from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts/scene_prompt.txt"
async def scene_node(state: StoryStateModel) -> StoryStateModel:
    # Read and format prompt
    with open(PROMPT_FILE, "r") as f:
        prompt_text = f.read().format(
            outline="\n".join(state.outline),
            characters="\n".join([f"{c['name']} - {c['description']}" for c in state.characters])
        )
    
    # Generate scenes
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    
    # Split response into lines and clean
    lines = response.text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    # Update state
    state.scenes = cleaned_lines
    state.history.append({"role": "assistant", "content": response.text})
    state.current_node = "end_node"  # Assuming this is the last node
    
    return state