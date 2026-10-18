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
    "*" 
])

# ==========================================
# 🔑 API KEYS & SETUP (Using your existing Groq key)
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY is not set!")

client = Groq(api_key=GROQ_API_KEY)

# মডেল সেটআপ
GROQ_TEXT_MODEL = "llama-3.3-70b-versatile" # কোডিং, রিজনিং ও মেডিকেল প্রশ্নের জন্য সেরা
GROQ_VISION_MODEL = "llama-3.2-11b-vision-preview" # ছবি বিশ্লেষণের জন্য

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# ==========================================
# 📝 SYSTEM PROMPTS
# ==========================================
SYSTEM_PROMPT_TEXT = (
    "You are an elite AI assistant integrated into the 'Medical Admission Tracker' app. "
    "You excel at coding, complex problem-solving, and advanced reasoning. "
    "You are also an expert medical admission guide for Bangladeshi students. "
    "\n\nRules:\n"
    "1. If the user speaks in Bengali, reply in Bengali. If in English, reply in English.\n"
    "2. For coding questions, provide clean, well-commented code.\n"
    "3. Do NOT use LaTeX or complex math symbols in Bengali responses. Explain math in simple text.\n"
    "4. Keep your answers precise, clear, and highly helpful."
)

SYSTEM_PROMPT_VISION = (
    "You are an expert AI vision assistant. Analyze the provided image in detail. "
    "If it's a medical/biology diagram, explain the parts. "
    "If it's a math/physics problem, solve it step-by-step in Bengali. "
    "Be as helpful and accurate as possible."
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
        "status": "online (Groq AI)",
        "provider": "Groq",
        "vision": "enabled",
        "tts": "edge-tts",
        "imgbb": "enabled" if IMGBB_API_KEY else "disabled"
    })

# ==========================================
# 🤖 ROUTE 1: GROQ AI CHAT (Text + Vision)
# ==========================================
@app.route('/api/chat', methods=['POST'])
def chat_groq():
    if not GROQ_API_KEY:
        return jsonify({"error": "Groq API key missing in server."}), 500

    try:
        user_message = request.form.get('message', '').strip()
        image_file = request.files.get('image')
        
        if not user_message and not image_file:
            return jsonify({"error": "Message or image required"}), 400

        # Vision (Image) Handling
        if image_file:
            mime = image_file.mimetype
            if mime not in ['image/jpeg','image/png','image/webp','image/gif']:
                return jsonify({"error": "Only JPG, PNG, WEBP, GIF allowed"}), 400
            
            image_b64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            content_parts = [
                {"type": "text", "text": user_message or "এই ছবিটি বিস্তারিত বিশ্লেষণ করে বাংলায় বলো।"},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}}
            ]
            
            response = client.chat.completions.create(
                model=GROQ_VISION_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_VISION},
                    {"role": "user", "content": content_parts}
                ],
                temperature=0.5, max_tokens=1500
            )
            provider = "groq-vision"
        else:
            # Text Chat
            response = client.chat.completions.create(
                model=GROQ_TEXT_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_TEXT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7, max_tokens=2048
            )
            provider = "groq-llama"

        return jsonify({"reply": response.choices[0].message.content, "provider": provider})
        
    except Exception as e:
        print(f"Groq Chat Error: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# 🖼️ ROUTE 2: IMGBB UPLOAD (For Avatars)
# ==========================================
@app.route('/api/upload', methods=['POST'])
def upload_image():
    if not IMGBB_API_KEY:
        return jsonify({"error": "ImgBB API key missing."}), 500
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        payload = {"image": image_data}
        response = requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}", data=payload)
        response_data = response.json()

        if response_data.get('success'):
            return jsonify({"success": True, "url": response_data['data']['display_url']})
        return jsonify({"error": "ImgBB upload failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 🎙️ ROUTE 3: TEXT-TO-SPEECH (Edge-TTS)
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
    return jsonify({"error": "File size exceeds 5MB limit"}), 413

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
