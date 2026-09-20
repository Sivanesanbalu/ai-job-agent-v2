"use client";

import React from "react";
import Link from "next/link";
import {
  Sparkles,
  Search,
  Bot,
  ShieldCheck,
  Zap,
  CheckCircle2,
  ArrowRight,
  Briefcase,
  FileText,
  Sliders,
  Send,
  Layers,
  Clock,
  HelpCircle,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-indigo-500 selection:text-white">
      {/* Navigation */}
      <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm shadow-indigo-200">
              <Bot className="h-6 w-6" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-slate-900">
                JobAgent<span className="text-indigo-600">.ai</span>
              </span>
              <span className="ml-2 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-semibold text-indigo-700 border border-indigo-200">
                v2.0 SaaS
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#how-it-works" className="hover:text-indigo-600 transition">
              How It Works
            </a>
            <a href="#sources" className="hover:text-indigo-600 transition">
              Portals
            </a>
            <a href="#features" className="hover:text-indigo-600 transition">
              Features
            </a>
            <a href="#pricing" className="hover:text-indigo-600 transition">
              Pricing
            </a>
            <a href="#faq" className="hover:text-indigo-600 transition">
              FAQ
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-indigo-600 transition"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 transition"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-24 lg:pt-28 lg:pb-32">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50/70 px-4 py-1.5 text-xs font-medium text-indigo-700 mb-8">
            <Sparkles className="h-4 w-4" />
            Next-Gen Autonomous Career Agent for 2026
          </div>

          <h1 className="mx-auto max-w-4xl text-5xl font-extrabold tracking-tight text-slate-900 sm:text-6xl lg:text-7xl">
            Your AI Job Search &{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">
              Application Agent
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600 leading-relaxed">
            Upload your resume. Set your target roles, locations, and salary.
            Let your dedicated browser agent autonomously discover verified
            openings, match requirements, and submit eligible applications.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-8 py-3.5 text-base font-semibold text-white shadow-md shadow-indigo-200 hover:bg-indigo-700 transition"
            >
              Start Free (100 Applications)
              <ArrowRight className="h-5 w-5" />
            </Link>
            <a
              href="#how-it-works"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-6 py-3.5 text-base font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              Explore Workflow
            </a>
          </div>

          <div className="mt-12 flex items-center justify-center gap-8 text-xs font-medium text-slate-500">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              100 Free Applications Included
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              Isolated Browser Sandboxes
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              Never Bypasses Anti-Bot Gates
            </span>
          </div>

          {/* Interactive Preview Mockup Card */}
          <div className="mx-auto mt-16 max-w-5xl rounded-2xl border border-slate-200 bg-white p-4 shadow-xl lg:p-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-rose-400" />
                <span className="h-3 w-3 rounded-full bg-amber-400" />
                <span className="h-3 w-3 rounded-full bg-emerald-400" />
                <span className="ml-3 text-xs font-mono text-slate-400">
                  agent.jobagent.ai/automation/cockpit
                </span>
              </div>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 border border-emerald-200">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                Agent Active • 182 Jobs Discovered
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-left">
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <div className="text-xs font-medium text-slate-500">Discovered</div>
                <div className="text-2xl font-bold text-slate-900 mt-1">182</div>
                <div className="text-xs text-indigo-600 mt-1">LinkedIn, Naukri, Indeed</div>
              </div>
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <div className="text-xs font-medium text-slate-500">AI Matched</div>
                <div className="text-2xl font-bold text-slate-900 mt-1">72</div>
                <div className="text-xs text-emerald-600 mt-1">Score &ge; 70% threshold</div>
              </div>
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <div className="text-xs font-medium text-slate-500">Submitted</div>
                <div className="text-2xl font-bold text-slate-900 mt-1">37</div>
                <div className="text-xs text-slate-500 mt-1">Verified submissions</div>
              </div>
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <div className="text-xs font-medium text-slate-500">Credits Remaining</div>
                <div className="text-2xl font-bold text-indigo-600 mt-1">63</div>
                <div className="text-xs text-slate-500 mt-1">Free balance</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-24 border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center max-w-3xl mx-auto">
            <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-600">
              Structured Automation
            </h2>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">
              How the AI Agent Works in 4 Steps
            </p>
            <p className="mt-4 text-base text-slate-600">
              Full transparency, complete user control, and zero fake submissions.
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 text-white font-bold mb-4">
                1
              </div>
              <h3 className="text-lg font-bold text-slate-900">Upload & Parse</h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed">
                Upload your PDF or DOCX resume. Our parser extracts your skills,
                projects, and experience without inventing details.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 text-white font-bold mb-4">
                2
              </div>
              <h3 className="text-lg font-bold text-slate-900">Set Preferences</h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed">
                Define your minimum salary, maximum experience, target locations,
                and whether you require human review before submitting.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 text-white font-bold mb-4">
                3
              </div>
              <h3 className="text-lg font-bold text-slate-900">Discover & Match</h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed">
                The agent browses portal listings, reads real descriptions, and
                scores semantic match percentage against your profile.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 text-white font-bold mb-4">
                4
              </div>
              <h3 className="text-lg font-bold text-slate-900">Apply & Verify</h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed">
                Isolated browser sessions open eligible forms, fill your real
                answers, upload your resume, and record proof in your dashboard.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Sources Section */}
      <section id="sources" className="py-20 bg-slate-50 border-t border-slate-200">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-600">
            Multi-Source Integration
          </h2>
          <p className="mt-2 text-2xl font-bold text-slate-900 sm:text-3xl">
            Supported Job Platforms
          </p>

          <div className="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-6">
            <div className="flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="text-xl font-bold text-slate-800">LinkedIn</div>
              <span className="mt-2 text-xs text-emerald-600 font-medium">Easy Apply & Direct</span>
            </div>
            <div className="flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="text-xl font-bold text-slate-800">Naukri</div>
              <span className="mt-2 text-xs text-emerald-600 font-medium">Fast-Track Search</span>
            </div>
            <div className="flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="text-xl font-bold text-slate-800">Indeed</div>
              <span className="mt-2 text-xs text-emerald-600 font-medium">Verified Listings</span>
            </div>
            <div className="flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="text-xl font-bold text-slate-800">Company Portals</div>
              <span className="mt-2 text-xs text-emerald-600 font-medium">Workday / Greenhouse</span>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center max-w-3xl mx-auto">
            <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-600">
              Free + Pay-As-You-Go Credits
            </h2>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">
              Transparent, Zero-Commitment Pricing
            </p>
            <p className="mt-4 text-base text-slate-600">
              Start with 5 free application credits every month. Top up whenever you need more applications with zero subscriptions or recurring locks.
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 max-w-6xl mx-auto gap-6">
            {/* Free */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition flex flex-col justify-between">
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Free
                </div>
                <div className="mt-3 flex items-baseline gap-1">
                  <span className="text-3xl font-extrabold text-slate-900">₹0</span>
                  <span className="text-xs text-slate-500 uppercase">/ month</span>
                </div>
                <p className="mt-2 text-xs text-slate-600">
                  5 free applications per month. Free forever.
                </p>
                <ul className="mt-5 space-y-2.5 text-xs text-slate-700">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0" />
                    5 Applications / month
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0" />
                    Autonomous Form Agent
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0" />
                    Multi-Portal Discovery
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0" />
                    Auto-refund on challenge
                  </li>
                </ul>
              </div>
              <Link
                href="/register"
                className="mt-6 block w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 text-center text-xs font-semibold text-slate-900 hover:bg-slate-100 transition"
              >
                Start Free
              </Link>
            </div>

            {/* Starter Pack */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition flex flex-col justify-between">
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-indigo-600">
                  Starter Pack
                </div>
                <div className="mt-3 flex items-baseline gap-1">
                  <span className="text-3xl font-extrabold text-slate-900">₹149</span>
                  <span className="text-xs text-slate-400 uppercase">one-time</span>
                </div>
                <p className="mt-2 text-xs text-slate-600">
                  10 application credits for targeted outreach.
                </p>
                <ul className="mt-5 space-y-2.5 text-xs text-slate-700">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-indigo-600 flex-shrink-0" />
                    10 Application Credits
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-indigo-600 flex-shrink-0" />
                    Never expire
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-indigo-600 flex-shrink-0" />
                    Full LLM Form Answering
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-indigo-600 flex-shrink-0" />
                    Auto-refund on errors
                  </li>
                </ul>
              </div>
              <Link
                href="/register"
                className="mt-6 block w-full rounded-xl bg-slate-900 py-2.5 text-center text-xs font-semibold text-white hover:bg-black transition"
              >
                Get 10 Credits
              </Link>
            </div>

            {/* Job Seeker Pack */}
            <div className="relative rounded-2xl border-2 border-indigo-600 bg-white p-6 shadow-lg shadow-indigo-100 flex flex-col justify-between ring-2 ring-indigo-50">
              <div className="absolute -top-3 right-4 rounded-full bg-indigo-600 px-2.5 py-0.5 text-[10px] font-bold text-white uppercase tracking-wider">
                Most Popular
              </div>
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-indigo-600">
                  Job Seeker Pack
                </div>
                <div className="mt-3 flex items-baseline gap-1">
                  <span className="text-3xl font-extrabold text-slate-900">₹299</span>
                  <span className="text-xs text-slate-400 uppercase">one-time</span>
                </div>
                <p className="mt-2 text-xs text-slate-600">
                  25 application credits for active job hunters.
                </p>
                <ul className="mt-5 space-y-2.5 text-xs text-slate-700">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-indigo-600 flex-shrink-0" />
                    25 Application Credits
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-indigo-600 flex-shrink-0" />
                    Priority browser runner
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-indigo-600 flex-shrink-0" />
                    Cover Letter & Pitch Tuning
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-indigo-600 flex-shrink-0" />
                    Auto-refund on errors
                  </li>
                </ul>
              </div>
              <Link
                href="/register"
                className="mt-6 block w-full rounded-xl bg-indigo-600 py-2.5 text-center text-xs font-semibold text-white hover:bg-indigo-700 shadow-sm transition"
              >
                Get 25 Credits
              </Link>
            </div>

            {/* Power Pack */}
            <div className="relative rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 text-white p-6 shadow-lg flex flex-col justify-between">
              <div className="absolute -top-3 right-4 rounded-full bg-amber-400 px-2.5 py-0.5 text-[10px] font-extrabold text-slate-950 uppercase tracking-wider">
                Best Value
              </div>
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-amber-400">
                  Power Pack
                </div>
                <div className="mt-3 flex items-baseline gap-1">
                  <span className="text-3xl font-extrabold text-white">₹499</span>
                  <span className="text-xs text-slate-400 uppercase">one-time</span>
                </div>
                <p className="mt-2 text-xs text-slate-400">
                  50 application credits for high-volume campaigns.
                </p>
                <ul className="mt-5 space-y-2.5 text-xs text-slate-300">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-amber-400 flex-shrink-0" />
                    50 Application Credits
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-amber-400 flex-shrink-0" />
                    Lowest cost per application
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-amber-400 flex-shrink-0" />
                    Ultra-fast parallel matching
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-amber-400 flex-shrink-0" />
                    Instant Razorpay activation
                  </li>
                </ul>
              </div>
              <Link
                href="/register"
                className="mt-6 block w-full rounded-xl bg-amber-400 py-2.5 text-center text-xs font-bold text-slate-950 hover:bg-amber-300 transition"
              >
                Get 50 Credits
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 border-t border-slate-200 bg-slate-50">
        <div className="mx-auto max-w-4xl px-6">
          <h2 className="text-center text-3xl font-extrabold text-slate-900 mb-12">
            Frequently Asked Questions
          </h2>

          <div className="space-y-6">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-base font-bold text-slate-900">
                Does the agent attempt to bypass CAPTCHAs or Cloudflare?
              </h3>
              <p className="mt-2 text-sm text-slate-600">
                Never. In accordance with strict security standards, whenever a
                portal presents a CAPTCHA, OTP, or identity challenge, the
                application is marked as <strong>VERIFICATION_REQUIRED</strong>.
                Your credit is refunded automatically and the agent continues processing other eligible jobs.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-base font-bold text-slate-900">
                When are credits consumed?
              </h3>
              <p className="mt-2 text-sm text-slate-600">
                Exactly 1 credit is consumed ONLY when an application is actually processed and submitted to an employer portal.
                Job discovery, keyword matching, viewing postings, and account setup consume zero credits.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-base font-bold text-slate-900">
                How does user data isolation work?
              </h3>
              <p className="mt-2 text-sm text-slate-600">
                Every user has a dedicated database scope, an isolated resume
                storage vault, and an independent Playwright browser context.
                User A can never see or share cookies, credentials, or answers
                with User B.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-base font-bold text-slate-900">
                Can I require manual review before submitting?
              </h3>
              <p className="mt-2 text-sm text-slate-600">
                Yes! You can toggle "Require Human Review" in your preferences.
                Eligible jobs will pause in your Review Queue for your explicit
                one-click approval.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-12">
        <div className="mx-auto max-w-7xl px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Bot className="h-5 w-5 text-indigo-600" />
            &copy; 2026 AI Job Agent SaaS. All rights reserved. Secured by Razorpay.
          </div>
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-slate-600">
            <Link href="/terms" className="hover:text-indigo-600 transition">
              Terms & Conditions
            </Link>
            <Link href="/privacy" className="hover:text-indigo-600 transition">
              Privacy Policy
            </Link>
            <Link href="/refund-policy" className="hover:text-indigo-600 transition">
              Cancellation & Refund Policy
            </Link>
            <Link href="/contact" className="hover:text-indigo-600 transition">
              Contact Us
            </Link>
            <Link href="/login" className="hover:text-indigo-600 transition">
              Sign In
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
