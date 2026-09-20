"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Plan } from "@/types";
import { 
  Check, Zap, Shield, Sparkles, CreditCard, 
  CheckCircle2, AlertCircle, ArrowRight
} from "lucide-react";

export default function BillingPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingSlug, setProcessingSlug] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    try {
      setLoading(true);
      const [plansData, historyData] = await Promise.all([
        api.billing.getPlans(),
        api.billing.getHistory(),
      ]);
      setPlans(plansData);
      setHistory(historyData);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load subscription plans.");
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async (slug: string) => {
    try {
      setProcessingSlug(slug);
      setErrorMessage("");
      setSuccessMessage("");
      const res = await api.billing.checkout(slug);
      setSuccessMessage(res.message || `Successfully activated plan ${slug}!`);
      await fetchBillingData();
      setTimeout(() => setSuccessMessage(""), 5000);
    } catch (err: any) {
      setErrorMessage(err.message || "Payment checkout failed.");
    } finally {
      setProcessingSlug(null);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl space-y-10">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Subscription & Credit Top-ups</h1>
        <p className="text-sm text-slate-500 mt-1">
          Scale your job hunt with higher application limits, automated background workers, and priority LLM matching.
        </p>
      </div>

      {successMessage && (
        <div className="flex items-center gap-2 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-emerald-800 text-sm">
          <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-emerald-600" />
          <span>{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-2 rounded-xl bg-rose-50 border border-rose-200 p-4 text-rose-800 text-sm">
          <AlertCircle className="h-5 w-5 flex-shrink-0 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Plan Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => {
          const isPro = plan.slug === "pro_booster";
          const isFree = plan.price_inr === 0;

          return (
            <div
              key={plan.id}
              className={`rounded-3xl p-7 flex flex-col justify-between transition relative ${
                isPro
                  ? "bg-white border-2 border-indigo-600 shadow-xl shadow-indigo-100 ring-4 ring-indigo-50"
                  : "bg-white border border-slate-200 shadow-xs"
              }`}
            >
              {isPro && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3.5 py-1 rounded-full bg-indigo-600 text-white text-[11px] font-bold uppercase tracking-wider shadow-sm">
                  Most Popular
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">{plan.name}</h3>
                  <p className="text-xs text-slate-500 mt-1">{plan.name} package</p>
                </div>

                <div className="flex items-baseline gap-1 py-2">
                  <span className="text-4xl font-extrabold text-slate-900 tracking-tight">
                    ₹{plan.price_inr}
                  </span>
                  <span className="text-xs font-semibold text-slate-400 uppercase">
                    / one-time
                  </span>
                </div>

                <div className="p-3.5 rounded-2xl bg-indigo-50/50 border border-indigo-100 flex items-center gap-3 text-xs text-indigo-900 font-semibold">
                  <Sparkles className="h-4 w-4 text-indigo-600 flex-shrink-0" />
                  <span>{plan.included_applications} Guaranteed Application Credits</span>
                </div>

                <div className="space-y-2.5 pt-3 border-t border-slate-100">
                  <p className="text-xs font-bold text-slate-700 uppercase tracking-wider">Features Included:</p>
                  {(plan.features as string[] || []).map((feat, idx) => (
                    <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-600">
                      <Check className="h-4 w-4 text-indigo-600 flex-shrink-0 mt-0.5" />
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-8">
                <button
                  type="button"
                  disabled={processingSlug === plan.slug || isFree}
                  onClick={() => handleCheckout(plan.slug)}
                  className={`w-full py-3 px-4 rounded-xl text-xs font-bold tracking-wide transition flex items-center justify-center gap-2 ${
                    isPro
                      ? "bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm shadow-indigo-300 disabled:opacity-50"
                      : isFree
                      ? "bg-slate-100 text-slate-500 cursor-default"
                      : "bg-slate-900 hover:bg-black text-white disabled:opacity-50"
                  }`}
                >
                  {processingSlug === plan.slug ? (
                    "Processing..."
                  ) : isFree ? (
                    "Current Default Plan"
                  ) : (
                    <>
                      Activate {plan.name} <ArrowRight className="h-3.5 w-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Payment Security Footer */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-6 py-4 text-xs text-slate-400">
        <div className="flex items-center gap-1.5">
          <Shield className="h-4 w-4 text-emerald-500" />
          <span>256-bit Encrypted Payment Gateway</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Zap className="h-4 w-4 text-indigo-500" />
          <span>Instant Credit Allocation</span>
        </div>
        <div className="flex items-center gap-1.5">
          <CreditCard className="h-4 w-4 text-slate-500" />
          <span>Supports International Cards & UPI</span>
        </div>
      </div>

      {/* Invoicing / Billing History */}
      <div className="rounded-2xl border border-slate-200/80 bg-white shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100">
          <h2 className="text-base font-semibold text-slate-900">Billing History & Invoices</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-100">
              <tr>
                <th className="px-5 py-3 font-semibold">Date</th>
                <th className="px-5 py-3 font-semibold">Plan Description</th>
                <th className="px-5 py-3 font-semibold">Status</th>
                <th className="px-5 py-3 font-semibold text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {history.length > 0 ? (
                history.map((inv) => (
                  <tr key={inv.id} className="hover:bg-slate-50/60 transition">
                    <td className="px-5 py-3.5 text-xs text-slate-500">
                      {new Date(inv.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-3.5 text-xs font-medium text-slate-800">
                      {inv.plan_name || "Plan Subscription"}
                    </td>
                    <td className="px-5 py-3.5 text-xs">
                      <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {inv.status || "Paid"}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-xs font-bold text-slate-900 text-right">
                      ₹{inv.amount_inr ?? 0}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-5 py-8 text-center text-xs text-slate-400">
                    No billing transactions yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
