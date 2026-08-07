import os
from supabase import create_client, Client
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 3000))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Server running"}

if __name__ == "__main__":
    if supabase:
        print("Server running and connected to Supabase")
    uvicorn.run(app, host="0.0.0.0", port=PORT)