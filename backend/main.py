import os
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_engine import RAGEngine
from ollama_client import OllamaClient
from skills import register_student_skill, convert_currency_skill

app = FastAPI(title="Colombian Language Academy RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Initializing Colombian Language Academy Customer Service RAG Backend...")
rag = RAGEngine()
rag.load_documents()
ollama_client = OllamaClient()
print("Backend is ready!")

metrics_store = {
    "queriesProcessed": 0,
    "estimatedCost": 0.0,
    "escalatedCount": 0
}

semantic_cache = []

class QueryRequest(BaseModel):
    prompt: str

@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    try:
        raw_query = request.prompt.strip()
        if not raw_query:
            raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")
        
        normalized_query = " ".join(raw_query.lower().split())
        response_text = ""
        cached = False

        # 1. INTERCEPCIÓN DE SKILLS LOCALES (MCP / Habilidades personalizadas)
        if "inscribirme" in normalized_query or "registrar" in normalized_query:
            metrics_store["queriesProcessed"] += 1
            response_text = register_student_skill("Estudiante Local", "Francés", "A1", "contacto@academia.com")
            
            escalation_rate = (metrics_store["escalatedCount"] / metrics_store["queriesProcessed"]) * 100 if metrics_store["queriesProcessed"] > 0 else 0.0
            return {
                "response": response_text,
                "cached": False,
                "metrics": {
                    "queriesProcessed": metrics_store["queriesProcessed"],
                    "estimatedCost": round(metrics_store["estimatedCost"], 4),
                    "escalationRate": round(escalation_rate, 1)
                }
            }
            
        elif "en dólares" in normalized_query or "usd" in normalized_query:
            metrics_store["queriesProcessed"] += 1
            response_text = convert_currency_skill(740000.0)
            
            escalation_rate = (metrics_store["escalatedCount"] / metrics_store["queriesProcessed"]) * 100 if metrics_store["queriesProcessed"] > 0 else 0.0
            return {
                "response": response_text,
                "cached": False,
                "metrics": {
                    "queriesProcessed": metrics_store["queriesProcessed"],
                    "estimatedCost": round(metrics_store["estimatedCost"], 4),
                    "escalationRate": round(escalation_rate, 1)
                }
            }

        # 2. FLUJO NORMAL: CACHÉ Y RAG
        metrics_store["queriesProcessed"] += 1
        current_embedding = rag._get_embedding(raw_query)
        q_emb = np.array(current_embedding)

        matched_cached_response = None
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
                        # Umbral ajustado a 0.75 para mayor flexibilidad en paráfrasis
                        if similarity >= 0.80:
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
                is_english = any(word in raw_query.lower() for word in ["what", "how", "do", "you", "is", "are", "cost", "where", "can"])
                response_text = "I cannot find this information, escalating to a human agent." if is_english else "No encuentro esta información, escalando a un agente humano."
            else:
                response_text = ollama_client.generate_response(raw_query, retrieved_chunks)
                
                lower_resp = response_text.lower()
                if (
                    "no encontr" in lower_resp or 
                    "cannot find" in lower_resp or 
                    "escalating" in lower_resp or 
                    "escalando" in lower_resp or
                    "oficina de admisiones" in lower_resp or
                    "admissions office" in lower_resp
                ):
                    metrics_store["escalatedCount"] += 1

            if len(q_emb) > 0:
                semantic_cache.append({
                    "query": raw_query,
                    "embedding": current_embedding,
                    "response": response_text
                })

        escalation_rate = (metrics_store["escalatedCount"] / metrics_store["queriesProcessed"]) * 100 if metrics_store["queriesProcessed"] > 0 else 0.0

        return {
            "response": response_text,
            "cached": cached,
            "metrics": {
                "queriesProcessed": metrics_store["queriesProcessed"],
                "estimatedCost": round(metrics_store["estimatedCost"], 4),
                "escalationRate": round(escalation_rate, 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))