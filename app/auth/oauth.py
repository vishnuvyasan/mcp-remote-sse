from fastapi import Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import os

# These would typically be stored in environment variables or a secure configuration
# For demonstration purposes, they are hardcoded here
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory client database for demonstration
# In production, use a proper database
CLIENT_DATABASE = {
    "example_client_id": {
        "client_id": "example_client_id",
        "client_secret": "example_client_secret",
        "scopes": ["calculator", "sse"]
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Custom OAuth2 client credentials form
class OAuth2ClientCredentialsRequestForm:
    def __init__(
        self,
        grant_type: str = Form(...),
        client_id: str = Form(...),
        client_secret: str = Form(...),
        scope: str = Form(""),
    ):
        self.grant_type = grant_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scope.split() if scope else []

def authenticate_client(client_id: str, client_secret: str) -> Optional[Dict]:
    """
    Authenticate a client using client_id and client_secret
    """
    if client_id in CLIENT_DATABASE and CLIENT_DATABASE[client_id]["client_secret"] == client_secret:
        return CLIENT_DATABASE[client_id]
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_client(token: str = Depends(oauth2_scheme)):
    """
    Validate the access token and return the current client
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id = payload.get("sub")
        if client_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    client = CLIENT_DATABASE.get(client_id)
    if client is None:
        raise credentials_exception
        
    return client

async def get_token(form_data: OAuth2ClientCredentialsRequestForm = Depends()):
    """
    Authenticate client and provide an access token
    """
    # Validate grant type
    if form_data.grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type",
        )
        
    client = authenticate_client(form_data.client_id, form_data.client_secret)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect client_id or client_secret",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate requested scopes
    for scope in form_data.scopes:
        if scope not in client["scopes"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Client doesn't have access to scope: {scope}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": client["client_id"], "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "scope": " ".join(form_data.scopes)
    }

# Made with Bob
