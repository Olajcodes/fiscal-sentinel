import { Check, AlertTriangle, CreditCard, FileText, Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import type { Transaction } from '@/lib/types';

interface TransactionTableProps {
  transactions: Transaction[];
  selectedTransactions: string[];
  onSelectTransaction: (id: string) => void;
  onSelectAll: () => void;
  totalTransactions: number;
  currentPage: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
  onItemsPerPageChange: (value: number) => void;
}

const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  selectedTransactions,
  onSelectTransaction,
  onSelectAll,
  totalTransactions,
  currentPage,
  itemsPerPage,
  onPageChange,
  onItemsPerPageChange,
}) => {
  const totalPages = Math.ceil(totalTransactions / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage + 1;
  const endIndex = Math.min(currentPage * itemsPerPage, totalTransactions);

  if (transactions.length === 0) {
    return (
      <div className="text-center py-8 md:py-12">
        <CreditCard className="h-10 w-10 md:h-12 md:w-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-base md:text-lg font-medium text-gray-900 mb-2">No transactions found</h3>
        <p className="text-sm text-gray-600">Upload your bank statements to get started</p>
      </div>
    );
  }

  // Generate page numbers for pagination
  const getPageNumbers = () => {
    const pageNumbers = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      // Show all pages
      for (let i = 1; i <= totalPages; i++) {
        pageNumbers.push(i);
      }
    } else {
      // Always show first page
      pageNumbers.push(1);
      
      // Calculate start and end of visible pages
      let start = Math.max(2, currentPage - 1);
      let end = Math.min(totalPages - 1, currentPage + 1);
      
      // Adjust if near the beginning
      if (currentPage <= 3) {
        end = Math.min(totalPages - 1, maxVisiblePages - 1);
      }
      
      // Adjust if near the end
      if (currentPage >= totalPages - 2) {
        start = Math.max(2, totalPages - maxVisiblePages + 2);
      }
      
      // Add ellipsis if needed
      if (start > 2) {
        pageNumbers.push('...');
      }
      
      // Add middle pages
      for (let i = start; i <= end; i++) {
        pageNumbers.push(i);
      }
      
      // Add ellipsis if needed
      if (end < totalPages - 1) {
        pageNumbers.push('...');
      }
      
      // Always show last page
      if (totalPages > 1) {
        pageNumbers.push(totalPages);
      }
    }
    
    return pageNumbers;
  };

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto -mx-6 sm:mx-0">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-3 py-3 sm:px-6">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={transactions.length > 0 && selectedTransactions.length === transactions.length}
                    onChange={onSelectAll}
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </div>
              </th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                Date
              </th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Merchant
              </th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                Amount
              </th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">
                Category
              </th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                Status
              </th>
              <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">
                Notes
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {transactions.map((transaction) => {
              const isSelected = selectedTransactions.includes(transaction.transaction_id);
              const hasIssue = transaction.notes.toLowerCase().includes('fee') || 
                             transaction.notes.toLowerCase().includes('hike') ||
                             transaction.notes.toLowerCase().includes('cancel');
              
              return (
                <tr 
                  key={transaction.transaction_id}
                  className={`hover:bg-gray-50 ${isSelected ? 'bg-blue-50' : ''}`}
                >
                  <td className="px-3 py-4 sm:px-6">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => onSelectTransaction(transaction.transaction_id)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-3 py-4 whitespace-nowrap">
                    <div className="flex items-center text-sm text-gray-900">
                      <Calendar className="mr-2 h-4 w-4 text-gray-400 flex-shrink-0" />
                      <span>{transaction.date}</span>
                    </div>
                  </td>
                  <td className="px-3 py-4">
                    <div className="flex items-center">
                      <div className="h-8 w-8 flex items-center justify-center rounded-lg bg-blue-100 mr-2 md:mr-3 flex-shrink-0">
                        <CreditCard className="h-4 w-4 text-blue-600" />
                      </div>
                      <span className="text-sm font-medium text-gray-900 truncate max-w-[120px] sm:max-w-none">
                        {transaction.merchant_name}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className='text-gray-400 p-1'>₦</span>
                      <span className={`text-sm font-bold ${
                        transaction.category.includes('Fees') ? 'text-red-600' : 'text-gray-900'
                      }`}>
                        {transaction.amount.toFixed(2)}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-4 hidden sm:table-cell">
                    <div className="flex flex-wrap gap-1">
                      {transaction.category.slice(0, 2).map((cat) => (
                        <span
                          key={cat}
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            cat === 'Fees'
                              ? 'bg-red-100 text-red-800'
                              : cat === 'Subscription'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {cat}
                          {transaction.category.length > 2 && cat === transaction.category[1] && '+'}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-3 py-4 whitespace-nowrap">
                    {hasIssue ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        <AlertTriangle className="mr-1 h-3 w-3" />
                        <span className="hidden sm:inline">Issue</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <Check className="mr-1 h-3 w-3" />
                        <span className="hidden sm:inline">Normal</span>
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-4 hidden md:table-cell">
                    <div className="flex items-center text-sm text-gray-600 max-w-[200px]">
                      <FileText className="mr-2 h-4 w-4 text-gray-400 flex-shrink-0" />
                      <span className="truncate">{transaction.notes}</span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-gray-200">
        {/* Items per page selector */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-700">Show</span>
          <select
            value={itemsPerPage}
            onChange={(e) => onItemsPerPageChange(Number(e.target.value))}
            className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
          <span className="text-sm text-gray-700">per page</span>
        </div>

        {/* Page info */}
        <div className="text-sm text-gray-700">
          Showing <span className="font-medium">{startIndex}</span> to <span className="font-medium">{endIndex}</span> of{' '}
          <span className="font-medium">{totalTransactions}</span> transactions
        </div>

        {/* Pagination buttons */}
        <div className="flex items-center space-x-2">
          {/* Previous button */}
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="inline-flex items-center px-3 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </button>

          {/* Page numbers */}
          <div className="hidden sm:flex items-center space-x-1">
            {getPageNumbers().map((pageNumber, index) => (
              <button
                key={index}
                onClick={() => typeof pageNumber === 'number' && onPageChange(pageNumber)}
                disabled={pageNumber === '...'}
                className={`min-w-[2.5rem] px-3 py-2 rounded-md text-sm font-medium ${
                  pageNumber === currentPage
                    ? 'bg-blue-600 text-white'
                    : pageNumber === '...'
                    ? 'text-gray-500 cursor-default'
                    : 'text-gray-700 hover:bg-gray-100 border border-gray-300'
                }`}
              >
                {pageNumber}
              </button>
            ))}
          </div>

          {/* Mobile page indicator */}
          <div className="sm:hidden text-sm font-medium text-gray-700">
            Page {currentPage} of {totalPages}
          </div>

          {/* Next button */}
          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="inline-flex items-center px-3 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default TransactionTable;