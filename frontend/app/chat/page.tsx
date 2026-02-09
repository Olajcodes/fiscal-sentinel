'use client';

import { useMemo, useState } from 'react';
import { api } from '@/lib/api';
import type { ChatMessage } from '@/lib/types';

const ChatPage = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = useMemo(
    () => (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/^https?:\/\//, ''),
    [],
  );

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput('');
    setError(null);
    setLoading(true);

    const optimistic = [...messages, { role: 'user', content: text }];
    setMessages(optimistic);

    try {
      const result = await api.analyze({ query: text });
      if (result.history && result.history.length) {
        setMessages(result.history);
      } else {
        setMessages([...optimistic, { role: 'assistant', content: result.response }]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      setMessages(optimistic);
    } finally {
      setLoading(false);
    }
  };

  const startNewChat = () => {
    api.resetConversation();
    setMessages([]);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto flex w-full max-w-4xl flex-col px-6 py-10">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Fiscal Sentinel Chat</h1>
            <p className="text-sm text-muted-foreground">
              Connected API: {apiUrl}
            </p>
          </div>
          <button
            className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted"
            onClick={startNewChat}
          >
            New Chat
          </button>
        </div>

        <div className="flex-1 space-y-4 rounded-2xl border border-border bg-card p-6 shadow-sm">
          {messages.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border bg-muted/40 p-6 text-sm text-muted-foreground">
              Ask a transaction question, for example: "What is the highest charge this month?"
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={`${msg.role}-${idx}`}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-foreground'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))
          )}
        </div>

        {error && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="mt-6 flex gap-3">
          <input
            className="flex-1 rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Ask about your transactions..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                event.preventDefault();
                sendMessage();
              }
            }}
          />
          <button
            className="rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-sm transition hover:opacity-90"
            onClick={sendMessage}
            disabled={loading}
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
