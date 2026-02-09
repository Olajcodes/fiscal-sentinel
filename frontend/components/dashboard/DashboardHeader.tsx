import React from 'react';
import { Shield, Bell, ChevronDown, Upload, User } from 'lucide-react';
import Link from 'next/link';

interface DashboardHeaderProps {
  user: any;
  onUploadClick: () => void;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ user, onUploadClick }) => {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/95 backdrop-blur-sm">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 md:h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="flex h-7 w-7 md:h-8 md:w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
              <Shield className="h-4 w-4 md:h-5 md:w-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <span className="text-lg md:text-xl font-bold text-gray-900">Fiscal Sentinel</span>
              <div className="-mt-1 text-xs text-gray-500">Dashboard</div>
            </div>
          </Link>

          {/* Search and Actions */}
          <div className="flex items-center space-x-2 md:space-x-4">
            <button
              onClick={onUploadClick}
              className="hidden md:flex items-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:from-blue-700 hover:to-purple-700 transition-colors"
            >
              <Upload className="h-4 w-4" />
              Upload Transactions
            </button>

            <button className="relative rounded-lg p-1.5 md:p-2 text-gray-600 hover:bg-gray-100 transition-colors">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full bg-red-500"></span>
            </button>

            {/* User Menu */}
            <div className="group relative">
              <button className="flex items-center space-x-2 rounded-lg p-1.5 md:p-2 hover:bg-gray-100 transition-colors">
                <div className="flex h-7 w-7 md:h-8 md:w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-100 to-purple-100">
                  <User className="h-3 w-3 md:h-4 md:w-4 text-blue-600" />
                </div>
                <div className="hidden text-left md:block">
                  <p className="text-sm font-medium text-gray-900 truncate max-w-[120px]">
                    {user?.firstName} {user?.lastName}
                  </p>
                  <p className="text-xs text-gray-500">{user?.role || 'User'}</p>
                </div>
                <ChevronDown className="hidden h-4 w-4 text-gray-400 md:block" />
              </button>

              {/* Dropdown Menu */}
              <div className="absolute right-0 top-full mt-2 hidden w-48 rounded-lg border border-gray-200 bg-white py-2 shadow-lg group-hover:block">
                <Link
                  href="/profile"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Profile Settings
                </Link>
                <Link
                  href="/settings"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Account Settings
                </Link>
                <Link
                  href="/security"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Security
                </Link>
                <div className="my-2 border-t border-gray-200"></div>
                <button
                  onClick={() => {
                    // Add logout logic
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    window.location.href = '/signin';
                  }}
                  className="block w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-50"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;