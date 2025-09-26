import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import AsyncMongoClient
from src.endpoints import router_auth
from src.database.connection import get_db
from src.auth.models import UserCreate
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt,JWTError
from src.config import SECRET_KEY,ALGORITHM,REFRESH_SECRET_KEY
from src.config import MongoDB_url
# ---- Simple DB Setup ----
async def override_get_db():
    client = AsyncMongoClient(MongoDB_url) 
    db = client["test_story_db"]
    await db.users.drop()     # clean before each test
    return db


# ---- Test App ----
app = FastAPI()
app.include_router(router_auth.router, prefix="/auth")
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ---- Import route functions directly ----
register = router_auth.register
login = router_auth.login


# ---- TEST CASES ----
@pytest.mark.asyncio
async def test_register_success():
    db = await override_get_db()
    user_data = UserCreate(username="alice", password="secret123", email= "alice@gmail.com")
    resp = await register(user=user_data, db=db)

    assert resp["username"] == "alice"
    assert resp["email"] == "alice@gmail.com"
    


@pytest.mark.asyncio
async def test_register_duplicate_user():
    db = await override_get_db()
    user_data = UserCreate(username="bob", password="secret123",email="bob@gmail.com")
    await register(user=user_data, db=db)  # first time ok

    with pytest.raises(Exception):
        await register(user=user_data, db=db)  # should raise validation_error

@pytest.mark.asyncio
async def test_login_success():
    db = await override_get_db()

    # register first
    user_data = UserCreate(username="charlie", password="mypassword",email="charlie@gmail.com")
    await register(user=user_data, db=db)
    # simulate login form
   
    form = OAuth2PasswordRequestForm(username="charlie", password="mypassword", scope="")

    resp = await login(form_data=form, db=db)
    assert "access_token" in resp
    assert resp["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_user():
    db = await override_get_db()


    form = OAuth2PasswordRequestForm(username="ghost", password="wrongpw", scope="")

    with pytest.raises(Exception):
        await login(form_data=form, db=db)

@pytest.mark.asyncio
async def test_login_wrong_password():
    db = await override_get_db()

    # Register a user
    user_data = UserCreate(username="dave", password="correctpw", email="dave@gmail.com")
    await register(user=user_data, db=db)

    # Try logging in with wrong password
    form = OAuth2PasswordRequestForm(username="dave", password="wrongpw", scope="")
    with pytest.raises(Exception):
        await login(form_data=form, db=db)
   
@pytest.mark.asyncio
async def test_login_wrong_username():
    db = await override_get_db()

    # Register real user
    user_data = UserCreate(username="eve", password="testpw",email="eve@gmail.com")
    await register(user=user_data, db=db)

    # Try login with wrong username
    form = OAuth2PasswordRequestForm(username="not_eve", password="testpw", scope="")
    with pytest.raises(Exception) :
        await login(form_data=form, db=db)
    
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    db = await override_get_db()
    user_data = UserCreate(username="harry", password="harrypw", email="harry@gmail.com")
    registered = await router_auth.register(user=user_data, db=db)

    token = registered["access_token"]
    current_user = await router_auth.get_current_user(token=token, db=db)

    assert current_user.username == "harry"
    assert current_user.email == "harry@gmail.com"

@pytest.mark.asyncio
async def test_access_token_contains_user_info():
    db=await override_get_db()
    user_data= UserCreate(username="frank",password="secret12",email="frank@gmail.com")
    user=await router_auth.register(user=user_data,db=db)
    token=user["access_token"]
    payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    assert payload["sub"]==user["user_id"]
    assert payload["username"]=="frank"
    assert payload["email"]=="frank@gmail.com"
    assert "exp" in payload

@pytest.mark.asyncio
async def test_refresh_token_contains_user_info():
    db=await override_get_db()
    user_data= UserCreate(username="grace",password="secret12",email="grace@gmail.com")
    user=await router_auth.register(user=user_data,db=db)
    token=user["refresh_token"]
    payload=jwt.decode(token,REFRESH_SECRET_KEY,algorithms=[ALGORITHM])
    assert payload["sub"]==user["user_id"]
    assert payload["username"]=="grace"
    assert payload["email"]=="grace@gmail.com"
    assert "exp" in payload