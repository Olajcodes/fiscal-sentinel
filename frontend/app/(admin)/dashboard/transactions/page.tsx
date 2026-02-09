// app/dashboard/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Shield, Upload, FileText, AlertTriangle, 
  TrendingUp, CreditCard, Activity, DollarSign,
  Filter, Download, Search, Bell, ChevronRight,
  BarChart3, PieChart, LineChart, Wallet
} from 'lucide-react';
import { api } from '@/lib/api';
import type { Transaction } from '@/lib/types';
import DashboardHeader from '@/components/dashboard/DashboardHeader';
import TransactionTable from '@/components/dashboard/TransactionsTable';
import StatsCards from '@/components/dashboard/StatsCard';
import UploadModal from '@/components/dashboard/UploadModal';
import AnalysisPanel from '@/components/dashboard/AnalysisPanel';
import QuickActions from '@/components/dashboard/QuickActions';

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

  const handleTransactionSelect = (id: string) => {
    setSelectedTransactions(prev => 
      prev.includes(id) 
        ? prev.filter(txId => txId !== id)
        : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedTransactions.length === transactions.length) {
      setSelectedTransactions([]);
    } else {
      setSelectedTransactions(transactions.map(tx => tx.transaction_id));
    }
  };

  const handleUploadSuccess = () => {
    // Refresh transactions
    api.getTransactions().then(setTransactions).catch(console.error);
  };

  const filteredTransactions = transactions.filter(tx => 
    tx.merchant_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tx.category.some(cat => cat.toLowerCase().includes(searchQuery.toLowerCase())) ||
    tx.notes.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Calculate stats
  const totalAmount = transactions.reduce((sum, tx) => sum + tx.amount, 0);
  const subscriptionTransactions = transactions.filter(tx => 
    tx.category.includes('Subscription')
  );
  const feeTransactions = transactions.filter(tx => 
    tx.category.includes('Fees')
  );

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

      <main className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <StatsCards 
          totalAmount={totalAmount}
          subscriptionCount={subscriptionTransactions.length}
          feeCount={feeTransactions.length}
          transactionCount={transactions.length}
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
          {/* Left Column - Transactions */}
          <div className="lg:col-span-2 space-y-8">
            {/* Transaction Table */}
            <div className="card">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Recent Transactions</h2>
                  <p className="text-gray-600">Monitor and manage your financial activity</p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search transactions..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <button
                    onClick={() => setUploadModalOpen(true)}
                    className="btn-primary flex items-center gap-2"
                  >
                    <Upload className="h-4 w-4" />
                    Upload
                  </button>
                </div>
              </div>

              <TransactionTable
                transactions={filteredTransactions}
                selectedTransactions={selectedTransactions}
                onSelectTransaction={handleTransactionSelect}
                onSelectAll={handleSelectAll}
                totalTransactions={filteredTransactions.length}
                currentPage={currentPage}
                itemsPerPage={itemsPerPage}
                onPageChange={setCurrentPage}
                onItemsPerPageChange={setItemsPerPage}
              />
            </div>

            {/* Quick Actions */}
            <QuickActions selectedTransactions={selectedTransactions} />
          </div>

          {/* Right Column - Analysis & Insights */}
          <div className="space-y-8">
            {/* AI Analysis Panel */}
            <AnalysisPanel transactions={transactions} />

            {/* Recent Activity */}
            <div className="card">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-gray-900">Recent Activity</h3>
                <Activity className="h-5 w-5 text-gray-400" />
              </div>
              <div className="space-y-4">
                {[
                  { action: 'Dispute generated', target: 'Netflix fee hike', time: '10 min ago' },
                  { action: 'Subscription flagged', target: 'Adobe Creative Cloud', time: '1 hour ago' },
                  { action: 'Bank fee detected', target: 'Chase maintenance fee', time: '2 hours ago' },
                  { action: 'Analysis completed', target: 'Subscription audit', time: '1 day ago' },
                ].map((activity, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{activity.action}</p>
                      <p className="text-sm text-gray-600">{activity.target}</p>
                    </div>
                    <span className="text-sm text-gray-500">{activity.time}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Category Breakdown */}
            <div className="card">
              <h3 className="text-lg font-bold text-gray-900 mb-6">Spending by Category</h3>
              <div className="space-y-4">
                {['Subscription', 'Fees', 'Fitness', 'Shopping', 'Dining'].map((category) => {
                  const categoryAmount = transactions
                    .filter(tx => tx.category.includes(category))
                    .reduce((sum, tx) => sum + tx.amount, 0);
                  
                  return (
                    <div key={category} className="space-y-2">
                      <div className="flex justify-between">
                        <span className="font-medium text-gray-700">{category}</span>
                        <span className="font-bold">${categoryAmount.toFixed(2)}</span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                          style={{ 
                            width: `${(categoryAmount / totalAmount) * 100}%` 
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
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