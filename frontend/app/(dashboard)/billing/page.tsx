"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api/client";
import { Plan } from "@/types";
import { 
  Check, Zap, Shield, Sparkles, CreditCard, 
  CheckCircle2, AlertCircle, ArrowRight, RefreshCw, Lock
} from "lucide-react";

declare global {
  interface Window {
    Razorpay: any;
  }
}

export default function BillingPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingSlug, setProcessingSlug] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchBillingData();
    loadRazorpayScript();
  }, []);

  const loadRazorpayScript = (): Promise<boolean> => {
    return new Promise((resolve) => {
      if (typeof window === "undefined") return resolve(false);
      if (window.Razorpay) return resolve(true);

      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.async = true;
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

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

  const handleSelectPack = async (plan: Plan) => {
    if (plan.price_inr === 0) {
      return; // Free plan is already default
    }

    try {
      setProcessingSlug(plan.slug);
      setErrorMessage("");
      setSuccessMessage("");

      // 1. Create Razorpay order on backend
      const order = await api.billing.createRazorpayOrder(plan.slug);

      // 2. Ensure Razorpay checkout script is loaded
      const isLoaded = await loadRazorpayScript();
      if (!isLoaded && !window.Razorpay) {
        throw new Error("Unable to load Razorpay payment SDK. Please check your network connection.");
      }

      // 3. Open Razorpay Checkout modal
      const options = {
        key: order.key_id || "rzp_test_placeholder",
        amount: order.amount,
        currency: order.currency || "INR",
        name: "AI Job Agent",
        description: `${order.plan_name} (${order.credits} Application Credits)`,
        order_id: order.order_id,
        prefill: {
          name: order.user_name || "Job Seeker",
          email: order.user_email || "",
          contact: order.user_phone || "+918438692752",
        },
        theme: {
          color: "#4f46e5",
        },
        handler: async function (response: any) {
          try {
            setProcessingSlug(plan.slug);
            // 4. Send payment response to backend for cryptographic HMAC verification
            const verifyRes = await api.billing.verifyRazorpayPayment({
              razorpay_order_id: response.razorpay_order_id || order.order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });

            setSuccessMessage(
              verifyRes.message || `Payment verified! +${verifyRes.credits_granted} credits added to your account.`
            );
            await fetchBillingData();
            setTimeout(() => setSuccessMessage(""), 7000);
          } catch (verifyErr: any) {
            setErrorMessage(verifyErr.message || "Cryptographic payment verification failed.");
          } finally {
            setProcessingSlug(null);
          }
        },
        modal: {
          ondismiss: function () {
            setProcessingSlug(null);
          },
        },
      };

      if (window.Razorpay) {
        const rzp = new window.Razorpay(options);
        rzp.on("payment.failed", function (resp: any) {
          setErrorMessage(resp.error?.description || "Payment failed at gateway.");
          setProcessingSlug(null);
        });
        rzp.open();
      } else {
        // Fallback for simulated test environments
        const mockSig = `test_sig_${order.order_id}`;
        const mockPaymentId = `pay_sim_${Date.now()}`;
        const verifyRes = await api.billing.verifyRazorpayPayment({
          razorpay_order_id: order.order_id,
          razorpay_payment_id: mockPaymentId,
          razorpay_signature: mockSig,
        });
        setSuccessMessage(verifyRes.message || "Test order verified successfully!");
        await fetchBillingData();
        setProcessingSlug(null);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Unable to initiate Razorpay checkout.");
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
    <div className="max-w-6xl space-y-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-xs font-semibold text-indigo-700 mb-2">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
            <span>Pay-As-You-Go Credits</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
            Application Credits & Top-Up Packs
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Free users get 5 credits monthly. Top up whenever you need more applications with zero recurring commitments.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/credits"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 shadow-xs transition"
          >
            <RefreshCw className="h-3.5 w-3.5 text-slate-500" />
            View Balance Ledger
          </Link>
        </div>
      </div>

      {successMessage && (
        <div className="flex items-center gap-2.5 rounded-2xl bg-emerald-50 border border-emerald-200 p-4 text-emerald-800 text-sm shadow-xs">
          <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-emerald-600" />
          <span className="font-medium">{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-2.5 rounded-2xl bg-rose-50 border border-rose-200 p-4 text-rose-800 text-sm shadow-xs">
          <AlertCircle className="h-5 w-5 flex-shrink-0 text-rose-600" />
          <span className="font-medium">{errorMessage}</span>
        </div>
      )}

      {/* Plan Cards Grid: 4 Packs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {plans.map((plan) => {
          const isFree = plan.price_inr === 0;
          const isPopular = plan.slug === "job_seeker_pack";
          const isPower = plan.slug === "power_pack";

          return (
            <div
              key={plan.id}
              className={`rounded-3xl p-6 flex flex-col justify-between transition relative ${
                isPopular
                  ? "bg-white border-2 border-indigo-600 shadow-xl shadow-indigo-100 ring-4 ring-indigo-50"
                  : isPower
                  ? "bg-gradient-to-b from-slate-900 to-slate-950 text-white border border-slate-800 shadow-lg"
                  : "bg-white border border-slate-200 shadow-xs hover:border-slate-300"
              }`}
            >
              {isPopular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-indigo-600 text-white text-[10px] font-bold uppercase tracking-wider shadow-sm">
                  Most Popular
                </div>
              )}

              {isPower && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-amber-400 text-slate-950 text-[10px] font-extrabold uppercase tracking-wider shadow-sm">
                  Best Value
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <h3 className={`text-base font-bold ${isPower ? "text-white" : "text-slate-900"}`}>
                    {plan.name}
                  </h3>
                  <p className={`text-xs mt-1 ${isPower ? "text-slate-400" : "text-slate-500"}`}>
                    {isFree ? "Default free allowance" : `${plan.included_applications} application credits`}
                  </p>
                </div>

                <div className="flex items-baseline gap-1 py-1">
                  <span className={`text-3xl font-extrabold tracking-tight ${isPower ? "text-white" : "text-slate-900"}`}>
                    ₹{plan.price_inr}
                  </span>
                  <span className={`text-xs font-medium uppercase ${isPower ? "text-slate-400" : "text-slate-400"}`}>
                    {isFree ? "/ month" : "one-time"}
                  </span>
                </div>

                <div className={`p-3 rounded-xl flex items-center gap-2.5 text-xs font-semibold ${
                  isPower 
                    ? "bg-slate-800/80 border border-slate-700 text-amber-300" 
                    : isPopular 
                    ? "bg-indigo-50 border border-indigo-100 text-indigo-900" 
                    : "bg-slate-50 border border-slate-100 text-slate-700"
                }`}>
                  <Sparkles className={`h-4 w-4 flex-shrink-0 ${isPower ? "text-amber-400" : "text-indigo-600"}`} />
                  <span>
                    {isFree ? "5 Free Monthly Applications" : `${plan.included_applications} Application Credits`}
                  </span>
                </div>

                <div className={`space-y-2 pt-3 border-t ${isPower ? "border-slate-800" : "border-slate-100"}`}>
                  <p className={`text-[11px] font-bold uppercase tracking-wider ${isPower ? "text-slate-300" : "text-slate-700"}`}>
                    Included:
                  </p>
                  {(plan.features as string[] || []).map((feat, idx) => (
                    <div key={idx} className={`flex items-start gap-2 text-xs ${isPower ? "text-slate-300" : "text-slate-600"}`}>
                      <Check className={`h-3.5 w-3.5 flex-shrink-0 mt-0.5 ${isPower ? "text-emerald-400" : "text-indigo-600"}`} />
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-6">
                <button
                  type="button"
                  disabled={processingSlug === plan.slug || isFree}
                  onClick={() => handleSelectPack(plan)}
                  className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold tracking-wide transition flex items-center justify-center gap-2 ${
                    isFree
                      ? "bg-slate-100 text-slate-400 cursor-default"
                      : isPower
                      ? "bg-amber-400 hover:bg-amber-300 text-slate-950 shadow-sm shadow-amber-400/20 disabled:opacity-50"
                      : isPopular
                      ? "bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm shadow-indigo-300 disabled:opacity-50"
                      : "bg-slate-900 hover:bg-black text-white disabled:opacity-50"
                  }`}
                >
                  {processingSlug === plan.slug ? (
                    <span className="flex items-center gap-2">
                      <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                      Connecting Razorpay...
                    </span>
                  ) : isFree ? (
                    "Active Default Plan"
                  ) : (
                    <>
                      Pay ₹{plan.price_inr} via Razorpay <ArrowRight className="h-3.5 w-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Security & Gateway Badges */}
      <div className="rounded-2xl border border-slate-200/80 bg-slate-50/50 p-5">
        <div className="flex flex-wrap items-center justify-center gap-8 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <Lock className="h-4 w-4 text-emerald-600" />
            <span>Razorpay 256-bit Encrypted Checkout</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-indigo-600" />
            <span>Instant Cryptographic Credit Fulfillment</span>
          </div>
          <div className="flex items-center gap-2">
            <CreditCard className="h-4 w-4 text-slate-600" />
            <span>UPI, Google Pay, PhonePe, Cards & NetBanking</span>
          </div>
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-blue-600" />
            <span>Deducted Only on Actual Submitted Application</span>
          </div>
        </div>
      </div>

      {/* Transaction / Invoice Ledger */}
      <div className="rounded-2xl border border-slate-200/80 bg-white shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Payment & Credit Invoices</h2>
            <p className="text-xs text-slate-500 mt-0.5">Auditable records of purchases verified via Razorpay</p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-100">
              <tr>
                <th className="px-5 py-3 font-semibold">Date</th>
                <th className="px-5 py-3 font-semibold">Description</th>
                <th className="px-5 py-3 font-semibold">Razorpay Order / ID</th>
                <th className="px-5 py-3 font-semibold">Status</th>
                <th className="px-5 py-3 font-semibold">Credits</th>
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
                      {inv.plan_name || "Credit Pack"}
                    </td>
                    <td className="px-5 py-3.5 text-xs font-mono text-slate-500">
                      {inv.razorpay_payment_id || inv.razorpay_order_id || inv.provider_tx_id || "—"}
                    </td>
                    <td className="px-5 py-3.5 text-xs">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                        inv.status === "completed" || inv.status === "paid"
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          : inv.status === "pending"
                          ? "bg-amber-50 text-amber-700 border border-amber-200"
                          : "bg-rose-50 text-rose-700 border border-rose-200"
                      }`}>
                        {inv.status || "Completed"}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-xs font-bold text-indigo-600">
                      +{inv.credits_granted ?? 0}
                    </td>
                    <td className="px-5 py-3.5 text-xs font-bold text-slate-900 text-right">
                      ₹{inv.amount_inr ?? 0}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-xs text-slate-400">
                    No payment transactions recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Razorpay Merchant Compliance Footer */}
      <div className="pt-6 border-t border-slate-200 text-center space-y-2">
        <p className="text-xs text-slate-500">
          Payments are securely processed by Razorpay Payments India Pvt Ltd.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4 text-xs font-medium text-slate-600">
          <Link href="/terms" className="hover:text-indigo-600 hover:underline">
            Terms & Conditions
          </Link>
          <span>•</span>
          <Link href="/privacy" className="hover:text-indigo-600 hover:underline">
            Privacy Policy
          </Link>
          <span>•</span>
          <Link href="/refund-policy" className="hover:text-indigo-600 hover:underline">
            Cancellation & Refund Policy
          </Link>
          <span>•</span>
          <Link href="/contact" className="hover:text-indigo-600 hover:underline">
            Contact Us
          </Link>
        </div>
      </div>
    </div>
  );
}
