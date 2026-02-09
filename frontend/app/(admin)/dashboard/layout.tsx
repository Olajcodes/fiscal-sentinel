// app/dashboard/layout.tsx
import React from 'react';

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {children}
    </div>
  );
}