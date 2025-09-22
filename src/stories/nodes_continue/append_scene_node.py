from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.models import StoryStateModel
from src.config import api_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
PROMPT_FILE = r"src/stories/prompts_continue/append_scene_prompt.txt"

async def append_scene_node(state: StoryStateModel) -> StoryStateModel:
    if state.scenes:
        last_scene = state.scenes[-1]
    else:
        last_scene = ""

    outline_text = "\n".join(state.outline)
    names = []
    for character in state.characters:
        name = character.get("name")
        if name:
            names.append(name)

    characters_text = ", ".join(names)


    with open(PROMPT_FILE, "r") as f:
        prompt_text = f.read().format(
            last_scene=last_scene,
            input=state.user_input,
            outline=outline_text,
            characters=characters_text
        )

    response = await llm.ainvoke([{"role": "user", "content": prompt_text}])
    assistant_text = response.content.strip()
    assistant_text_clean = " ".join(assistant_text.split())  # collapses newlines + extra spaces

    state.scenes.append(assistant_text_clean)
    state.history.append({"role": "assistant", "content": assistant_text_clean})


    state.scenes.append(assistant_text)
    state.history.append({"role": "assistant", "content": assistant_text})
    state.current_node = "done"  # end node
    return state
