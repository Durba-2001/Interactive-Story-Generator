from fastapi import APIRouter, Depends, HTTPException, status
from src.database.connection import get_db
from src.database.models import StoryModel, StoryCreate, StoryStateModel
from src.stories.workflow import create_workflow
import uuid
from loguru import logger
from src.auth.router import get_current_user
from datetime import datetime, timezone

router = APIRouter()


@router.post("/new", response_model=StoryModel)
async def create_story(
    request: StoryCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    story_id = str(uuid.uuid4())
    workflow = create_workflow()  # Initialize LangGraph workflow

    # Initialize state with prompt
    initial_state = StoryStateModel(prompt=request.prompt)

    # Run async
    final_state = await workflow.ainvoke(initial_state)

    new_story = StoryModel(
        story_id=story_id,
        user_id=current_user.user_id,
        prompt=request.prompt,
        state=final_state,
        history=[{"role": "user", "content": request.prompt}],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    await db["stories"].insert_one(new_story.model_dump())
    logger.success(
        f"New story created with ID: {story_id} for user: {current_user.username}"
    )
    return new_story


@router.post("/continue/{story_id}", response_model=StoryModel)
async def continue_story(
    story_id: str,
    user_input: StoryCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    story = await db["stories"].find_one(
        {"story_id": story_id, "user_id": current_user["user_id"]}
    )
    if not story:
        logger.error(
            f"Story not found or access denied for story ID: {story_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Story not found"
        )

    story_doc = StoryModel(**story)
    workflow = create_workflow()  # Re-initialize LangGraph workflow

    # Feed existing state and new input
    story_doc.state.prompt = user_input.input_text
    updated_state = await workflow.ainvoke(story_doc.state)

    story_doc.state = updated_state
    story_doc.history.append({"role": "user", "content": user_input.input_text})
    story_doc.updated_at = datetime.now(timezone.utc)

    await db["stories"].update_one(
        {"story_id": story_id, "user_id": current_user["user_id"]},
        {
            "$set": {
                "state": story_doc.state.model_dump(),
                "history": story_doc.history,
                "updated_at": story_doc.updated_at,
            }
        },
    )

    logger.info(
        f"Story with ID: {story_id} updated for user: {current_user['username']}"
    )
    return story_doc


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
        logger.error(
            f"Story not found or access denied for story ID: {story_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Story not found"
        )

    logger.info(
        f"Story with ID: {story_id} retrieved for user: {current_user.username}"
    )
    return StoryModel(**story)
