"""
Vaani AI - Qdrant Vector Store Manager
Handles knowledge base, user history, and semantic search
"""
import uuid
import json
import time
from datetime import datetime
from typing import Optional

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, PointStruct,
        Filter, FieldCondition, MatchValue,
        SearchRequest, UpdateCollection,
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from config import (
    QDRANT_URL, QDRANT_API_KEY,
    COLLECTION_KNOWLEDGE, COLLECTION_USER_HISTORY, COLLECTION_SESSIONS,
    EMBEDDING_DIM,
)


class VaaniQdrantManager:
    """
    Production-grade Qdrant manager for Vaani AI.
    Handles:
    - Knowledge base ingestion & retrieval
    - User session & interaction history
    - Personalized context retrieval
    - Semantic search across domains
    """

    def __init__(self):
        self.client = None
        self.encoder = None
        self._initialized = False
        self._mock_mode = False

        # Try to connect
        self._connect()

    def _connect(self):
        """Initialize Qdrant client and embedding model."""
        if not QDRANT_AVAILABLE:
            self._mock_mode = True
            return

        try:
            kwargs = {"url": QDRANT_URL, "timeout": 10}
            if QDRANT_API_KEY:
                kwargs["api_key"] = QDRANT_API_KEY
            self.client = QdrantClient(**kwargs)
            self.client.get_collections()  # Test connection

            # Load embedding model
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

            self._ensure_collections()
            self._initialized = True
        except Exception as e:
            print(f"[Qdrant] Connection failed: {e}. Running in mock mode.")
            self._mock_mode = True

    def _ensure_collections(self):
        """Create collections if they don't exist."""
        if not self.client:
            return

        existing = {c.name for c in self.client.get_collections().collections}

        collections_config = [
            COLLECTION_KNOWLEDGE,
            COLLECTION_USER_HISTORY,
            COLLECTION_SESSIONS,
        ]

        for name in collections_config:
            if name not in existing:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(
                        size=EMBEDDING_DIM,
                        distance=Distance.COSINE,
                    ),
                )
                print(f"[Qdrant] Created collection: {name}")

    def encode(self, text: str) -> list:
        """Generate embedding for text."""
        if self.encoder:
            return self.encoder.encode(text).tolist()
        # Fallback: simple hash-based mock vector
        import hashlib
        h = hashlib.md5(text.encode()).hexdigest()
        return [(int(h[i:i+2], 16) / 255.0) for i in range(0, EMBEDDING_DIM * 2, 2)][:EMBEDDING_DIM]

    # ── Knowledge Base ────────────────────────────────────────

    def upsert_knowledge(self, documents: list[dict]) -> dict:
        """
        Ingest documents into knowledge base.
        Each doc: {text, domain, category, language, source, metadata}
        """
        if self._mock_mode:
            return {"status": "mock", "count": len(documents)}

        points = []
        for doc in documents:
            vec = self.encode(doc["text"])
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vec,
                payload={
                    "text": doc["text"],
                    "domain": doc.get("domain", "general"),
                    "category": doc.get("category", "info"),
                    "language": doc.get("language", "en"),
                    "source": doc.get("source", "manual"),
                    "created_at": datetime.utcnow().isoformat(),
                    **doc.get("metadata", {}),
                },
            )
            points.append(point)

        self.client.upsert(collection_name=COLLECTION_KNOWLEDGE, points=points)
        return {"status": "ok", "count": len(points)}

    def search_knowledge(
        self,
        query: str,
        domain: Optional[str] = None,
        language: Optional[str] = None,
        top_k: int = 5,
    ) -> list[dict]:
        """Semantic search in knowledge base."""
        if self._mock_mode:
            return self._mock_knowledge_results(query, domain)

        query_vec = self.encode(query)

        filters = []
        if domain:
            filters.append(FieldCondition(key="domain", match=MatchValue(value=domain)))
        if language:
            filters.append(FieldCondition(key="language", match=MatchValue(value=language)))

        qdrant_filter = Filter(must=filters) if filters else None

        results = self.client.search(
            collection_name=COLLECTION_KNOWLEDGE,
            query_vector=query_vec,
            query_filter=qdrant_filter,
            limit=top_k,
            with_payload=True,
        )

        return [
            {
                "text": r.payload["text"],
                "score": r.score,
                "domain": r.payload.get("domain"),
                "category": r.payload.get("category"),
                "source": r.payload.get("source"),
            }
            for r in results
        ]

    # ── User History ──────────────────────────────────────────

    def save_interaction(self, user_id: str, interaction: dict) -> str:
        """Save user voice/chat interaction for personalization."""
        if self._mock_mode:
            return str(uuid.uuid4())

        text = f"{interaction.get('query', '')} {interaction.get('response', '')}"
        vec = self.encode(text)

        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=COLLECTION_USER_HISTORY,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vec,
                    payload={
                        "user_id": user_id,
                        "query": interaction.get("query", ""),
                        "response": interaction.get("response", ""),
                        "domain": interaction.get("domain", "general"),
                        "language": interaction.get("language", "en"),
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": interaction.get("session_id", ""),
                        "call_id": interaction.get("call_id", ""),
                    },
                )
            ],
        )
        return point_id

    def get_user_context(self, user_id: str, current_query: str, top_k: int = 3) -> list[dict]:
        """Retrieve relevant past interactions for context."""
        if self._mock_mode:
            return []

        query_vec = self.encode(current_query)

        results = self.client.search(
            collection_name=COLLECTION_USER_HISTORY,
            query_vector=query_vec,
            query_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            ),
            limit=top_k,
            with_payload=True,
        )

        return [
            {
                "query": r.payload["query"],
                "response": r.payload["response"],
                "domain": r.payload.get("domain"),
                "timestamp": r.payload.get("timestamp"),
                "score": r.score,
            }
            for r in results
        ]

    def get_user_stats(self, user_id: str) -> dict:
        """Get user usage statistics."""
        if self._mock_mode:
            return {
                "total_interactions": 12,
                "domains_used": ["healthcare", "finance"],
                "languages_used": ["en", "hi"],
                "last_active": datetime.utcnow().isoformat(),
            }

        try:
            results = self.client.scroll(
                collection_name=COLLECTION_USER_HISTORY,
                scroll_filter=Filter(
                    must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
                ),
                limit=1000,
                with_payload=True,
            )
            records = results[0]
            domains = list({r.payload.get("domain") for r in records if r.payload.get("domain")})
            langs = list({r.payload.get("language") for r in records if r.payload.get("language")})
            last = max((r.payload.get("timestamp", "") for r in records), default="")
            return {
                "total_interactions": len(records),
                "domains_used": domains,
                "languages_used": langs,
                "last_active": last,
            }
        except Exception:
            return {"total_interactions": 0, "domains_used": [], "languages_used": [], "last_active": ""}

    # ── Session Management ────────────────────────────────────

    def save_session(self, session_data: dict) -> str:
        """Persist session metadata."""
        if self._mock_mode:
            return str(uuid.uuid4())

        session_text = json.dumps(session_data)
        vec = self.encode(session_text[:500])

        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=COLLECTION_SESSIONS,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vec,
                    payload={
                        **session_data,
                        "created_at": datetime.utcnow().isoformat(),
                    },
                )
            ],
        )
        return point_id

    # ── Analytics ─────────────────────────────────────────────

    def get_global_stats(self) -> dict:
        """Get platform-wide usage statistics."""
        if self._mock_mode:
            return {
                "total_queries": 1428,
                "total_users": 312,
                "knowledge_docs": 847,
                "top_domain": "healthcare",
                "top_language": "hi",
            }

        try:
            kb_count = self.client.count(COLLECTION_KNOWLEDGE).count
            hist_count = self.client.count(COLLECTION_USER_HISTORY).count
            return {
                "total_queries": hist_count,
                "knowledge_docs": kb_count,
                "status": "connected",
            }
        except Exception:
            return {"status": "error", "total_queries": 0, "knowledge_docs": 0}

    def is_connected(self) -> bool:
        return self._initialized and not self._mock_mode

    def get_status(self) -> dict:
        if self._mock_mode:
            return {"connected": False, "mode": "demo", "url": QDRANT_URL}
        return {"connected": True, "mode": "live", "url": QDRANT_URL}

    # ── Mock Data ─────────────────────────────────────────────

    def _mock_knowledge_results(self, query: str, domain: Optional[str]) -> list[dict]:
        """Return demo knowledge results when Qdrant is unavailable."""
        demo_results = {
            "healthcare": [
                {"text": "For fever above 103°F, drink plenty of fluids and consult a doctor immediately.", "score": 0.91, "domain": "healthcare", "category": "symptoms"},
                {"text": "Ayushman Bharat provides free health coverage up to ₹5 lakh per year for eligible families.", "score": 0.87, "domain": "healthcare", "category": "schemes"},
            ],
            "finance": [
                {"text": "PM-KISAN provides ₹6000/year to small and marginal farmers in 3 installments.", "score": 0.93, "domain": "finance", "category": "schemes"},
                {"text": "Jan Dhan Yojana provides zero-balance bank accounts with ₹10,000 overdraft facility.", "score": 0.89, "domain": "finance", "category": "banking"},
            ],
            "education": [
                {"text": "National Scholarship Portal (NSP) offers scholarships for SC/ST/OBC students up to post-graduation.", "score": 0.92, "domain": "education", "category": "scholarships"},
            ],
            "agriculture": [
                {"text": "Kisan Call Centre (1800-180-1551) provides 24/7 free agricultural advice in local languages.", "score": 0.90, "domain": "agriculture", "category": "helpline"},
            ],
            "legal": [
                {"text": "You can file an RTI application for ₹10 to get information from any government department.", "score": 0.88, "domain": "legal", "category": "rights"},
            ],
            "employment": [
                {"text": "PMKVY provides free skill training with monthly stipend and certificate recognized by industry.", "score": 0.91, "domain": "employment", "category": "training"},
            ],
        }
        key = domain if domain in demo_results else "healthcare"
        return demo_results.get(key, [])


# ── Knowledge Base Seeder ─────────────────────────────────────

SEED_KNOWLEDGE = [
    # Healthcare
    {"text": "Ayushman Bharat (PM-JAY) provides health coverage up to ₹5 lakh per year for 50 crore beneficiaries.", "domain": "healthcare", "category": "schemes", "language": "en", "source": "govt"},
    {"text": "For chest pain, call 108 emergency immediately. Do not drive yourself to the hospital.", "domain": "healthcare", "category": "emergency", "language": "en", "source": "medical"},
    {"text": "Oral Rehydration Solution (ORS) for diarrhea: mix 6 tsp sugar + 1/2 tsp salt in 1 liter clean water.", "domain": "healthcare", "category": "firstaid", "language": "en", "source": "WHO"},
    {"text": "National Health Mission provides free medicines and diagnostics at government health centers.", "domain": "healthcare", "category": "services", "language": "en", "source": "govt"},
    {"text": "ASHA workers in villages provide free maternal and child health services.", "domain": "healthcare", "category": "services", "language": "en", "source": "govt"},
    # Finance
    {"text": "PM-KISAN provides ₹6000/year to small farmers in 3 equal installments directly to bank account.", "domain": "finance", "category": "schemes", "language": "en", "source": "govt"},
    {"text": "Pradhan Mantri Jan Dhan Yojana (PMJDY) offers zero-balance bank accounts with free RuPay debit card.", "domain": "finance", "category": "banking", "language": "en", "source": "govt"},
    {"text": "Mudra loan provides up to ₹10 lakh for small businesses without collateral under 3 categories.", "domain": "finance", "category": "loans", "language": "en", "source": "govt"},
    {"text": "Never share OTP, CVV or PIN with anyone. Banks never ask for this information.", "domain": "finance", "category": "fraud", "language": "en", "source": "RBI"},
    # Education
    {"text": "Mid-Day Meal Scheme provides free nutritious meals to children in government schools up to class 8.", "domain": "education", "category": "schemes", "language": "en", "source": "govt"},
    {"text": "National Scholarship Portal (scholarships.gov.in) has 100+ scholarships for students from class 1 to PhD.", "domain": "education", "category": "scholarships", "language": "en", "source": "govt"},
    {"text": "Right to Education Act guarantees free and compulsory education for children aged 6-14 years.", "domain": "education", "category": "rights", "language": "en", "source": "govt"},
    {"text": "DigiLocker provides free digital storage for academic certificates, mark sheets and government documents.", "domain": "education", "category": "digital", "language": "en", "source": "govt"},
    # Agriculture
    {"text": "Kisan Call Centre (1800-180-1551) provides free agricultural advice 24/7 in 22 languages.", "domain": "agriculture", "category": "helpline", "language": "en", "source": "govt"},
    {"text": "PM Fasal Bima Yojana provides crop insurance to protect farmers from losses due to natural calamities.", "domain": "agriculture", "category": "insurance", "language": "en", "source": "govt"},
    {"text": "eNAM (National Agriculture Market) allows farmers to sell crops online at competitive prices.", "domain": "agriculture", "category": "market", "language": "en", "source": "govt"},
    # Legal
    {"text": "RTI application can be filed for ₹10 to get information from any government department within 30 days.", "domain": "legal", "category": "rights", "language": "en", "source": "govt"},
    {"text": "National Legal Services Authority (NALSA) provides free legal aid to poor people. Call 15100.", "domain": "legal", "category": "services", "language": "en", "source": "govt"},
    {"text": "Domestic violence victims can call 181 (Women Helpline) for immediate help and shelter.", "domain": "legal", "category": "emergency", "language": "en", "source": "govt"},
    # Employment
    {"text": "MGNREGA guarantees 100 days of paid work per year to rural households. Contact your Gram Panchayat.", "domain": "employment", "category": "schemes", "language": "en", "source": "govt"},
    {"text": "PMKVY (Pradhan Mantri Kaushal Vikas Yojana) provides free skill training with industry certification.", "domain": "employment", "category": "training", "language": "en", "source": "govt"},
    {"text": "National Career Service Portal (ncs.gov.in) lists jobs, training, and career counseling for all.", "domain": "employment", "category": "jobs", "language": "en", "source": "govt"},
]


def seed_knowledge_base(manager: VaaniQdrantManager) -> dict:
    """Seed the knowledge base with initial data."""
    return manager.upsert_knowledge(SEED_KNOWLEDGE)
