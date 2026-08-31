# Asistente de Atención al Cliente Inteligente (RAG + Skills con Ollama, FastAPI y Vue.js)

Repositorio de la aplicación de Inteligencia Artificial basada en RAG (Retrieval-Augmented Generation) y Habilidades Personalizadas (Local MCP) desarrollada para una academia de idiomas. Combina un motor de búsqueda vectorial local con Llama 3, un backend robusto en FastAPI con caché semántica y skills transaccionales, y un panel de métricas en tiempo real con Vue.js y Tailwind CSS.

---

## 🏗️ Arquitectura del Sistema

El proyecto está estructurado en dos componentes principales: el **Backend** (Python / FastAPI) que gestiona la lógica de recuperación de documentos, inferencia local, caché, métricas y ejecución de skills, y el **Frontend** (Vue.js / TypeScript) que ofrece la interfaz visual de chat y monitoreo.

```text
├── backend/
│   ├── main.py            # Servidor FastAPI, endpoints, caché semántica, métricas y enrutamiento de skills
│   ├── rag_engine.py      # Motor de indexación, chunking y búsqueda por similitud coseno
│   ├── ollama_client.py   # Cliente para la API de Ollama (Llama 3 y prompts bilingües)
│   ├── skills.py          # Habilidades personalizadas (registro de estudiantes en JSON y conversión de divisa)
│   └── analizar/          # Directorio con documentos de negocio en formato Markdown/TXT
└── frontend/
    ├── src/
    │   ├── components/    # Componentes de Chat y Panel de Métricas
    │   └── types/         # Definiciones de tipos e interfaces en TypeScript
    └── package.json       # Dependencias y scripts de Vue.js
```

## 🚀 Características Principales

*   **Motor RAG Local y Seguro:** Indexación de documentos internos de la academia mediante fragmentación optimizada (`chunk_size`) y embeddings vectoriales (`nomic-embed-text`) ejecutados localmente con Ollama.
*   **Caché Semántica Vectorial Avanzada:** Sistema de optimización en memoria que calcula la similitud por coseno entre las consultas nuevas y las almacenadas (umbral $\ge 0.85$). Las preguntas con intenciones similares se responden de forma instantánea sin gastar recursos del LLM.
*   **Skills Personalizados (Acciones Locales / MCP):** Funciones ejecutables integradas en el backend que permiten procesar acciones transaccionales directas (como registrar un estudiante guardando los datos en un archivo JSON local o calcular conversiones a dólares) sin requerir servicios externos.
*   **Detección Automática de Idioma:** Soporte bilingüe fluido (Español e Inglés) adaptándose de manera automática al idioma de entrada del usuario.
*   **Protección contra Alucinaciones y Escalamiento Automático:** Restricciones estrictas en el prompt del sistema para evitar inventar información, disparando un protocolo de derivación a agentes humanos cuando un tema no se encuentra en la base de conocimiento.
*   **Panel de Métricas en Tiempo Real:** Monitoreo reactivo de consultas procesadas, costo estimado acumulado, tasa de escalamiento a humanos y estado de caché (LLM vs Caché).

## 🛠️ Requisitos del Sistema y Tecnologías

*   Python 3.10+ (FastAPI, Uvicorn, NumPy, Requests, Python-Dotenv)
*   Node.js 18+ (Vue 3, TypeScript, Vite, Tailwind CSS)
*   Ollama ejecutándose localmente (`http://localhost:11434`) con los modelos:
    *   `nomic-embed-text` (para embeddings)
    *   `llama3` (para generación de lenguaje)

## ⚙️ Guía de Instalación y Ejecución

### 1. Configuración del Backend

```bash
# Entrar al directorio del backend e instalar dependencias
cd backend
pip install fastapi uvicorn numpy requests python-dotenv

# Asegurar que Ollama esté activo y ejecutar el servidor FastAPI
uvicorn main:app --reload --port 8000
```

### 2. Configuración del Frontend

```bash
# Entrar al directorio del frontend
cd frontend

# Instalar dependencias
npm install

# Iniciar el entorno de desarrollo
npm run dev
```

## 📊 Panel de Control y Métricas

La interfaz de usuario incluye un panel lateral que recopila los siguientes indicadores en tiempo real:

*   **Consultas Procesadas:** Conteo total de interacciones enviadas al servidor.
*   **Costo Estimado:** Acumulado financiero calculado por uso de inferencia del LLM (las consultas resueltas por caché semántica y skills optimizan este valor).
*   **Escalamiento a Humanos (%):** Porcentaje de consultas derivadas debido a restricciones de información no encontrada en los documentos base.
*   **Estado de Caché:** Indicador visual dinámico que diferencia si la respuesta provino directamente del modelo de lenguaje (LLM), de la memoria semántica (Caché) o de una ejecución directa de habilidades.

---

### Preguntas clave para verificar todo el sistema

1. **Para probar el Skill de Inscripción:**
   * *Pregunta:* `"Quiero inscribirme a un curso"`
   * *Qué verificar:* El backend interceptará la intención, ejecutará la función localmente, creará o actualizará el archivo `student_registrations.json` en la carpeta de tu backend y devolverá el mensaje de éxito de inmediato.

2. **Para probar el Skill de Conversión de Divisas:**
   * *Pregunta:* `"¿Cuánto cuesta un módulo en dólares USD?"`
   * *Qué verificar:* El sistema calculará la tasa de cambio estimada basada en pesos colombianos y devolverá el valor convertido.

3. **Para probar la Caché Semántica:**
   * *Pregunta previa:* `"¿Cuánto dura el nivel básico de francés y qué incluye?"`
   * *Pregunta nueva (variante parecida):* `"¿Qué contiene el nivel básico de francés y cuál es su duración?"`
   * *Qué verificar:* El sistema calculará la similitud de los embeddings (mayor al 85%) y cambiará el estado de la interfaz a verde indicando **Caché**.

4. **Para probar el Escalamiento a Humanos:**
   * *Pregunta:* `"¿Tienen clases presenciales de natación o deportes en la sede?"`
   * *Qué verificar:* Al no estar en los documentos, se negará a inventar y la tasa de escalamiento en el panel lateral subirá de porcentaje.

---