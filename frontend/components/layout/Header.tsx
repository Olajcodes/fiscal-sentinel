// components/layout/Header.tsx
'use client';

import React, { useState } from 'react';
import { Shield, Menu, X, AlertTriangle, FileText, Zap } from 'lucide-react';
import Link from 'next/link';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navItems = [
    { label: 'Features', href: '#features', icon: AlertTriangle },
    { label: 'How It Works', href: '#how-it-works', icon: Zap },
    { label: 'Security', href: '#security', icon: Shield },
    { label: 'Pricing', href: '/pricing' },
    { label: 'Documentation', href: '/docs', icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/90 backdrop-blur-sm">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient">
              <Shield className="h-5 w-5 text-cyan-400" />
            </div>
            <div>
              <span className="text-xl font-bold text-foreground">
                Fiscal Sentinel
              </span>
              <div className="-mt-1 text-xs text-muted-foreground">
                AI Financial Bodyguard
              </div>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden items-center space-x-8 md:flex">
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="flex items-center space-x-1 text-sm font-medium text-muted-foreground transition-colors hover:text-accent"
              >
                {item.icon && <item.icon className="h-4 w-4" />}
                <span>{item.label}</span>
              </a>
            ))}
          </nav>

          {/* CTA Buttons */}
          <div className="hidden items-center space-x-4 md:flex">
            <Link
              href="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-muted-foreground transition hover:text-accent"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="rounded-lg bg-gradient px-6 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-gradient-hover"
            >
              Get Started Free
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            className="rounded-lg p-2 text-muted-foreground hover:bg-muted md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="border-t border-border py-4 md:hidden">
            <div className="space-y-2">
              {navItems.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className="flex items-center space-x-3 rounded-lg px-4 py-3 text-sm font-medium text-foreground hover:bg-muted"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.icon && (
                    <item.icon className="h-5 w-5 text-muted-foreground" />
                  )}
                  <span>{item.label}</span>
                </a>
              ))}
              <div className="mt-4 space-y-2 px-4">
                <Link
                  href="/login"
                  className="block rounded-lg px-4 py-3 text-center text-sm font-medium text-foreground hover:bg-muted"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Sign In
                </Link>
                <Link
                  href="/signup"
                  className="block rounded-lg bg-gradient px-4 py-3 text-center text-sm font-medium text-white"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Get Started Free
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
