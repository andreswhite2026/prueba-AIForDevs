# backend/ollama_client.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")

class OllamaClient:
    def __init__(self):
        self.system_prompt = (
            "You are an expert, empathetic, and professional Customer Service Assistant for the Colombian Language Academy. "
            "Your goal is to assist students with high conversational quality.\n\n"
            "LANGUAGE RULE (CRITICAL):\n"
            "- You MUST detect the language of the user's query.\n"
            "- If the user writes in Spanish, you MUST reply entirely in natural, fluent Spanish.\n"
            "- If the user writes in English, you MUST reply entirely in natural, fluent English.\n\n"
            "TONE & STYLE:\n"
            "- Do not just copy and paste the raw text literally. Synthesize, restructure, and explain the information clearly like a real customer service representative.\n"
            "- Structure your answers cleanly using clear paragraphs and bullet points where helpful.\n"
            "- Perform mathematical calculations accurately when asked for totals (e.g., multiplying module costs, adding registration fees or books), and explain the breakdown clearly.\n\n"
            "CORE RESTRICTION:\n"
            "Answer the user's question strictly using ONLY the factual context provided below. "
            "Do not assume, extrapolate, or bring in outside knowledge. If the answer cannot be found "
            "within the provided context, you must output exact words in the user's language: "
            "For Spanish: \"No encuentro esta información, escalando a un agente humano.\" "
            "For English: \"I cannot find this information, escalating to a human agent.\"\n"
        )

    def generate_response(self, query, context_chunks):
        formatted_context = "\n\n".join([f"Source ({c['source']}): {c['text']}" for c in context_chunks])
        
        prompt = (
            f"{self.system_prompt}\n\n"
            f"--- CONTEXT START ---\n"
            f"{formatted_context}\n"
            f"--- CONTEXT END ---\n\n"
            f"User Query: {query}\n"
            f"Assistant Response:"
        )

        url = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "options": {
                "temperature": 0.2
            },
            "stream": False
        }

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            raise Exception(f"Failed to generate response from Ollama: {response.text}")