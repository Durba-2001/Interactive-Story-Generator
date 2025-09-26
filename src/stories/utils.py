# src/stories/nodes/utils.py
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import api_key

# Single LLM instance
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=api_key
)

async def run_llm(prompt_text: str, system_instruction: str, story_history: list) -> str:
    """Send prompt to Gemini and return plain text response."""
    response = await llm.ainvoke([
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt_text}
    ])

    text = response.content.strip()

    # Save in history (compact for logging/debugging)
    history_text = text.replace("\n", " ").strip()
    story_history.append({"role": "assistant", "content": history_text})

    return text
