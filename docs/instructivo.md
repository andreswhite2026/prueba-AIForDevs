# Instructivo de uso — Instalación, ejecución y uso básico

 Este instructivo explica cómo instalar y ejecutar el proyecto en una máquina local. Incluye pasos para backend, frontend y requisitos externos como Ollama.

Requisitos previos
------------------

- Python 3.10+
- Node.js 18+ y `npm`
- Ollama instalado y accesible desde la terminal (`ollama`)

1) Preparar Ollama

```bash
 # Instalar modelos requeridos y arrancar el servicio
 ollama pull nomic-embed-text
 ollama pull llama3
 ollama serve
```

2) Backend (FastAPI)

```bash
 cd backend
 python -m venv .venv
 source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
 pip install -r requirements.txt
 python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

 Comprobación rápida del backend:

```bash
 curl http://127.0.0.1:8000/health
```

3) Frontend (Vue 3 + Vite)

```bash
 cd frontend
 npm install
 # instalar Tailwind (mínimo requerido)
 npm install tailwindcss @tailwindcss/vite
 npm run dev
```

 Abrir la app en el navegador:

```
 http://127.0.0.1:3000
```

4) Uso básico

- En la interfaz de chat escribe preguntas sobre los programas y servicios; el sistema responderá usando documentos en `backend/analizar/`.
- Para iniciar una inscripción escribe: "Quiero inscribirme; me llamo [nombre], mi correo es [email], quiero [idioma] nivel [nivel]". El backend valida y persiste la inscripción en `backend/student_registrations.json`.

Problemas frecuentes
--------------------

- `ragReady` = false: Ollama no está corriendo o faltan modelos. Ejecuta `ollama serve` y revisa `ollama list`.
- Error de CORS en desarrollo: asegúrate de usar `http://127.0.0.1:3000` y que el backend esté en `127.0.0.1:8000`.
