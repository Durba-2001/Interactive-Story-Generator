import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.endpoints.router_auth import get_current_user
from src.auth.models import UserSchema
from src.database.connection import get_db
from pymongo import AsyncMongoClient
from src.config import MongoDB_url
# -------------------------------
# Use test database
# -------------------------------
TEST_DB_NAME = "test_story_db"

def override_get_db():
    client = AsyncMongoClient(MongoDB_url)
    db = client[TEST_DB_NAME]
    try:
        yield db
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

# -------------------------------
# Override authentication
# -------------------------------
def override_get_current_user():
    return UserSchema(
        user_id="test_user",
        username="tester",
        email="tester@example.com",
        hashed_password="fakehashed"
    )

app.dependency_overrides[get_current_user] = override_get_current_user

# -------------------------------
# Fixtures
# -------------------------------
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def user():
    return {"user_id": "test_user"}

# -------------------------------
# Tests
# -------------------------------
@pytest.mark.asyncio
async def test_create_story(client, user):
    response = client.post("/stories/new", json={"prompt": "A hero saves the world"})
    assert response.status_code == 200
    data = response.json()
    assert "story_id" in data
    assert len(data["full_story"]["outline"]) > 0



@pytest.mark.asyncio
async def test_get_all_stories(client, user):
    response = client.get("/stories/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


