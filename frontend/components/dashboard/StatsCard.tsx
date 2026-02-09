import React from 'react';
import { DollarSign, CreditCard, AlertTriangle, TrendingUp, Wallet2Icon } from 'lucide-react';


interface StatsCardsProps {
  totalAmount: number;
  subscriptionCount: number;
  feeCount: number;
  transactionCount: number;
}

const StatsCards: React.FC<StatsCardsProps> = ({
  totalAmount,
  subscriptionCount,
  feeCount,
  transactionCount,
}) => {
  const cards = [
    {
      title: 'Total Spent',
      value: `₦${totalAmount.toFixed(2)}`,
      change: '+12.5%',
      icon: Wallet2Icon,
      color: 'bg-blue-500/20',
      textColor: 'text-blue-500',
    },
    {
      title: 'Subscriptions',
      value: subscriptionCount,
      change: `${subscriptionCount > 0 ? '+2' : '0'}`,
      icon: CreditCard,
      color: 'bg-purple-500/20',
      textColor: 'text-purple-500',
    },
    {
      title: 'Hidden Fees',
      value: feeCount,
      change: feeCount > 0 ? 'Needs attention' : 'All clear',
      icon: AlertTriangle,
      color: 'bg-yellow-500/20',
      textColor: 'text-yellow-500',
    },
    {
      title: 'Transactions',
      value: transactionCount,
      change: '+15.3%',
      icon: TrendingUp,
      color: 'bg-green-500/20',
      textColor: 'text-green-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 ">
      {cards.map((card) => (
        <div key={card.title} className="card2 hover:shadow-lg transition-shadow p-4 md:p-6 bg-white">
          <div className="flex items-center justify-between mb-3 md:mb-4">
            <div className={`p-2 md:p-3 rounded-lg ${card.color} bg-opacity-10`}>
              <card.icon className={`h-5 w-5 md:h-6 md:w-6 ${card.textColor}`} />
            </div>
            <span className={`text-xs md:text-sm font-medium ${card.change.includes('attention') ? 'text-red-600' : 'text-green-600'}`}>
              {card.change}
            </span>
          </div>
          <div >
            <p className="text-xs md:text-sm text-gray-600 mb-1">{card.title}</p>
            <p className="text-lg md:text-2xl font-bold text-gray-900">{card.value}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatsCards;