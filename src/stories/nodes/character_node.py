import json
from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key
from src.stories.nodes.prompts import character_prompt
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)

async def character_node(state: StoryStateModel,story_history:list) -> StoryStateModel:
    state.current_node = "character_node"
    # Inject outline
    prompt_text = character_prompt.replace("{outline}", "\n".join(state.outline))
    
    # Call LLM
    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    text = response.content.strip()

    # Parse JSON safely
    try:
        characters_json = json.loads(text)
        if isinstance(characters_json, list):
            state.characters = characters_json
        else:
            state.characters = [{"name": str(characters_json)}]
    except json.JSONDecodeError:
        state.characters = [{"name": text}]
        characters_json = [{"name": text}]

    # Store structured JSON in history (no \ escapes)
    story_history.append({"role": "assistant", "content": characters_json})
    

    return state
