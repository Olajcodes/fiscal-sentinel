'use client';

import React, { useState } from 'react';
import { Send, Brain, AlertTriangle, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import type { Transaction, ChatMessage } from '@/lib/types';

interface AnalysisPanelProps {
  transactions: Transaction[];
}

const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ transactions }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) {
      setError('Please enter a question');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    const optimistic: ChatMessage[] = [
      ...messages,
      { role: 'user', content: trimmed },
    ];
    setMessages(optimistic);

    try {
      const result = await api.analyze({ query: trimmed });
      if (result.history && result.history.length) {
        setMessages(result.history);
      } else {
        setMessages([
          ...optimistic,
          { role: 'assistant', content: result.response },
        ]);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to analyze');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAnalyze = async () => {
    await runAnalysis(query);
  };

  const handleQuickQuestion = async (question: string) => {
    setQuery(question);
    await runAnalysis(question);
  };

  const handleNewChat = () => {
    api.resetConversation();
    setMessages([]);
    setError(null);
  };

  const quickQuestions = [
    "What are my recurring subscriptions?",
    "Show me hidden fees I can dispute",
    "Which subscriptions can I cancel?",
    "Analyze my spending patterns"
  ];

  return (
    <div className="card p-6 bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="flex h-10 w-10 md:h-12 md:w-12 items-center justify-center rounded-xl bg-gradient-to-r from-blue-100 to-purple-100">
            <Brain className="h-5 w-5 md:h-6 md:w-6 text-blue-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-base md:text-lg font-bold text-gray-900">AI Financial Analysis</h3>
            <p className="text-sm text-gray-600 truncate">Ask questions about your transactions</p>
          </div>
          <button
            onClick={handleNewChat}
            className="text-xs md:text-sm text-gray-500 hover:text-gray-700"
          >
            New chat
          </button>
        </div>

      {/* Quick Questions */}
      <div className="mb-6">
        <p className="text-sm font-medium text-gray-700 mb-3">Quick Questions</p>
        <div className="flex flex-wrap gap-2">
          {quickQuestions.map((question, idx) => (
            <button
              key={idx}
              onClick={() => handleQuickQuestion(question)}
              disabled={isAnalyzing}
              className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-xs md:text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors flex-1 sm:flex-none min-w-0"
            >
              <Brain className="h-3 w-3 shrink-0" />
              <span className="truncate text-left">{question}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Query Input */}
      <div className="mb-6">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask me anything about your transactions..."
            className="w-full rounded-lg border border-gray-300 p-3 pr-12 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 resize-none"
            rows={3}
            disabled={isAnalyzing}
          />
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || !query.trim()}
            className="absolute bottom-3 right-3 flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-colors"
          >
            {isAnalyzing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </div>
        {error && (
          <div className="mt-3 flex items-center gap-2 text-xs md:text-sm text-red-600">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Conversation */}
      {messages.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 space-y-3 max-h-72 overflow-y-auto">
          {messages.map((msg, idx) => (
            <div
              key={`${msg.role}-${idx}`}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-xl px-3 py-2 text-sm shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-800 border border-gray-200'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 gap-3">
        <div className="rounded-lg bg-blue-50 p-3 md:p-4">
          <p className="text-xs md:text-sm text-blue-700 mb-1">Transactions</p>
          <p className="text-lg md:text-2xl font-bold text-blue-900">{transactions.length}</p>
        </div>
        <div className="rounded-lg bg-purple-50 p-3 md:p-4">
          <p className="text-xs md:text-sm text-purple-700 mb-1">AI Ready</p>
          <p className="text-lg md:text-2xl font-bold text-purple-900">
            {transactions.length > 0 ? 'Yes' : '0'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPanel;
