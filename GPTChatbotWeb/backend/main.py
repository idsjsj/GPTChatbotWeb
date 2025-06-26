# ✅ backend/main.py - All-in-One GPT Chatbot Backend (with password, history, model choice)
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai, os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

# Config
PASSWORD = "12345678"

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    if data.get("password") != PASSWORD:
        raise HTTPException(status_code=403, detail="Incorrect password")

    message = data.get("message", "")
    history = data.get("history", [])
    model = data.get("model", "gpt-4")

    messages = history + [{"role": "user", "content": message}]

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        return {"reply": reply, "history": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
