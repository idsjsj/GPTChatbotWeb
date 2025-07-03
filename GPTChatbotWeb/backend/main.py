# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai

# OpenAI API 키 입력
openai.api_key = "YOUR_OPENAI_API_KEY"

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정 (프론트와 연결 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# POST 요청 처리: /api/chat
@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    return {"reply": response["choices"][0]["message"]["content"]}
