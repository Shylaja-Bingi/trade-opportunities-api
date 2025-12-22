from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.config import settings
from app.models import TokenData, User

# Simple in-memory user store with plain passwords for demo
fake_users_db = {
    "guest": {
        "username": "guest",
        "password": "guest",  # Plain text for demo
        "disabled": False,
    },
    "trader": {
        "username": "trader", 
        "password": "trading123",  # Plain text for demo
        "disabled": False,
    }
}

def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return User(username=user_dict["username"], disabled=user_dict.get("disabled", False))
    return None

def authenticate_user(username: str, password: str):
    user_data = fake_users_db.get(username)
    if not user_data:
        return False
    # Simple plain text comparison for demo
    if password != user_data["password"]:
        return False
    return User(username=user_data["username"], disabled=user_data.get("disabled", False))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user