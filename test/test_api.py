# tests/integration/test_story_async.py
import pytest
from httpx import AsyncClient
from src.main import app
from src.database.connection import get_db
from pymongo import AsyncMongoClient
import os
from dotenv import load_dotenv, find_dotenv
from src.endpoints.router_auth import get_current_user
from types import SimpleNamespace

# ---------------------------
# Load environment
# ---------------------------
load_dotenv(find_dotenv())
MONGODB_URL = os.environ.get("MONGODB_URI")
TEST_DB_NAME = "test_story_db"

# ---------------------------
# Async DB override
# ---------------------------
async def override_get_db():
    client = AsyncMongoClient(MONGODB_URL)
    db = client[TEST_DB_NAME]
    await db.drop_collection("stories")  # clean before each test
    try:
        yield db
    finally:
        await client.drop_database(TEST_DB_NAME)

# ---------------------------
# Fake user override
# ---------------------------
async def override_user():
    return SimpleNamespace(user_id="test_user", username="test_username")

# ---------------------------
# Apply overrides
# ---------------------------
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_user

# ---------------------------
# Tests
# ---------------------------

@pytest.mark.asyncio
async def test_create_story():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/stories/new", json={"prompt": "Test story"})
        assert resp.status_code == 200
        data = resp.json()
        assert "story_id" in data
        assert data["user_id"] == "test_user"

@pytest.mark.asyncio
async def test_get_all_stories():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create multiple stories
        await ac.post("/stories/new", json={"prompt": "Story 1"})
        await ac.post("/stories/new", json={"prompt": "Story 2"})

        resp = await ac.get("/stories/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2
        assert all(d["user_id"] == "test_user" for d in data)

@pytest.mark.asyncio
async def test_get_story():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        create_resp = await ac.post("/stories/new", json={"prompt": "My Story"})
        story_id = create_resp.json()["story_id"]

        resp = await ac.get(f"/stories/{story_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["story_id"] == story_id
        assert data["user_id"] == "test_user"

@pytest.mark.asyncio
async def test_continue_story():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        create_resp = await ac.post("/stories/new", json={"prompt": "Start Story"})
        story_id = create_resp.json()["story_id"]

        resp = await ac.post(f"/stories/{story_id}/continue", json={"prompt": "Continue Story"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["story_id"] == story_id
        assert data["user_id"] == "test_user"
        assert "Continue Story" in [m["content"] for m in data["full_story"].get("scenes", [])]

@pytest.mark.asyncio
async def test_delete_story():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        create_resp = await ac.post("/stories/new", json={"prompt": "Delete Me"})
        story_id = create_resp.json()["story_id"]

        resp = await ac.delete(f"/stories/{story_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert f"Story {story_id} deleted successfully" in data["message"]
