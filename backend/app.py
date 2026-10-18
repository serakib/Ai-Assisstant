from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os, io, asyncio, base64, requests
from dotenv import load_dotenv
from groq import Groq, AuthenticationError, APIStatusError
import edge_tts

load_dotenv()
app = Flask(__name__)
CORS(app)

GROQ_API_KEY = (
    os.getenv("GROQ_API_KEY") or
    os.getenv("GROK_API_KEY") or
    ""
).strip()

IMGBB_API_KEY = (os.getenv("IMGBB_API_KEY") or "").strip()

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

GROQ_TEXT_MODEL = "llama-3.3-70b-versatile"
GROQ_VISION_MODEL = "llama-3.2-11b-vision-preview"

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

SYSTEM_PROMPT_TEXT = (
    "You are an elite AI assistant integrated into the 'Medical Admission Tracker' app. "
    "You excel at coding, complex problem-solving, and advanced reasoning. "
    "You are also an expert medical admission guide for Bangladeshi students.\n\n"
    "Rules:\n"
    "1. If the user speaks in Bengali, reply in Bengali. If in English, reply in English.\n"
    "2. For coding questions, provide clean, well-commented code.\n"
    "3. Do NOT use LaTeX or complex math symbols in Bengali responses.\n"
    "4. Keep answers precise, clear, and highly helpful."
)

SYSTEM_PROMPT_VISION = (
    "You are an expert AI vision assistant. Analyze the provided image in detail. "
    "If it's a medical/biology diagram, explain the parts. "
    "If it's a math/physics problem, solve it step-by-step in Bengali. "
    "Be as helpful and accurate as possible."
)

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
        "provider": "Groq",
        "vision": "enabled",
        "tts": "edge-tts",
        "groq_key_set": bool(GROQ_API_KEY),
    })


@app.route('/api/chat', methods=['POST'])
def chat_groq():
    if not GROQ_API_KEY:
        return jsonify({
            "error": "GROQ_API_KEY missing. Add it on Render → Environment."
        }), 500

    try:
        user_message = request.form.get('message', '').strip()
        image_file = request.files.get('image')

        if not user_message and not image_file:
            return jsonify({"error": "Message or image required"}), 400

        if image_file:
            mime = image_file.mimetype
            if mime not in ['image/jpeg', 'image/png', 'image/webp', 'image/gif']:
                return jsonify({"error": "Only JPG, PNG, WEBP, GIF allowed"}), 400

            image_b64 = base64.b64encode(image_file.read()).decode('utf-8')
            response = client.chat.completions.create(
                model=GROQ_VISION_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_VISION},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_message or "এই ছবিটি বাংলায় বিশ্লেষণ করো।"},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}}
                    ]}
                ],
                temperature=0.5, max_tokens=1500
            )
            provider = "groq-vision"
        else:
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

    except AuthenticationError:
        return jsonify({
            "error": "401: GROQ_API_KEY invalid/expired. "
                     "Get new key at console.groq.com/keys and update Render Environment."
        }), 401
    except APIStatusError as e:
        return jsonify({"error": f"Groq API {e.status_code}: {e.message}"}), e.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_image():
    if not IMGBB_API_KEY:
        return jsonify({"error": "IMGBB_API_KEY missing."}), 500
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image"}), 400
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        response = requests.post(
            f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}",
            data={"image": image_data}
        )
        data = response.json()
        if data.get('success'):
            return jsonify({"success": True, "url": data['data']['display_url']})
        return jsonify({"error": "ImgBB upload failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
            communicate = edge_tts.Communicate(
                text, preset['voice'], rate=preset['rate'], pitch=preset['pitch']
            )
            audio = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio += chunk["data"]
            return audio

        audio_bytes = asyncio.run(generate())
        if not audio_bytes:
            return jsonify({"error": "No audio"}), 500

        return send_file(io.BytesIO(audio_bytes), mimetype='audio/mpeg', as_attachment=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File exceeds 5MB"}), 413


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
