from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai
import os
import PyPDF2

# ✅ API 키 및 비밀번호는 환경변수로부터
openai.api_key = os.getenv("OPENAI_API_KEY")
PASSWORD = os.getenv("CHATBOT_PASSWORD", "12345678")

app = FastAPI()

# ✅ CORS 허용 (프론트와 연결)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 프론트엔드 정적 파일 제공
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

# ✅ 채팅 처리 API
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    # 🔐 비밀번호 확인
    if data.get("password") != PASSWORD:
        raise HTTPException(status_code=403, detail="Incorrect password")

    message = data.get("message", "")
    history = data.get("history", [])
    model = data.get("model", "gpt-4")
    temperature = float(data.get("temperature", 0.7))
    max_tokens = int(data.get("max_tokens", 1024))

    messages = history + [{"role": "user", "content": message}]

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        return {"reply": reply, "history": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ 파일 업로드 API (.pdf, .txt)
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
        raise HTTPException(status_code=400, detail="Unsupported file format")

    return {"content": content[:3000]}  # 최대 3,000자만 미리보기로 반환
