# 🎙️ Vaani AI — Voice AI for Accessibility & Societal Impact

> Breaking digital barriers through intelligent, multilingual voice AI

---

## 🌟 Overview

**Vaani AI** is a voice-first AI agent that bridges the digital divide for millions who face literacy, language, or usability barriers. Built with **Vapi** (voice AI) and **Qdrant** (vector search), it delivers personalized, contextual guidance across 6 service domains in 15+ languages.

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
cd vaani
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your Vapi & Qdrant keys
```

### 3. Start Qdrant (Docker)
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 4. Run the App
```bash
streamlit run app.py
```

### 5. Seed Knowledge Base
- Navigate to **Knowledge Base** → Click **"Seed Default KB"**

---


---

## 🔑 API Keys Needed

| Service | Purpose | Get at |
|---------|---------|--------|
| **Vapi** | Voice calls, AI assistant | [vapi.ai](https://vapi.ai) |
| **Qdrant** | Vector storage & search | [cloud.qdrant.io](https://cloud.qdrant.io) |
| **OpenAI** | Chat responses (optional) | [platform.openai.com](https://platform.openai.com) |

---

## 🌐 Features

- 🎙️ **Real Voice Calls** — Powered by Vapi with natural AI voice
- 🔍 **Semantic Search** — Qdrant RAG for contextual knowledge retrieval
- 🌍 **15+ Languages** — Hindi, Tamil, Telugu, Bengali, English & more
- 📞 **Phone Outreach** — Reach users without smartphones
- 🧠 **Personalization** — Qdrant stores user history for adaptive responses
- 📊 **Analytics** — Impact tracking dashboard
- 🏥 **6 Domains** — Healthcare, Finance, Education, Legal, Agriculture, Employment

---


## 📄 License

MIT License — Built for social good 🌱
