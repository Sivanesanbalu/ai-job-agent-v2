import React from "react";
import Link from "next/link";
import { Bot, ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Terms & Conditions - JobAgent.ai",
  description: "Terms and conditions of using the JobAgent.ai platform.",
};

export default function TermsPage() {
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
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">Legal Agreement</span>
            <h1 className="text-3xl font-extrabold text-slate-900 mt-1">Terms and Conditions</h1>
            <p className="text-xs text-slate-400 mt-2">Last Updated: September 20, 2026</p>
          </div>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">1. Acceptance of Terms</h2>
            <p>
              By accessing or using the JobAgent.ai service (referred to as "Service", "Platform", "we", "us", or "our"), 
              you ("User", "Candidate", or "You") agree to be bound by these Terms and Conditions. If you disagree with any 
              part of these terms, you must discontinue the use of our services immediately.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">2. Description of Service</h2>
            <p>
              JobAgent.ai is an autonomous career assistance and browser automation platform designed to assist individual 
              job seekers in discovering relevant job opportunities and submitting application forms on their behalf using 
              candidate-provided resumes and profile data.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">3. User Accounts & Responsibilities</h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>You must be at least 18 years old or the legal age of majority in your jurisdiction to create an account.</li>
              <li>You are solely responsible for ensuring the accuracy, legality, and veracity of all resume details, contact numbers, educational history, work experience, and screening answers submitted to our system.</li>
              <li>You agree to keep your login credentials confidential. Any activity under your authenticated session is your sole responsibility.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">4. Application Credits & Monetization Terms</h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li><strong>Free Monthly Allowance:</strong> Every registered user receives 5 free application credits every month.</li>
              <li><strong>Pay-As-You-Go Packs:</strong> Users may purchase top-up application credits (Starter Pack: ₹149 for 10 credits; Job Seeker Pack: ₹299 for 25 credits; Power Pack: ₹499 for 50 credits). All pricing is in Indian Rupees (INR) inclusive of applicable taxes.</li>
              <li><strong>Deduction Policy:</strong> Exactly 1 application credit is consumed ONLY when an application is actually processed and submitted to an employer portal. No credits are ever charged for job discovery, keyword matching, viewing listings, or account setup.</li>
              <li><strong>Fairness Guarantee:</strong> If an application fails due to network issues or encountering an automated security challenge (CAPTCHA/OTP), the associated credit is refunded to your account balance.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">5. Payment Gateway & Security</h2>
            <p>
              All online payments are securely processed through our authorized payment partner, <strong>Razorpay Payments India Pvt Ltd</strong>. 
              We do not store or process your credit card numbers, CVV, debit card PINs, or UPI PINs on our servers. All transactions comply with 
              PCI-DSS standards and Reserve Bank of India (RBI) regulations.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">6. Third-Party Portals & Employer Decoupling</h2>
            <p>
              JobAgent.ai is an independent automation tool and is not affiliated, endorsed, or partnered with third-party job boards 
              such as LinkedIn, Indeed, Naukri, or corporate applicant tracking systems (Greenhouse, Lever, Workday). The decision to 
              interview, shortlist, or hire candidates rests solely with the hiring employers. We do not guarantee job offers or interviews.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">7. Limitation of Liability</h2>
            <p>
              To the maximum extent permitted by applicable Indian laws, JobAgent.ai and its operators shall not be liable for any 
              indirect, incidental, special, consequential, or punitive damages, including loss of profits, data, employment opportunities, 
              or business interruption resulting from the use or inability to use the service.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">8. Governing Law & Jurisdiction</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of the Republic of India. Any disputes arising 
              out of or in connection with these Terms shall be subject to the exclusive jurisdiction of the competent courts in Tamil Nadu, India.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-base font-bold text-slate-900">9. Contact Information</h2>
            <p>
              For legal inquiries or questions concerning these Terms, contact us at: <br />
              <strong>Email:</strong> support@jobagent.ai | apsiva69@gmail.com <br />
              <strong>Phone:</strong> +91 84386 92752 <br />
              <strong>Address:</strong> Coimbatore, Tamil Nadu, India - 623707
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
