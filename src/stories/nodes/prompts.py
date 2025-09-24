outline_prompt = """
You are an expert story planner. 

Based on the following user prompt:
"{prompt}"

Create a high-level plot outline with 3–5 key events.  
Output as a structured list of events, each 1–2 sentences long.  

Ensure the story is coherent, original, and engaging.  
Return only the outline text (no extra explanations).
"""
character_prompt="""You are a creative character designer.  
Using the following plot outline:

"{outline}"

Generate detailed profiles for 2–4 main characters.  
Each character must include:
- Name  
- Background  
- Personality & motivations  
- Role in the story  

Return the output as a valid JSON list of objects, only JSON, no markdown or code fences:
[
  {
    "name": "...",
    "background": "...",
    "motivations": "...",
    "role": "..."
  }
]

Ensure diversity, depth, and alignment with the story's genre and setting.
"""
scene_prompt="""You are a professional novelist.  
Write the opening scene of the story using this outline and character set:

Outline: {outline}  
Characters: {characters}

Guidelines:
- Length: 200–400 words  
- Focus on vivid descriptions, character introduction, and setting  
- Build suspense and end with a small cliffhanger  
- Use a natural, engaging narrative style  

Return only the story text (no extra explanations).
"""
