# Frontend — Vue 3

## Propósito

Interfaz de chat construida con Vue 3, TypeScript, Vite y Tailwind CSS. Muestra respuestas del asistente y métricas operativas del backend.

## Ejecución

```bash
cd frontend
npm install
npm run dev
```

Abre `http://127.0.0.1:3000`.

El backend debe estar ejecutándose en `127.0.0.1:8000`.

## Comunicación con la API

El navegador usa la ruta relativa `POST /api/chat`. Vite la redirige al backend mediante el proxy definido en `vite.config.ts`:

```text
127.0.0.1:3000/api/chat → 127.0.0.1:8000/chat
```

Usar una ruta relativa evita problemas de CORS durante el desarrollo. Si hay un error de red, confirma primero:

```bash
curl http://127.0.0.1:3000/api/health
```

## Componentes

| Componente | Función |
| --- | --- |
| `App.vue` | Distribución general de la pantalla. |
| `ChatInterface.vue` | Mensajes, envío, estado de carga, errores y sesión del chat. |
| `MetricsPanel.vue` | Consultas procesadas, costo estimado, escalamiento y estado de caché. |

## Sesión de inscripción

`ChatInterface.vue` genera un UUID y lo conserva en `localStorage`. Lo envía como `session_id` en cada solicitud para que el backend pueda completar una inscripción en varios mensajes sin mezclar datos entre navegadores.

No se almacena el contenido del chat ni información personal en el frontend; el UUID solo identifica el borrador temporal del backend.

## Desarrollo

```bash
npm run build
```

Tailwind CSS
------------
Para instalar Tailwind (instrucción mínima requerida):

```bash
cd frontend
npm install tailwindcss @tailwindcss/vite
```

Asegúrese de que `src/style.css` contenga las directivas:

```
@import "tailwindcss";
```

El comando valida TypeScript y genera la versión de producción en `frontend/dist/`.
