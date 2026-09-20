"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Briefcase,
  Send,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Play,
  Pause,
  Square,
  ArrowRight,
  TrendingUp,
  Clock,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";
import { api } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/AuthContext";
import { AnalyticsSummary, AutomationStatus, Application, JobListing } from "@/types";
import { formatDate } from "@/lib/utils";

export default function DashboardPage() {
  const { user, creditsRemaining, refreshUserData } = useAuth();
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [automation, setAutomation] = useState<AutomationStatus | null>(null);
  const [recentApps, setRecentApps] = useState<Application[]>([]);
  const [recentJobs, setRecentJobs] = useState<JobListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [submittingAppId, setSubmittingAppId] = useState<number | null>(null);

  const handleQuickSubmit = async (appId: number) => {
    setSubmittingAppId(appId);
    try {
      await api.applications.submit(appId);
      await fetchDashboardData();
      await refreshUserData();
    } catch (err) {
      console.error("Quick submit error:", err);
    } finally {
      setSubmittingAppId(null);
    }
  };

  const fetchDashboardData = async () => {
    try {
      const [analyticsData, autoData, appsData, jobsData] = await Promise.all([
        api.analytics.getSummary(),
        api.automation.getStatus(),
        api.applications.list({ limit: 5 }),
        api.jobs.list({ limit: 5 }),
      ]);
      setAnalytics(analyticsData);
      setAutomation(autoData);
      setRecentApps(appsData.slice(0, 5));
      setRecentJobs(jobsData.slice(0, 5));
    } catch (err) {
      console.error("Failed to load dashboard:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleAutomationAction = async (action: "start" | "pause" | "resume" | "stop") => {
    setActionLoading(true);
    try {
      if (action === "start") await api.automation.start();
      else if (action === "pause") await api.automation.pause();
      else if (action === "resume") await api.automation.resume();
      else if (action === "stop") await api.automation.stop();
      await fetchDashboardData();
      await refreshUserData();
    } catch (err) {
      console.error(`Failed to ${action} automation:`, err);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Banner / Welcome */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Agent Dashboard
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Real-time status of your autonomous job discovery and application pipeline.
          </p>
        </div>

        {/* Quick Automation Controls */}
        <div className="flex items-center gap-3">
          {automation?.is_running ? (
            <>
              {automation.status === "paused" ? (
                <button
                  onClick={() => handleAutomationAction("resume")}
                  disabled={actionLoading}
                  className="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-amber-700 transition"
                >
                  <Play className="h-4 w-4" />
                  Resume Agent
                </button>
              ) : (
                <button
                  onClick={() => handleAutomationAction("pause")}
                  disabled={actionLoading}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition"
                >
                  <Pause className="h-4 w-4" />
                  Pause
                </button>
              )}
              <button
                onClick={() => handleAutomationAction("stop")}
                disabled={actionLoading}
                className="inline-flex items-center gap-2 rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-rose-700 transition"
              >
                <Square className="h-4 w-4" />
                Stop Agent
              </button>
            </>
          ) : (
            <button
              onClick={() => handleAutomationAction("start")}
              disabled={actionLoading}
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition"
            >
              <Play className="h-4 w-4 fill-white" />
              Start Autonomous Agent
            </button>
          )}
        </div>
      </div>

      {/* Credit Warning & Auto-Upgrade Card */}
      {creditsRemaining === 0 && (
        <div className="rounded-2xl border border-amber-300 bg-linear-to-r from-amber-50 to-orange-50 p-5 shadow-xs">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500 text-white shadow-xs">
                <Zap className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Free Monthly Allowance Exhausted (0 Credits Remaining)
                </h3>
                <p className="text-xs text-slate-600 mt-0.5">
                  Your 5 free applications have been used. Top up with Starter Pack (10 credits for ₹149) or Job Seeker Pack (25 credits for ₹299) to keep applying automatically.
                </p>
              </div>
            </div>
            <Link
              href="/billing"
              className="shrink-0 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-indigo-700 transition"
            >
              Get Application Credits &rarr;
            </Link>
          </div>
        </div>
      )}

      {/* Live Automation Status Banner */}
      <div className="rounded-2xl border border-indigo-100 bg-gradient-to-r from-indigo-50/70 via-white to-violet-50/50 p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div
              className={`flex h-12 w-12 items-center justify-center rounded-2xl ${
                automation?.is_running
                  ? automation.status === "paused"
                    ? "bg-amber-100 text-amber-700"
                    : "bg-indigo-600 text-white animate-pulse"
                  : "bg-slate-200 text-slate-600"
              }`}
            >
              <Zap className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold text-slate-900">
                  {automation?.is_running
                    ? automation.status === "paused"
                      ? "Agent Paused"
                      : "Agent Running"
                    : "Agent Idle"}
                </span>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                    automation?.is_running
                      ? automation.status === "paused"
                        ? "bg-amber-100 text-amber-800"
                        : "bg-emerald-100 text-emerald-800"
                      : "bg-slate-100 text-slate-600"
                  }`}
                >
                  {automation?.status || "stopped"}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {automation?.current_action || "Ready to run. Click Start to begin discovering and submitting applications."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
            <div>
              <span className="text-slate-400">Available Credits:</span>{" "}
              <span className="font-bold text-indigo-700">{creditsRemaining}</span>
            </div>
            <Link
              href="/automation"
              className="text-indigo-600 hover:text-indigo-700 font-semibold inline-flex items-center gap-1"
            >
              Open Full Cockpit <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Jobs Discovered</span>
            <Briefcase className="h-4 w-4 text-slate-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">
            {analytics?.total_jobs_found || 0}
          </div>
          <div className="mt-1 text-xs text-indigo-600 font-medium">
            Across portals
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>AI Matches</span>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">
            {analytics?.total_jobs_matched || 0}
          </div>
          <div className="mt-1 text-xs text-emerald-600 font-medium">
            Score &ge; threshold
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Applications Submitted</span>
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">
            {analytics?.applications_submitted || 0}
          </div>
          <div className="mt-1 text-xs text-slate-500">
            Verified submissions
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Verification Required</span>
            <ShieldAlert className="h-4 w-4 text-amber-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">
            {analytics?.verification_required || 0}
          </div>
          <div className="mt-1 text-xs text-amber-600 font-medium">
            CAPTCHA / MFA flagged
          </div>
        </div>
      </div>

      {/* Two-Column Lists: Recent Applications & Recent Jobs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Applications */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-slate-900">
              Recent Applications
            </h2>
            <Link
              href="/applications"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              View All
            </Link>
          </div>

          {recentApps.length === 0 ? (
            <div className="py-12 text-center text-sm text-slate-500">
              No applications recorded yet. Start the agent to apply automatically.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {recentApps.map((app) => (
                <div
                  key={app.id}
                  className="flex items-center justify-between py-3.5"
                >
                  <div className="min-w-0 flex-1 pr-4">
                    <div className="truncate text-sm font-semibold text-slate-900">
                      {app.job?.title || "Role"}
                    </div>
                    <div className="text-xs text-slate-500">
                      {app.job?.company} • {app.job?.location}
                    </div>
                  </div>

                  <div className="flex items-center gap-2.5">
                    {app.status === "ready_to_submit" && (
                      <button
                        onClick={() => handleQuickSubmit(app.id)}
                        disabled={submittingAppId === app.id}
                        className="rounded-lg bg-emerald-600 px-2.5 py-1 text-[11px] font-bold text-white hover:bg-emerald-700 transition shadow-xs"
                      >
                        {submittingAppId === app.id ? "Submitting..." : "Submit Now"}
                      </button>
                    )}
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${
                        app.status === "submitted"
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          : app.status === "ready_to_submit"
                          ? "bg-blue-50 text-blue-700 border border-blue-200"
                          : app.status === "verification_required"
                          ? "bg-amber-50 text-amber-700 border border-amber-200"
                          : "bg-indigo-50 text-indigo-700 border border-indigo-200"
                      }`}
                    >
                      {app.status.replace(/_/g, " ")}
                    </span>
                    <span className="text-[11px] text-slate-400">
                      {formatDate(app.created_at)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Discovered Jobs */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-slate-900">
              Discovered Opportunities
            </h2>
            <Link
              href="/jobs"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              Explore All Jobs
            </Link>
          </div>

          {recentJobs.length === 0 ? (
            <div className="py-12 text-center text-sm text-slate-500">
              No jobs discovered yet. Click Start Agent or search jobs.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {recentJobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between py-3.5"
                >
                  <div className="min-w-0 flex-1 pr-4">
                    <div className="truncate text-sm font-semibold text-slate-900">
                      {job.title}
                    </div>
                    <div className="text-xs text-slate-500">
                      {job.company} • {job.location || "Remote"} • {job.salary || "Salary not disclosed"}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {job.match_score !== null && job.match_score !== undefined && (
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${
                          job.match_score >= 80
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : "bg-indigo-50 text-indigo-700 border border-indigo-200"
                        }`}
                      >
                        {job.match_score}% Match
                      </span>
                    )}
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noreferrer"
                      className="p-1 text-slate-400 hover:text-slate-600"
                      title="Open source listing"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
