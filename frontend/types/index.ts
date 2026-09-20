export interface User {
  id: number;
  email: string;
  is_admin: boolean;
  first_name?: string;
  last_name?: string;
}

export interface Profile {
  id: number;
  user_id: number;
  first_name: string;
  middle_name: string;
  last_name: string;
  preferred_name: string;
  email: string;
  phone: string;
  dob: string;
  country: string;
  state: string;
  city: string;
  address: string;
  pincode: string;
  headline: string;
  summary: string;
  linkedin_url: string;
  github_url: string;
  portfolio_url: string;
  education: string;
  experience_years: number;
  skills: string[];
  projects: any[];
}

export interface Resume {
  id: number;
  user_id: number;
  filename: string;
  file_size: number;
  mime_type: string;
  is_active: boolean;
  version: number;
  parsed_data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Preferences {
  id: number;
  user_id: number;
  preferred_roles: string[];
  preferred_locations: string[];
  remote_friendly: boolean;
  min_salary_lpa: number;
  max_experience_years: number;
  min_match_score: number;
  max_applications_per_day: number | null;
  auto_submit: boolean;
  require_human_review: boolean;
  employment_types: string[];
  keywords: string[];
  excluded_keywords: string[];
  sponsorship_required: boolean;
  relocation: boolean;
}

export interface ApplicationProfile {
  id: number;
  user_id: number;
  notice_period_days: number;
  work_authorization: string;
  expected_salary_lpa: number;
  current_salary_lpa: number | null;
  years_of_experience: number;
  willing_to_relocate: boolean;
  disability_status: string;
  veteran_status: string;
  gender: string;
  ethnicity: string;
  custom_answers: Record<string, any>;
}

export interface JobListing {
  id: number;
  external_id?: string;
  source: string;
  url: string;
  title: string;
  company: string;
  location: string;
  description: string;
  experience_years?: number | null;
  salary?: string | null;
  match_score?: number | null;
  match_details?: {
    relevance: string;
    matched_skills: string[];
    missing_skills: string[];
    reason: string;
    apply_decision: boolean;
  } | null;
  created_at: string;
}

export interface ApplicationEvent {
  id: number;
  status: string;
  stage: string;
  message: string;
  data: Record<string, any>;
  created_at: string;
}

export interface Application {
  id: number;
  user_id: number;
  job_id: number;
  resume_id?: number | null;
  status: string;
  stage: string;
  match_score: number;
  error_message?: string | null;
  verification_reason?: string | null;
  submitted_at?: string | null;
  created_at: string;
  updated_at: string;
  job?: JobListing;
  events?: ApplicationEvent[];
}

export interface AutomationStatus {
  is_running: boolean;
  status: "running" | "paused" | "stopped";
  current_action: string;
  jobs_discovered: number;
  jobs_analyzed: number;
  jobs_matched: number;
  eligible_applications: number;
  applications_submitted: number;
  verification_required: number;
  login_required: number;
  failed: number;
  credits_remaining: number;
  active_tasks: number;
}

export interface ConnectedAccount {
  id: number;
  platform: string;
  account_identifier: string;
  auth_status: "connected" | "not_connected" | "login_required" | "reauth_required";
  last_verified_at?: string | null;
  created_at: string;
}

export interface CreditBalance {
  balance: number;
  total_included: number;
  total_purchased: number;
  total_used: number;
  updated_at: string;
}

export interface CreditTransaction {
  id: number;
  type: string;
  amount: number;
  balance_before: number;
  balance_after: number;
  description: string;
  created_at: string;
}

export interface Plan {
  id: number;
  name: string;
  slug: string;
  price_inr: number;
  included_applications: number;
  features: string[];
  is_active: boolean;
}

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  metadata_json: Record<string, any>;
  created_at: string;
}

export interface AnalyticsSummary {
  total_jobs_found: number;
  total_jobs_matched: number;
  total_applications: number;
  applications_submitted: number;
  applications_pending: number;
  applications_failed: number;
  verification_required: number;
  credits_remaining: number;
  credits_used: number;
}
