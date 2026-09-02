# Backend — FastAPI y RAG local

## Responsabilidades

El backend recibe consultas, ejecuta skills deterministas cuando aplica y, para el resto, recupera contexto desde `analizar/` antes de consultar el modelo local de Ollama.

## Componentes

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | API, CORS, estado de salud, caché, idioma y flujo de inscripción. |
| `rag_engine.py` | Carga Markdown/TXT, fragmenta texto, genera embeddings y recupera contexto. |
| `ollama_client.py` | Construye el prompt fundamentado y llama a `llama3`. |
| `skills.py` | Inscripción validada y conversión determinista COP/USD. |
| `analizar/` | Fuente de conocimiento institucional. |

## Configuración

`backend/.env` es opcional y no se versiona. Valores disponibles:

```dotenv
OLLAMA_BASE_URL=http://127.0.0.1:11434
MODEL_NAME=llama3
EMBEDDING_MODEL=nomic-embed-text
ANALIZAR_DIR=analizar
CORS_ORIGINS=http://127.0.0.1:3000,http://localhost:3000
```

Las rutas relativas se resuelven desde la carpeta `backend`, no desde la terminal que inicie Uvicorn.

## Arranque

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Ollama debe estar disponible y tener los modelos necesarios:

```bash
ollama pull nomic-embed-text
ollama pull llama3
ollama serve
```

La API inicia aunque Ollama no esté disponible. La indexación ocurre en segundo plano y se reintenta cada cinco segundos.

## Endpoints

### `GET /health`

```json
{
  "api": "ok",
  "ragReady": true,
  "ragError": null
}
```

`ragReady: false` significa que FastAPI está activo, pero el índice RAG aún no se pudo preparar.

### `POST /chat`

```json
{
  "prompt": "What schedules are available?",
  "session_id": "opcional-para-borradores-de-inscripcion"
}
```

```json
{
  "response": "...",
  "cached": false,
  "metrics": {
    "queriesProcessed": 1,
    "estimatedCost": 0.0002,
    "escalationRate": 0.0
  }
}
```

## Idioma y fundamentación

`langdetect` detecta el idioma de entrada. El idioma detectado se envía explícitamente a Ollama y también forma parte de la clave lógica de la caché, por lo que una respuesta en español no se reutiliza para una pregunta en inglés.

El prompt exige que toda afirmación exista de forma explícita en el contexto recuperado. Si falta información esencial, el asistente escala la solicitud en el idioma correspondiente.

## Inscripciones

Las solicitudes de inscripción no se envían al LLM. Se validan de forma determinista:

- Nombre completo.
- Correo electrónico.
- Idioma: Inglés, Francés o Alemán.
- Nivel: A1, A2, B1, B2 o C1.

Los borradores viven en memoria durante 30 minutos por `session_id`. Solo se escribe `student_registrations.json` cuando todos los campos son válidos. Los registros incluyen ID UUID, fecha UTC, estado `pending_confirmation` y protección contra duplicados de correo + idioma + nivel.
