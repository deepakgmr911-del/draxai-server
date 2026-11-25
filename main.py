import os
import httpx

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DraxAI Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "DraxAI server is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/chat/completions")
async def chat(request: dict):
    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("AI_MODEL")

    if not api_key or not model:
        raise HTTPException(
            status_code=503,
            detail="AI server configuration is missing"
        )

    payload = {
        "model": model,
        "messages": request.get("messages", []),
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                base_url.rstrip("/") + "/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail="AI provider returned an error"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to AI provider"
        )
