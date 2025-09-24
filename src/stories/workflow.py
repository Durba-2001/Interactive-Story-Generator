from langgraph.graph import StateGraph, END
from src.stories.nodes.outline_node import outline_node
from src.stories.nodes.character_node import character_node
from src.stories.nodes.scene_node import scene_node
from src.stories.nodes_continue.continuation_router_node import continuation_router_node
from src.stories.nodes_continue.extend_plot_node import extend_plot_node
from src.stories.nodes_continue.develop_character_node import develop_character_node
from src.stories.nodes_continue.append_scene_node import append_scene_node
from src.database.models import StoryStateModel

def node_with_history(node_func, story_history):
    async def wrapped_node(state):
        return await node_func(state, story_history)
    return wrapped_node

# ---------------------------
# Workflow for NEW stories
# ---------------------------
def create_workflow(story_history):
    graph = StateGraph(StoryStateModel)

    # Wrap nodes with history
    graph.add_node("outline_node", node_with_history(outline_node, story_history))
    graph.add_node("character_node", node_with_history(character_node, story_history))
    graph.add_node("scene_node", node_with_history(scene_node, story_history))

    # Entry point
    graph.set_entry_point("outline_node")

    # Edges
    graph.add_edge("outline_node", "character_node")
    graph.add_edge("character_node", "scene_node")
    graph.add_edge("scene_node", END)

    return graph.compile()


# ---------------------------
# Workflow for CONTINUATION
# ---------------------------
def create_continuation_workflow(story_history):
    graph = StateGraph(StoryStateModel)

    graph.add_node("continuation_router_node", node_with_history(continuation_router_node, story_history))
    graph.add_node("extend_plot_node", node_with_history(extend_plot_node, story_history))
    graph.add_node("develop_character_node", node_with_history(develop_character_node, story_history))
    graph.add_node("append_scene_node", node_with_history(append_scene_node, story_history))

    graph.add_conditional_edges(
        "continuation_router_node",
        continuation_router_condition,
        {
            "extend_plot": "extend_plot_node",
            "develop_character": "develop_character_node",
            "append_scene": "append_scene_node"
        }
    )

    graph.add_edge("extend_plot_node", END)
    graph.add_edge("develop_character_node", END)
    graph.add_edge("append_scene_node", END)

    graph.set_entry_point("continuation_router_node")

    return graph.compile()


# ---------------------------
# Safe router condition
# ---------------------------
def continuation_router_condition(state: StoryStateModel) -> str:
    """
    Return the next node explicitly set by the continuation_router_node.
    If no route is set, end the workflow safely.
    """
    if state.current_node: 
        return state.current_node 
    else:
      return END