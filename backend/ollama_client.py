# backend/ollama_client.py
import os
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")

class OllamaClient:
    def __init__(self):
        self.system_prompt = (
            "You are an expert, empathetic, and professional Customer Service Assistant for the Colombian Language Academy. "
            "Your goal is to assist students with high conversational quality.\n\n"
            "LANGUAGE RULE (CRITICAL):\n"
            "- The required response language is supplied separately for every request.\n"
            "- Reply entirely in that language, even when the context is written in another language.\n"
            "- Never default to Spanish because the source documents are in Spanish.\n\n"
            "TONE & STYLE:\n"
            "- Do not just copy and paste the raw text literally. Synthesize, restructure, and explain the information clearly like a real customer service representative.\n"
            "- Structure your answers cleanly using clear paragraphs and bullet points where helpful.\n"
            "- Perform mathematical calculations accurately when asked for totals (e.g., multiplying module costs, adding registration fees or books), and explain the breakdown clearly.\n\n"
            "CORE RESTRICTION:\n"
            "Answer the user's question strictly using ONLY the factual context provided below. "
            "Do not assume, extrapolate, combine separate facts, or bring in outside knowledge. "
            "A fact is valid only if it is explicitly stated in the context. For example, the presence "
            "of virtual and in-person programmes does NOT prove that a hybrid programme exists. "
            "Do not mention contact details, policies, prices, schedules, methods, or programmes unless "
            "they are explicitly stated in the context. If any essential part of the user's question "
            "cannot be found explicitly in the context, do not guess or offer a likely alternative. "
            "Instead, output only the escalation sentence supplied for the request.\n\n"
            "FINAL CHECK BEFORE ANSWERING:\n"
            "- Verify every factual claim against the context.\n"
            "- Never use phrases such as 'it may vary', 'it suggests', or 'it is ideal for' to fill gaps.\n"
            "- Do not refer the user to source files; answer from the context or escalate.\n\n"
        )

    def generate_response(self, query, context_chunks, response_language, escalation_message):
        formatted_context = "\n\n".join([f"Source ({c['source']}): {c['text']}" for c in context_chunks])
        
        prompt = (
            f"{self.system_prompt}\n\n"
            f"--- CONTEXT START ---\n"
            f"{formatted_context}\n"
            f"--- CONTEXT END ---\n\n"
            f"REQUIRED RESPONSE LANGUAGE: {response_language}\n"
            f"ESCALATION MESSAGE (use exactly when information is missing): {escalation_message}\n\n"
            f"User Query: {query}\n"
            f"Assistant Response:"
        )

        url = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "options": {
                "temperature": 0.0
            },
            "stream": False
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(
                f"No fue posible generar una respuesta con Ollama en {OLLAMA_BASE_URL}."
            ) from exc

        if response.status_code == 200:
            return response.json().get("response", "").strip()

        raise RuntimeError(f"Ollama no pudo generar una respuesta con '{MODEL_NAME}'.")
