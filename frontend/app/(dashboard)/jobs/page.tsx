"use client";

import React, { useState, useEffect } from "react";
import {
  Search,
  Filter,
  Briefcase,
  ExternalLink,
  Sparkles,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
  MapPin,
  X,
  Loader2,
} from "lucide-react";
import { api } from "@/lib/api/client";
import { JobListing } from "@/types";
import { formatDate } from "@/lib/utils";

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState("");
  const [location, setLocation] = useState("");
  const [selectedSource, setSelectedSource] = useState("");
  const [selectedJob, setSelectedJob] = useState<JobListing | null>(null);
  const [matchingJobId, setMatchingJobId] = useState<number | null>(null);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const data = await api.jobs.list({
        keyword: keyword || undefined,
        location: location || undefined,
        source: selectedSource || undefined,
        limit: 50,
      });
      setJobs(data);
    } catch (err) {
      console.error("Failed to load jobs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [selectedSource]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs();
  };

  const handleMatch = async (jobId: number) => {
    setMatchingJobId(jobId);
    try {
      const res = await api.jobs.match(jobId);
      // Update local state
      setJobs((prev) =>
        prev.map((j) =>
          j.id === jobId
            ? {
                ...j,
                match_score: res.match_score,
                match_details: {
                  relevance: res.relevance,
                  matched_skills: res.matched_skills,
                  missing_skills: res.missing_skills,
                  reason: res.reason,
                  apply_decision: res.apply_decision,
                },
              }
            : j
        )
      );
      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob((prev) =>
          prev
            ? {
                ...prev,
                match_score: res.match_score,
                match_details: {
                  relevance: res.relevance,
                  matched_skills: res.matched_skills,
                  missing_skills: res.missing_skills,
                  reason: res.reason,
                  apply_decision: res.apply_decision,
                },
              }
            : null
        );
      }
    } catch (err) {
      console.error("Match calculation failed:", err);
    } finally {
      setMatchingJobId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Discovered Job Listings
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Real job listings extracted from LinkedIn, Naukri, Indeed, and company sites.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
        <form
          onSubmit={handleSearch}
          className="flex flex-col md:flex-row items-center gap-3"
        >
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Search by role title, technology, or company..."
              className="w-full rounded-xl border border-slate-200 pl-10 pr-4 py-2.5 text-sm focus:border-indigo-600 focus:outline-none"
            />
          </div>

          <div className="relative w-full md:w-56">
            <MapPin className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Location..."
              className="w-full rounded-xl border border-slate-200 pl-10 pr-4 py-2.5 text-sm focus:border-indigo-600 focus:outline-none"
            />
          </div>

          <div className="w-full md:w-44">
            <select
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
              className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm focus:border-indigo-600 focus:outline-none bg-white"
            >
              <option value="">All Sources</option>
              <option value="linkedin">LinkedIn</option>
              <option value="naukri">Naukri</option>
              <option value="indeed">Indeed</option>
              <option value="generic">Company Sites</option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full md:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition"
          >
            Search
          </button>
        </form>
      </div>

      {/* Jobs Grid / List */}
      {loading ? (
        <div className="py-16 text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-indigo-600" />
          <p className="mt-3 text-sm text-slate-500">Loading discovered jobs...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center">
          <Briefcase className="mx-auto h-12 w-12 text-slate-300" />
          <h3 className="mt-4 text-base font-bold text-slate-900">No jobs found</h3>
          <p className="mt-1 text-sm text-slate-500">
            Try adjusting your search filters or start the autonomous agent to discover new opportunities.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <div
              key={job.id}
              onClick={() => setSelectedJob(job)}
              className="cursor-pointer rounded-2xl border border-slate-200 bg-white p-5 shadow-xs hover:border-indigo-300 hover:shadow-md transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2">
                  <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-700 uppercase">
                    {job.source}
                  </span>
                  {job.match_score !== null && job.match_score !== undefined ? (
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${
                        job.match_score >= 80
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          : "bg-indigo-50 text-indigo-700 border border-indigo-200"
                      }`}
                    >
                      {job.match_score}% Match
                    </span>
                  ) : (
                    <span className="text-xs text-slate-400">Unanalyzed</span>
                  )}
                </div>

                <h3 className="mt-3 text-base font-bold text-slate-900 line-clamp-1">
                  {job.title}
                </h3>
                <div className="mt-1 text-sm font-medium text-slate-600">
                  {job.company}
                </div>

                <div className="mt-3 flex flex-wrap items-center gap-y-1 gap-x-3 text-xs text-slate-500">
                  <span>📍 {job.location || "Location not specified"}</span>
                  {job.salary && <span>💰 {job.salary}</span>}
                  {job.experience_years !== null && job.experience_years !== undefined && (
                    <span>⏳ {job.experience_years} yrs exp</span>
                  )}
                </div>

                <p className="mt-3 text-xs text-slate-600 line-clamp-2">
                  {job.description || "No description preview available."}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-slate-400">{formatDate(job.created_at)}</span>
                <span className="font-semibold text-indigo-600 hover:text-indigo-700">
                  View Details &rarr;
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Job Details Modal / Drawer */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl">
            <button
              onClick={() => setSelectedJob(null)}
              className="absolute top-5 right-5 p-1 text-slate-400 hover:text-slate-600 rounded-lg"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="flex items-center gap-2 text-xs font-semibold text-indigo-600 uppercase">
              <span>{selectedJob.source}</span>
              <span>•</span>
              <span>{formatDate(selectedJob.created_at)}</span>
            </div>

            <h2 className="mt-2 text-xl font-bold text-slate-900">
              {selectedJob.title}
            </h2>
            <div className="mt-1 text-base font-semibold text-slate-700">
              {selectedJob.company} • {selectedJob.location}
            </div>

            {/* AI Match Overview */}
            <div className="mt-6 rounded-xl border border-indigo-100 bg-indigo-50/50 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-indigo-600" />
                  <span className="text-sm font-bold text-slate-900">
                    AI Match Evaluation
                  </span>
                </div>
                {selectedJob.match_score !== null && selectedJob.match_score !== undefined ? (
                  <span className="text-sm font-extrabold text-indigo-700">
                    {selectedJob.match_score}%
                  </span>
                ) : (
                  <button
                    onClick={() => handleMatch(selectedJob.id)}
                    disabled={matchingJobId === selectedJob.id}
                    className="inline-flex items-center gap-1 rounded-lg bg-indigo-600 px-3 py-1 text-xs font-semibold text-white hover:bg-indigo-700 transition"
                  >
                    {matchingJobId === selectedJob.id ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      "Calculate Match"
                    )}
                  </button>
                )}
              </div>

              {selectedJob.match_details && (
                <div className="mt-3 text-xs space-y-2 text-slate-700">
                  <p>
                    <strong>Reasoning:</strong> {selectedJob.match_details.reason}
                  </p>
                  {selectedJob.match_details.matched_skills.length > 0 && (
                    <div>
                      <strong>Matched Skills:</strong>{" "}
                      {selectedJob.match_details.matched_skills.join(", ")}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Description */}
            <div className="mt-6">
              <h3 className="text-sm font-bold text-slate-900 mb-2">Job Description</h3>
              <div className="text-sm text-slate-700 whitespace-pre-line leading-relaxed max-h-60 overflow-y-auto pr-2 border rounded-lg p-3 bg-slate-50">
                {selectedJob.description}
              </div>
            </div>

            {/* Footer Action */}
            <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4">
              <a
                href={selectedJob.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900"
              >
                Open Original Posting <ExternalLink className="h-3.5 w-3.5" />
              </a>

              <button
                onClick={() => setSelectedJob(null)}
                className="rounded-xl border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
