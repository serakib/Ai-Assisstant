from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app, origins=["https://serakib.github.io", "http://localhost:5500", "http://127.0.0.1:5500", "*"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")


@app.route('/')
def home():
    return jsonify({"status": "online", "provider": AI_PROVIDER})


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        if AI_PROVIDER == "groq":
            reply = call_groq(user_message)
        elif AI_PROVIDER == "openrouter":
            reply = call_openrouter(user_message)
        elif AI_PROVIDER == "gemini":
            reply = call_gemini(user_message)
        else:
            return jsonify({"error": "Invalid AI provider"}), 500

        return jsonify({"reply": reply, "provider": AI_PROVIDER})
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def call_groq(message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant for medical admission students in Bangladesh. Answer in the same language the user asks in."},
            {"role": "user", "content": message}
        ]
    }
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_openrouter(message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://serakib.github.io/Medical-Admission-Tracker/",
        "X-Title": "MedTracker AI"
    }
    payload = {
        "model": "meta-llama/llama-3.2-3b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant for medical admission students."},
            {"role": "user", "content": message}
        ]
    }
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_gemini(message):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    payload = {"contents": [{"parts": [{"text": message}]}]}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
