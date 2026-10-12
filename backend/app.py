from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
app = Flask(__name__)
CORS(app, origins=["https://serakib.github.io", "http://127.0.0.1:5000"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

@app.route('/')
def home():
    return jsonify({"status": "online", "provider": "groq", "model": MODEL})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "তুমি Medical Admission Tracker-এর একজন সহায়ক AI। বাংলায় সংক্ষেপে উত্তর দাও।"},
                {"role": "user", "content": user_message}
            ]
        )
        return jsonify({"reply": response.choices[0].message.content, "provider": "groq"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
