import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">
                CareFlow AI
              </h1>
            </div>
            <nav className="flex items-center gap-4">
              <Link
                href="/login"
                className="text-gray-600 hover:text-gray-900"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="btn btn-primary"
              >
                Get Started
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="flex-1">
        <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Autonomous Clinic Operations
            </h2>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Transform your practice with AI-powered patient triage, intelligent scheduling,
              and automated clinical documentation. Built for modern healthcare.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="/register"
                className="btn btn-primary px-6 py-3 text-lg"
              >
                Start Free Trial
              </Link>
              <Link
                href="#features"
                className="btn btn-outline px-6 py-3 text-lg"
              >
                Learn More
              </Link>
            </div>
          </div>

          {/* Features */}
          <div id="features" className="mt-24 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <FeatureCard
              icon="🩺"
              title="AI Triage"
              description="24/7 symptom assessment with intelligent urgency classification"
            />
            <FeatureCard
              icon="📅"
              title="Smart Scheduling"
              description="Automated appointment booking with calendar optimization"
            />
            <FeatureCard
              icon="📝"
              title="Clinical Scribe"
              description="Automatic SOAP note generation from visit transcripts"
            />
            <FeatureCard
              icon="💳"
              title="Billing Assistant"
              description="ICD-10/CPT code suggestions and claim validation"
            />
          </div>

          {/* Compliance */}
          <div className="mt-24 rounded-lg bg-primary-50 p-8 text-center">
            <h3 className="text-2xl font-bold text-primary-900">
              HIPAA Ready • GDPR Compliant • EHR Integrated
            </h3>
            <p className="mt-2 text-primary-700">
              Built with security and compliance as the foundation
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white py-8">
        <div className="mx-auto max-w-7xl px-4 text-center text-gray-600">
          <p>&copy; 2024 CareFlow AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="card">
      <div className="text-4xl">{icon}</div>
      <h3 className="mt-4 text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-gray-600">{description}</p>
    </div>
  )
}
