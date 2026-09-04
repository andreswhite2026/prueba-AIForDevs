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

## Asistente local para la academia — RAG local

Autor: Andres Felipe Blanco Centeno

Identificación (T.I): 1042856488

Resumen
-------
Proyecto que implementa un asistente local (RAG) para una academia de idiomas. Integra:

- `backend/`: API en FastAPI, motor RAG y habilidades locales (skills).
- `frontend/`: SPA en Vue 3 + Vite + Tailwind (código fuente en `src/`, salida en `dist/` si se construye).

Este README ahora incluye: visión general, estructura del proyecto, pasos de instalación y ejecución, y referencias a los documentos de diseño y técnicos.

Estructura del proyecto
-----------------------

- `backend/` — Servicio FastAPI, lógica RAG y skills.
- `backend/analizar/` — Documentos fuente indexados por el RAG (*.md, *.txt).
- `frontend/` — Código fuente del frontend (Vue 3 + Vite). `frontend/dist/` es la salida de `npm run build`.
- `docs/` — Documentos de diseño, diagramas (Mermaid/.mmd, draw.io) y mockups.
- `db/` — Scripts y esquema SQL (informativo).
- `README.md` — Este archivo.

Entregables incluidos
---------------------

- Documentos de diseño y técnicos (`docs/*.md`, `docs/*.pdf`).
- Diagramas UML en Mermaid y Draw.io (`docs/diagrams/`).
- Mockups SVG en `docs/mockups/`.

Guía rápida
----------

1. Instale prerrequisitos: Python 3.10+, Node.js 18+, Ollama.
2. Levante backend y frontend por separado (ver la sección "Pasos de instalación y ejecución" más abajo).
3. Para ver y editar diagramas Mermaid use Visual Studio Code con la extensión "Mermaid MMD Tools" (instrucciones más abajo).


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
Antes de crear el ZIP, elimine dependencias instaladas y entornos virtuales locales para reducir tamaño.

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

Si la otra persona usa Windows (PowerShell), pídale que elimine `node_modules` y la carpeta virtual `.venv` antes de descomprimir o que use las herramientas nativas para crear un ZIP excluyendo carpetas.

Notas sobre `requirements.txt` y `package.json`
---------------------------------------------
- `backend/requirements.txt` ya incluye las dependencias mínimas: `fastapi`, `uvicorn`, `langdetect`, `numpy`, `requests`, `python-dotenv`.
- `frontend/package.json` ya incluye `tailwindcss` y `@tailwindcss/vite`.

Archivos de referencia
---------------------
- Documentación del backend: [backend/backend.md](backend/backend.md#L1)
- Documentación del frontend: [frontend/frontend.md](frontend/frontend.md#L1)

Ver diagramas (Mermaid) en Visual Studio Code
---------------------------------------------
Si la persona que recibe el proyecto quiere ver o editar los diagramas Mermaid (`.mmd` / `.mermaid`) dentro de Visual Studio Code, instale la extensión "Mermaid MMD Tools" desde la vista de Extensiones. Pasos rápidos:

- Abra Visual Studio Code y vaya a la vista de Extensiones (Ctrl+Shift+X). Busque e instale "Mermaid MMD Tools".
- Abra cualquier archivo `.mmd` o `.mermaid` en Visual Studio Code.
- Haga clic en el ícono del diagrama en la barra de título del editor para abrir la vista previa.
- El diagrama se mostrará en un panel de vista previa con funciones para desplazarse y hacer zoom.

Si quieres, puedes añadir una captura (foto) indicando exactamente dónde está el ícono; colócala en `docs/images/` y la referencia aquí para que quien abra el repositorio la vea.

---
Último cambio: README principal traducido y pasos de empaquetado añadidos.