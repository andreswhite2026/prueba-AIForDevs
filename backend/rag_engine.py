import os
import glob
import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
ANALIZAR_DIR = os.getenv("ANALIZAR_DIR", "analizar")

class RAGEngine:
    def __init__(self, analizar_dir=ANALIZAR_DIR):
        self.analizar_dir = analizar_dir
        self.chunks = []
        self.embeddings = []
        
    def load_documents(self):
        if not os.path.exists(self.analizar_dir):
            os.makedirs(self.analizar_dir, exist_ok=True)
            print(f"Directory '{self.analizar_dir}' created. Please place 3 business documents inside.")
            return
        
        pattern = os.path.join(self.analizar_dir, "*.*")
        files = glob.glob(pattern)
        
        loaded_count = 0
        for file_path in files:
            if file_path.endswith(('.txt', '.md')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._chunk_and_store(content, source=os.path.basename(file_path))
                    loaded_count += 1
                    
        print(f"Successfully indexed documents from {loaded_count} files.")

    def _chunk_and_store(self, text, source, chunk_size=600, overlap=50):
        words = text.split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            if chunk_text.strip():
                embedding = self._get_embedding(chunk_text)
                self.chunks.append({"text": chunk_text, "source": source})
                self.embeddings.append(embedding)

    def _get_embedding(self, text):
        url = f"{OLLAMA_BASE_URL}/api/embeddings"
        payload = {
            "model": EMBEDDING_MODEL,
            "prompt": text
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get("embedding", [])
        else:
            raise Exception(f"Failed to fetch embedding from Ollama: {response.text}")

    def retrieve(self, query, top_k=3):
        if not self.embeddings:
            return []
            
        query_embedding = self._get_embedding(query)
        q_emb = np.array(query_embedding)
        doc_embs = np.array(self.embeddings)
        
        dot_product = np.dot(doc_embs, q_emb)
        norm_a = np.linalg.norm(doc_embs, axis=1)
        norm_b = np.linalg.norm(q_emb)
        
        scores = dot_product / (norm_a * norm_b + 1e-10)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append(self.chunks[idx])
        return results