// src/types/chat.ts
export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  cached?: boolean;
}

export interface Metrics {
  queriesProcessed: number;
  estimatedCost: number;
  escalationRate: number;
  lastResponseCached: boolean;
}