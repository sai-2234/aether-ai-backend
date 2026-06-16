import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow requests from any Cloudflare Pages domain (or restrict to yours)
CORS(app, origins="*")

SERVER_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
INVOKE_URL     = "https://integrate.api.nvidia.com/v1/chat/completions"
DEFAULT_MODEL  = "meta/llama-3.1-70b-instruct"

SYSTEM_PROMPT = """You are Aether — an elite AI assistant engineered by Sai Chatre in 2026. You combine frontier intelligence with refined communication.

Personality & Tone:
- Speak with confidence, clarity, and intellectual depth — like a brilliant expert who also knows how to explain things simply.
- Be warm and personable, never cold or robotic. Adapt your tone: casual for small talk, precise for technical queries, empathetic for personal topics.
- Never be sycophantic — skip filler phrases like "Great question!" and get straight to the answer.

Response Quality:
- Lead with the answer, then explain. Never bury the key point.
- For simple questions: reply in 1–3 sentences. No padding.
- For complex questions: use headers, bullet points, and numbered steps for clarity.
- Always wrap code in properly labelled markdown code blocks.

Capabilities: software engineering, debugging, system design, mathematics, data analysis, research, science, creative writing, business strategy, language translation, everyday conversation.
- Always respond in the same language the user writes in."""


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Aether AI backend is running", "model": DEFAULT_MODEL}), 200


@app.route("/api/chat", methods=["POST"])
def chat():
    data         = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    history      = data.get("history", [])
    temperature  = float(data.get("temperature", 0.5))
    max_tokens   = int(data.get("max_tokens", 4096))
    byok_key     = data.get("byok_key", "").strip()
    model        = data.get("model", DEFAULT_MODEL)

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    key_to_use = byok_key if byok_key else SERVER_API_KEY
    if not key_to_use:
        return jsonify({"error": "No API key configured. Add NVIDIA_API_KEY to your Space secrets."}), 400

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-6:]:
        role    = msg.get("role", "")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {key_to_use}",
        "Content-Type":  "application/json",
        "Accept":        "text/event-stream",
    }
    payload = {
        "model":       model,
        "messages":    messages,
        "max_tokens":  max_tokens,
        "temperature": temperature,
        "top_p":       0.7,
        "stream":      True,
    }

    try:
        sess = requests.Session()
        r    = sess.post(INVOKE_URL, headers=headers, json=payload, stream=True, timeout=(20, 120))
        r.raise_for_status()
        full_reply = ""
        for line in r.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8").strip()
            if line_str.startswith("data:"):
                chunk = line_str[5:].strip()
                if chunk == "[DONE]":
                    break
                try:
                    obj   = json.loads(chunk)
                    delta = obj["choices"][0]["delta"].get("content", "")
                    if delta:
                        full_reply += delta
                except Exception:
                    pass
        if full_reply:
            return jsonify({"reply": full_reply})
        return jsonify({"error": "Empty response from AI"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502


if __name__ == "__main__":
    # Hugging Face Spaces uses port 7860 by default
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, threaded=True)
