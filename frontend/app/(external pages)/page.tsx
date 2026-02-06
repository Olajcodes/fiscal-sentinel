import {
  Shield,
  AlertTriangle,
  FileText,
  CheckCircle,
  Zap,
  BarChart,
  Lock,
  ArrowRight,
} from 'lucide-react';

const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-muted to-background">
      {/* Navigation */}
      <nav className="hidden sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold text-foreground">
                Fiscal Sentinel
              </span>
            </div>

            <div className="hidden md:flex items-center space-x-8">
              <a
                href="#features"
                className="font-medium text-muted-foreground hover:text-accent transition"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                className="font-medium text-muted-foreground hover:text-accent transition"
              >
                How It Works
              </a>
              <a
                href="#security"
                className="font-medium text-muted-foreground hover:text-accent transition"
              >
                Security
              </a>
              <button className="rounded-lg bg-gradient px-6 py-2 font-medium text-white transition hover:bg-gradient-hover">
                Get Started
              </button>
            </div>

            <button className="rounded-lg border border-border px-4 py-2 text-sm font-medium md:hidden">
              Menu
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid gap-12 lg:grid-cols-2">
            <div className="space-y-8">
              <div className="inline-flex items-center rounded-full bg-accent/10 px-4 py-2">
                <AlertTriangle className="mr-2 h-4 w-4 text-accent" />
                <span className="text-sm font-medium text-accent">
                  AI-Powered Financial Protection
                </span>
              </div>

              <h1 className="text-4xl font-bold leading-tight text-foreground md:text-5xl lg:text-6xl">
                Your AI Financial Bodyguard
                <span className="block text-accent">
                  Fights Corporate Bureaucracy
                </span>
              </h1>

              <p className="text-xl text-muted-foreground">
                Connect your accounts and let Fiscal Sentinel automatically
                identify hidden fees, price hikes, and unused subscriptions. We
                draft legal dispute letters to resolve them for you.
              </p>

              <div className="flex flex-col gap-4 sm:flex-row">
                <button className="flex items-center justify-center rounded-xl bg-gradient px-8 py-4 text-lg font-semibold text-white transition hover:bg-gradient-hover">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </button>
                <button className="rounded-xl border border-border bg-background px-8 py-4 text-lg font-semibold text-foreground hover:bg-muted transition">
                  Watch Demo
                </button>
              </div>

              <div className="flex items-center space-x-8 pt-8">
                <div className="flex items-center">
                  <CheckCircle className="mr-2 h-5 w-5 text-green-500" />
                  <span className="text-muted-foreground">
                    No credit card required
                  </span>
                </div>
                <div className="flex items-center">
                  <Shield className="mr-2 h-5 w-5 text-accent" />
                  <span className="text-muted-foreground">
                    Bank-level security
                  </span>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -inset-4 rounded-3xl bg-gradient opacity-20 blur-xl"></div>
              <div className="relative rounded-2xl border border-border bg-background p-8 shadow-xl">
                <div className="mb-6 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="h-3 w-3 rounded-full bg-red-400"></div>
                    <div className="h-3 w-3 rounded-full bg-yellow-400"></div>
                    <div className="h-3 w-3 rounded-full bg-green-400"></div>
                  </div>
                  <Shield className="h-6 w-6 text-accent" />
                </div>

                <div className="space-y-6">
                  <div className="rounded-lg border border-border p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
                          <AlertTriangle className="h-5 w-5 text-red-500" />
                        </div>
                        <div>
                          <p className="font-medium">Netflix Price Hike</p>
                          <p className="text-sm text-muted-foreground">
                            Increased by $3 without notice
                          </p>
                        </div>
                      </div>
                      <span className="font-bold text-red-500">$3.00</span>
                    </div>
                  </div>

                  <div className="rounded-lg border border-border p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-yellow-500/10">
                          <AlertTriangle className="h-5 w-5 text-yellow-500" />
                        </div>
                        <div>
                          <p className="font-medium">Hidden Bank Fee</p>
                          <p className="text-sm text-muted-foreground">
                            Undisclosed maintenance fee
                          </p>
                        </div>
                      </div>
                      <span className="font-bold text-yellow-500">$5.99</span>
                    </div>
                  </div>

                  <div className="rounded-lg border border-border bg-accent/10 p-4">
                    <div className="flex items-center">
                      <div className="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-accent/20">
                        <FileText className="h-5 w-5 text-accent" />
                      </div>
                      <div>
                        <p className="font-medium">Auto-generated Dispute</p>
                        <p className="text-sm text-muted-foreground">
                          Legal letter ready for signature
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-8 rounded-lg bg-muted p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">
                        This month's savings
                      </p>
                      <p className="text-2xl font-bold text-green-500">
                        $124.85
                      </p>
                    </div>
                    <BarChart className="h-8 w-8 text-green-500" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-muted">
        <div className="container mx-auto max-w-6xl">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-3xl font-bold text-foreground md:text-4xl">
              Advanced AI Protection Features
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              Fiscal Sentinel uses cutting-edge AI to protect your finances
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl border border-border bg-background p-8 shadow-sm transition hover:shadow-lg">
              <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-red-500/10">
                <AlertTriangle className="h-7 w-7 text-red-500" />
              </div>
              <h3 className="mb-3 text-xl font-bold">Threat Detection</h3>
              <p className="text-muted-foreground">
                Automatically scans transaction history for anomalies like hidden
                fees, price hikes, or unused subscriptions.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-background p-8 shadow-sm transition hover:shadow-lg">
              <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-accent/10">
                <FileText className="h-7 w-7 text-accent" />
              </div>
              <h3 className="mb-3 text-xl font-bold">Legal RAG Brain</h3>
              <p className="text-muted-foreground">
                Uses Retrieval Augmented Generation (RAG) to search actual FTC
                Rules and Banking Agreements for disputes.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-background p-8 shadow-sm transition hover:shadow-lg">
              <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-green-500/10">
                <Zap className="h-7 w-7 text-green-500" />
              </div>
              <h3 className="mb-3 text-xl font-bold">Auto-Drafting</h3>
              <p className="text-muted-foreground">
                Generates formal, legally-sound cancellation or dispute letters
                ready for your signature.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-background p-8 shadow-sm transition hover:shadow-lg">
              <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-xl bg-yellow-500/10">
                <Shield className="h-7 w-7 text-yellow-500" />
              </div>
              <h3 className="mb-3 text-xl font-bold">Safety Evaluation</h3>
              <p className="text-muted-foreground">
                Integrated with Opik to track agent performance and ensure
                compliant, safe financial advice.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-3xl font-bold text-foreground md:text-4xl">
              How Fiscal Sentinel Works
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              Three simple steps to take back control of your finances
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex flex-col items-center text-center">
                <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-accent/10 text-2xl font-bold text-accent">
                  {step}
                </div>
                <h3 className="mb-3 text-xl font-bold">
                  {step === 1
                    ? 'Connect Securely'
                    : step === 2
                    ? 'AI Analysis'
                    : 'Resolve & Save'}
                </h3>
                <p className="text-muted-foreground">
                  {step === 1 &&
                    'Link your bank accounts with bank-level security. We use read-only access and 256-bit encryption.'}
                  {step === 2 &&
                    'Our AI scans transactions, identifies issues, and researches applicable laws for dispute justification.'}
                  {step === 3 &&
                    'Review auto-generated dispute letters, sign with one click, and let us handle the bureaucracy.'}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

        {/* Security Section */}
      <section id="security" className="py-20 px-4 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="container mx-auto max-w-6xl">
          <div className="grid gap-12 lg:grid-cols-2">
            <div>
              <h2 className="mb-6 text-3xl font-bold text-gray-900 md:text-4xl">
                Enterprise-Grade Security
              </h2>
              <p className="mb-8 text-lg text-gray-600">
                Your financial data is protected with bank-level security measures and compliance frameworks.
              </p>
              
              <div className="space-y-6">
                <div className="flex items-start">
                  <Lock className="mr-4 mt-1 h-6 w-6 text-blue-600" />
                  <div>
                    <h4 className="font-bold text-gray-900">256-bit Encryption</h4>
                    <p className="text-gray-600">All data is encrypted in transit and at rest</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <Shield className="mr-4 mt-1 h-6 w-6 text-blue-600" />
                  <div>
                    <h4 className="font-bold text-gray-900">Read-Only Access</h4>
                    <p className="text-gray-600">We never have permission to move your money</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <CheckCircle className="mr-4 mt-1 h-6 w-6 text-blue-600" />
                  <div>
                    <h4 className="font-bold text-gray-900">Opik Integration</h4>
                    <p className="text-gray-600">Continuous safety evaluation and compliance monitoring</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-xl">
              <div className="mb-6 flex items-center justify-between">
                <h3 className="text-2xl font-bold">Monthly Savings Report</h3>
                <BarChart className="h-8 w-8 text-blue-600" />
              </div>
              
              <div className="mb-8 space-y-4">
                <div>
                  <div className="mb-2 flex justify-between">
                    <span className="font-medium">Hidden Fees Recovered</span>
                    <span className="font-bold text-green-600">$89.50</span>
                  </div>
                  <div className="h-2 rounded-full bg-gray-200">
                    <div className="h-2 w-3/4 rounded-full bg-green-500"></div>
                  </div>
                </div>
                
                <div>
                  <div className="mb-2 flex justify-between">
                    <span className="font-medium">Subscription Cancellations</span>
                    <span className="font-bold text-blue-600">$35.35</span>
                  </div>
                  <div className="h-2 rounded-full bg-gray-200">
                    <div className="h-2 w-2/3 rounded-full bg-blue-500"></div>
                  </div>
                </div>
                
                <div>
                  <div className="mb-2 flex justify-between">
                    <span className="font-medium">Price Hike Disputes</span>
                    <span className="font-bold text-purple-600">$124.85</span>
                  </div>
                  <div className="h-2 rounded-full bg-gray-200">
                    <div className="h-2 w-4/5 rounded-full bg-gradient"></div>
                  </div>
                </div>
              </div>
              
              <div className="rounded-xl bg-gradient p-6">
                <p className="mb-2 text-sm text-white/90">Total Protected This Month</p>
                <p className="text-3xl font-bold text-white">$249.70</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <div className="rounded-3xl bg-gradient p-12">
            <h2 className="mb-6 text-3xl font-bold text-white md:text-4xl">
              Ready to Fight Financial Bureaucracy?
            </h2>
            <p className="mb-10 text-xl text-white/90">
              Join thousands who are taking back control of their finances with
              AI
            </p>

            <div className="flex flex-col justify-center gap-4 sm:flex-row">
              <button className="rounded-xl bg-white px-10 py-4 text-lg font-semibold text-foreground hover:bg-muted transition">
                Start Free Trial
              </button>
              <button className="rounded-xl border border-white/30 bg-transparent px-10 py-4 text-lg font-semibold text-white hover:bg-white/10 transition">
                Schedule a Demo
              </button>
            </div>

            <p className="mt-8 text-white/70">
              No credit card required • 30-day money back guarantee • Cancel
              anytime
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-muted py-12 px-4">
        <div className="container mx-auto max-w-6xl text-center text-muted-foreground">
          <p>
            © {new Date().getFullYear()} Fiscal Sentinel. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
