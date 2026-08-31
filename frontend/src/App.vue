<script setup lang="ts">
import { reactive } from 'vue';
import ChatInterface from './components/ChatInterface.vue';
import MetricsPanel from './components/MetricsPanel.vue';
import type { Metrics } from './types/chat';

const metrics = reactive<Metrics>({
  queriesProcessed: 0,
  estimatedCost: 0.0,
  escalationRate: 0.0,
  lastResponseCached: false
});

const handleUpdateMetrics = (newMetrics: Metrics) => {
  metrics.queriesProcessed = newMetrics.queriesProcessed;
  metrics.estimatedCost = newMetrics.estimatedCost;
  metrics.escalationRate = newMetrics.escalationRate;
  metrics.lastResponseCached = newMetrics.lastResponseCached;
};
</script>

<template>
  <main class="flex flex-col lg:flex-row h-screen w-screen overflow-hidden bg-slate-950 font-sans antialiased">
    <ChatInterface @update-metrics="handleUpdateMetrics" />
    <MetricsPanel :metrics="metrics" />
  </main>
</template>