## Asistente local para la academia — RAG local

Autor: Andres Felipe Blanco Centeno

Identificación (T.I): 1042856488

Descripción
-----------
Este proyecto ofrece un asistente local (RAG) para una academia de idiomas. Combina un frontend en Vue 3, un backend en FastAPI y modelos locales mediante Ollama. El sistema indexa documentos en `backend/analizar/`, genera embeddings con `nomic-embed-text` y produce respuestas con el modelo configurado en `MODEL_NAME`.

Estructura rápida
-----------------
- `backend/` — Servicio FastAPI y código de indexación.
- `frontend/` — Interfaz Vue 3 + Vite + Tailwind CSS.
- `backend/analizar/` — Documentos fuente (`.md` / `.txt`) usados por RAG.

Prerrequisitos
--------------
- Sistema: Linux, macOS o Windows (PowerShell).
- Python 3.10 o superior.
- Node.js 18+ y `npm`.
- Visual Studio Code (opcional, recomendado) — si es la primera vez, instale las extensiones de Python y Vue/TypeScript.
- Ollama: visite https://ollama.com/ y siga las instrucciones de instalación para su sistema. En todos los casos debe poder ejecutar el comando `ollama` desde la terminal.

Modelos Ollama requeridos (ejecutar después de instalar Ollama)
-------------------------------------------------------------
```bash
ollama pull nomic-embed-text
ollama pull llama3
ollama serve
```

Pasos de instalación y ejecución (Linux / macOS)
------------------------------------------------
Siga estos pasos en terminales separados cuando corresponda.

1) Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

2) Frontend (Vue + Vite)

```bash
cd frontend
npm install
# Ejecutar desarrollo
npm run dev
```

Nota sobre Tailwind

Instale Tailwind desde la carpeta `frontend` usando el comando mínimo requerido:

```bash
cd frontend
npm install tailwindcss @tailwindcss/vite
```

Asegúrese de que `src/style.css` contenga las directivas de Tailwind:

```
@import "tailwindcss";
```

El `package.json` ya incluye `@tailwindcss/vite`; con la instalación anterior Tailwind funciona con Vite en desarrollo.

3) Verificar servicios

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:3000/api/health
```

Preparar el proyecto para compartir (ZIP)
---------------------------------------
En caso de querer convertirlo otra vez en ZIP, elimine dependencias instaladas y entornos virtuales locales para reducir tamaño.

Comandos recomendados (Linux/macOS):

```bash
# Desde la raíz del proyecto
rm -rf frontend/node_modules
rm -rf backend/.venv
find . -name "__pycache__" -type d -exec rm -rf {} +
# (opcional) eliminar archivos .pyc
find . -name "*.pyc" -delete

# Crear ZIP sin node_modules y sin entornos locales
zip -r prueba-AI.zip . -x "*/node_modules/*" "*/.venv/*" "*/__pycache__/*" "*.pyc"
```

Si usted utiliza Windows (PowerShell), porfavor elimine `node_modules` y la carpeta virtual `.venv` antes de descomprimir o use las herramientas nativas para crear un ZIP excluyendo carpetas.

Notas sobre `requirements.txt` y `package.json`
---------------------------------------------
- `backend/requirements.txt` ya incluye las dependencias mínimas: `fastapi`, `uvicorn`, `langdetect`, `numpy`, `requests`, `python-dotenv`.
- `frontend/package.json` ya incluye `tailwindcss` y `@tailwindcss/vite`.

Archivos de referencia
---------------------
- Documentación del backend: [backend/backend.md](backend/backend.md#L1)
- Documentación del frontend: [frontend/frontend.md](frontend/frontend.md#L1)

Ver diagramas (drawio) en Visual Studio Code
---------------------------------------------
Si la persona que recibe el proyecto quiere ver o editar los diagramas drawio (`.drawio`) dentro de Visual Studio Code, instale la extensión "Draw.io Integration" desde la vista de Extensiones. Pasos rápidos:

- Abra Visual Studio Code y vaya a la vista de Extensiones (Ctrl+Shift+X). Busque e instale "Draw.io Integration".
- Abra cualquier archivo `.drawio` en Visual Studio Code Y Vera los diagramas echos.