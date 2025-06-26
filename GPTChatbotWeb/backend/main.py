
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai, os, uuid

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경변수 비밀번호
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "12345678")
openai.api_key = os.getenv("OPENAI_API_KEY")

# 세션 저장소 (메모리)
sessions = {}

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        raise HTTPException(status_code=400, detail="아이디와 비밀번호가 필요합니다")
    is_admin = username.lower() == "admin" and password == ADMIN_PASSWORD
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"user": username, "is_admin": is_admin, "history": []}
    return {"session_id": session_id, "is_admin": is_admin}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    message = data.get("message")
    model = data.get("model", "gpt-3.5-turbo")

    if session_id not in sessions:
        raise HTTPException(status_code=403, detail="유효하지 않은 세션")

    if message == "[REPEAT_LAST]" and sessions[session_id]["history"]:
        history = sessions[session_id]["history"][:-1]  # 마지막 응답 제거
    else:
        sessions[session_id]["history"].append({"role": "user", "content": message})
        history = sessions[session_id]["history"]

    response = openai.ChatCompletion.create(
        model=model,
        messages=history,
        temperature=0.7,
        max_tokens=1024
    )
    reply = response.choices[0].message.content
    sessions[session_id]["history"].append({"role": "assistant", "content": reply})
    return {"reply": reply, "history": sessions[session_id]["history"]}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8", errors="ignore")
    return {"content": content.strip()[:1000]}  # 예시 요약

@app.post("/image")
async def image_description(file: UploadFile = File(...)):
    return {"description": "[이미지 설명 결과 예시]"}

@app.post("/voice")
async def voice_upload(file: UploadFile = File(...)):
    return {"text": "[음성 인식 결과 예시]"}

@app.get("/admin")
async def admin_log(session_id: str):
    if session_id not in sessions or not sessions[session_id]["is_admin"]:
        raise HTTPException(status_code=403, detail="관리자 권한 없음")
    return {"all_sessions": sessions}
