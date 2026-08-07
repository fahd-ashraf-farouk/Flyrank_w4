import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

# تحميل ملف .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 3000))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Supabase FastAPI Auth API",
    version="1.0.0",
    description="Authentication and Authorization API with Supabase and FastAPI"
)

# إعداد خيار HTTPBearer لعرض زر القفل في Swagger UI (/docs)
security = HTTPBearer()


class UserAuthSchema(BaseModel):
    email: EmailStr
    password: str


# --- Stage 4: Reusable Auth Dependency (Middleware Guard) ---
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
        )

    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        
        # إرجاع المستخدم والتوكن للاستخدام داخل الـ Routes
        return {"user": user, "token": token}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


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


# --- Stage 4: Logout Route ---
@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: dict = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# --- Stage 2 & 3: Public & Protected Routes ---
@app.get("/public/info", status_code=status.HTTP_200_OK)
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile", status_code=status.HTTP_200_OK)
def protected_profile(current_user: dict = Depends(get_current_user)):
    user = current_user["user"]
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }


# Stage 4 Checkpoint Route: Dashboard
@app.get("/protected/dashboard", status_code=status.HTTP_200_OK)
def protected_dashboard(current_user: dict = Depends(get_current_user)):
    user = current_user["user"]
    return {
        "message": f"Welcome to your dashboard, {user.email}!",
        "status": "active"
    }


if __name__ == "__main__":
    if supabase:
        print("Server running and connected to Supabase")
    uvicorn.run(app, host="0.0.0.0", port=PORT)