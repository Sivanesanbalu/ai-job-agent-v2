import {
  User,
  Profile,
  Resume,
  Preferences,
  ApplicationProfile,
  JobListing,
  Application,
  AutomationStatus,
  ConnectedAccount,
  CreditBalance,
  CreditTransaction,
  Plan,
  Notification,
  AnalyticsSummary,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

class ApiClient {
  private getHeaders(isFormData = false): HeadersInit {
    const headers: Record<string, string> = {};
    if (!isFormData) {
      headers["Content-Type"] = "application/json";
    }
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth_token");
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }
    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const isFormData = options.body instanceof FormData;
    const headers = { ...this.getHeaders(isFormData), ...options.headers };

    try {
      const response = await fetch(url, { ...options, headers });

      if (response.status === 401) {
        if (typeof window !== "undefined") {
          localStorage.removeItem("auth_token");
          if (!window.location.pathname.startsWith("/login") && !window.location.pathname.startsWith("/register")) {
            window.location.href = "/login";
          }
        }
      }

      const data = await response.json();
      if (!response.ok) {
        const errorDetail =
          data.detail || data.message || "An unexpected error occurred.";
        throw new Error(
          typeof errorDetail === "string"
            ? errorDetail
            : JSON.stringify(errorDetail)
        );
      }
      return data as T;
    } catch (error: any) {
      throw error;
    }
  }

  // Auth APIs
  auth = {
    register: (body: any) =>
      this.request<{ access_token: string; user: User }>("/auth/register", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    login: (body: any) =>
      this.request<{ access_token: string; user: User }>("/auth/login", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    logout: () => this.request("/auth/logout", { method: "POST" }),
    getMe: () => this.request<any>("/auth/me"),
    forgotPassword: (email: string) =>
      this.request("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      }),
    resetPassword: (body: any) =>
      this.request("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify(body),
      }),
  };

  // Profile APIs
  profile = {
    get: () => this.request<Profile>("/profile"),
    update: (body: Partial<Profile>) =>
      this.request<Profile>("/profile", {
        method: "PATCH",
        body: JSON.stringify(body),
      }),
  };

  // Resume APIs
  resumes = {
    list: () => this.request<Resume[]>("/resumes"),
    get: (id: number) => this.request<Resume>(`/resumes/${id}`),
    upload: (formData: FormData) =>
      this.request<Resume>("/resumes", {
        method: "POST",
        body: formData,
      }),
    update: (id: number, body: any) =>
      this.request<Resume>(`/resumes/${id}`, {
        method: "PATCH",
        body: JSON.stringify(body),
      }),
    delete: (id: number) =>
      this.request(`/resumes/${id}`, {
        method: "DELETE",
      }),
    getDownloadUrl: (id: number) => `${API_BASE}/resumes/${id}/download`,
  };

  // Preferences APIs
  preferences = {
    get: () => this.request<Preferences>("/preferences"),
    update: (body: Partial<Preferences>) =>
      this.request<Preferences>("/preferences", {
        method: "PATCH",
        body: JSON.stringify(body),
      }),
  };

  // Application Profile APIs
  applicationProfile = {
    get: () => this.request<ApplicationProfile>("/application-profile"),
    update: (body: Partial<ApplicationProfile>) =>
      this.request<ApplicationProfile>("/application-profile", {
        method: "PATCH",
        body: JSON.stringify(body),
      }),
  };

  // Job APIs
  jobs = {
    list: (params?: {
      keyword?: string;
      location?: string;
      source?: string;
      min_score?: number;
      limit?: number;
    }) => {
      const sp = new URLSearchParams();
      if (params?.keyword) sp.set("keyword", params.keyword);
      if (params?.location) sp.set("location", params.location);
      if (params?.source) sp.set("source", params.source);
      if (params?.min_score) sp.set("min_score", params.min_score.toString());
      if (params?.limit) sp.set("limit", params.limit.toString());
      return this.request<JobListing[]>(`/jobs?${sp.toString()}`);
    },
    get: (id: number) => this.request<JobListing>(`/jobs/${id}`),
    search: (body: any) =>
      this.request("/jobs/search", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    match: (id: number) =>
      this.request<any>(`/jobs/${id}/match`, {
        method: "POST",
      }),
  };

  // Application APIs
  applications = {
    list: (params?: { status?: string; search?: string; limit?: number; skip?: number }) => {
      const sp = new URLSearchParams();
      if (params?.status) sp.set("status", params.status);
      if (params?.search) sp.set("search", params.search);
      if (params?.limit) sp.set("limit", params.limit.toString());
      if (params?.skip) sp.set("skip", params.skip.toString());
      return this.request<Application[]>(`/applications?${sp.toString()}`);
    },
    get: (id: number) => this.request<Application>(`/applications/${id}`),
    approve: (id: number) =>
      this.request(`/applications/${id}/approve`, {
        method: "POST",
      }),
    reject: (id: number) =>
      this.request(`/applications/${id}/reject`, {
        method: "POST",
      }),
  };

  // Automation APIs
  automation = {
    getStatus: () => this.request<AutomationStatus>("/automation/status"),
    start: () =>
      this.request<AutomationStatus>("/automation/start", {
        method: "POST",
      }),
    pause: () =>
      this.request<AutomationStatus>("/automation/pause", {
        method: "POST",
      }),
    resume: () =>
      this.request<AutomationStatus>("/automation/resume", {
        method: "POST",
      }),
    stop: () =>
      this.request<AutomationStatus>("/automation/stop", {
        method: "POST",
      }),
  };

  // Connected Accounts
  connectedAccounts = {
    list: () => this.request<ConnectedAccount[]>("/connected-accounts"),
    connect: (body: any) =>
      this.request<ConnectedAccount>("/connected-accounts", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    disconnect: (id: number) =>
      this.request(`/connected-accounts/${id}`, {
        method: "DELETE",
      }),
  };

  // Credits & Billing
  credits = {
    getBalance: () => this.request<CreditBalance>("/credits"),
    getTransactions: () =>
      this.request<CreditTransaction[]>("/credits/transactions"),
  };

  billing = {
    getPlans: () => this.request<Plan[]>("/billing/plans"),
    createRazorpayOrder: (planSlug: string) =>
      this.request<{
        order_id: string;
        amount: number;
        amount_inr: number;
        currency: string;
        key_id: string;
        plan_name: string;
        plan_slug: string;
        credits: number;
        user_email: string;
        user_name: string;
        user_phone: string;
      }>("/billing/create-order", {
        method: "POST",
        body: JSON.stringify({ plan_slug: planSlug }),
      }),
    verifyRazorpayPayment: (payload: {
      razorpay_order_id: string;
      razorpay_payment_id: string;
      razorpay_signature: string;
    }) =>
      this.request<{
        status: string;
        message: string;
        payment_id: number;
        razorpay_order_id: string;
        razorpay_payment_id: string;
        credits_granted: number;
        amount_inr: number;
      }>("/billing/verify-payment", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    checkout: (planSlug: string) =>
      this.request<any>("/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ plan_slug: planSlug }),
      }),
    getHistory: () => this.request<any[]>("/billing/history"),
  };

  // Notifications
  notifications = {
    list: () => this.request<Notification[]>("/notifications"),
    markRead: (id: number) =>
      this.request(`/notifications/${id}/read`, {
        method: "POST",
      }),
    markAllRead: () =>
      this.request("/notifications/read-all", {
        method: "POST",
      }),
  };

  // Analytics
  analytics = {
    getSummary: () => this.request<AnalyticsSummary>("/analytics"),
  };
}

export const api = new ApiClient();
