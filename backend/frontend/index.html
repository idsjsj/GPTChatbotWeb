<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>GPT Chatbot</title>
  <style>
    body { font-family: sans-serif; padding: 2em; background: #f2f2f2; }
    #chatbox { background: white; padding: 1em; height: 400px; overflow-y: scroll; border: 1px solid #ccc; }
    input, button { margin-top: 1em; width: 100%; padding: 0.5em; }
  </style>
</head>
<body>
  <h2>GPT Chatbot</h2>
  <div id="chatbox"></div>
  <input id="userInput" placeholder="메시지를 입력하세요..." />
  <button onclick="sendMessage()">보내기</button>

  <script>
    const chatbox = document.getElementById('chatbox');
    const input = document.getElementById('userInput');
    let history = [];

    async function sendMessage() {
      const message = input.value;
      if (!message) return;
      chatbox.innerHTML += `<div><b>나:</b> ${message}</div>`;
      input.value = '';

      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, history })
      });

      const data = await res.json();
      history = data.history;
      chatbox.innerHTML += `<div><b>GPT:</b> ${data.reply}</div>`;
      chatbox.scrollTop = chatbox.scrollHeight;
    }
  </script>
</body>
</html>
