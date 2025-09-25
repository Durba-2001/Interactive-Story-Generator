from fastapi import APIRouter, Depends, HTTPException, status
from src.database.connection import get_db
from src.database.models import StoryModel, StoryCreate, StoryStateModel, StoryContinue,StoryResponse
from src.stories.workflow import create_workflow, create_continuation_workflow
import uuid
from loguru import logger
from src.endpoints.router_auth import get_current_user
from datetime import datetime, timezone

router = APIRouter()


# ---------------------------
# CREATE NEW STORY
# ---------------------------
@router.post("/new", response_model=StoryResponse)
async def create_story(
    request: StoryCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    story_id = str(uuid.uuid4())
    
    # Initialize state with user prompt
    initial_state = StoryStateModel(prompt=request.prompt)

    # Initialize single story history
    story_history = [{"role": "user", "content": request.prompt}]

    # Create workflow with history wrapped nodes
    workflow = create_workflow(story_history)

    # Run workflow
    final_state_dict = await workflow.ainvoke(initial_state)
    final_state = StoryStateModel(**final_state_dict)

    # ✅ Build structured story step by step (no inline one-liners)
    structured_story = {}

    # Outline
    outline_list = []
    for point in final_state.outline:
        outline_list.append(point)
    structured_story["outline"] = outline_list

    # Characters
    characters_list = []
    for c in final_state.characters:
        character = {
            "name": c.get("name", "Unknown"),
            "background": c.get("background", "No background available."),
            "motivations": c.get("motivations", "No motivations specified."),
            "role": c.get("role", "No role specified."),
        }
        characters_list.append(character)
    structured_story["characters"] = characters_list

    # Scenes
    scenes_list = []
    for idx, scene in enumerate(final_state.scenes, start=1):
        scenes_list.append({
            "scene_number": idx,
            "content": scene
        })
    structured_story["scenes"] = scenes_list

    # Save story
    new_story = StoryModel(
        story_id=story_id,
        user_id=current_user.user_id,
        prompt=request.prompt,
        state=final_state,
        history=story_history,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    new_story_api = StoryResponse(
        story_id=new_story.story_id,
        user_id=new_story.user_id,
        full_story=structured_story,   # ✅ structured JSON (no full text)
        created_at=new_story.created_at,
        updated_at=new_story.updated_at,
    )

    await db["stories"].insert_one(new_story.model_dump())
    logger.success(f"New story created with ID: {story_id} for user: {current_user.username}")
    
    return new_story_api



# ---------------------------
# CONTINUE STORY
# ---------------------------
@router.post("/{story_id}/continue", response_model=StoryResponse)
async def continue_story(
    story_id: str,
    user_input: StoryContinue,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Fetch story
    story_doc = await db["stories"].find_one(
        {"story_id": story_id, "user_id": current_user.user_id}
    )
    if not story_doc:
        raise HTTPException(status_code=404, detail="Story not found")

    # Load into Pydantic model
    story_model = StoryModel(**story_doc)

    # Append user input to history
    story_model.history.append({"role": "user", "content": user_input.prompt})

    # Update prompt in state
    story_model.state.prompt = user_input.prompt

    # Create continuation workflow with history
    workflow = create_continuation_workflow(story_model.history)

    # Run workflow
    updated_state_dict = await workflow.ainvoke(story_model.state)
    updated_state = StoryStateModel(**updated_state_dict)

    # Update story model
    story_model.state = updated_state
    story_model.updated_at = datetime.now(timezone.utc)

    # Persist updated state & history
    await db["stories"].update_one(
        {"story_id": story_id, "user_id": current_user.user_id},
        {
            "$set": {
                "state": story_model.state.model_dump(),
                "history": story_model.history,
                "updated_at": story_model.updated_at,
            }
        },
    )

    # Build structured JSON response
    structured_story = {}

    # Outline
    outline_list = []
    for point in updated_state.outline:
        outline_list.append(point)
    structured_story["outline"] = outline_list

    # Characters
    characters_list = []
    for c in updated_state.characters:
        character = {
            "name": c.get("name", "Unknown"),
            "background": c.get("background", "No background available."),
            "motivations": c.get("motivations", "No motivations specified."),
            "role": c.get("role", "No role specified."),
        }
        characters_list.append(character)
    structured_story["characters"] = characters_list

    # Scenes
    scenes_list = []
    for idx, scene in enumerate(updated_state.scenes, start=1):
        scenes_list.append({
            "scene_number": idx,
            "content": scene
        })
    structured_story["scenes"] = scenes_list

    return StoryResponse(
        story_id=story_model.story_id,
        user_id=story_model.user_id,
        full_story=structured_story,
        created_at=story_model.created_at,
        updated_at=story_model.updated_at,
    )



# ---------------------------
# GET ALL STORIES
# ---------------------------
@router.get("/", response_model=list[dict])
async def get_all_stories(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    stories_cursor = db["stories"].find({"user_id": current_user.user_id})
    stories_list = []
    story_number = 1

    async for story_doc in stories_cursor:
        story_model = StoryModel(**story_doc)

        # Build structured story
        structured_story = {
            "outline": story_model.state.outline or [],
            "characters": [
                {
                    "name": c.get("name", "Unknown"),
                    "background": c.get("background", "No background available."),
                    "motivations": c.get("motivations", "No motivations specified."),
                    "role": c.get("role", "No role specified."),
                } for c in story_model.state.characters
            ],
            "scenes": [
                {"scene_number": idx + 1, "content": scene} 
                for idx, scene in enumerate(story_model.state.scenes or [])
            ],
        }

        # Append story with a number for clear separation
        stories_list.append({
            "story_number": story_number,
            "story_id": story_model.story_id,
            "user_id": story_model.user_id,
            "full_story": structured_story,
            "created_at": story_model.created_at,
            "updated_at": story_model.updated_at,
        })

        story_number += 1

    logger.success(f"{len(stories_list)} stories fetched for user: {current_user.username} with id :{current_user.user_id}")
    return stories_list



# ---------------------------
# GET STORY BY ID
# ---------------------------
@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    story_doc = await db["stories"].find_one(
        {"story_id": story_id, "user_id": current_user.user_id}
    )
    if not story_doc:
        raise HTTPException(status_code=404, detail="Story not found")

    story_model = StoryModel(**story_doc)

    # Build structured story
    structured_story = {}

    # Outline
    outline_list = []
    for point in story_model.state.outline:
        outline_list.append(point)
    structured_story["outline"] = outline_list

    # Characters
    characters_list = []
    for c in story_model.state.characters:
        character = {
            "name": c.get("name", "Unknown"),
            "background": c.get("background", "No background available."),
            "motivations": c.get("motivations", "No motivations specified."),
            "role": c.get("role", "No role specified."),
        }
        characters_list.append(character)
    structured_story["characters"] = characters_list

    # Scenes
    scenes_list = []
    for idx, scene in enumerate(story_model.state.scenes, start=1):
        scenes_list.append({
            "scene_number": idx,
            "content": scene
        })
    structured_story["scenes"] = scenes_list
    logger.success(f"Story fetched: {story_id} for user: {current_user.username} with id :{current_user.user_id}")
    return StoryResponse(
        story_id=story_model.story_id,
        user_id=story_model.user_id,
        full_story=structured_story,
        created_at=story_model.created_at,
        updated_at=story_model.updated_at,
    )

# ---------------------------
# DELETE STORY
# ---------------------------
@router.delete("/{story_id}", status_code=200)
async def delete_story(
    story_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    story = await db["stories"].find_one(
        {"story_id": story_id, "user_id": current_user.user_id}
    )
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    await db["stories"].delete_one({"story_id": story_id, "user_id": current_user.user_id})
    logger.success(f"Story deleted: {story_id} for user: {current_user.username} with id {current_user.user_id}")
    return {"message": f"Story {story_id} deleted successfully"}
