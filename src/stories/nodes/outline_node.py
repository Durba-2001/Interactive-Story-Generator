from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts/outline_prompt.txt"
async def outline_node(state: StoryStateModel) -> StoryStateModel:
    # Read and format prompt
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_text = f.read().format(prompt=state.prompt)
    
    # Generate outline
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    
    # Extract text from AIMessage
    text = response.content

    # Split and clean lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # Assign to state
    state.outline = lines
    state.history.append({"role": "assistant", "content": text})
    state.current_node = "character_node"
    
    return state
