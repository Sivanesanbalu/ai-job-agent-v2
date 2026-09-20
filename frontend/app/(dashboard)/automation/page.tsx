"use client";

import React, { useState, useEffect } from "react";
import {
  Zap,
  Play,
  Pause,
  Square,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Layers,
  ShieldAlert,
  Loader2,
  Coins,
} from "lucide-react";
import { api } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/AuthContext";
import { AutomationStatus } from "@/types";

export default function AutomationCockpitPage() {
  const { creditsRemaining, refreshUserData } = useAuth();
  const [status, setStatus] = useState<AutomationStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const data = await api.automation.getStatus();
      setStatus(data);
    } catch (err) {
      console.error("Failed to fetch automation status:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleAction = async (action: "start" | "pause" | "resume" | "stop") => {
    setActionLoading(true);
    try {
      if (action === "start") await api.automation.start();
      else if (action === "pause") await api.automation.pause();
      else if (action === "resume") await api.automation.resume();
      else if (action === "stop") await api.automation.stop();
      await fetchStatus();
      await refreshUserData();
    } catch (err) {
      console.error(`Failed action ${action}:`, err);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Cockpit Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Agent Automation Cockpit
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Live browser automation engine, background queues, and safety boundaries.
          </p>
        </div>

        {/* Master Controls */}
        <div className="flex items-center gap-3">
          {status?.is_running ? (
            <>
              {status.status === "paused" ? (
                <button
                  onClick={() => handleAction("resume")}
                  disabled={actionLoading}
                  className="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-amber-700 transition"
                >
                  <Play className="h-4 w-4 fill-white" />
                  Resume
                </button>
              ) : (
                <button
                  onClick={() => handleAction("pause")}
                  disabled={actionLoading}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition"
                >
                  <Pause className="h-4 w-4" />
                  Pause
                </button>
              )}
              <button
                onClick={() => handleAction("stop")}
                disabled={actionLoading}
                className="inline-flex items-center gap-2 rounded-xl bg-rose-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-rose-700 transition"
              >
                <Square className="h-4 w-4 fill-white" />
                Stop Agent
              </button>
            </>
          ) : (
            <button
              onClick={() => handleAction("start")}
              disabled={actionLoading}
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-md hover:bg-indigo-700 transition"
            >
              <Play className="h-4 w-4 fill-white" />
              Launch Automation
            </button>
          )}
        </div>
      </div>

      {/* Main Status Cockpit Card */}
      <div className="rounded-2xl border border-indigo-100 bg-white p-8 shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 pb-6 mb-6">
          <div className="flex items-center gap-4">
            <div
              className={`flex h-14 w-14 items-center justify-center rounded-2xl ${
                status?.is_running
                  ? status.status === "paused"
                    ? "bg-amber-100 text-amber-700"
                    : "bg-indigo-600 text-white animate-pulse"
                  : "bg-slate-100 text-slate-500"
              }`}
            >
              <Zap className="h-7 w-7" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-bold text-slate-900">
                  {status?.is_running
                    ? status.status === "paused"
                      ? "Automation Paused"
                      : "Automation Active & Processing"
                    : "Automation Stopped"}
                </h2>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wider ${
                    status?.is_running
                      ? status.status === "paused"
                        ? "bg-amber-50 text-amber-800 border border-amber-200"
                        : "bg-emerald-50 text-emerald-800 border border-emerald-200"
                      : "bg-slate-100 text-slate-600 border border-slate-200"
                  }`}
                >
                  {status?.status || "idle"}
                </span>
              </div>
              <p className="mt-1 text-sm font-medium text-slate-600">
                {status?.current_action || "Awaiting command to start autonomous pipeline."}
              </p>
            </div>
          </div>

          <div className="hidden sm:flex flex-col items-end">
            <span className="text-xs text-slate-400">Application Balance</span>
            <div className="flex items-center gap-1.5 text-lg font-bold text-indigo-700 mt-0.5">
              <Coins className="h-4 w-4 text-indigo-600" />
              {creditsRemaining} Available
            </div>
          </div>
        </div>

        {/* Live Counters */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
            <div className="text-xs font-medium text-slate-500">Jobs Discovered</div>
            <div className="text-2xl font-extrabold text-slate-900 mt-1">
              {status?.jobs_discovered || 0}
            </div>
          </div>

          <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
            <div className="text-xs font-medium text-slate-500">Descriptions Analyzed</div>
            <div className="text-2xl font-extrabold text-slate-900 mt-1">
              {status?.jobs_analyzed || 0}
            </div>
          </div>

          <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
            <div className="text-xs font-medium text-slate-500">AI Matched</div>
            <div className="text-2xl font-extrabold text-indigo-600 mt-1">
              {status?.jobs_matched || 0}
            </div>
          </div>

          <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
            <div className="text-xs font-medium text-slate-500">Applications Submitted</div>
            <div className="text-2xl font-extrabold text-emerald-600 mt-1">
              {status?.applications_submitted || 0}
            </div>
          </div>

          <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
            <div className="text-xs font-medium text-slate-500">Verification Required</div>
            <div className="text-2xl font-extrabold text-amber-600 mt-1">
              {status?.verification_required || 0}
            </div>
          </div>

          <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
            <div className="text-xs font-medium text-slate-500">Login Required</div>
            <div className="text-2xl font-extrabold text-slate-700 mt-1">
              {status?.login_required || 0}
            </div>
          </div>

          <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
            <div className="text-xs font-medium text-slate-500">Failed / Expired</div>
            <div className="text-2xl font-extrabold text-rose-600 mt-1">
              {status?.failed || 0}
            </div>
          </div>

          <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
            <div className="text-xs font-medium text-slate-500">Active Workers</div>
            <div className="text-2xl font-extrabold text-slate-900 mt-1">
              {status?.active_tasks || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Safety & Compliance Notice */}
      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-emerald-600" />
          Autonomous Safety & Anti-Bot Protection
        </h3>
        <p className="mt-2 text-xs text-slate-600 leading-relaxed">
          The agent utilizes isolated Chromium browser sandboxes and obeys all platform security challenges.
          When anti-bot challenges (CAPTCHAs, Cloudflare checks, or OTP prompts) appear, the agent does not attempt
          bypass; it safely marks the job as <strong>VERIFICATION_REQUIRED</strong> and seamlessly moves to other opportunities.
        </p>
      </div>
    </div>
  );
}
