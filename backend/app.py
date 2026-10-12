from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)

# ✅ CORS — সব প্রয়োজনীয় origin
CORS(app, origins=[
    "https://serakib.github.io",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
])

# ✅ Groq ক্লায়েন্ট
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set!")

client = Groq(api_key=GROQ_API_KEY)

# ✅ ভিশন মডেল
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

# ✅ সর্বোচ্চ ফাইল সাইজ: ৫ MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# ✅ System Prompt — LaTeX নিষিদ্ধ
SYSTEM_PROMPT = (
    "তুমি Medical Admission Tracker-এর একজন সহায়ক AI। "
    "মেডিকেল ভর্তি, প্রশ্নপত্র, সিলেবাস, প্রস্তুতি সংক্রান্ত প্রশ্নের উত্তর দাও। "
    "বাংলায় সংক্ষেপে এবং স্পষ্টভাবে উত্তর দাও। "
    "যদি ছবি পাঠানো হয়, ছবির বিষয়বস্তু বিশ্লেষণ করে সাহায্য কর। "
    "\n\nগুরুত্বপূর্ণ নিয়ম:\n"
    "১. কোনো LaTeX বা গাণিতিক চিহ্ন ($, \\, \\frac, \\int, ^, _) ব্যবহার করবে না। "
    "২. অঙ্ক বা সূত্র সাধারণ বাংলা লেখায় লিখবে। "
    "৩. উদাহরণ: 'x এর বর্গ' বা 'x²' লিখবে, '$x^2$' নয়। "
    "৪. ভগ্নাংশ লিখতে '২/৩' বা '২ ভাগ ৩' লিখবে, '\\frac{2}{3}' নয়। "
    "৫. উত্তর হবে সহজ, একজন সাধারণ শিক্ষার্থী যেন বুঝতে পারে।"
)


@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "provider": "groq",
        "model": GROQ_MODEL,
        "features": ["text", "image"],
        "routes": ["/api/chat"]
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.form.get('message', '').strip()
        image_file = request.files.get('image')

        if not user_message and not image_file:
            return jsonify({"error": "Message or image required"}), 400

        content_parts = []

        if user_message:
            content_parts.append({"type": "text", "text": user_message})
        else:
            content_parts.append({
                "type": "text",
                "text": "এই ছবিটি বিশ্লেষণ করে বাংলায় সংক্ষেপে বলো।"
            })

        if image_file:
            mime_type = image_file.mimetype
            allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']

            if mime_type not in allowed:
                return jsonify({"error": "শুধু JPG, PNG, WEBP, GIF ছবি সাপোর্ট করে"}), 400

            image_bytes = image_file.read()
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')

            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_b64}"
                }
            })

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content_parts}
            ],
            temperature=0.5,
            max_tokens=1024
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply, "provider": "groq"})

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "ফাইল অনেক বড়, সর্বোচ্চ ৫ MB"}), 413


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
