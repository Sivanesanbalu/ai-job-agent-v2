import React from "react";
import Link from "next/link";
import { Bot, ArrowLeft, Mail, Phone, MapPin, Clock, ShieldCheck } from "lucide-react";

export const metadata = {
  title: "Contact Us - JobAgent.ai",
  description: "Get in touch with the JobAgent.ai customer support team.",
};

export default function ContactPage() {
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
        <div className="rounded-3xl border border-slate-200 bg-white p-8 sm:p-12 shadow-xs space-y-10">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">Help & Support</span>
            <h1 className="text-3xl font-extrabold text-slate-900 mt-1">Contact Us</h1>
            <p className="text-sm text-slate-500 mt-2">
              Have questions about your credits, billing, or job automation? Our dedicated support team is here to help.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl border border-slate-100 bg-slate-50/60 flex items-start gap-4">
              <div className="h-10 w-10 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center flex-shrink-0">
                <Mail className="h-5 w-5" />
              </div>
              <div className="space-y-1 text-sm">
                <h3 className="font-bold text-slate-900">Email Support</h3>
                <p className="text-xs text-slate-500">For inquiries, billing issues, and technical support:</p>
                <p className="font-semibold text-indigo-600">support@jobagent.ai</p>
                <p className="text-xs text-slate-600 font-mono">apsiva69@gmail.com</p>
              </div>
            </div>

            <div className="p-6 rounded-2xl border border-slate-100 bg-slate-50/60 flex items-start gap-4">
              <div className="h-10 w-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0">
                <Phone className="h-5 w-5" />
              </div>
              <div className="space-y-1 text-sm">
                <h3 className="font-bold text-slate-900">Phone & WhatsApp</h3>
                <p className="text-xs text-slate-500">Direct phone support & merchant assistance:</p>
                <p className="font-semibold text-slate-900">+91 84386 92752</p>
                <p className="text-xs text-slate-500">Mon - Sat: 9:00 AM - 7:00 PM IST</p>
              </div>
            </div>

            <div className="p-6 rounded-2xl border border-slate-100 bg-slate-50/60 flex items-start gap-4">
              <div className="h-10 w-10 rounded-xl bg-violet-100 text-violet-700 flex items-center justify-center flex-shrink-0">
                <MapPin className="h-5 w-5" />
              </div>
              <div className="space-y-1 text-sm">
                <h3 className="font-bold text-slate-900">Operating Address</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  JobAgent.ai Developer Operations<br />
                  Coimbatore, Tamil Nadu, India - 623707
                </p>
              </div>
            </div>

            <div className="p-6 rounded-2xl border border-slate-100 bg-slate-50/60 flex items-start gap-4">
              <div className="h-10 w-10 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center flex-shrink-0">
                <Clock className="h-5 w-5" />
              </div>
              <div className="space-y-1 text-sm">
                <h3 className="font-bold text-slate-900">Resolution SLA</h3>
                <p className="text-xs text-slate-500">Average response times:</p>
                <p className="text-xs font-semibold text-slate-800">Email: Under 4 hours</p>
                <p className="text-xs font-semibold text-slate-800">Refund processing: 24 to 48 hours</p>
              </div>
            </div>
          </div>

          <div className="p-5 rounded-2xl border border-indigo-100 bg-indigo-50/50 flex items-center gap-3 text-xs text-indigo-950">
            <ShieldCheck className="h-5 w-5 text-indigo-600 flex-shrink-0" />
            <span>
              All digital payment transactions are authenticated and processed under Indian banking standards by Razorpay.
            </span>
          </div>
        </div>
      </main>
    </div>
  );
}
