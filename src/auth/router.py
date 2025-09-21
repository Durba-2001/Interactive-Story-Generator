from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from loguru import logger
from bson import ObjectId
from src.database.connection import get_db
from src.auth.models import UserSchema, UserCreate, UserResponse
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, REFRESH_SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()

# -------------------------
# JWT Functions
# -------------------------
def create_access_token(user: UserSchema, expires_delta: timedelta = None):
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(user.user_id),  # store user_id, not username
        "username": user.username,
        "email": user.email,
        "exp": expire
    }
    logger.debug(f"Creating access token for {user.username} expiring at {expire}")
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user: UserSchema, expires_delta: timedelta = None):
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    payload = {
        "sub": str(user.user_id),
        "username": user.username,
        "email": user.email,
        "exp": expire
    }
    logger.debug(f"Creating refresh token for {user.username} expiring at {expire}")
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

# -------------------------
# Auth Utilities
# -------------------------
async def authenticate_user(db, username: str, password: str):
    user = await db["users"].find_one({"username": username})
    if not user:
        logger.warning(f"Authentication failed: user '{username}' not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

    user_doc = UserSchema(**user)
    if not pwd_context.verify(password, user_doc.hashed_password):
        logger.warning(f"Authentication failed: incorrect password for '{username}'")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    logger.info(f"User authenticated successfully: {username}")
    return user_doc

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            logger.error("Token missing user_id")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user = await db["users"].find_one({"user_id": user_id})
        if not user:
            logger.error(f"User not found for token: {user_id}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

        logger.debug(f"Token validated for user: {user['username']}")
        return UserSchema(**user)
    except JWTError:
        logger.exception("JWT decode error")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# -------------------------
# Routes
# -------------------------
@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db=Depends(get_db)):
    logger.info(f"Register endpoint called for: {user.username}")
    existing = await db["users"].find_one({"username": user.username})
    if existing:
        logger.error(f"User already exists: {user.username}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    hashed_pw = pwd_context.hash(user.password)
    user_doc = UserSchema(
        user_id=str(ObjectId()),
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        created_at=datetime.now(timezone.utc)
    )
    await db["users"].insert_one(user_doc.model_dump())
    logger.success(f"User registered successfully: {user.username}")

    access_token = create_access_token(user_doc)
    refresh_token = create_refresh_token(user_doc)

    return {
        "username": user_doc.username,
        "email": user_doc.email,
        "created_at": user_doc.created_at,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    logger.info(f"Login endpoint called for: {form_data.username}")
    user = await authenticate_user(db, form_data.username, form_data.password)

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    logger.success(f"Login successful for: {user.username}")

    return {
        "username": user.username,
        "email": user.email,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token(refresh_token: str, db=Depends(get_db)):
    logger.info("Refresh token endpoint called")
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            logger.error("Refresh token missing user_id")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user = await db["users"].find_one({"user_id": user_id})
        if not user:
            logger.error(f"User not found for refresh token: {user_id}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

        user_doc = UserSchema(**user)
        new_access_token = create_access_token(user_doc)
        new_refresh_token = create_refresh_token(user_doc)
        logger.success(f"Tokens refreshed successfully for: {user_doc.username}")

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        logger.exception("JWT decode error on refresh")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
