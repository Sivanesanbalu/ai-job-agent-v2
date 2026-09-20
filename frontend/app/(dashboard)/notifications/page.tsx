"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Notification } from "@/types";
import { 
  Bell, CheckCheck, AlertTriangle, CheckCircle2, 
  Info, Sparkles, Clock, RefreshCw 
} from "lucide-react";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "unread">("all");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const data = await api.notifications.list();
      setNotifications(data);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load notifications.");
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (id: number) => {
    try {
      await api.notifications.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to mark notification as read.");
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.notifications.markAllRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to mark all as read.");
    }
  };

  const filteredNotifications = notifications.filter((n) => {
    if (filter === "unread") return !n.is_read;
    return true;
  });

  const getNotificationIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "verification_required":
      case "security_challenge":
        return <AlertTriangle className="h-5 w-5 text-amber-500" />;
      case "application_submitted":
      case "success":
        return <CheckCircle2 className="h-5 w-5 text-emerald-500" />;
      case "credit_granted":
        return <Sparkles className="h-5 w-5 text-indigo-500" />;
      default:
        return <Info className="h-5 w-5 text-blue-500" />;
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
    <div className="max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Notifications & Alerts</h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time events, safety challenges requiring human intervention, and submission updates.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchNotifications}
            className="p-2 rounded-xl border border-slate-200 text-slate-500 hover:bg-slate-50 transition"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          <button
            onClick={handleMarkAllRead}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
          >
            <CheckCheck className="h-4 w-4 text-slate-500" />
            Mark all read
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm">
          {errorMessage}
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-3">
        <button
          onClick={() => setFilter("all")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            filter === "all"
              ? "bg-indigo-50 text-indigo-700"
              : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          All ({notifications.length})
        </button>
        <button
          onClick={() => setFilter("unread")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            filter === "unread"
              ? "bg-indigo-50 text-indigo-700"
              : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          Unread ({notifications.filter((n) => !n.is_read).length})
        </button>
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {filteredNotifications.length > 0 ? (
          filteredNotifications.map((notif) => (
            <div
              key={notif.id}
              className={`p-4 rounded-2xl border transition flex items-start justify-between gap-4 ${
                notif.is_read
                  ? "bg-white border-slate-200/80"
                  : "bg-indigo-50/30 border-indigo-200 shadow-xs"
              }`}
            >
              <div className="flex items-start gap-3.5">
                <div className="p-2 rounded-xl bg-white border border-slate-100 shadow-xs mt-0.5">
                  {getNotificationIcon(notif.type)}
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-slate-900">{notif.title}</h3>
                    {!notif.is_read && (
                      <span className="h-2 w-2 rounded-full bg-indigo-600" />
                    )}
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">{notif.message}</p>
                  <div className="flex items-center gap-1.5 text-[11px] text-slate-400 pt-1">
                    <Clock className="h-3.5 w-3.5" />
                    <span>{new Date(notif.created_at).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {!notif.is_read && (
                <button
                  type="button"
                  onClick={() => handleMarkRead(notif.id)}
                  className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 whitespace-nowrap px-2 py-1 rounded-md hover:bg-indigo-50 transition"
                >
                  Mark read
                </button>
              )}
            </div>
          ))
        ) : (
          <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center">
            <Bell className="h-8 w-8 text-slate-300 mx-auto mb-3" />
            <p className="text-sm font-medium text-slate-700">No notifications found</p>
            <p className="text-xs text-slate-400 mt-1">You are completely up to date.</p>
          </div>
        )}
      </div>
    </div>
  );
}
