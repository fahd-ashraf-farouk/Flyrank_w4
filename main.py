import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
import uvicorn
from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel, EmailStr

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 3000))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()


class UserAuthSchema(BaseModel):
    email: EmailStr
    password: str


@app.get("/")
def read_root():
    return {"status": "Server running"}


# --- Stage 1 Routes ---
@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(credentials: UserAuthSchema):
    if not credentials.email or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    try:
        res = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not res.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sign up failed"
            )

        return {
            "message": "User created successfully",
            "user": res.user
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/auth/login", status_code=status.HTTP_200_OK)
def login(credentials: UserAuthSchema):
    if not credentials.email or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    try:
        res = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        if not res.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials"
            )

        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "token_type": "bearer"
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )


# --- Stage 2 Routes ---

# 1. GET /public/info
@app.get("/public/info", status_code=status.HTTP_200_OK)
def public_info():
    return {"message": "Welcome stranger! This info is public."}


# 2. GET /protected/profile
@app.get("/protected/profile")
def protected_profile(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required"
        )
    
    token = authorization.split(" ")[1]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required"
        )

    return {"message": "Access granted", "token": token}


if __name__ == "__main__":
    if supabase:
        print("Server running and connected to Supabase")
    uvicorn.run(app, host="0.0.0.0", port=PORT)