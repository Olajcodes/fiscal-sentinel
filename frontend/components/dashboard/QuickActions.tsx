import React from 'react';
import { FileText, AlertTriangle, Download, Settings, Shield } from 'lucide-react';

interface QuickActionsProps {
  selectedTransactions: string[];
}

const QuickActions: React.FC<QuickActionsProps> = ({ selectedTransactions }) => {
  const actions = [
    {
      icon: FileText,
      title: 'Generate Dispute Letter',
      description: 'Create legal dispute letter for selected transactions',
      action: () => console.log('Generate dispute for:', selectedTransactions),
      color: 'bg-blue-100 text-blue-600',
      disabled: selectedTransactions.length === 0,
    },
    {
      icon: AlertTriangle,
      title: 'Flag for Review',
      description: 'Mark transactions for manual review',
      action: () => console.log('Flag for review:', selectedTransactions),
      color: 'bg-yellow-100 text-yellow-600',
      disabled: selectedTransactions.length === 0,
    },
    {
      icon: Download,
      title: 'Export Report',
      description: 'Download transactions as CSV or PDF',
      action: () => console.log('Export transactions'),
      color: 'bg-green-100 text-green-600',
      disabled: false,
    },
    {
      icon: Settings,
      title: 'Settings',
      description: 'Configure analysis preferences',
      action: () => console.log('Open settings'),
      color: 'bg-purple-100 text-purple-600',
      disabled: false,
    },
  ];

  return (
    <div className="card p-6 bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-6">Quick Actions</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        {actions.map((action, idx) => (
          <button
            key={idx}
            onClick={action.action}
            disabled={action.disabled}
            className={`flex flex-col items-center justify-center rounded-xl border border-gray-200 p-4 md:p-6 text-center hover:border-blue-300 hover:shadow-md transition-all ${
              action.disabled ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <div className={`mb-3 md:mb-4 flex h-10 w-10 md:h-12 md:w-12 items-center justify-center rounded-lg ${action.color}`}>
              <action.icon className="h-5 w-5 md:h-6 md:w-6" />
            </div>
            <h4 className="font-bold text-gray-900 mb-1 md:mb-2 text-sm md:text-base">{action.title}</h4>
            <p className="text-xs md:text-sm text-gray-600">{action.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;