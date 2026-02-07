// app/register/page.tsx
'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Shield, Mail, Lock, Eye, EyeOff, User, CheckCircle, AlertCircle, ArrowRight, CreditCard, Key } from 'lucide-react';

const RegisterPage = () => {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    acceptTerms: false,
    marketingEmails: true,
  });
  const [showPassword, setShowPassword] = useState({
    password: false,
    confirmPassword: false,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [passwordStrength, setPasswordStrength] = useState(0);

  const calculatePasswordStrength = (password: string) => {
    let score = 0;
    if (password.length >= 8) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    return score;
  };

  const handlePasswordChange = (password: string) => {
    setFormData({ ...formData, password });
    setPasswordStrength(calculatePasswordStrength(password));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!formData.acceptTerms) {
      setError('You must accept the terms and conditions');
      return;
    }

    if (passwordStrength < 2) {
      setError('Please choose a stronger password');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Registration failed');
      }

      // Simulate successful registration
      console.log('Registration successful:', data);
      
      // Redirect to verification or dashboard
      router.push('/dashboard?welcome=true');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoRegistration = (type: 'personal' | 'business') => {
    const demoData = {
      name: type === 'personal' ? 'Demo User' : 'Business Account',
      email: type === 'personal' ? 'demo@fiscalsentinel.com' : 'business@demo.com',
      password: 'SecurePass123!',
      confirmPassword: 'SecurePass123!',
      acceptTerms: true,
      marketingEmails: false,
    };
    setFormData(demoData);
    setPasswordStrength(calculatePasswordStrength(demoData.password));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-blue-100/50 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-purple-100/50 blur-3xl" />
      </div>

      <div className="container relative mx-auto flex min-h-screen items-center justify-center px-4 py-12">
        <div className="w-full max-w-4xl">
          {/* Logo and header */}
          <div className="mb-10 text-center">
            <Link href="/" className="inline-flex items-center justify-center space-x-2">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient shadow-lg">
                <Shield className="h-7 w-7 text-white" />
              </div>
              <div className="text-left">
                <span className="text-2xl font-bold text-gray-900">Fiscal Sentinel</span>
                <div className="text-sm text-gray-600">AI Financial Bodyguard</div>
              </div>
            </Link>
          </div>

          <div className="grid gap-8 lg:grid-cols-2">
            {/* Left column - Benefits */}
            <div className="space-y-8">
              <div>
                <h2 className="text-3xl font-bold text-gray-900">
                  Start Protecting Your Finances Today
                </h2>
                <p className="mt-3 text-lg text-gray-600">
                  Join thousands of users who are already saving money with AI-powered financial protection.
                </p>
              </div>

              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100">
                    <CreditCard className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Automatic Fee Detection</h3>
                    <p className="mt-1 text-gray-600">
                      AI scans your transactions 24/7 for hidden fees and price hikes.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-100">
                    <Key className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Legal Dispute Automation</h3>
                    <p className="mt-1 text-gray-600">
                      Auto-generated legal letters based on FTC rules and banking agreements.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-green-100">
                    <Shield className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Bank-Level Security</h3>
                    <p className="mt-1 text-gray-600">
                      256-bit encryption and read-only access to your financial data.
                    </p>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl bg-gradient-to-r from-blue-50 to-purple-50 p-6">
                <h3 className="font-semibold text-gray-900">Free 30-Day Trial</h3>
                <p className="mt-2 text-gray-600">
                  No credit card required. Cancel anytime. Start protecting your finances immediately.
                </p>
              </div>
            </div>

            {/* Right column - Registration form */}
            <div className="card border-gray-200 bg-white/80 backdrop-blur-sm shadow-2xl">
              <div className="p-8">
                <div className="mb-8 text-center">
                  <h1 className="text-2xl font-bold text-gray-900">Create Your Account</h1>
                  <p className="mt-2 text-gray-600">Start your journey to financial protection</p>
                </div>

                {/* Demo registration buttons */}
                <div className="mb-6 grid grid-cols-2 gap-3">
                  <button
                    onClick={() => handleDemoRegistration('personal')}
                    className="flex items-center justify-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    <User className="h-4 w-4" />
                    Personal Demo
                  </button>
                  <button
                    onClick={() => handleDemoRegistration('business')}
                    className="flex items-center justify-center gap-2 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm font-medium text-blue-700 hover:bg-blue-100"
                  >
                    <Key className="h-4 w-4" />
                    Business Demo
                  </button>
                </div>

                {/* Divider */}
                <div className="relative mb-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="bg-white px-2 text-gray-500">Or create your account</span>
                  </div>
                </div>

                {/* Error message */}
                {error && (
                  <div className="mb-6 flex items-center gap-3 rounded-lg border border-red-200 bg-red-50 p-4">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <span className="text-sm font-medium text-red-700">{error}</span>
                  </div>
                )}

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label htmlFor="name" className="mb-2 block text-sm font-medium text-gray-700">
                      Full Name
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                      <input
                        id="name"
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="input pl-20"
                        placeholder="John Doe"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="email" className="mb-2 block text-sm font-medium text-gray-700">
                      Email Address
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                      <input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="input pl-10"
                        placeholder="you@example.com"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="password" className="mb-2 block text-sm font-medium text-gray-700">
                      Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                      <input
                        id="password"
                        type={showPassword.password ? 'text' : 'password'}
                        value={formData.password}
                        onChange={(e) => handlePasswordChange(e.target.value)}
                        className="input pl-10 pr-10"
                        placeholder="••••••••"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword({ ...showPassword, password: !showPassword.password })}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPassword.password ? (
                          <EyeOff className="h-5 w-5" />
                        ) : (
                          <Eye className="h-5 w-5" />
                        )}
                      </button>
                    </div>

                    {/* Password strength indicator */}
                    {formData.password && (
                      <div className="mt-3">
                        <div className="mb-2 flex justify-between text-sm">
                          <span className="text-gray-600">Password strength</span>
                          <span className="font-medium">
                            {passwordStrength === 0 && 'Very Weak'}
                            {passwordStrength === 1 && 'Weak'}
                            {passwordStrength === 2 && 'Fair'}
                            {passwordStrength === 3 && 'Good'}
                            {passwordStrength === 4 && 'Strong'}
                          </span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-gray-200">
                          <div
                            className={`h-full transition-all duration-300 ${
                              passwordStrength === 1
                                ? 'w-1/4 bg-red-500'
                                : passwordStrength === 2
                                ? 'w-1/2 bg-yellow-500'
                                : passwordStrength === 3
                                ? 'w-3/4 bg-blue-500'
                                : passwordStrength === 4
                                ? 'w-full bg-green-500'
                                : 'w-0 bg-red-500'
                            }`}
                          />
                        </div>
                        <ul className="mt-2 grid grid-cols-2 gap-1 text-xs text-gray-500">
                          <li className="flex items-center gap-1">
                            {formData.password.length >= 8 ? (
                              <CheckCircle className="h-3 w-3 text-green-500" />
                            ) : (
                              <div className="h-3 w-3 rounded-full border border-gray-300" />
                            )}
                            8+ characters
                          </li>
                          <li className="flex items-center gap-1">
                            {/[A-Z]/.test(formData.password) ? (
                              <CheckCircle className="h-3 w-3 text-green-500" />
                            ) : (
                              <div className="h-3 w-3 rounded-full border border-gray-300" />
                            )}
                            Uppercase letter
                          </li>
                          <li className="flex items-center gap-1">
                            {/[0-9]/.test(formData.password) ? (
                              <CheckCircle className="h-3 w-3 text-green-500" />
                            ) : (
                              <div className="h-3 w-3 rounded-full border border-gray-300" />
                            )}
                            Number
                          </li>
                          <li className="flex items-center gap-1">
                            {/[^A-Za-z0-9]/.test(formData.password) ? (
                              <CheckCircle className="h-3 w-3 text-green-500" />
                            ) : (
                              <div className="h-3 w-3 rounded-full border border-gray-300" />
                            )}
                            Special character
                          </li>
                        </ul>
                      </div>
                    )}
                  </div>

                  <div>
                    <label htmlFor="confirmPassword" className="mb-2 block text-sm font-medium text-gray-700">
                      Confirm Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                      <input
                        id="confirmPassword"
                        type={showPassword.confirmPassword ? 'text' : 'password'}
                        value={formData.confirmPassword}
                        onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                        className="input pl-10 pr-10"
                        placeholder="••••••••"
                        required
                      />
                      <button
                        type="button"
                        onClick={() =>
                          setShowPassword({ ...showPassword, confirmPassword: !showPassword.confirmPassword })
                        }
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPassword.confirmPassword ? (
                          <EyeOff className="h-5 w-5" />
                        ) : (
                          <Eye className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                    {formData.confirmPassword &&
                      formData.password !== formData.confirmPassword && (
                        <p className="mt-2 text-sm text-red-600">Passwords do not match</p>
                      )}
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-start">
                      <input
                        id="acceptTerms"
                        type="checkbox"
                        checked={formData.acceptTerms}
                        onChange={(e) => setFormData({ ...formData, acceptTerms: e.target.checked })}
                        className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <label htmlFor="acceptTerms" className="ml-2 text-sm text-gray-700">
                        I agree to the{' '}
                        <Link href="/terms" className="font-medium text-blue-600 hover:text-blue-500">
                          Terms of Service
                        </Link>{' '}
                        and{' '}
                        <Link href="/privacy" className="font-medium text-blue-600 hover:text-blue-500">
                          Privacy Policy
                        </Link>
                      </label>
                    </div>

                    <div className="flex items-start">
                      <input
                        id="marketingEmails"
                        type="checkbox"
                        checked={formData.marketingEmails}
                        onChange={(e) => setFormData({ ...formData, marketingEmails: e.target.checked })}
                        className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <label htmlFor="marketingEmails" className="ml-2 text-sm text-gray-700">
                        I want to receive security updates, product news, and tips via email
                      </label>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="btn-primary w-full py-3 text-base"
                  >
                    {isLoading ? (
                      <div className="flex items-center justify-center gap-2">
                        <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                        Creating account...
                      </div>
                    ) : (
                      <div className="flex items-center justify-center gap-2">
                        Create Free Account
                        <ArrowRight className="h-5 w-5" />
                      </div>
                    )}
                  </button>
                </form>

                {/* Sign in link */}
                <div className="mt-8 text-center">
                  <p className="text-gray-600">
                    Already have an account?{' '}
                    <Link
                      href="/signin"
                      className="font-semibold text-blue-600 hover:text-blue-500"
                    >
                      Sign in
                    </Link>
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Security features */}
          <div className="mt-8 text-center">
            <div className="inline-flex items-center gap-4 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <Shield className="h-4 w-4" />
                Bank-level security
              </div>
              <div className="h-4 w-px bg-gray-300"></div>
              <div className="flex items-center gap-1">
                <Lock className="h-4 w-4" />
                256-bit encryption
              </div>
              <div className="h-4 w-px bg-gray-300"></div>
              <div>GDPR compliant</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;