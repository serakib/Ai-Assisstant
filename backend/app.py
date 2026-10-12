from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# CORS সেটআপ (আপনার GitHub Pages ও লোকালহোস্ট থেকে রিকোয়েস্ট গ্রহণ)
CORS(app, origins=[
    "https://serakib.github.io",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "provider": "gemini",
        "model": GEMINI_MODEL
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        reply = call_gemini(user_message)
        return jsonify({"reply": reply, "provider": "gemini"})

    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = e.response.json().get("error", {}).get("message", str(e))
        except:
            error_detail = str(e)
        print(f"Gemini HTTP Error: {error_detail}")
        return jsonify({"error": f"Gemini API error: {error_detail}"}), 500

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def call_gemini(message):
    """Google Gemini API কল করা"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in environment variables")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY   # AQ. key-এর জন্য এটাই সঠিক হেডার
    }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "You are a helpful AI assistant for medical admission students in Bangladesh. "
                            "Always answer in the same language the user asks in (Bengali or English). "
                            "Keep answers concise, accurate, and helpful."
                        )
                    }
                ]
            },
            {
                "role": "user",
                "parts": [{"text": message}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
