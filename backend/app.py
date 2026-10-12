from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from google import genai  # ✅ নতুন SDK ইমপোর্ট

load_dotenv()

app = Flask(__name__)
CORS(app, origins=[
    "https://serakib.github.io",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
])

# ✅ নতুন SDK-তে ক্লায়েন্ট তৈরি
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "provider": "gemini",
        "model": GEMINI_MODEL,
        "sdk": "google-genai"
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # ✅ নতুন SDK দিয়ে কনটেন্ট জেনারেট
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_message
        )

        return jsonify({"reply": response.text, "provider": "gemini"})

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
