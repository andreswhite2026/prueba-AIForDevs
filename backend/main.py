import os
import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any
import numpy as np
import re
import unicodedata
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from rag_engine import RAGEngine
from ollama_client import OllamaClient
from skills import (
    convert_currency_skill,
    extract_registration_details,
    missing_registration_fields,
    register_student_skill,
    registration_missing_data_message,
)
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

LANGUAGE_NAMES = {
    "es": "Spanish",
    "en": "English",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
}
ESCALATION_MESSAGES = {
    "es": "No encuentro esta información, escalando a un agente humano.",
    "en": "I cannot find this information, escalating to a human agent.",
    "fr": "Je ne trouve pas cette information, je transmets votre demande à un agent humain.",
    "de": "Ich kann diese Information nicht finden und leite Ihre Anfrage an eine menschliche Fachkraft weiter.",
    "it": "Non trovo queste informazioni e inoltro la richiesta a un operatore umano.",
    "pt": "Não encontro estas informações e encaminho sua solicitação para um atendente humano.",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Colombian Language Academy RAG API")

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", ",".join(DEFAULT_CORS_ORIGINS)).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGEngine()
ollama_client = OllamaClient()
rag_ready = False
rag_error = "El índice RAG se está inicializando."


def initialize_rag() -> bool:
    """Build the local index without taking the HTTP API down if it fails."""
    global rag_ready, rag_error
    logger.info("Initializing Colombian Language Academy Customer Service RAG Backend...")
    try:
        rag.load_documents()
        rag_ready = True
        rag_error = ""
        logger.info("Backend is ready with %s indexed chunks.", len(rag.chunks))
        return True
    except Exception as exc:
        rag_ready = False
        rag_error = str(exc)
        logger.warning("RAG initialization failed; API remains available: %s", exc)
        return False


def initialize_rag_with_retries() -> None:
    """Retry in the background when Ollama is started after FastAPI."""
    while not initialize_rag():
        logger.info("Retrying RAG initialization in 5 seconds.")
        time.sleep(5)


@app.on_event("startup")
def start_rag_initialization() -> None:
    """Do not block FastAPI startup while Ollama loads or is unavailable."""
    threading.Thread(
        target=initialize_rag_with_retries,
        name="rag-initializer",
        daemon=True,
    ).start()


@app.get("/health")
def health_check():
    """Reports API and Ollama/RAG readiness without requiring a chat request."""
    return {
        "api": "ok",
        "ragReady": rag_ready,
        "ragError": None if rag_ready else rag_error,
    }

metrics_store = {
    "queriesProcessed": 0,
    "estimatedCost": 0.0,
    "escalatedCount": 0
}

semantic_cache = []
pending_registrations: dict[str, dict[str, Any]] = {}
pending_registrations_lock = threading.Lock()
REGISTRATION_DRAFT_TTL = timedelta(minutes=30)

class QueryRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2_000)
    session_id: str | None = Field(default=None, min_length=8, max_length=128)


def _metrics_payload(response_text: str, cached: bool = False) -> dict[str, Any]:
    escalation_rate = (
        (metrics_store["escalatedCount"] / metrics_store["queriesProcessed"]) * 100
        if metrics_store["queriesProcessed"]
        else 0.0
    )
    return {
        "response": response_text,
        "cached": cached,
        "metrics": {
            "queriesProcessed": metrics_store["queriesProcessed"],
            "estimatedCost": round(metrics_store["estimatedCost"], 4),
            "escalationRate": round(escalation_rate, 1),
        },
    }


def _escalation_message(language_code: str) -> str:
    return ESCALATION_MESSAGES.get(language_code, ESCALATION_MESSAGES["en"])


def _registration_intent(normalized_query: str) -> bool:
    # Detecta variaciones comunes de intención de inscripción.
    # Buscamos raíces y formas conjugadas para capturar frases como
    # "me quiero inscribir", "quiero inscribirme", "inscripción", "registrar", "matrícula", etc.
    try:
        return bool(
            re.search(r"\b(inscrib|inscripc|matricul|registr|apunt|inscribir|registrar)\w*\b", normalized_query)
        )
    except Exception:
        # En caso de cualquier error en la regex, no bloquear la ruta principal.
        return False


def _clear_expired_registration_drafts(now: datetime) -> None:
    expired_sessions = [
        session_id
        for session_id, draft in pending_registrations.items()
        if now - draft["updated_at"] > REGISTRATION_DRAFT_TTL
    ]
    for session_id in expired_sessions:
        pending_registrations.pop(session_id, None)


def _handle_registration(
    session_id: str | None, raw_query: str, normalized_query: str
) -> str | None:
    """Handle an enrollment without exposing personal data to the RAG/LLM."""
    details = extract_registration_details(raw_query)
    has_explicit_field = any(details.values())
    has_intent = _registration_intent(normalized_query)
    is_cancel = any(phrase in normalized_query for phrase in ("cancelar inscripción", "cancelar inscripcion", "cancelar registro"))
    now = datetime.now(timezone.utc)

    with pending_registrations_lock:
        _clear_expired_registration_drafts(now)
        draft = pending_registrations.get(session_id) if session_id else None

        if draft and is_cancel:
            pending_registrations.pop(session_id, None)
            return "Cancelé la solicitud de inscripción pendiente. No se creó ningún registro."

        # A normal knowledge-base question must remain available while a draft exists.
        if not has_intent and not (draft and has_explicit_field):
            return None

        merged_details = dict(draft["details"]) if draft else {}
        for field, value in details.items():
            if value:
                merged_details[field] = value

        missing_fields = missing_registration_fields(merged_details)
        if missing_fields:
            if session_id:
                pending_registrations[session_id] = {"details": merged_details, "updated_at": now}
            return registration_missing_data_message(missing_fields)

        if session_id:
            pending_registrations.pop(session_id, None)

    return register_student_skill(
        name=merged_details["name"],
        course=merged_details["course"],
        level=merged_details["level"],
        email=merged_details["email"],
    )

@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    try:
        raw_query = request.prompt.strip()
        if not raw_query:
            raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")
        
        normalized_query = " ".join(raw_query.lower().split())
        response_text = ""
        cached = False

        # Detección automática de idioma con langdetect
        try:
            detected_lang = detect(raw_query)
        except Exception:
            detected_lang = "es"
        
        response_language = LANGUAGE_NAMES.get(detected_lang, "the language of the user query")
        escalation_message = _escalation_message(detected_lang)

        # 1. INTERCEPCIÓN DE SKILLS LOCALES (MCP / Habilidades personalizadas)
        registration_response = _handle_registration(
            request.session_id, raw_query, normalized_query
        )
        if registration_response is not None:
            metrics_store["queriesProcessed"] += 1
            return _metrics_payload(registration_response)
            
        elif "en dólares" in normalized_query or "usd" in normalized_query:
            metrics_store["queriesProcessed"] += 1
            response_text = convert_currency_skill(740000.0)
            return _metrics_payload(response_text)

        # 2. FLUJO NORMAL: CACHÉ Y RAG
        if not rag_ready:
            raise HTTPException(
                status_code=503,
                detail=(
                    "El backend está activo, pero Ollama/RAG no está listo. "
                    f"Detalle: {rag_error}"
                ),
            )

        metrics_store["queriesProcessed"] += 1
        current_embedding = rag._get_embedding(raw_query)
        q_emb = np.array(current_embedding)

        matched_cached_response = None
        def _normalize_text(s: str) -> str:
            return "".join(
                c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn"
            )

        if semantic_cache and len(q_emb) > 0:
            for cached_item in semantic_cache:
                cached_emb = np.array(cached_item["embedding"])
                if len(cached_emb) == len(q_emb):
                    dot_product = np.dot(cached_emb, q_emb)
                    norm_a = np.linalg.norm(cached_emb)
                    norm_b = np.linalg.norm(q_emb)
                    if norm_a > 0 and norm_b > 0:
                        similarity = dot_product / (norm_a * norm_b)
                        print(f"DEBUG - Comparando con caché. Similitud: {similarity:.2f}")
                        
                        # Umbral estricto para evitar falsos positivos
                        if similarity >= 0.88:
                            cached_q = cached_item["query"]
                            # Normalizar para coincidencias insensibles a acentos
                            cached_q_norm = _normalize_text(cached_q)
                            query_norm = _normalize_text(normalized_query)

                            # Doble validación de intención (precio vs general) con más sinónimos
                            price_keywords = [
                                "cuanto", "cuánto", "precio", "precios", "costo", "costos",
                                "valor", "valores", "cuestan", "cuesta", "costar",
                                "dolares", "usd", "cop", "pesos",
                            ]
                            cached_is_price = any(w in cached_q_norm for w in price_keywords)
                            query_is_price = any(w in query_norm for w in price_keywords)

                            # Validación por idioma basada solo en la etiqueta de idioma almacenada
                            same_lang = (
                                cached_item.get("language") == detected_lang or cached_item.get("language") is None
                            )

                            if cached_is_price == query_is_price and same_lang:
                                matched_cached_response = cached_item["response"]
                                break

        if matched_cached_response:
            cached = True
            response_text = matched_cached_response
        else:
            metrics_store["estimatedCost"] += 0.0002
            retrieved_chunks = rag.retrieve(raw_query, top_k=3)
            
            if not retrieved_chunks:
                metrics_store["escalatedCount"] += 1
                response_text = escalation_message
            else:
                response_text = ollama_client.generate_response(
                    raw_query,
                    retrieved_chunks,
                    response_language,
                    escalation_message,
                )
                
                def _is_escalation_response(text: str) -> bool:
                    """Detecta si la respuesta representa una falta de información real
                    que justifique escalar a un operador humano.

                    Reglas principales:
                    - Si la respuesta contiene montos/cifras monetarias (ej. $ o COP o USD),
                      asumimos que no es una falta de información y NO escalamos.
                    - Si la respuesta contiene frases de incapacidad/ausencia de datos
                      ("no puedo", "no encuentro", "cannot find", "no hay información", etc.)
                      marcamos escalación.
                    - Palabras explícitas de escalación ("escalar", "escalating", "oficina de admisiones")
                      también indican escalado.
                    """
                    if not text:
                        return False
                    lower = text.lower()

                    # Si contiene signos de moneda o patrones de precio, no escalamos
                    if re.search(r"\$\s?\d|\d+\s?cop\b|cop\b|usd\b|\beuros?\b", lower):
                        return False

                    inability_pattern = re.compile(
                        r"\b(no\s+(?:encontr(?:é|o|ar)|puedo|tenemos|ten[eí]s|tengo)|"
                        r"no\s+hay\s+informaci[oó]n|cannot\s+find|can't\s+find|i\s+can't\s+find|"
                        r"no\s+es\s+posible|no\s+puedo\s+ayudar|no\s+tenemos)\b",
                        re.IGNORECASE,
                    )

                    if inability_pattern.search(lower):
                        return True

                    # Frases explícitas de escalación
                    if any(k in lower for k in ["escalar", "escalating", "escalando", "oficina de admisiones", "admissions office", "contacte" , "contactar"]):
                        return True

                    return False

                if _is_escalation_response(response_text):
                    metrics_store["escalatedCount"] += 1

            if len(q_emb) > 0:
                semantic_cache.append({
                    "query": raw_query,
                    "embedding": current_embedding,
                    "response": response_text,
                    "language": detected_lang,
                })

        return _metrics_payload(response_text, cached)
        
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error while processing /chat")
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error interno al procesar la consulta.",
        )
