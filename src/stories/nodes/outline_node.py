from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key
from src.stories.nodes.prompts import outline_prompt
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)

async def outline_node(state: StoryStateModel) -> StoryStateModel:
    # Read and format prompt
   
    prompt_text = outline_prompt.format(prompt=state.prompt)
    
    # Generate outline
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    
    # Extract text from AIMessage
    text = response.content

    # Split and clean lines
    lines = []
    for line in text.splitlines():  # Split the text into individual lines
        stripped_line = line.strip()  # Remove leading/trailing whitespace
        if stripped_line:  # Only keep non-empty lines
            lines.append(stripped_line)

    history_text = text.replace("\n", " ").strip()
    # Assign to state
    state.outline = lines
    state.history.append({"role": "assistant", "content": history_text})
    state.current_node = "character_node"
    
    return state
