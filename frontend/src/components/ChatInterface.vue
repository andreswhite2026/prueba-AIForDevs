<script setup lang="ts">
import { ref, nextTick } from 'vue';
import type { Message, Metrics } from '../types/chat';

const emit = defineEmits<{
  (e: 'update-metrics', metrics: Metrics): void;
}>();

const messages = ref<Message[]>([
  {
    id: '1',
    sender: 'assistant',
    text: '¡Hola! Soy tu asistente inteligente respaldado por Ollama y RAG. ¿En qué puedo ayudarte hoy?',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    cached: false
  }
]);

const inputMessage = ref('');
const loading = ref(false);
const chatContainer = ref<HTMLElement | null>(null);

const SESSION_STORAGE_KEY = 'academy-rag-chat-session-id';
const getSessionId = () => {
  const existingSessionId = localStorage.getItem(SESSION_STORAGE_KEY);
  if (existingSessionId) return existingSessionId;

  const sessionId = crypto.randomUUID();
  localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  return sessionId;
};
const sessionId = getSessionId();

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return;

  const userText = inputMessage.value;
  inputMessage.value = '';

  messages.value.push({
    id: Date.now().toString(),
    sender: 'user',
    text: userText,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  });

  await scrollToBottom();
  loading.value = true;

  try {
    // Vite sends this same-origin route to 127.0.0.1:8000 (see vite.config.ts).
    // The browser therefore does not perform a CORS request in development.
    const response = await fetch('/api/chat', {
      method: 'POST',
      // /api is served by the same Vite origin and proxied server-side.
      // Explicitly avoid Firefox treating this development request as CORS.
      mode: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: userText, session_id: sessionId })
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => null);
      throw new Error(errorBody?.detail || `Error HTTP ${response.status}`);
    }

    const data = await response.json();

    messages.value.push({
      id: (Date.now() + 1).toString(),
      sender: 'assistant',
      text: data.response || 'Respuesta generada correctamente por el backend.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      cached: data.cached ?? false
    });

    if (data.metrics) {
      emit('update-metrics', {
        queriesProcessed: data.metrics.queriesProcessed,
        estimatedCost: data.metrics.estimatedCost,
        escalationRate: data.metrics.escalationRate,
        lastResponseCached: data.cached ?? false
      });
    }

  } catch (error) {
    const detail = error instanceof Error ? error.message : 'Error desconocido';
    messages.value.push({
      id: (Date.now() + 1).toString(),
      sender: 'assistant',
      text: `No pude procesar la consulta. ${detail}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      cached: false
    });
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
};
</script>

<template>
  <div class="flex-1 flex flex-col h-full bg-slate-950">
    <header class="h-16 border-b border-slate-800 flex items-center px-6 bg-slate-900/50 backdrop-blur">
      <div class="flex items-center gap-3">
        <div class="w-3 h-3 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/50" />
        <h1 class="font-semibold text-white tracking-wide">Asistente de Atención al Cliente (Ollama / Llama 3)</h1>
      </div>
    </header>

    <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-6">
      <div 
        v-for="msg in messages" 
        :key="msg.id"
        class="flex flex-col"
        :class="msg.sender === 'user' ? 'items-end' : 'items-start'"
      >
        <div 
          class="max-w-xl rounded-2xl px-5 py-3.5 text-sm leading-relaxed shadow-sm"
          :class="msg.sender === 'user' 
            ? 'bg-blue-600 text-white rounded-br-xs' 
            : 'bg-slate-900 text-slate-200 border border-slate-800 rounded-bl-xs'"
        >
          {{ msg.text }}
        </div>
        <div class="flex items-center gap-2 mt-1.5 px-1">
          <span class="text-[10px] text-slate-500">{{ msg.timestamp }}</span>
          <span v-if="msg.sender === 'assistant' && msg.cached !== undefined" 
                class="text-[10px] px-1.5 py-0.5 rounded font-medium"
                :class="msg.cached ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/50' : 'bg-slate-900 text-slate-400 border border-slate-800'">
            {{ msg.cached ? 'Caché' : 'LLM' }}
          </span>
        </div>
      </div>

      <div v-if="loading" class="flex items-start">
        <div class="bg-slate-900 text-slate-400 border border-slate-800 rounded-2xl rounded-bl-xs px-5 py-3.5 text-sm flex items-center gap-2 animate-pulse">
          <div class="w-2 h-2 rounded-full bg-blue-500 animate-bounce" />
          <div class="w-2 h-2 rounded-full bg-blue-500 animate-bounce [animation-delay:0.2s]" />
          <div class="w-2 h-2 rounded-full bg-blue-500 animate-bounce [animation-delay:0.4s]" />
        </div>
      </div>
    </div>

    <div class="p-4 border-t border-slate-800 bg-slate-900/50 backdrop-blur">
      <form @submit.prevent="sendMessage" class="flex gap-3 max-w-4xl mx-auto">
        <input 
          v-model="inputMessage"
          type="text"
          placeholder="Escribe tu consulta sobre la documentación..."
          class="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
          :disabled="loading"
        />
        <button 
          type="submit"
          class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl text-sm font-medium transition shadow-lg shadow-blue-600/25 disabled:opacity-50 cursor-pointer"
          :disabled="loading || !inputMessage.trim()"
        >
          Enviar
        </button>
      </form>
    </div>
  </div>
</template>
