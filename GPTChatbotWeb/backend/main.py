from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai, os, uuid, base64
import PyPDF2

openai.api_key = os.getenv("OPENAI_API_KEY")
PASSWORD = os.getenv("CHATBOT_PASSWORD", "12345678")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 프론트 정적 파일 제공
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

# 세션 메모리 저장소
sessions = {}  # { session_id: { name, is_admin, history: [] } }

@app.post("/login")
async def login(req: Request):
    data = await req.json()
    if data.get("password") != PASSWORD:
        raise HTTPException(status_code=403, detail="비밀번호가 틀렸습니다.")
    username = data.get("username", "anonymous")
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "name": username,
        "is_admin": username.lower() == "admin",
        "history": []
    }
    return {"session_id": session_id, "is_admin": username.lower() == "admin"}

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    session_id = data.get("session_id")
    message = data.get("message")
    model = data.get("model", "gpt-4")
    temperature = float(data.get("temperature", 0.7))
    max_tokens = int(data.get("max_tokens", 1024))

    if session_id not in sessions:
        raise HTTPException(status_code=400, detail="세션이 존재하지 않습니다.")

    session = sessions[session_id]
    history = session["history"]

    if message == "[REPEAT_LAST]":
        history = history[:-1] if history else []
    else:
        history.append({"role": "user", "content": message})

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=history,
            temperature=temperature,
            max_tokens=max_tokens
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        session["history"] = history
        return {"reply": reply, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset(req: Request):
    data = await req.json()
    session_id = data.get("session_id")
    if session_id in sessions:
        sessions[session_id]["history"] = []
    return {"status": "cleared"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = ""
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                content += text.strip() + "\n"
    elif file.filename.endswith(".txt"):
        content = (await file.read()).decode("utf-8").strip()
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")

    return {"content": content[:3000]}

@app.post("/voice")
async def voice_to_text(file: UploadFile = File(...)):
    try:
        response = openai.Audio.transcribe("whisper-1", file.file)
        return {"text": response["text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/image")
async def image_to_text(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        image_data_url = f"data:{file.content_type};base64,{base64_image}"
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "이 이미지를 설명해줘"},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }],
            max_tokens=1024
        )
        return {"description": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin")
async def admin_view(session_id: str):
    if session_id not in sessions or not sessions[session_id]["is_admin"]:
        raise HTTPException(status_code=403, detail="관리자 권한이 없습니다.")
    return {
        "all_sessions": {
            sid: {
                "user": sess["name"],
                "history": sess["history"]
            }
            for sid, sess in sessions.items()
        }
    }
