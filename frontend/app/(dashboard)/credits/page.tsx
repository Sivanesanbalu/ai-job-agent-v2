"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api/client";
import { CreditBalance, CreditTransaction } from "@/types";
import { 
  Coins, ArrowUpRight, ArrowDownLeft, RefreshCcw, 
  Sparkles, History, ShieldCheck, CreditCard
} from "lucide-react";

export default function CreditsPage() {
  const [balance, setBalance] = useState<CreditBalance | null>(null);
  const [transactions, setTransactions] = useState<CreditTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchCreditsData();
  }, []);

  const fetchCreditsData = async () => {
    try {
      setLoading(true);
      const [bal, txs] = await Promise.all([
        api.credits.getBalance(),
        api.credits.getTransactions(),
      ]);
      setBalance(bal);
      setTransactions(txs);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load credits ledger.");
    } finally {
      setLoading(false);
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
    <div className="max-w-5xl space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Credit Balance & Ledger</h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time auditable balance. 1 credit is deducted per qualified application. Failed applications are refunded atomically.
          </p>
        </div>
        <Link
          href="/billing"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold shadow-sm shadow-indigo-200 transition"
        >
          <CreditCard className="h-4 w-4" />
          Add Credits / Upgrade
        </Link>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm">
          {errorMessage}
        </div>
      )}

      {/* Credit Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-indigo-200/80 bg-gradient-to-br from-indigo-50/50 to-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-indigo-600 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-900">Available Balance</span>
            <Coins className="h-5 w-5" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
            {balance?.balance ?? 0}
          </div>
          <p className="text-xs text-slate-500 mt-1">Ready for automated applications</p>
        </div>

        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Free Allowance</span>
            <Sparkles className="h-5 w-5 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 tracking-tight">
            {balance?.total_included ?? 5}
          </div>
          <p className="text-xs text-slate-400 mt-1">5 credits renewed monthly</p>
        </div>

        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Purchased Credits</span>
            <ArrowUpRight className="h-5 w-5 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 tracking-tight">
            {balance?.total_purchased ?? 0}
          </div>
          <p className="text-xs text-slate-400 mt-1">Via plan boosters</p>
        </div>

        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Total Utilized</span>
            <ArrowDownLeft className="h-5 w-5 text-rose-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 tracking-tight">
            {balance?.total_used ?? 0}
          </div>
          <p className="text-xs text-slate-400 mt-1">Successfully applied</p>
        </div>
      </div>

      {/* Transparent Guarantee Card */}
      <div className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 flex items-center gap-3 text-xs text-slate-600">
        <ShieldCheck className="h-5 w-5 text-indigo-600 flex-shrink-0" />
        <span>
          <strong>Zero Waste Guarantee:</strong> If an application is halted due to a portal safety challenge (CAPTCHA, 2FA) or submission error, your credit is immediately unlocked and returned to your balance.
        </span>
      </div>

      {/* Transaction History Table */}
      <div className="rounded-2xl border border-slate-200/80 bg-white shadow-sm overflow-hidden">
        <div className="flex items-center justify-between p-5 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <History className="h-5 w-5 text-slate-500" />
            <h2 className="text-base font-semibold text-slate-900">Ledger Activity & Deductions</h2>
          </div>
          <button
            onClick={fetchCreditsData}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 transition"
          >
            <RefreshCcw className="h-4 w-4" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-100">
              <tr>
                <th className="px-5 py-3 font-semibold">Date & Time</th>
                <th className="px-5 py-3 font-semibold">Transaction Type</th>
                <th className="px-5 py-3 font-semibold">Description</th>
                <th className="px-5 py-3 font-semibold text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {transactions.length > 0 ? (
                transactions.map((tx) => {
                  const isPositive = tx.amount > 0;
                  return (
                    <tr key={tx.id} className="hover:bg-slate-50/60 transition">
                      <td className="px-5 py-3.5 text-xs text-slate-500 whitespace-nowrap">
                        {new Date(tx.created_at).toLocaleString()}
                      </td>
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                          tx.type.includes("bonus") || tx.type.includes("purchase") || tx.type.includes("grant")
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : tx.type.includes("refund")
                            ? "bg-blue-50 text-blue-700 border border-blue-200"
                            : "bg-slate-100 text-slate-700"
                        }`}>
                          {tx.type.replace(/_/g, " ")}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-xs text-slate-700">
                        {tx.description || "Credit transaction"}
                      </td>
                      <td className="px-5 py-3.5 text-xs font-bold text-right whitespace-nowrap">
                        <span className={isPositive ? "text-emerald-600" : "text-rose-600"}>
                          {isPositive ? `+${tx.amount}` : tx.amount} credits
                        </span>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={4} className="px-5 py-8 text-center text-xs text-slate-400">
                    No transactions recorded yet.
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
