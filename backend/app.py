from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os, io, asyncio, base64, requests
from dotenv import load_dotenv
from groq import Groq
import edge_tts

load_dotenv()
app = Flask(__name__)
CORS(app, origins=[
    "https://serakib.github.io",
    "http://localhost:5500", "http://127.0.0.1:5500",
    "http://localhost:5000", "http://127.0.0.1:5000",
    "*" # ফ্রন্টএন্ড ডেভেলপমেন্টের সুবিধার্থে
])

# ==========================================
# 🔑 API KEYS & MODELS
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") # Render-এ এটা যোগ করতে হবে
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")       # Render-এ এটা যোগ করতে হবে

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set!")

client = Groq(api_key=GROQ_API_KEY)
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# ==========================================
# 📝 SYSTEM PROMPTS
# ==========================================
SYSTEM_PROMPT_GROQ = (
    "তুমি Medical Admission Tracker-এর একজন সহায়ক AI। "
    "মেডিকেল ভর্তি, প্রশ্নপত্র, সিলেবাস, প্রস্তুতি সংক্রান্ত প্রশ্নের উত্তর দাও। "
    "বাংলায় সংক্ষেপে এবং স্পষ্টভাবে উত্তর দাও। "
    "যদি ছবি পাঠানো হয়, ছবির বিষয়বস্তু বিশ্লেষণ করে সাহায্য কর। "
    "\n\nগুরুত্বপূর্ণ নিয়ম:\n"
    "১. কোনো LaTeX বা গাণিতিক চিহ্ন ($, \\, \\frac, \\int, ^, _) ব্যবহার করবে না। "
    "২. অঙ্ক বা সূত্র সাধারণ বাংলা লেখায় লিখবে। "
    "৩. উত্তর হবে সহজ, একজন সাধারণ শিক্ষার্থী যেন বুঝতে পারে।"
)

SYSTEM_PROMPT_DEEPSEEK = (
    "You are a highly capable AI assistant integrated into the 'Medical Admission Tracker' app. "
    "You excel at complex problem-solving, coding (Python, JS, etc.), and advanced reasoning. "
    "You can answer any question the user asks, but keep your tone helpful and concise. "
    "If the user speaks in Bengali, reply in Bengali. If in English, reply in English."
)

# ==========================================
# 🎙️ VOICE PRESETS (Edge-TTS)
# ==========================================
VOICE_PRESETS = {
    "emma":      {"voice": "bn-BD-NabanitaNeural",  "rate": "+0%",  "pitch": "+0Hz"},
    "ryan":      {"voice": "bn-BD-PradeepNeural",   "rate": "+0%",  "pitch": "+0Hz"},
    "sophia":    {"voice": "bn-IN-TanishaaNeural",  "rate": "+8%",  "pitch": "+5Hz"},
    "david":     {"voice": "bn-IN-BashkarNeural",   "rate": "+0%",  "pitch": "+0Hz"},
    "olivia":    {"voice": "bn-BD-NabanitaNeural",  "rate": "-12%", "pitch": "-15Hz"},
    "james":     {"voice": "bn-BD-PradeepNeural",   "rate": "-10%", "pitch": "-20Hz"},
    "charlotte": {"voice": "en-US-AriaNeural",      "rate": "+0%",  "pitch": "+0Hz"},
}
VOICE_FALLBACK = "emma"

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "provider": "groq + deepseek",
        "groq_model": GROQ_MODEL,
        "tts": "edge-tts",
        "imgbb": "enabled" if IMGBB_API_KEY else "disabled",
        "voices": list(VOICE_PRESETS.keys())
    })

# ==========================================
# 🤖 ROUTE 1: GROQ AI CHAT (Text + Image Vision)
# ==========================================
@app.route('/api/chat', methods=['POST'])
def chat_groq():
    try:
        user_message = request.form.get('message', '').strip()
        image_file = request.files.get('image')
        if not user_message and not image_file:
            return jsonify({"error": "Message or image required"}), 400

        content_parts = []
        if user_message:
            content_parts.append({"type": "text", "text": user_message})
        else:
            content_parts.append({"type": "text", "text": "এই ছবিটি বিশ্লেষণ করে বাংলায় সংক্ষেপে বলো।"})

        if image_file:
            mime = image_file.mimetype
            if mime not in ['image/jpeg','image/png','image/webp','image/gif']:
                return jsonify({"error": "শুধু JPG, PNG, WEBP, GIF"}), 400
            image_b64 = base64.b64encode(image_file.read()).decode('utf-8')
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{image_b64}"}
            })

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_GROQ},
                {"role": "user", "content": content_parts}
            ],
            temperature=0.5, max_tokens=1500
        )
        return jsonify({"reply": response.choices[0].message.content, "provider": "groq"})
    except Exception as e:
        print(f"Groq Chat Error: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# 🧠 ROUTE 2: DEEPSEEK AI CHAT (For Coding/Complex Problems)
# ==========================================
@app.route('/api/deepseek', methods=['POST'])
def chat_deepseek():
    if not DEEPSEEK_API_KEY:
        return jsonify({"error": "DeepSeek API key missing in server."}), 500
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({"error": "Message required"}), 400

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_DEEPSEEK},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()

        if response.status_code != 200:
            raise Exception(response_data.get("error", {}).get("message", "DeepSeek API Error"))

        reply = response_data['choices'][0]['message']['content']
        return jsonify({"reply": reply, "provider": "deepseek"})
    except Exception as e:
        print(f"DeepSeek Error: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# 🖼️ ROUTE 3: IMGBB UPLOAD (For Avatars)
# ==========================================
@app.route('/api/upload', methods=['POST'])
def upload_image():
    if not IMGBB_API_KEY:
        return jsonify({"error": "ImgBB API key missing in server."}), 500
    try:
        if 'image' not in request.files:
            return jsonify({"error": "কোনো ছবি পাওয়া যায়নি"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "ফাইল সিলেক্ট করা হয়নি"}), 400

        # Read and encode to base64
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

        payload = {"image": image_data}
        response = requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}", data=payload)
        response_data = response.json()

        if response_data.get('success'):
            return jsonify({
                "success": True,
                "url": response_data['data']['display_url']
            })
        else:
            return jsonify({"error": "ImgBB তে আপলোড ব্যর্থ হয়েছে"}), 500
    except Exception as e:
        print(f"Upload Error: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# 🎙️ ROUTE 4: TEXT-TO-SPEECH (Edge-TTS)
# ==========================================
@app.route('/api/tts', methods=['POST'])
def tts():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        voice_key = data.get('voice', VOICE_FALLBACK)
        if not text:
            return jsonify({"error": "Text required"}), 400

        is_bangla = any('\u0980' <= c <= '\u09FF' for c in text)
        if voice_key not in VOICE_PRESETS:
            voice_key = VOICE_FALLBACK
        preset = VOICE_PRESETS[voice_key]

        if is_bangla and preset['voice'].startswith('en-'):
            preset = VOICE_PRESETS['emma']
        if not is_bangla and preset['voice'].startswith('bn-'):
            preset = VOICE_PRESETS['charlotte']

        text = text[:500]

        async def generate():
            communicate = edge_tts.Communicate(text, preset['voice'], rate=preset['rate'], pitch=preset['pitch'])
            audio = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio += chunk["data"]
            return audio

        audio_bytes = asyncio.run(generate())
        if not audio_bytes:
            return jsonify({"error": "No audio generated"}), 500

        return send_file(io.BytesIO(audio_bytes), mimetype='audio/mpeg', as_attachment=False)
    except Exception as e:
        print(f"TTS Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "ফাইল ৫ MB এর বেশি"}), 413

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
