from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai, os, uuid

openai.api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    session_id = data.get("session_id") or str(uuid.uuid4())
    message = data.get("message")
    model = data.get("model", "gpt-4")

    if session_id not in sessions:
        sessions[session_id] = []

    history = sessions[session_id]

    if message == "[REPEAT_LAST]":
        history = history[:-1]

    else:
        history.append({"role": "user", "content": message})

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=history,
            temperature=0.7,
            max_tokens=1024
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        return {"reply": reply, "history": history, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
