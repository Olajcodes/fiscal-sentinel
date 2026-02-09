'use client';

import React, { useState, useEffect } from 'react';
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
    if (selectedTransactions.length === currentTransactions.length) {
      setSelectedTransactions([]);
    } else {
      setSelectedTransactions(currentTransactions.map(tx => tx.transaction_id));
    }
  };

  const handleUploadSuccess = () => {
    // Refresh transactions
    api.getTransactions().then(setTransactions).catch(console.error);
    setCurrentPage(1); // Reset to first page after upload
  };

  const filteredTransactions = transactions.filter(tx => 
    tx.merchant_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tx.category.some(cat => cat.toLowerCase().includes(searchQuery.toLowerCase())) ||
    tx.notes.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Calculate pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentTransactions = filteredTransactions.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage);

  // Calculate stats
  const totalAmount = transactions.reduce((sum, tx) => sum + tx.amount, 0);
  const subscriptionTransactions = transactions.filter(tx => 
    tx.category.includes('Subscription')
  );
  const feeTransactions = transactions.filter(tx => 
    tx.category.includes('Fees')
  );

  // Handle page change
  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
  };

  // Handle items per page change
  const handleItemsPerPageChange = (value: number) => {
    setItemsPerPage(value);
    setCurrentPage(1); // Reset to first page when changing items per page
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
        {/* Stats Overview */}
        <StatsCards 
          totalAmount={totalAmount}
          subscriptionCount={subscriptionTransactions.length}
          feeCount={feeTransactions.length}
          transactionCount={transactions.length}
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6 md:mt-8">
          {/* Left Column - Transactions */}
          <div className="lg:col-span-2 space-y-6">
            {/* Transaction Table */}
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
                        setCurrentPage(1); // Reset to first page when searching
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

            {/* Quick Actions */}
            <QuickActions selectedTransactions={selectedTransactions} />
          </div>

          {/* Right Column - Analysis & Insights */}
          <div className="space-y-6">
            {/* AI Analysis Panel */}
            <AnalysisPanel transactions={transactions} />

            {/* Recent Activity */}
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

            {/* Category Breakdown */}
            <div className="card bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-6">Spending by Category</h3>
              <div className="space-y-4">
                {['Subscription', 'Fees', 'Fitness', 'Shopping', 'Dining'].map((category) => {
                  const categoryAmount = transactions
                    .filter(tx => tx.category.includes(category))
                    .reduce((sum, tx) => sum + tx.amount, 0);
                  
                  const percentage = totalAmount > 0 ? (categoryAmount / totalAmount) * 100 : 0;
                  
                  return (
                    <div key={category} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-gray-700 text-sm">{category}</span>
                        <span className="font-bold text-gray-900">${categoryAmount.toFixed(2)}</span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                          style={{ 
                            width: `${percentage}%` 
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