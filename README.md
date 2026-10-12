
---

## 🛠️ টেক স্ট্যাক

| স্তর | প্রযুক্তি |
|---|---|
| **ফ্রন্টএন্ড** | HTML5, CSS3, Vanilla JavaScript |
| **ব্যাকএন্ড** | Python 3.11, Flask, Flask-CORS |
| **AI প্রোভাইডার** | Groq (`qwen/qwen3.8-27b`) |
| **TTS (বাংলা ভয়েস)** | Google Text-to-Speech (gTTS) |
| **STT (ভয়েস ইনপুট)** | Web Speech API (ব্রাউজার বিল্ট-ইন) |
| **হোস্টিং** | GitHub Pages (ফ্রন্টএন্ড), Render.com (ব্যাকএন্ড) |

---

## 🚀 এই প্রজেক্ট কীভাবে বানাবেন — ধাপে ধাপে

### ধাপ ১: প্রস্তুতি

**যা যা লাগবে:**
- একটি GitHub অ্যাকাউন্ট
- একটি Render.com অ্যাকাউন্ট (ফ্রি)
- একটি Groq API Key (ফ্রি)
- Python 3.11+ (লোকাল টেস্টের জন্য)
- Chrome বা Edge ব্রাউজার (ভয়েসের জন্য)

### ধাপ ২: Groq API Key তৈরি

1. [Groq Console](https://console.groq.com)-এ যান
2. GitHub বা Google দিয়ে সাইনআপ করুন
3. বাম দিকে **API Keys** → **Create API Key**
4. কী কপি করুন (`gsk_...` দিয়ে শুরু হবে)
5. নিরাপদে রাখুন — পরে Render-এ লাগবে

### ধাপ ৩: GitHub রিপো তৈরি

1. GitHub-এ নতুন রিপো তৈরি করুন: `Ai-Assisstant`
2. README ছাড়া খালি রিপো বানান
3. আপনার কম্পিউটারে ক্লোন করুন

### ধাপ ৪: ফ্রন্টএন্ড তৈরি (`chat.html`)

**যা যা রাখবেন:**
- HTML স্ট্রাকচার: হেডার, মেইন (৪টি ভিউ), ফুটার
- CSS: থিম ভেরিয়েবল, ডার্ক মোড, রেসপন্সিভ
- JavaScript:
  - থিম টগল
  - Tabbed View System
  - FAQ Accordion
  - চ্যাট লজিক (fetch API)
  - ফাইল হ্যান্ডলিং
  - ভয়েস ইনপুট (Web Speech API)
  - ভয়েস আউটপুট (gTTS API কল)

**মূল কনফিগারেশন:**
- `BACKEND_URL` — Render-এর URL বসান
- `MAX_FILE_SIZE` — ৫ MB
- `SILENCE_TIMEOUT` — ২.৫ সেকেন্ড

### ধাপ ৫: ব্যাকএন্ড তৈরি (`app.py`)

**যা যা রাখবেন:**
- Flask অ্যাপ সেটআপ
- CORS কনফিগার (শুধু অনুমোদিত origin)
- Groq ক্লায়েন্ট ইনিশিয়ালাইজ
- System Prompt (LaTeX নিষিদ্ধ)
- ২টি এন্ডপয়েন্ট:
  - `POST /api/chat` — টেক্সট + ছবি
  - `POST /api/tts` — বাংলা ভয়েস

**মূল কনফিগারেশন:**
- `GROQ_API_KEY` — Environment Variable থেকে
- `GROQ_MODEL` — `qwen/qwen3.8-27b`
- `MAX_CONTENT_LENGTH` — ৫ MB

### ধাপ ৬: `requirements.txt` তৈরি

**যা যা লাগবে:**
- Flask
- flask-cors
- groq
- python-dotenv
- gunicorn
- gTTS

### ধাপ ৭: `.env` ফাইল তৈরি (লোকাল টেস্টের জন্য)

**যা যা রাখবেন:**
- `GROQ_API_KEY=gsk_...`
- `GROQ_MODEL=qwen/qwen3.8-27b`

⚠️ `.env` ফাইল কখনো GitHub-এ পুশ করবেন না। `.gitignore`-এ যোগ করুন।

### ধাপ ৮: `.gitignore` তৈরি

**যা যা রাখবেন:**
- `.env`
- `__pycache__/`
- `*.pyc`
- `venv/`
- `.venv/`

### ধাপ ৯: GitHub-এ Push

```bash

# 🚀 MedTracker AI — Deployment & Setup Guide

## GitHub-এ Push

```bash
git add .
git commit -m "Initial commit: MedTracker AI"
git push origin main
```

---

## ধাপ ১০: ফ্রন্টএন্ড ডিপ্লয় (GitHub Pages)

1. GitHub রিপো → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** → Folder: **/ (root)**
4. **Save** ক্লিক করুন
5. ২-৩ মিনিট পর সাইট লাইভ: `https://serakib.github.io/Ai-Assisstant/`

---

## ধাপ ১১: ব্যাকএন্ড ডিপ্লয় (Render.com)

1. Render Dashboard → **New** → **Web Service**
2. GitHub রিপো কানেক্ট করুন
3. সেটিংস:
   - **Name:** `ai-assisstant-2`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free
4. **Environment Variables:**

   | Key | Value |
   |---|---|
   | `GROQ_API_KEY` | `gsk_...` |
   | `GROQ_MODEL` | `qwen/qwen3.8-27b` |
   | `PYTHON_VERSION` | `3.11.0` |

5. **Create Web Service** ক্লিক করুন
6. লাইভ URL কপি করুন (যেমন: `https://ai-assisstant-2.onrender.com`)

---

## ধাপ ১২: ফ্রন্টএন্ড-ব্যাকএন্ড কানেক্ট

`chat.html`-এ `BACKEND_URL` লাইনটি খুঁজে Render-এর URL বসান:

```javascript
const BACKEND_URL = "https://ai-assisstant-2.onrender.com";
```

তারপর GitHub-এ আবার push করুন।

---

## ধাপ ১৩: টেস্ট করুন

1. `https://ai-assisstant-2.onrender.com/` খুলুন — JSON দেখাবে (সার্ভার ঠিক আছে)
2. `https://serakib.github.io/Ai-Assisstant/` খুলুন
3. `Ctrl + Shift + R` দিয়ে হার্ড রিফ্রেশ
4. টেক্সট, ছবি, ভয়েস — সব টেস্ট করুন

---

## 📡 API এন্ডপয়েন্ট

### `GET /`
সার্ভারের অবস্থা চেক।

### `POST /api/chat`
চ্যাট মেসেজ পাঠান (টেক্সট + ঐচ্ছিক ছবি)।

- **Request:** `multipart/form-data`
  - `message` (string) — টেক্সট
  - `image` (file) — ঐচ্ছিক ছবি
- **Response:** `{ "reply": "...", "provider": "groq" }`

### `POST /api/tts`
টেক্সট থেকে বাংলা অডিও তৈরি করে।

- **Request:** `application/json` — `{ "text": "..." }`
- **Response:** `audio/mpeg` (MP3 ফাইল)

---

## 🔐 নিরাপত্তা

- ✅ API Key কখনো ফ্রন্টএন্ডে রাখা হয় না
- ✅ CORS সীমাবদ্ধ — শুধু অনুমোদিত ডোমেইন
- ✅ ছবি সাইজ ৫ MB লিমিট
- ✅ `.gitignore`-এ `.env`

---

## 🧪 টেস্টিং চেকলিস্ট

- [ ] টেক্সট প্রশ্ন → AI উত্তর দেয়
- [ ] 📎 ছবি → AI বিশ্লেষণ করে
- [ ] 🎤 ক্লিক → AI বলে "আমি আপনাকে কীভাবে সাহায্য করতে পারি?"
- [ ] কথা বলা → ইনপুটে লেখা আসে
- [ ] ২.৫ সেকেন্ড চুপ → অটো সেন্ড
- [ ] 🔊 → AI-এর উত্তর বাংলায় শোনায়
- [ ] ডার্ক/লাইট টগল → থিম বদলায়
- [ ] FAQ Accordion → ক্লিকে খোলে
- [ ] মোবাইল ভিউ → সব রেসপন্সিভ

---

## 🐛 জানা সমস্যা ও সমাধান

| সমস্যা | কারণ | সমাধান |
|---|---|---|
| `401 UNAUTHENTICATED` | ভুল API Key বা OAuth মোড | Groq ব্যবহার করুন, env var ঠিক করুন |
| `404 model_not_found` | মডেল ডেপ্রিকেটেড | `qwen/qwen3.8-27b` ব্যবহার করুন |
| `insertBefore NotFoundError` | typingIndicator DOM-এর বাইরে | `chatMessages`-এর ভেতরে রাখুন |
| ভয়েস কাজ করে না | Firefox বা পারমিশন নেই | Chrome/Edge + মাইক Allow |
| বাংলা ভয়েস না আসে | ব্রাউজারে বাংলা ভয়েস নেই | gTTS ব্যাকএন্ড ব্যবহার করুন |
| Render সার্ভার ঘুমিয়ে | ফ্রি প্ল্যান ১৫ মিনিট নিষ্ক্রিয় | প্রথম রিকোয়েস্টে ৩০ সেকেন্ড অপেক্ষা |

---

## 💡 গুরুত্বপূর্ণ টিপস

1. **API Key কখনো GitHub-এ পুশ করবেন না** — `.env` + Render Environment Variable
2. **Render ফ্রি প্ল্যান** — ১৫ মিনিট নিষ্ক্রিয় থাকলে সার্ভার ঘুমায়
3. **প্রতিটি কমিটের পর** Render-এ Manual Deploy দিতে হয়
4. **হার্ড রিফ্রেশ** (`Ctrl + Shift + R`) সবসময় দরকার
5. **ভয়েস Chrome/Edge-এ** ভালো কাজ করে
6. **বাংলা ভয়েসের জন্য** gTTS ব্যাকএন্ড বাধ্যতামূলক
7. **লোকাল টেস্টে** `BACKEND_URL` বদলে `http://127.0.0.1:5000` দিন

---

## 🎯 ভবিষ্যৎ পরিকল্পনা

- [ ] চ্যাট হিস্টোরি ডেটাবেসে সেভ
- [ ] মাল্টি-ল্যাঙ্গুয়েজ সাপোর্ট (ইংরেজি UI)
- [ ] PDF ফাইল সাপোর্ট
- [ ] ভয়েস ক্লোনিং (ইউজারের নিজের কণ্ঠ)
- [ ] অ্যাডমিন প্যানেল
- [ ] প্রশ্ন-উত্তর ক্যাটাগরি
- [ ] ইউজার ফিডব্যাক সিস্টেম
- [ ] অফলাইন মোড

---

## 🤝 অবদান

1. Fork করুন
2. Feature branch বানান
3. Commit করুন
4. Push করুন
5. Pull Request খুলুন

---

## 📜 লাইসেন্স

MIT License

---

## 👨‍💻 ডেভেলপার

**S. Rakib**  
GitHub: [@serakib](https://github.com/serakib)

---

## 🙏 ক্রেডিট

- [Groq](https://groq.com) — দ্রুত AI ইনফারেন্স
- [Render.com](https://render.com) — ফ্রি ব্যাকএন্ড হোস্টিং
- [gTTS](https://github.com/pndurette/gTTS) — বাংলা TTS
- [Google Fonts](https://fonts.google.com) — Inter ফন্ট

---

**❤️ মেডিকেল শিক্ষার্থীদের জন্য ভালোবাসা দিয়ে তৈরি**
