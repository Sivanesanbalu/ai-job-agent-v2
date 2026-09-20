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
              Transparent Credit Model
            </h2>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">
              Simple, Pay-As-You-Apply Pricing
            </p>
            <p className="mt-4 text-base text-slate-600">
              Every user starts with 100 free applications. Top up anytime with transparent credit pricing.
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 md:grid-cols-2 max-w-4xl mx-auto gap-8">
            {/* Free Starter */}
            <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm hover:shadow-md transition">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Starter Tier
              </div>
              <div className="mt-4 flex items-baseline gap-2">
                <span className="text-4xl font-extrabold text-slate-900">₹0</span>
                <span className="text-sm text-slate-500">Free forever</span>
              </div>
              <p className="mt-3 text-sm text-slate-600">
                Everything you need to experience autonomous applications.
              </p>

              <ul className="mt-6 space-y-3 text-sm text-slate-700">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  100 Included Applications
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  PDF / DOCX Resume Parsing
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  AI Matching Engine
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  Real-Time Tracking Dashboard
                </li>
              </ul>

              <Link
                href="/register"
                className="mt-8 block w-full rounded-xl border border-slate-200 bg-slate-50 py-3 text-center text-sm font-semibold text-slate-900 hover:bg-slate-100 transition"
              >
                Sign Up & Claim 100 Credits
              </Link>
            </div>

            {/* Pro Booster */}
            <div className="relative rounded-2xl border-2 border-indigo-600 bg-white p-8 shadow-lg">
              <div className="absolute -top-3 right-6 rounded-full bg-indigo-600 px-3 py-1 text-xs font-bold text-white uppercase tracking-wider">
                Popular Booster
              </div>
              <div className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
                Additional Applications
              </div>
              <div className="mt-4 flex items-baseline gap-2">
                <span className="text-4xl font-extrabold text-slate-900">₹100</span>
                <span className="text-sm text-slate-500">/ 100 applications</span>
              </div>
              <p className="mt-3 text-sm text-slate-600">
                Just ₹1 per submitted application. Credits never expire.
              </p>

              <ul className="mt-6 space-y-3 text-sm text-slate-700">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-indigo-600" />
                  +100 Additional Auto Applications
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-indigo-600" />
                  Priority Browser Execution Queue
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-indigo-600" />
                  Multi-Resume Version Support
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-indigo-600" />
                  Credits refunded on failed submissions
                </li>
              </ul>

              <Link
                href="/register"
                className="mt-8 block w-full rounded-xl bg-indigo-600 py-3 text-center text-sm font-semibold text-white shadow-md hover:bg-indigo-700 transition"
              >
                Get Started
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
                The agent alerts you and continues processing other eligible jobs.
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
        <div className="mx-auto max-w-7xl px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Bot className="h-5 w-5 text-indigo-600" />
            &copy; 2026 AI Job Agent SaaS. All rights reserved.
          </div>
          <div className="flex gap-6 text-sm text-slate-500">
            <Link href="/login" className="hover:text-slate-900">
              Sign In
            </Link>
            <Link href="/register" className="hover:text-slate-900">
              Register
            </Link>
            <a href="#privacy" className="hover:text-slate-900">
              Privacy Policy
            </a>
            <a href="#terms" className="hover:text-slate-900">
              Terms of Service
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
