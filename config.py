"""
Vaani AI - Configuration & Constants
Voice AI Agent for Accessibility & Societal Impact
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── App Metadata ──────────────────────────────────────────────
APP_NAME = "Vaani AI"
APP_TAGLINE = "Voice AI for Everyone — Breaking Barriers, Building Bridges"
APP_VERSION = "1.0.0"

# ── API Keys ──────────────────────────────────────────────────
VAPI_API_KEY = os.getenv("VAPI_API_KEY", "")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID", "")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID", "")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ── Qdrant Collections ────────────────────────────────────────
COLLECTION_KNOWLEDGE = "vaani_knowledge_base"
COLLECTION_USER_HISTORY = "vaani_user_history"
COLLECTION_SESSIONS = "vaani_sessions"

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2

# ── Supported Languages ───────────────────────────────────────
LANGUAGES = {
    "en": {"name": "English", "flag": "🇬🇧", "native": "English"},
    "hi": {"name": "Hindi", "flag": "🇮🇳", "native": "हिन्दी"},
    "ta": {"name": "Tamil", "flag": "🇮🇳", "native": "தமிழ்"},
    "te": {"name": "Telugu", "flag": "🇮🇳", "native": "తెలుగు"},
    "bn": {"name": "Bengali", "flag": "🇧🇩", "native": "বাংলা"},
    "mr": {"name": "Marathi", "flag": "🇮🇳", "native": "मराठी"},
    "gu": {"name": "Gujarati", "flag": "🇮🇳", "native": "ગુજરાતી"},
    "kn": {"name": "Kannada", "flag": "🇮🇳", "native": "ಕನ್ನಡ"},
    "ml": {"name": "Malayalam", "flag": "🇮🇳", "native": "മലയാളം"},
    "pa": {"name": "Punjabi", "flag": "🇮🇳", "native": "ਪੰਜਾਬੀ"},
    "ur": {"name": "Urdu", "flag": "🇵🇰", "native": "اردو"},
    "es": {"name": "Spanish", "flag": "🇪🇸", "native": "Español"},
    "fr": {"name": "French", "flag": "🇫🇷", "native": "Français"},
    "ar": {"name": "Arabic", "flag": "🇸🇦", "native": "العربية"},
    "sw": {"name": "Swahili", "flag": "🇰🇪", "native": "Kiswahili"},
}

# ── Service Domains ───────────────────────────────────────────
SERVICE_DOMAINS = {
    "healthcare": {
        "icon": "🏥",
        "title": "Healthcare",
        "desc": "Symptom check, medicine info, doctor guidance",
        "color": "#E8F5E9",
        "accent": "#2E7D32",
    },
    "education": {
        "icon": "📚",
        "title": "Education",
        "desc": "Learning support, scholarships, skill programs",
        "color": "#E3F2FD",
        "accent": "#1565C0",
    },
    "finance": {
        "icon": "💰",
        "title": "Finance",
        "desc": "Banking help, government schemes, loans",
        "color": "#FFF8E1",
        "accent": "#F57F17",
    },
    "legal": {
        "icon": "⚖️",
        "title": "Legal Aid",
        "desc": "Rights awareness, legal guidance, RTI help",
        "color": "#F3E5F5",
        "accent": "#6A1B9A",
    },
    "agriculture": {
        "icon": "🌾",
        "title": "Agriculture",
        "desc": "Crop advice, weather, govt subsidies",
        "color": "#E8F5E9",
        "accent": "#388E3C",
    },
    "employment": {
        "icon": "💼",
        "title": "Employment",
        "desc": "Job search, skill development, MGNREGA",
        "color": "#FBE9E7",
        "accent": "#BF360C",
    },
}

# ── Vapi Assistant Prompts (System Prompts per domain) ────────
DOMAIN_SYSTEM_PROMPTS = {
    "healthcare": """You are a compassionate healthcare assistant named Vaani. 
    Help users in simple, clear language about health symptoms, when to see a doctor, 
    basic medicine information, and nearby health services. 
    Always recommend professional medical advice for serious issues. 
    Be sensitive to low-literacy users - use simple words and short sentences.""",
    
    "education": """You are an educational guidance assistant named Vaani. 
    Help users find scholarships, government education schemes, skill development programs, 
    and learning resources. Explain eligibility clearly. Support first-generation learners.""",
    
    "finance": """You are a financial literacy assistant named Vaani. 
    Explain banking, government schemes like PM-KISAN, Jan Dhan, PMJDY in simple terms. 
    Help users understand their rights, avoid fraud, and access formal financial services.""",
    
    "legal": """You are a legal awareness assistant named Vaani. 
    Help users understand their basic legal rights, how to file RTI, 
    domestic violence support, consumer rights, and legal aid services. 
    Always clarify you are not a lawyer but provide general awareness.""",
    
    "agriculture": """You are an agricultural support assistant named Vaani. 
    Help farmers with crop advice, weather information, government subsidies (PM-KISAN), 
    market prices, and pest management. Use simple language suitable for rural users.""",
    
    "employment": """You are an employment assistance guide named Vaani. 
    Help users find jobs, understand MGNREGA, skill development programs, 
    resume guidance, and vocational training. Support job seekers from all backgrounds.""",
}

# ── UI Theme ──────────────────────────────────────────────────
THEME = {
    "primary": "#1A73E8",
    "secondary": "#34A853",
    "accent": "#FBBC04",
    "danger": "#EA4335",
    "bg": "#F8F9FA",
    "card": "#FFFFFF",
    "text": "#202124",
    "muted": "#5F6368",
    "border": "#DADCE0",
}
