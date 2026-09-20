import React from "react";
import Link from "next/link";
import { Bot, ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Privacy Policy - JobAgent.ai",
  description: "Privacy policy describing how JobAgent.ai protects and manages candidate data.",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white">
              <Bot className="h-5 w-5" />
            </div>
            <span className="text-lg font-bold tracking-tight text-slate-900">
              JobAgent<span className="text-indigo-600">.ai</span>
            </span>
          </Link>
          <Link
            href="/"
            className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-indigo-600 transition"
          >
            <ArrowLeft className="h-4 w-4" /> Back to Home
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-12">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 sm:p-12 shadow-xs space-y-8 text-sm leading-relaxed text-slate-700">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">Data Protection</span>
            <h1 className="text-3xl font-extrabold text-slate-900 mt-1">Privacy Policy</h1>
            <p className="text-xs text-slate-400 mt-2">Last Updated: September 20, 2026</p>
          </div>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">1. Information We Collect</h2>
            <p>We collect only information necessary to provide automated job discovery and application services:</p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li><strong>Account Credentials:</strong> Email address, hashed password, and contact details.</li>
              <li><strong>Resume & Profile Data:</strong> Full name, telephone number, educational degrees, work history, technical skills, portfolio links, and screening question answers.</li>
              <li><strong>Payment Metadata:</strong> Transaction IDs, Razorpay order identifiers, payment status, and credit pack selected. We never store credit card numbers, CVVs, or bank account credentials.</li>
              <li><strong>Application Telemetry:</strong> Log of matched job postings, timestamps, and application submission verification statuses.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">2. How We Use Your Information</h2>
            <p>Your data is used strictly for:</p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>Parsing your resume into structured attributes to match with employer job descriptions.</li>
              <li>Pre-filling and submitting authorized job application forms on your behalf using browser automation.</li>
              <li>Providing you with real-time audit logs and status updates on your job applications.</li>
              <li>Processing your credit purchases and maintaining your payment receipts.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">3. Strict Multi-User Data Isolation</h2>
            <p>
              JobAgent.ai enforces strict multi-tenant isolation at every architecture layer:
            </p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>Every user account has an isolated database foreign-key partition.</li>
              <li>Candidate resumes are stored in cryptographically separated directory structures.</li>
              <li>Browser automation sessions run in sandboxed, ephemeral browser contexts that do not share cookies, cache, or state across accounts.</li>
              <li>We <strong>NEVER</strong> sell, rent, or trade your personal resume data to third-party advertisers or recruitment agencies.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">4. Third-Party Service Providers</h2>
            <p>
              We partner with trusted third-party service providers who adhere to strict data security protocols:
            </p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li><strong>Razorpay:</strong> For secure payment gateway processing and invoice generation.</li>
              <li><strong>Job Portals:</strong> When you authorize the agent to apply for a job, your candidate package (resume, name, email, phone) is submitted directly to the employer or job portal specified by you.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">5. Data Retention & Right to Erasure</h2>
            <p>
              You retain total ownership of your data. You may update your profile, replace your uploaded resume, or request complete account deletion at any time through the Settings dashboard or by contacting support. Upon account deletion, all personal data, resumes, and stored credentials are permanently purged from our database.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">6. Contact Our Privacy Officer</h2>
            <p>
              For any questions or concerns regarding your privacy and data security, contact us at: <br />
              <strong>Email:</strong> privacy@jobagent.ai | apsiva69@gmail.com <br />
              <strong>Location:</strong> Coimbatore, Tamil Nadu, India
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
