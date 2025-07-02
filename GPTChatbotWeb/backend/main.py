from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
import uuid

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정 (프론트엔드 연결 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_methods=["*"],
    allow_headers=["*"],
)

# 세션 저장소
sessions = {}  # session_id: [{"role": "user", "content": ...}, ...]

@app.get("/")
async def root():
    return {"message": "✅ GPT Chatbot 백엔드가 실행 중입니다."}

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    session_id = data.get("session_id") or str(uuid.uuid4())
    message = data.get("message")
    model = data.get("model", "gpt-4")

    if not message:
        raise HTTPException(status_code=400, detail="메시지가 비어 있습니다.")

    # 세션 초기화
    if session_id not in sessions:
        sessions[session_id] = []

    history = sessions[session_id]

    # 다시 생성 요청이면 마지막 질문 제거
    if message == "[REPEAT_LAST]":
        history = history[:-1]
    else:
        history.append({"role": "user", "content": message})

    try:
        # OpenAI GPT 호출
        response = openai.ChatCompletion.create(
            model=model,
            messages=history,
            temperature=0.7,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        return {"reply": reply, "history": history, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI 오류: {str(e)}")
