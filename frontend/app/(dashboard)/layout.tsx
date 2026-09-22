"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Bot,
  LayoutDashboard,
  Briefcase,
  Send,
  FileText,
  User,
  Sliders,
  FileSpreadsheet,
  Link2,
  Zap,
  CreditCard,
  Receipt,
  Bell,
  Settings,
  LogOut,
  Menu,
  X,
  Compass,
  Coins,
} from "lucide-react";
import { useAuth } from "@/lib/auth/AuthContext";
import { api } from "@/lib/api/client";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/onboarding", label: "Onboarding Wizard", icon: Compass },
  { href: "/jobs", label: "Discover Jobs", icon: Briefcase },
  { href: "/applications", label: "Applications", icon: Send },
  { href: "/automation", label: "Agent Cockpit", icon: Zap },
  { href: "/resume", label: "Resume Vault", icon: FileText },
  { href: "/profile", label: "Personal Profile", icon: User },
  { href: "/preferences", label: "Job Preferences", icon: Sliders },
  { href: "/application-profile", label: "Application Q&A", icon: FileSpreadsheet },
  { href: "/connected-accounts", label: "Job Portals", icon: Link2 },
  { href: "/credits", label: "Application Credits", icon: Coins },
  { href: "/billing", label: "Plans & Billing", icon: Receipt },
  { href: "/notifications", label: "Notifications", icon: Bell },
  { href: "/settings", label: "Settings & Privacy", icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, profile, creditsRemaining, loading, logout, refreshUserData } =
    useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [unreadNotifs, setUnreadNotifs] = useState(0);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (user) {
      api.notifications
        .list()
        .then((notifs) => {
          setUnreadNotifs(notifs.filter((n) => !n.is_read).length);
        })
        .catch(() => {});
    }
  }, [user, pathname]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="flex h-12 w-12 animate-pulse items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-sm">
            <Bot className="h-7 w-7" />
          </div>
          <span className="text-sm font-medium text-slate-500">
            Loading your workspace...
          </span>
        </div>
      </div>
    );
  }

  const displayName =
    profile?.first_name || user.first_name || user.email.split("@")[0];

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Sidebar Desktop */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-slate-200 bg-white lg:flex lg:flex-col">
        {/* Brand */}
        <div className="flex h-16 items-center gap-3 border-b border-slate-100 px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
            <Bot className="h-5 w-5" />
          </div>
          <div className="flex flex-col">
            <span className="text-base font-bold tracking-tight text-slate-900 leading-none">
              JobAgent<span className="text-indigo-600">.ai</span>
            </span>
            <span className="text-[10px] font-medium text-slate-400 mt-0.5">
              Production SaaS v2.0
            </span>
          </div>
        </div>

        {/* Navigation list */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition",
                  active
                    ? "bg-indigo-50 text-indigo-700 font-semibold"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                )}
              >
                <Icon
                  className={cn(
                    "h-4 w-4 shrink-0",
                    active ? "text-indigo-600" : "text-slate-400"
                  )}
                />
                <span>{item.label}</span>
                {item.href === "/notifications" && unreadNotifs > 0 && (
                  <span className="ml-auto rounded-full bg-indigo-600 px-2 py-0.5 text-[10px] font-bold text-white">
                    {unreadNotifs}
                  </span>
                )}
              </Link>
            );
          })}
        </div>

        {/* User Card & Logout */}
        <div className="border-t border-slate-100 p-3">
          <div className="flex items-center gap-3 rounded-xl p-2 bg-slate-50">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700 font-bold text-sm">
              {displayName.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-xs font-semibold text-slate-900">
                {displayName}
              </div>
              <div className="truncate text-[11px] text-slate-500">
                {user.email}
              </div>
            </div>
            <button
              onClick={logout}
              title="Logout"
              className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg transition"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="lg:pl-64 flex flex-col min-h-screen">
        {/* Header */}
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/90 px-6 backdrop-blur-sm">
          <div className="flex items-center gap-3 lg:hidden">
            <button
              onClick={() => setMobileOpen(true)}
              className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
            >
              <Menu className="h-5 w-5" />
            </button>
            <span className="font-bold text-slate-900">JobAgent.ai</span>
          </div>

          <div className="hidden lg:flex items-center gap-3">
            <h1 className="text-base font-semibold text-slate-800">
              Welcome, {displayName}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            {/* Credits pill */}
            <Link
              href="/billing"
              className={cn(
                "flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold transition shadow-xs",
                creditsRemaining === 0
                  ? "border-amber-400 bg-amber-50 text-amber-800 hover:bg-amber-100"
                  : "border-indigo-200 bg-indigo-50/70 text-indigo-700 hover:bg-indigo-100"
              )}
            >
              <Coins className={cn("h-3.5 w-3.5", creditsRemaining === 0 ? "text-amber-600" : "text-indigo-600")} />
              <span>{creditsRemaining} Credits Available</span>
              {creditsRemaining === 0 && (
                <span className="rounded bg-amber-200 px-1.5 py-0.2 text-[10px] font-bold text-amber-900">Upgrade</span>
              )}
            </Link>

            {/* Quick Link to Notifications */}
            <Link
              href="/notifications"
              className="relative rounded-lg p-2 text-slate-500 hover:bg-slate-100 transition"
              title="Notifications"
            >
              <Bell className="h-5 w-5" />
              {unreadNotifs > 0 && (
                <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-indigo-600" />
              )}
            </Link>
          </div>
        </header>

        {/* Mobile Navigation Drawer */}
        {mobileOpen && (
          <div className="fixed inset-0 z-50 flex lg:hidden">
            <div
              className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs"
              onClick={() => setMobileOpen(false)}
            />
            <div className="relative flex w-64 max-w-xs flex-1 flex-col bg-white py-4 shadow-xl">
              <div className="flex items-center justify-between px-6 pb-4 border-b border-slate-100">
                <span className="text-base font-bold text-slate-900">
                  JobAgent.ai
                </span>
                <button
                  onClick={() => setMobileOpen(false)}
                  className="rounded-lg p-1 text-slate-500 hover:bg-slate-100"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
                {NAV_ITEMS.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition",
                      pathname === item.href
                        ? "bg-indigo-50 text-indigo-700 font-semibold"
                        : "text-slate-600 hover:bg-slate-50"
                    )}
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </Link>
                ))}
              </div>

              {/* Mobile User Card & Logout */}
              <div className="border-t border-slate-100 p-3">
                <div className="flex items-center gap-3 rounded-xl p-2 bg-slate-50">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700 font-bold text-sm">
                    {displayName.charAt(0).toUpperCase()}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-xs font-semibold text-slate-900">
                      {displayName}
                    </div>
                    <div className="truncate text-[11px] text-slate-500">
                      {user.email}
                    </div>
                  </div>
                  <button
                    onClick={logout}
                    title="Logout"
                    className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg transition"
                  >
                    <LogOut className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Auto-Upgrade Alert Banner if credits exhausted */}
        {creditsRemaining === 0 && (
          <div className="bg-linear-to-r from-amber-600 to-orange-600 px-6 py-2.5 text-white text-xs font-medium flex items-center justify-between shadow-xs">
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="rounded-full bg-white/20 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider">
                Monthly Free Tier Used
              </span>
              <span>
                You have used your 5 free monthly application credits. Add a Pay-as-you-go pack starting at ₹149 (10 credits) to continue automated submissions.
              </span>
            </div>
            <Link
              href="/billing"
              className="ml-4 shrink-0 rounded-lg bg-white px-3.5 py-1 text-xs font-bold text-amber-900 hover:bg-amber-50 transition shadow-xs"
            >
              Add Credits &rarr;
            </Link>
          </div>
        )}

        {/* Page Content */}
        <main className="flex-1 p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
