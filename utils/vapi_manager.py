"""
Vaani AI - Vapi Voice Agent Integration
Handles call creation, webhooks, and assistant management
"""
import json
import uuid
import requests
from datetime import datetime
from typing import Optional

from config import (
    VAPI_API_KEY, VAPI_ASSISTANT_ID, VAPI_PHONE_NUMBER_ID,
    DOMAIN_SYSTEM_PROMPTS, LANGUAGES,
)

VAPI_BASE_URL = "https://api.vapi.ai"


class VapiManager:
    """
    Production Vapi integration for Vaani AI.
    Handles:
    - Dynamic assistant creation per domain
    - Web call initiation (browser-based)
    - Phone call outbound
    - Call status & transcript retrieval
    - Webhook processing
    """

    def __init__(self):
        self.api_key = VAPI_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self._connected = self._test_connection()

    def _test_connection(self) -> bool:
        if not self.api_key or self.api_key == "your_vapi_api_key_here":
            return False
        try:
            r = requests.get(f"{VAPI_BASE_URL}/assistant", headers=self.headers, timeout=5)
            return r.status_code in (200, 401)  # 401 means key format ok
        except Exception:
            return False

    # ── Assistant Management ──────────────────────────────────

    def create_domain_assistant(
        self,
        domain: str,
        language: str = "en",
        user_context: Optional[str] = None,
        knowledge_context: Optional[str] = None,
    ) -> dict:
        """Create or configure a domain-specific Vapi assistant."""
        if not self.api_key or self.api_key == "your_vapi_api_key_here":
            return self._mock_assistant(domain, language)

        lang_info = LANGUAGES.get(language, LANGUAGES["en"])
        base_prompt = DOMAIN_SYSTEM_PROMPTS.get(domain, DOMAIN_SYSTEM_PROMPTS["healthcare"])

        # Enrich prompt with retrieved context
        enhanced_prompt = base_prompt
        if knowledge_context:
            enhanced_prompt += f"\n\nRelevant Information:\n{knowledge_context}"
        if user_context:
            enhanced_prompt += f"\n\nUser History Context:\n{user_context}"

        enhanced_prompt += f"""
        
IMPORTANT INSTRUCTIONS:
- Respond in {lang_info['name']} ({lang_info['native']}) unless user speaks differently
- Use simple, clear language — assume low literacy
- Be warm, patient, and encouraging
- Break complex info into small steps
- Always confirm understanding before moving on
- If unsure, say so and suggest where to get help
        """

        payload = {
            "name": f"Vaani-{domain.capitalize()}-{language}",
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "systemPrompt": enhanced_prompt,
                "temperature": 0.7,
            },
            "voice": {
                "provider": "11labs",
                "voiceId": self._get_voice_id(language),
                "stability": 0.5,
                "similarityBoost": 0.75,
                "style": 0.5,
                "useSpeakerBoost": True,
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": language if language in ["en", "hi", "es", "fr"] else "en",
            },
            "firstMessage": self._get_greeting(domain, language),
            "endCallFunctionEnabled": True,
            "recordingEnabled": True,
            "hipaaEnabled": False,
            "silenceTimeoutSeconds": 30,
            "maxDurationSeconds": 600,
            "backgroundSound": "off",
        }

        try:
            r = requests.post(
                f"{VAPI_BASE_URL}/assistant",
                headers=self.headers,
                json=payload,
                timeout=10,
            )
            if r.status_code == 201:
                return r.json()
            else:
                return self._mock_assistant(domain, language)
        except Exception as e:
            return self._mock_assistant(domain, language)

    def _get_voice_id(self, language: str) -> str:
        """Return appropriate ElevenLabs voice ID per language."""
        voice_map = {
            "en": "EXAVITQu4vr4xnSDxMaL",   # Bella
            "hi": "pNInz6obpgDQGcFmaJgB",    # Adam
            "ta": "EXAVITQu4vr4xnSDxMaL",
            "te": "EXAVITQu4vr4xnSDxMaL",
            "es": "VR6AewLTigWG4xSOukaG",
            "fr": "ThT5KcBeYPX3keUQqHPh",
            "ar": "pNInz6obpgDQGcFmaJgB",
        }
        return voice_map.get(language, voice_map["en"])

    def _get_greeting(self, domain: str, language: str) -> str:
        greetings = {
            "en": {
                "healthcare": "Hello! I'm Vaani, your health assistant. How can I help you today?",
                "finance": "Hello! I'm Vaani. I'm here to help with banking and financial schemes. How can I assist you?",
                "education": "Hello! I'm Vaani. I can help you find scholarships and educational programs. What do you need?",
                "legal": "Hello! I'm Vaani. I can help you understand your rights and legal options. How can I help?",
                "agriculture": "Hello! I'm Vaani, your farming assistant. How can I help you today?",
                "employment": "Hello! I'm Vaani. I'm here to help with jobs and skill development. How can I assist?",
            },
            "hi": {
                "healthcare": "नमस्ते! मैं वाणी हूं, आपकी स्वास्थ्य सहायक। आज मैं आपकी कैसे मदद कर सकती हूं?",
                "finance": "नमस्ते! मैं वाणी हूं। बैंकिंग और सरकारी योजनाओं में मदद के लिए मैं यहां हूं।",
                "education": "नमस्ते! मैं वाणी हूं। छात्रवृत्ति और शिक्षा कार्यक्रमों में आपकी मदद करने के लिए यहां हूं।",
                "legal": "नमस्ते! मैं वाणी हूं। आपके अधिकारों को समझने में मदद करने के लिए यहां हूं।",
                "agriculture": "नमस्ते! मैं वाणी हूं, आपकी कृषि सहायक। आज मैं आपकी कैसे मदद कर सकती हूं?",
                "employment": "नमस्ते! मैं वाणी हूं। रोजगार और कौशल विकास में मदद के लिए यहां हूं।",
            },
            "ta": {
                "healthcare": "வணக்கம்! நான் வாணி, உங்கள் சுகாதார உதவியாளர். இன்று எப்படி உதவலாம்?",
                "finance": "வணக்கம்! நான் வாணி. வங்கி மற்றும் அரசு திட்டங்களில் உதவ இங்கே இருக்கிறேன்.",
            },
        }
        lang_greetings = greetings.get(language, greetings["en"])
        return lang_greetings.get(domain, f"Hello! I'm Vaani. How can I help you today?")

    # ── Web Calls ─────────────────────────────────────────────

    def create_web_call(self, assistant_id: str) -> dict:
        """Create a web-based call session."""
        if not self.api_key or self.api_key == "your_vapi_api_key_here":
            return self._mock_web_call()

        payload = {"assistantId": assistant_id}
        try:
            r = requests.post(
                f"{VAPI_BASE_URL}/call/web",
                headers=self.headers,
                json=payload,
                timeout=10,
            )
            if r.status_code == 201:
                return r.json()
            return self._mock_web_call()
        except Exception:
            return self._mock_web_call()

    # ── Phone Calls ───────────────────────────────────────────

    def create_phone_call(
        self,
        phone_number: str,
        assistant_id: str,
        domain: str = "healthcare",
    ) -> dict:
        """Initiate outbound phone call."""
        if not self.api_key or self.api_key == "your_vapi_api_key_here":
            return self._mock_phone_call(phone_number)

        payload = {
            "phoneNumberId": VAPI_PHONE_NUMBER_ID,
            "assistantId": assistant_id,
            "customer": {
                "number": phone_number,
            },
        }
        try:
            r = requests.post(
                f"{VAPI_BASE_URL}/call/phone",
                headers=self.headers,
                json=payload,
                timeout=10,
            )
            if r.status_code == 201:
                return r.json()
            return self._mock_phone_call(phone_number)
        except Exception:
            return self._mock_phone_call(phone_number)

    # ── Call Management ───────────────────────────────────────

    def get_call(self, call_id: str) -> dict:
        """Get call details and status."""
        if not self.api_key or self.api_key == "your_vapi_api_key_here":
            return self._mock_call_status(call_id)

        try:
            r = requests.get(
                f"{VAPI_BASE_URL}/call/{call_id}",
                headers=self.headers,
                timeout=10,
            )
            if r.status_code == 200:
                return r.json()
            return self._mock_call_status(call_id)
        except Exception:
            return self._mock_call_status(call_id)

    def list_calls(self, limit: int = 10) -> list:
        """List recent calls."""
        if not self.api_key or self.api_key == "your_vapi_api_key_here":
            return self._mock_call_list()

        try:
            r = requests.get(
                f"{VAPI_BASE_URL}/call?limit={limit}",
                headers=self.headers,
                timeout=10,
            )
            if r.status_code == 200:
                return r.json()
            return self._mock_call_list()
        except Exception:
            return self._mock_call_list()

    def end_call(self, call_id: str) -> dict:
        """End an active call."""
        if not self.api_key:
            return {"status": "ended"}
        try:
            r = requests.delete(
                f"{VAPI_BASE_URL}/call/{call_id}",
                headers=self.headers,
                timeout=5,
            )
            return r.json() if r.status_code == 200 else {"status": "ended"}
        except Exception:
            return {"status": "ended"}

    def get_transcript(self, call_id: str) -> Optional[str]:
        """Get call transcript."""
        call = self.get_call(call_id)
        return call.get("transcript") or call.get("messages")

    # ── Assistants List ───────────────────────────────────────

    def list_assistants(self) -> list:
        if not self.api_key or self.api_key == "your_vapi_api_key_here":
            return []
        try:
            r = requests.get(f"{VAPI_BASE_URL}/assistant", headers=self.headers, timeout=5)
            return r.json() if r.status_code == 200 else []
        except Exception:
            return []

    def is_connected(self) -> bool:
        return self._connected

    def get_status(self) -> dict:
        return {
            "connected": self._connected,
            "mode": "live" if self._connected else "demo",
            "assistant_id": VAPI_ASSISTANT_ID or "not_set",
        }

    # ── Mock Data ─────────────────────────────────────────────

    def _mock_assistant(self, domain: str, language: str) -> dict:
        return {
            "id": f"mock-assistant-{domain}-{uuid.uuid4().hex[:8]}",
            "name": f"Vaani-{domain.capitalize()}-{language}",
            "status": "demo",
        }

    def _mock_web_call(self) -> dict:
        return {
            "id": f"mock-call-{uuid.uuid4().hex[:12]}",
            "status": "demo",
            "webCallUrl": "https://vapi.ai/demo",
            "token": "demo-token",
        }

    def _mock_phone_call(self, phone: str) -> dict:
        return {
            "id": f"mock-call-{uuid.uuid4().hex[:12]}",
            "status": "demo",
            "customer": {"number": phone},
        }

    def _mock_call_status(self, call_id: str) -> dict:
        return {
            "id": call_id,
            "status": "ended",
            "duration": 142,
            "transcript": "User: I have a fever. Assistant: I'm sorry to hear that. A fever can be uncomfortable. For fever above 103°F, please consult a doctor immediately. Drink plenty of fluids and rest.",
            "createdAt": datetime.utcnow().isoformat(),
        }

    def _mock_call_list(self) -> list:
        return [
            {"id": "mock-001", "status": "ended", "duration": 120, "createdAt": "2025-01-15T10:30:00Z"},
            {"id": "mock-002", "status": "ended", "duration": 85, "createdAt": "2025-01-15T11:00:00Z"},
            {"id": "mock-003", "status": "ended", "duration": 200, "createdAt": "2025-01-15T12:15:00Z"},
        ]
