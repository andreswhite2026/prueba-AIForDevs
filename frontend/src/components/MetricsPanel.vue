<script setup lang="ts">
defineProps<{
  metrics: {
    queriesProcessed: number;
    estimatedCost: number;
    escalationRate: number;
    lastResponseCached: boolean;
  }
}>();
</script>

<template>
  <aside class="w-full lg:w-80 bg-slate-900 text-slate-100 p-6 flex flex-col gap-6 border-l border-slate-800">
    <div>
      <h2 class="text-xl font-bold tracking-tight text-white mb-1">Panel de Métricas</h2>
      <p class="text-xs text-slate-400">Monitoreo en tiempo real del asistente RAG</p>
    </div>

    <div class="grid grid-cols-1 gap-4">
      <div class="bg-slate-800/60 p-4 rounded-xl border border-slate-700/50">
        <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Consultas Procesadas</span>
        <div class="text-2xl font-semibold text-white mt-1">{{ metrics.queriesProcessed }}</div>
      </div>

      <div class="bg-slate-800/60 p-4 rounded-xl border border-slate-700/50">
        <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Costo Estimado</span>
        <div class="text-2xl font-semibold text-emerald-400 mt-1">${{ metrics.estimatedCost.toFixed(4) }}</div>
      </div>

      <div class="bg-slate-800/60 p-4 rounded-xl border border-slate-700/50">
        <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Escalamiento a Humanos</span>
        <div class="text-2xl font-semibold text-amber-400 mt-1">{{ metrics.escalationRate.toFixed(1) }}%</div>
      </div>

      <div class="bg-slate-800/60 p-4 rounded-xl border border-slate-700/50 flex items-center justify-between">
        <div>
          <span class="text-xs font-medium text-slate-400 uppercase tracking-wider block">Estado de Caché</span>
          <span class="text-sm font-medium text-white mt-1">
            {{ metrics.lastResponseCached ? 'Recuperado de Caché' : 'Generado por LLM' }}
          </span>
        </div>
        <div 
          class="w-3 h-3 rounded-full animate-pulse"
          :class="metrics.lastResponseCached ? 'bg-emerald-500 shadow-lg shadow-emerald-500/50' : 'bg-blue-500 shadow-lg shadow-blue-500/50'"
        />
      </div>
    </div>
  </aside>
</template>