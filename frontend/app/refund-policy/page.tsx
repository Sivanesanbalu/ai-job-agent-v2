import React from "react";
import Link from "next/link";
import { Bot, ArrowLeft, ShieldCheck, RefreshCw } from "lucide-react";

export const metadata = {
  title: "Cancellation & Refund Policy - JobAgent.ai",
  description: "Cancellation and refund policies for application credit purchases on JobAgent.ai.",
};

export default function RefundPolicyPage() {
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
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">Fair Use Assurance</span>
            <h1 className="text-3xl font-extrabold text-slate-900 mt-1">Cancellation & Refund Policy</h1>
            <p className="text-xs text-slate-400 mt-2">Last Updated: September 20, 2026</p>
          </div>

          <div className="rounded-2xl border border-emerald-200 bg-emerald-50/60 p-5 flex items-start gap-3.5">
            <ShieldCheck className="h-5 w-5 text-emerald-600 flex-shrink-0 mt-0.5" />
            <div className="text-xs text-emerald-900 space-y-1">
              <p className="font-bold">Automated Zero-Waste Credit Guarantee</p>
              <p>
                Credits are strictly deducted ONLY when an application is successfully submitted to an employer portal. 
                If an application encounters a technical error, network timeout, or security challenge (CAPTCHA), 
                the credit is instantly and automatically returned to your active ledger balance.
              </p>
            </div>
          </div>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">1. Nature of Products Sold</h2>
            <p>
              JobAgent.ai provides pay-as-you-go digital application credits (Starter Pack: ₹149 for 10 credits, 
              Job Seeker Pack: ₹299 for 25 credits, Power Pack: ₹499 for 50 credits). Application credits are digital goods 
              delivered immediately upon confirmed payment verification.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">2. Cancellation Policy</h2>
            <p>
              Because JobAgent.ai does not offer recurring auto-renewing subscriptions, there are no hidden subscription 
              charges or recurring cancellation fees. Users purchase pay-as-you-go credit packs voluntarily on demand.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">3. Gateway Refund Eligibility</h2>
            <p>
              You may request a full refund to your original payment method under the following circumstances:
            </p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li><strong>Duplicate Transaction:</strong> If you were charged more than once due to a technical glitch or network delay during checkout.</li>
              <li><strong>Unused Credit Pack:</strong> If you purchased a credit pack and have not utilized any credits from that pack, you may request a 100% refund within <strong>7 days</strong> of the purchase date.</li>
              <li><strong>System Inability to Deliver:</strong> If an unforeseen technical malfunction prevents our autonomous agent from executing on supported portals for more than 48 consecutive hours.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">4. Refund Processing Timeline</h2>
            <p>
              Once a refund request is received and verified:
            </p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>We will review and approve eligible requests within <strong>24 to 48 hours</strong>.</li>
              <li>Upon approval, refunds are issued via our payment partner <strong>Razorpay</strong> directly to the original payment source (bank account, credit card, or UPI VPA).</li>
              <li>Funds typically reflect in your account within <strong>5 to 7 business days</strong>, depending on your issuing bank&apos;s processing cycles.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">5. How to Initiate a Refund Request</h2>
            <p>
              To request a refund, email our support desk at <strong>support@jobagent.ai</strong> or <strong>apsiva69@gmail.com</strong> with:
            </p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>Your registered account email address.</li>
              <li>Razorpay Payment ID (e.g. <code className="bg-slate-100 px-1 py-0.5 rounded text-xs">pay_XXXXXXXX</code>) or Order ID.</li>
              <li>Reason for the refund request.</li>
            </ul>
          </section>
        </div>
      </main>
    </div>
  );
}
