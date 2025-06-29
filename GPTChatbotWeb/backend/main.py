from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai, os, uuid, base64
import PyPDF2

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 프론트엔드 정적 파일 경로
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

# 세션 저장소
sessions = {}

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    session_id = data.get("session_id") or str(uuid.uuid4())
    message = data.get("message")
    model = data.get("model", "gpt-4")
    temperature = float(data.get("temperature", 0.7))
    max_tokens = int(data.get("max_tokens", 1024))

    if session_id not in sessions:
        sessions[session_id] = {"history": []}

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
        return {"reply": reply, "history": history, "session_id": session_id}
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
