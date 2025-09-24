append_scene_prompt="""Continue the story from the last scene '{last_scene}', incorporating '{input}', outline '{outline}', and characters '{characters}'.  
Write 200-400 words building tension toward the next event.
Focus on vivid descriptions, character actions, and dialogue.  
End with a cliffhanger or suspenseful moment leading into the next plot point.
Return only the story text (no extra explanations)."""

continue_router_prompt="""Classify this input '{input}' for the story state '{state_summary}':
Choose one of 'extend_plot', 'develop_character', or 'append_scene'.
Only return the chosen keyword.
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
