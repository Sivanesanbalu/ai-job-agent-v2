import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth/AuthContext";

export const metadata: Metadata = {
  title: "AI Job Agent — Autonomous Multi-User AI Job Application SaaS",
  description:
    "AI-powered autonomous job discovery, intelligent resume matching, and multi-portal job applications for modern engineers.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-slate-50">
      <body className="h-full font-sans antialiased text-slate-900 bg-[#F8FAFC]">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
