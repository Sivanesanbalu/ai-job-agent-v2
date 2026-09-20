"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { ConnectedAccount } from "@/types";
import { 
  ShieldCheck, Lock, CheckCircle2, AlertCircle, 
  ExternalLink, Key, Trash2, Plus, RefreshCw, AlertTriangle
} from "lucide-react";

const SUPPORTED_PLATFORMS = [
  {
    id: "linkedin",
    name: "LinkedIn",
    description: "Supports Easy Apply and external company career page submissions.",
    icon: "💼",
    color: "blue",
  },
  {
    id: "naukri",
    name: "Naukri",
    description: "Supports FastForward one-click applications across India & GCC.",
    icon: "🇮🇳",
    color: "emerald",
  },
  {
    id: "indeed",
    name: "Indeed",
    description: "Automated Indeed Apply flow with resume and screening question sync.",
    icon: "🌐",
    color: "indigo",
  },
  {
    id: "generic",
    name: "Workday / Greenhouse / Lever",
    description: "Direct enterprise career portals and ATS systems.",
    icon: "🏢",
    color: "slate",
  },
];

export default function ConnectedAccountsPage() {
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Modal / Form state for connecting a portal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState("linkedin");
  const [accountIdentifier, setAccountIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const data = await api.connectedAccounts.list();
      setAccounts(data);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load connected portal accounts.");
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accountIdentifier.trim()) return;

    setSubmitting(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const newAcc = await api.connectedAccounts.connect({
        platform: selectedPlatform,
        account_identifier: accountIdentifier.trim(),
        credentials: { password },
      });
      setAccounts((prev) => [...prev.filter((a) => a.platform !== selectedPlatform), newAcc]);
      setSuccessMessage(`Successfully connected ${selectedPlatform} account!`);
      setIsModalOpen(false);
      setAccountIdentifier("");
      setPassword("");
      setTimeout(() => setSuccessMessage(""), 4000);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to connect portal account.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDisconnect = async (id: number, platform: string) => {
    if (!confirm(`Are you sure you want to disconnect ${platform}? Active browser sessions will be cleared.`)) {
      return;
    }

    try {
      await api.connectedAccounts.disconnect(id);
      setAccounts((prev) => prev.filter((a) => a.id !== id));
      setSuccessMessage(`Disconnected ${platform} successfully.`);
      setTimeout(() => setSuccessMessage(""), 4000);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to disconnect account.");
    }
  };

  const getAccountForPlatform = (platformId: string) => {
    return accounts.find((a) => a.platform.toLowerCase() === platformId.toLowerCase());
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
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Job Portal Integrations & Sessions</h1>
        <p className="text-sm text-slate-500 mt-1">
          Connect your portal logins so the autonomous browser agent can discover jobs and submit applications on your behalf.
        </p>
      </div>

      {/* Zero Leakage Security Guarantee Banner */}
      <div className="rounded-2xl border border-indigo-100 bg-gradient-to-r from-indigo-50/70 via-blue-50/50 to-white p-5 shadow-xs">
        <div className="flex items-start gap-3.5">
          <div className="p-2.5 bg-white rounded-xl shadow-xs border border-indigo-100 text-indigo-600">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-slate-900">100% Isolated Browser Storage Guarantee</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Every user operates in a strictly isolated sandbox. Your browser session storage, persistent cookies, and cached portal logins are maintained in your private user path (<code className="bg-white/80 px-1 py-0.5 rounded text-indigo-700 font-mono text-[11px]">data/browser_sessions/{`{user_id}`}</code>). No credentials or cookies are ever shared or accessible across users.
            </p>
          </div>
        </div>
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

      {/* Platform Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {SUPPORTED_PLATFORMS.map((platform) => {
          const connected = getAccountForPlatform(platform.id);
          const isConnected = !!connected;
          const needsLogin = connected?.auth_status === "login_required" || connected?.auth_status === "reauth_required";

          return (
            <div
              key={platform.id}
              className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{platform.icon}</span>
                    <div>
                      <h3 className="text-base font-semibold text-slate-900">{platform.name}</h3>
                      <p className="text-xs text-slate-500">{platform.description}</p>
                    </div>
                  </div>
                </div>

                {/* Status indicator */}
                <div className="my-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500">Integration Status</span>
                  {isConnected ? (
                    needsLogin ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                        <AlertTriangle className="h-3.5 w-3.5" /> Action Required
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle2 className="h-3.5 w-3.5" /> Connected & Active
                      </span>
                    )
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600">
                      Not Configured
                    </span>
                  )}
                </div>

                {isConnected && (
                  <div className="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1">
                    <p><strong className="text-slate-700">Account:</strong> {connected.account_identifier}</p>
                    {connected.last_verified_at && (
                      <p className="text-slate-400 text-[11px]">
                        Last verified: {new Date(connected.last_verified_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-end gap-3">
                {isConnected ? (
                  <>
                    <button
                      type="button"
                      onClick={() => handleDisconnect(connected.id, platform.name)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-rose-600 hover:bg-rose-50 transition"
                    >
                      <Trash2 className="h-3.5 w-3.5" /> Disconnect
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedPlatform(platform.id);
                        setAccountIdentifier(connected.account_identifier);
                        setIsModalOpen(true);
                      }}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 transition"
                    >
                      <RefreshCw className="h-3.5 w-3.5" /> Re-authenticate
                    </button>
                  </>
                ) : (
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedPlatform(platform.id);
                      setAccountIdentifier("");
                      setPassword("");
                      setIsModalOpen(true);
                    }}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-xs font-semibold text-white shadow-xs transition"
                  >
                    <Plus className="h-4 w-4" /> Connect {platform.name}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Connect Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl border border-slate-200 space-y-5 animate-scale-in">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                Connect {SUPPORTED_PLATFORMS.find((p) => p.id === selectedPlatform)?.name}
              </h3>
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleConnect} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Username / Email ID *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. john@example.com"
                  value={accountIdentifier}
                  onChange={(e) => setAccountIdentifier(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Portal Password / Session Token
                </label>
                <input
                  type="password"
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Encrypted using AES-256 before disk storage. Used solely by your sandboxed Playwright session.
                </p>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs disabled:opacity-50"
                >
                  {submitting ? "Connecting..." : "Confirm & Connect"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
