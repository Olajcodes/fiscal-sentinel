// components/layout/Footer.tsx
import React from 'react';
import { Shield, Twitter, Linkedin, Github, Mail } from 'lucide-react';
import Link from 'next/link';

const Footer = () => {
  const footerLinks = {
    Product: [
      { label: 'Features', href: '#features' },
      { label: 'How It Works', href: '#how-it-works' },
      { label: 'Security', href: '#security' },
      { label: 'Pricing', href: '/pricing' },
      { label: 'API', href: '/api' },
    ],
    Company: [
      { label: 'About', href: '/about' },
      { label: 'Blog', href: '/blog' },
      { label: 'Careers', href: '/careers' },
      { label: 'Press', href: '/press' },
      { label: 'Contact', href: '/contact' },
    ],
    Legal: [
      { label: 'Privacy Policy', href: '/privacy' },
      { label: 'Terms of Service', href: '/terms' },
      { label: 'Cookie Policy', href: '/cookies' },
      { label: 'Compliance', href: '/compliance' },
      { label: 'GDPR', href: '/gdpr' },
    ],
    Resources: [
      { label: 'Documentation', href: '/docs' },
      { label: 'Help Center', href: '/help' },
      { label: 'Community', href: '/community' },
      { label: 'Partners', href: '/partners' },
      { label: 'Status', href: '/status' },
    ],
  };

  const socialLinks = [
    { icon: Twitter, href: 'https://twitter.com/fiscalsentinel', label: 'Twitter' },
    { icon: Linkedin, href: 'https://linkedin.com/company/fiscalsentinel', label: 'LinkedIn' },
    { icon: Github, href: 'https://github.com/fiscalsentinel', label: 'GitHub' },
    { icon: Mail, href: 'mailto:contact@fiscalsentinel.com', label: 'Email' },
  ];

  return (
    <footer className="border-t border-gray-200 bg-gray-50">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-5">
          {/* Brand Column */}
          <div className="lg:col-span-2">
            <Link href="/" className="mb-6 inline-flex items-center space-x-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div>
                <span className="text-xl font-bold text-gray-900">Fiscal Sentinel</span>
                <div className="text-sm text-gray-600">AI Financial Bodyguard</div>
              </div>
            </Link>
            <p className="mb-6 max-w-md text-gray-600">
              Protecting users from predatory financial practices. We fight corporate bureaucracy so you don&apos;t have to.
            </p>
            <div className="flex space-x-4">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-lg p-2 text-gray-400 hover:bg-white hover:text-blue-600"
                  aria-label={social.label}
                >
                  <social.icon className="h-5 w-5" />
                </a>
              ))}
            </div>
          </div>

          {/* Footer Links Columns */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-900">
                {category}
              </h3>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-gray-600 hover:text-blue-600"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 border-t border-gray-200 pt-8">
          <div className="flex flex-col items-center justify-between md:flex-row">
            <div className="mb-4 md:mb-0">
              <p className="text-sm text-gray-600">
                © {new Date().getFullYear()} Fiscal Sentinel. All rights reserved.
              </p>
            </div>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
              <span>Protected by Opik Safety Framework</span>
              <span className="hidden md:inline">•</span>
              <span>Bank-level 256-bit encryption</span>
              <span className="hidden md:inline">•</span>
              <span>PCI DSS Compliant</span>
            </div>
            
            <div className="mt-4 flex items-center space-x-6 md:mt-0">
              <span className="text-sm text-gray-600">
                Made with ❤️ for financial justice
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;