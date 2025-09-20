
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from loguru import logger

from src.database.connection import get_db
from src.auth.models import UserSchema, UserCreate, UserResponse
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, REFRESH_SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter()

# -------------------------
# JWT Functions
# -------------------------
def create_access_token(username: str, expires_delta: timedelta = None):
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": username, "exp": expire}
    logger.debug(f"Creating access token for {username} expiring at {expire}")
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(username: str, expires_delta: timedelta = None):
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    payload = {"sub": username, "exp": expire}
    logger.debug(f"Creating refresh token for {username} expiring at {expire}")
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
        username = payload.get("sub")
        if not username:
            logger.error("Token missing username")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user = await db["users"].find_one({"username": username})
        if not user:
            logger.error(f"User not found for token: {username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

        logger.debug(f"Token validated for user: {username}")
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
        username=user.username,
        hashed_password=hashed_pw,
        created_at=datetime.now(timezone.utc)
    )
    await db["users"].insert_one(user_doc.model_dump())
    logger.success(f"User registered successfully: {user.username}")

    # Automatically return access token after registration
    access_token = create_access_token(user.username)
    refresh_token = create_refresh_token(user.username)

    return {
        "username": user_doc.username,
        "created_at": user_doc.created_at,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    logger.info(f"Login endpoint called for: {form_data.username}")
    user = await authenticate_user(db, form_data.username, form_data.password)

    access_token = create_access_token(user.username)
    refresh_token = create_refresh_token(user.username)
    logger.success(f"Login successful for: {user.username}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
