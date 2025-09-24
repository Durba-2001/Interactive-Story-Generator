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
    full_story_text = "\n\n".join([
        "Outline:\n" + "\n".join(final_state.outline),
        "Characters:\n" + "\n".join([c.get("name", "") for c in final_state.characters]),
        "Scenes:\n" + "\n".join(final_state.scenes),
    ])
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
    new_story_api=StoryResponse(story_id=new_story.story_id,
        user_id=new_story.user_id,
        full_story = full_story_text,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        )
    await db["stories"].insert_one(new_story.model_dump())
    logger.success(f"New story created with ID: {story_id} for user: {current_user.username}")
    
    return new_story_api


# ---------------------------
# CONTINUE STORY
# ---------------------------
@router.post("/{story_id}/continue", response_model=StoryModel)
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

    return story_model


# ---------------------------
# GET ALL STORIES
# ---------------------------
@router.get("/", response_model=list[StoryModel])
async def get_all_stories(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    stories_cursor = db["stories"].find({"user_id": current_user.user_id})
    stories = []
    async for story in stories_cursor:
        stories.append(StoryModel(**story))
    return stories


# ---------------------------
# GET STORY BY ID
# ---------------------------
@router.get("/{story_id}", response_model=StoryModel)
async def get_story(
    story_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    story = await db["stories"].find_one(
        {"story_id": story_id, "user_id": current_user.user_id}
    )
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return StoryModel(**story)


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
    return {"message": f"Story {story_id} deleted successfully"}
