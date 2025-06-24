from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

openai.api_key = "YOUR_OPENAI_API_KEY"

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    history = data.get("history", [])
    message = data.get("message", "")
    messages = history + [{"role": "user", "content": message}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=2048
    )
    reply = response.choices[0].message["content"]
    return {"reply": reply, "history": messages + [{"role": "assistant", "content": reply}]}
