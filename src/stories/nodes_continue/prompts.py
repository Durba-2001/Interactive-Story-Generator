append_scene_prompt="""Continue the story from the last scene '{last_scene}', incorporating '{input}', outline '{outline}', and characters '{characters}'.  
Write 200-400 words building tension toward the next event.
Focus on vivid descriptions, character actions, and dialogue.  
End with a cliffhanger or suspenseful moment leading into the next plot point.
Return only the story text (no extra explanations)."""

continue_router_prompt = """
You are analyzing a story update request. The current story state is summarized as:
'{state_summary}'

A user has provided this input:
'{input}'

Based on the content of this input, determine how it should affect the story.  
There are three possible actions:

1. extend_plot — the input introduces a new event or plot development.  
2. develop_character — the input adds depth, traits, or arcs to an existing character.  
3. append_scene — the input continues the story by adding narrative to the next scene.

Choose the single action that best fits the input.  
Return **only** the chosen action keyword: 'extend_plot', 'develop_character', or 'append_scene'.
"""

develop_character="""Develop the character '{character}' in response to '{input}', updating their profile with new traits or arcs.
Output concise updates suitable to append to the character's profile.
Return only the updated character profile text (no extra explanations).
"""
extended_plot_outline_prompt="""Extend the plot outline:
'{outline}'
by incorporating '{input}', adding 1-2 new events while maintaining consistency.
Output each event as 1-2 sentences.
Return the updated outline as a structured list of events."""
