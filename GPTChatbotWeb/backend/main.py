from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai
import os

# 👇 API 키는 환경변수에서 가져옴
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ 여기 반드시 있어야 함!
app = FastAPI()

# ✅ CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 정적 파일 (frontend 연결)
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

# ✅ 챗봇 POST 엔드포인트
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    history = data.get("history", [])
    messages = history + [{"role": "user", "content": message}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    reply = response.choices[0].message.content
    return {
        "reply": reply,
        "history": messages + [{"role": "assistant", "content": reply}]
    }
