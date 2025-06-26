import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 환경변수에서 비밀번호 불러오기, 기본값 12345678
CHATBOT_PASSWORD = os.getenv("CHATBOT_PASSWORD", "12345678")

# GPT 옵션 기본값
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024

def preprocess_pdf_text(text: str) -> str:
    # PDF 텍스트 전처리 - 불필요한 공백 제거
    return text.strip()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    password = data.get('password')
    user_input = data.get('message')
    temperature = data.get('temperature', DEFAULT_TEMPERATURE)
    max_tokens = data.get('max_tokens', DEFAULT_MAX_TOKENS)

    # 비밀번호 확인
    if password != CHATBOT_PASSWORD:
        return jsonify({"error": "Invalid password"}), 401

    # GPT 호출 예시 (여기선 예시로 간단히 반환)
    # 실제로는 OpenAI API 호출 코드 삽입
    response_text = f"Received your message: {user_input}\nOptions - temp: {temperature}, max_tokens: {max_tokens}"

    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(debug=True)
 
