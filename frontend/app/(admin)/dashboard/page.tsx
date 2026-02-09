'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Activity,
  AlertTriangle,
  Brain,
  Loader2,
  Search,
  Send,
  Upload,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { api } from '@/lib/api';
import type { ChatMessage, Transaction } from '@/lib/types';
import DashboardHeader from '@/components/dashboard/DashboardHeader';
import TransactionTable from '@/components/dashboard/TransactionsTable';
import StatsCards from '@/components/dashboard/StatsCard';
import UploadModal from '@/components/dashboard/UploadModal';
import QuickActions from '@/components/dashboard/QuickActions';

const DEFAULT_QUICK_QUESTIONS = [
  'What are my recurring subscriptions?',
  'Show me suspicious charges I can dispute',
  'Which subscriptions can I cancel?',
  'Summarize my spending this month',
];

const buildCurrencyFormatter = (currency?: string) => {
  // Fallback to NGN so amounts render predictably even if data is missing.
  const normalized = currency && currency.trim() ? currency.trim() : 'NGN';
  const locale = normalized === 'NGN' ? 'en-NG' : 'en-US';
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: normalized,
      currencyDisplay: 'symbol',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  } catch {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      currencyDisplay: 'symbol',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }
};

const formatCurrencyInText = (text: string, formatter: Intl.NumberFormat) => {
  // Only normalize likely currency mentions to avoid corrupting dates or IDs.
  const withSymbols = text.replace(
    /(?:₦|NGN|USD|EUR|GBP|\$|€|£)\s*-?\d{1,3}(?:,\d{3})*(?:\.\d+)?/g,
    (match) => {
      const numeric = match.replace(/[^\d.-]/g, '');
      if (!numeric) return match;
      const value = Number(numeric.replace(/,/g, ''));
      return Number.isFinite(value) ? formatter.format(value) : match;
    }
  );

  return withSymbols.replace(
    /\b(?:amount|amounting|total|totaling|fee|fees|charge|charged|payment|paid|spent|balance|deposit|withdrawal|transfer|refund|credit|debit)\s+(?:of\s+)?(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)/gi,
    (match, number) => {
      const value = Number(String(number).replace(/,/g, ''));
      if (!Number.isFinite(value)) return match;
      return match.replace(number, formatter.format(value));
    }
  );
};

const unwrapMarkdownFence = (text: string) => {
  const trimmed = text.trim();
  const match = trimmed.match(/^```[a-zA-Z0-9_-]*\n([\s\S]*?)\n```$/);
  if (match && match[1]) {
    return match[1].trim();
  }
  return text;
};

const DashboardPage = () => {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedTransactions, setSelectedTransactions] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      const currentUser = await api.getCurrentUser();
      if (!currentUser) {
        router.push('/signin');
        return;
      }
      setUser(currentUser);

      try {
        const txData = await api.getTransactions();
        setTransactions(txData);
      } catch (error) {
        console.error('Failed to load transactions:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const currencyFormatter = useMemo(() => {
    const inferredCurrency = transactions.find((tx) => tx.currency)?.currency;
    return buildCurrencyFormatter(inferredCurrency);
  }, [transactions]);

  const formatCurrency = (value: number) => currencyFormatter.format(value);

  const filteredTransactions = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return transactions;
    return transactions.filter((tx) => {
      const merchant = tx.merchant_name?.toLowerCase() || '';
      const categories = Array.isArray(tx.category)
        ? tx.category.join(' ').toLowerCase()
        : '';
      const notes = tx.notes?.toLowerCase() || '';
      return merchant.includes(query) || categories.includes(query) || notes.includes(query);
    });
  }, [transactions, searchQuery]);

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentTransactions = filteredTransactions.slice(indexOfFirstItem, indexOfLastItem);

  const totalAmount = useMemo(
    () => transactions.reduce((sum, tx) => sum + tx.amount, 0),
    [transactions]
  );

  const subscriptionTransactions = useMemo(
    () => transactions.filter((tx) => tx.category.includes('Subscription')),
    [transactions]
  );
  const feeTransactions = useMemo(
    () => transactions.filter((tx) => tx.category.includes('Fees')),
    [transactions]
  );

  const handleTransactionSelect = (id: string) => {
    setSelectedTransactions((prev) =>
      prev.includes(id) ? prev.filter((txId) => txId !== id) : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedTransactions.length === currentTransactions.length) {
      setSelectedTransactions([]);
    } else {
      setSelectedTransactions(currentTransactions.map((tx) => tx.transaction_id));
    }
  };

  const handleUploadSuccess = () => {
    api.getTransactions().then(setTransactions).catch(console.error);
    setCurrentPage(1);
  };

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
  };

  const handleItemsPerPageChange = (value: number) => {
    setItemsPerPage(value);
    setCurrentPage(1);
  };

  const handleSend = async (override?: string) => {
    const text = (override ?? chatInput).trim();
    if (!text || isSending) {
      if (!text) setChatError('Please enter a question to continue.');
      return;
    }

    setChatError(null);
    setChatInput('');
    // Optimistic UI keeps the conversation flowing while we wait on the API.
    const optimistic: ChatMessage[] = [...messages, { role: 'user', content: text }];
    setMessages(optimistic);
    setIsSending(true);

    try {
      const result = await api.analyze({ query: text });
      if (result.history?.length) {
        setMessages(result.history);
      } else {
        setMessages([...optimistic, { role: 'assistant', content: result.response }]);
      }
    } catch (err: unknown) {
      setChatError(err instanceof Error ? err.message : 'Failed to send message.');
      setMessages(optimistic);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleNewChat = () => {
    api.resetConversation();
    setMessages([]);
    setChatError(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your financial dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader
        user={user}
        onUploadClick={() => setUploadModalOpen(true)}
      />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
        <StatsCards
          totalAmount={totalAmount}
          subscriptionCount={subscriptionTransactions.length}
          feeCount={feeTransactions.length}
          transactionCount={transactions.length}
        />

        <section className="mt-6 md:mt-8 space-y-6">
          <div className="card bg-white rounded-2xl border border-gray-200 shadow-sm p-6 flex flex-col min-h-[65vh] lg:min-h-[72vh] xl:min-h-[calc(100vh-260px)]">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-100 to-purple-100">
                  <Brain className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-lg md:text-xl font-bold text-gray-900">AI Transaction Assistant</h2>
                  <p className="text-sm text-gray-600">Ask questions and draft dispute letters with evidence.</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs font-medium text-gray-500">Conversation saved</span>
                <button
                  onClick={handleNewChat}
                  className="text-xs md:text-sm font-medium text-gray-600 hover:text-gray-900"
                >
                  New chat
                </button>
              </div>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {DEFAULT_QUICK_QUESTIONS.map((question) => (
                <button
                  key={question}
                  onClick={() => handleSend(question)}
                  disabled={isSending}
                  className="inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-4 py-2 text-xs md:text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  <Brain className="h-3.5 w-3.5 shrink-0" />
                  <span className="truncate max-w-[180px] sm:max-w-none">{question}</span>
                </button>
              ))}
            </div>

            <div className="mt-6 flex-1 overflow-y-auto rounded-2xl border border-gray-200 bg-gray-50/70 p-4 md:p-6">
              {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center text-gray-500 px-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-sm">
                    <Brain className="h-5 w-5 text-blue-600" />
                  </div>
                  <p className="mt-3 font-medium text-gray-700">Start with a question about your transactions</p>
                  <p className="text-sm">We will answer instantly and only pull legal evidence when needed.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message, index) => {
                    const isUser = message.role === 'user';
                    const formattedContent = formatCurrencyInText(message.content, currencyFormatter);
                    const normalizedContent = unwrapMarkdownFence(formattedContent);
                    return (
                      <div
                        key={`${message.role}-${index}`}
                        className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm md:text-base shadow-sm border ${
                            isUser
                              ? 'bg-blue-600 text-white border-blue-600'
                              : 'bg-white text-gray-800 border-gray-200'
                          } break-words whitespace-pre-wrap`}
                        >
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              p: ({ children }) => (
                                <p className="leading-relaxed whitespace-pre-wrap break-words">{children}</p>
                              ),
                              ul: ({ children }) => <ul className="list-disc pl-5 space-y-1">{children}</ul>,
                              ol: ({ children }) => <ol className="list-decimal pl-5 space-y-1">{children}</ol>,
                              li: ({ children }) => (
                                <li className="leading-relaxed whitespace-pre-wrap break-words">{children}</li>
                              ),
                              a: ({ children, href }) => (
                                <a
                                  href={href}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="underline underline-offset-2"
                                >
                                  {children}
                                </a>
                              ),
                              code: ({ inline, children }) =>
                                inline ? (
                                  <code className="rounded bg-gray-100 px-1 py-0.5 text-xs md:text-sm">
                                    {children}
                                  </code>
                                ) : (
                                  <pre className="whitespace-pre-wrap break-words rounded-lg bg-gray-100 p-3 text-xs md:text-sm">
                                    <code>{children}</code>
                                  </pre>
                                ),
                            }}
                          >
                            {normalizedContent}
                          </ReactMarkdown>
                        </div>
                      </div>
                    );
                  })}

                  {isSending && (
                    <div className="flex justify-start">
                      <div className="max-w-[80%] rounded-2xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-600 shadow-sm flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Thinking through your request...</span>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {chatError && (
              <div className="mt-4 flex items-center gap-2 rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-sm text-red-700">
                <AlertTriangle className="h-4 w-4" />
                <span>{chatError}</span>
              </div>
            )}

            <div className="sticky bottom-0 mt-4 -mx-6 border-t border-gray-200 bg-white/90 px-6 py-4 backdrop-blur">
              {/* Sticky input keeps the composer visible while the message list scrolls. */}
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  handleSend();
                }}
                className="flex flex-col gap-3"
              >
                <textarea
                  value={chatInput}
                  onChange={(event) => setChatInput(event.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about a charge, totals, cancellations, or draft a dispute letter..."
                  rows={2}
                  disabled={isSending}
                  className="w-full resize-none rounded-xl border border-gray-300 bg-white p-3 text-sm md:text-base shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs text-gray-500">
                    Press Enter to send, Shift + Enter for a new line.
                  </p>
                  <button
                    type="submit"
                    disabled={isSending || !chatInput.trim()}
                    className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:from-blue-700 hover:to-purple-700 disabled:opacity-50"
                  >
                    {isSending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                    Send
                  </button>
                </div>
              </form>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <div className="card bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                  <div>
                    <h2 className="text-lg sm:text-xl font-bold text-gray-900">Recent Transactions</h2>
                    <p className="text-sm text-gray-600">Monitor and manage your financial activity</p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="relative flex-1 sm:flex-none">
                      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search transactions..."
                        value={searchQuery}
                        onChange={(e) => {
                          setSearchQuery(e.target.value);
                          setCurrentPage(1);
                        }}
                        className="w-full sm:w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <button
                      onClick={() => setUploadModalOpen(true)}
                      className="btn-primary flex items-center gap-2 whitespace-nowrap bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-sm hover:shadow disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Upload className="h-4 w-4" />
                      <span className="hidden sm:inline">Upload</span>
                    </button>
                  </div>
                </div>

                <TransactionTable
                  transactions={currentTransactions}
                  selectedTransactions={selectedTransactions}
                  onSelectTransaction={handleTransactionSelect}
                  onSelectAll={handleSelectAll}
                  totalTransactions={filteredTransactions.length}
                  currentPage={currentPage}
                  itemsPerPage={itemsPerPage}
                  onPageChange={handlePageChange}
                  onItemsPerPageChange={handleItemsPerPageChange}
                />
              </div>

              <QuickActions selectedTransactions={selectedTransactions} />
            </div>

            <div className="space-y-6">
              <div className="card bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-base sm:text-lg font-bold text-gray-900">Recent Activity</h3>
                  <Activity className="h-5 w-5 text-gray-400" />
                </div>
                <div className="space-y-4">
                  {[
                    { action: 'Dispute generated', target: 'Netflix fee hike', time: '10 min ago' },
                    { action: 'Subscription flagged', target: 'Adobe Creative Cloud', time: '1 hour ago' },
                    { action: 'Bank fee detected', target: 'Chase maintenance fee', time: '2 hours ago' },
                    { action: 'Analysis completed', target: 'Subscription audit', time: '1 day ago' },
                  ].map((activity, idx) => (
                    <div key={idx} className="flex items-start justify-between p-3 hover:bg-gray-50 rounded-lg">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">{activity.action}</p>
                        <p className="text-sm text-gray-600 truncate">{activity.target}</p>
                      </div>
                      <span className="text-sm text-gray-500 whitespace-nowrap ml-2">{activity.time}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-6">Spending by Category</h3>
                <div className="space-y-4">
                  {['Subscription', 'Fees', 'Fitness', 'Shopping', 'Dining'].map((category) => {
                    const categoryAmount = transactions
                      .filter((tx) => tx.category.includes(category))
                      .reduce((sum, tx) => sum + tx.amount, 0);

                    const percentage = totalAmount > 0 ? (categoryAmount / totalAmount) * 100 : 0;

                    return (
                      <div key={category} className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="font-medium text-gray-700 text-sm">{category}</span>
                          <span className="font-bold text-gray-900">{formatCurrency(categoryAmount)}</span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {uploadModalOpen && (
        <UploadModal
          isOpen={uploadModalOpen}
          onClose={() => setUploadModalOpen(false)}
          onSuccess={handleUploadSuccess}
        />
      )}
    </div>
  );
};

export default DashboardPage;
