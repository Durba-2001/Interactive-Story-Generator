import pytest
from src.stories.nodes.outline_node import outline_node
from src.stories.nodes.character_node import character_node
from src.stories.nodes.scene_node import scene_node
from src.stories.nodes_continue.append_scene_node import append_scene_node
from src.database.models import StoryStateModel
from unittest.mock import AsyncMock, patch
@pytest.mark.asyncio
async def test_outline_node():
    state = StoryStateModel(prompt="A story about AI taking over the world.")
    history = []

    # Mock run_llm so the real API is never called
    async def fake_run_llm(*args, **kwargs):
        history.append({"role": "assistant", "content": "Fake outline"})
        return "Fake outline"

    with patch("src.stories.nodes.outline_node.run_llm", new=fake_run_llm):
        new_state = await outline_node(state, history)

    assert len(new_state.outline) > 0
    assert history[-1]["role"] == "assistant"

@pytest.mark.asyncio
async def test_character_node_mock():
    state = StoryStateModel(
        prompt="A story about AI taking over the world.",
        outline=["Event 1", "Event 2"]
    )
    history = []

    # Mock run_llm to return fake JSON without calling API
    fake_response = '[{"name": "Alice", "background": "A brilliant AI scientist", "motivations": "Save the world", "role": "Protagonist"}]'

    with patch("src.stories.nodes.character_node.run_llm", new=AsyncMock(return_value=fake_response)):
        new_state = await character_node(state, history)

    assert len(new_state.characters) == 1
    assert new_state.characters[0]["name"] == "Alice"
    assert history == []  # history not updated in this version, adjust if needed


@pytest.mark.asyncio
async def test_scene_node_mock():
    state = StoryStateModel(
        prompt="A story about AI taking over the world.",
        outline=["Event 1", "Event 2"],
        characters=[{"name": "Alice", "role": "protagonist"}]
    )
    history = []

    fake_scene = "Alice enters the lab and notices the AI system blinking unexpectedly."

    # Patch run_llm so we don't call the real API
    with patch("src.stories.nodes.scene_node.run_llm", new=AsyncMock(return_value=fake_scene)):
        new_state = await scene_node(state, history)

    assert len(new_state.scenes) == 1
    assert "Alice enters the lab" in new_state.scenes[0]


@pytest.mark.asyncio
async def test_append_scene_node():
    state = StoryStateModel(prompt="User adds more events",
                            outline=["Event 1", "Event 2"],
                            characters=[{"name":"Alice"}],
                            scenes=["Opening scene"])
    history = []
    new_state = await append_scene_node(state, history)
    assert len(new_state.scenes) == 2
    assert history[-1]["role"] == "assistant"
