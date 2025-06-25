# backend/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai
import os

# OpenAI 키를 환경변수에서 읽어옵니다
openai.api_key = os.getenv("OPENAI_API_KEY")

# FastAPI 앱 인스턴스 선언 → 이 줄이 반드시 있어야 합니다!
app = FastAPI()

# CORS 전체 허용 (전체 도메인에서 호출 가능)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서비스 (frontend/index.html)
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

# POST /chat 엔드포인트
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    history = data.get("history", [])
    messages = history + [{"role": "user", "content": message}]
    # GPT 호출
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    reply = response.choices[0].message.content
    # 새 이력과 함께 응답 반환
    return {
        "reply": reply,
        "history": messages + [{"role": "assistant", "content": reply}]
    }
    
