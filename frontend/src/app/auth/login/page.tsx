"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = async (em: string, pw: string) => {
    setEmail(em);
    setPassword(pw);
    setError("");
    setLoading(true);
    try {
      await login(em, pw);
      router.push("/");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12 bg-background">
      <div className="w-full max-w-md">
        <div className="bg-surface rounded-2xl shadow-xl border border-border p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-foreground">Welcome Back</h1>
            <p className="text-muted-foreground mt-2 text-sm">Sign in to your CareSync account</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-rose-50 dark:bg-rose-950/50 border border-rose-300 dark:border-rose-800 rounded-xl text-rose-950 dark:text-rose-200 text-sm font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-foreground mb-1.5">Email Address</label>
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-border hover:border-gray-400 dark:hover:border-teal-700 bg-surface-subtle/60 dark:bg-surface-subtle/40 text-foreground placeholder:text-muted-foreground/70 focus:bg-surface focus:ring-2 focus:ring-accent focus:border-accent outline-none transition-all shadow-xs"
                placeholder="you@example.com" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-foreground mb-1.5">Password</label>
              <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-border hover:border-gray-400 dark:hover:border-teal-700 bg-surface-subtle/60 dark:bg-surface-subtle/40 text-foreground placeholder:text-muted-foreground/70 focus:bg-surface focus:ring-2 focus:ring-accent focus:border-accent outline-none transition-all shadow-xs"
                placeholder="••••••••" />
            </div>
            <button type="submit" disabled={loading}
              className="w-full py-3 bg-primary text-primary-foreground font-semibold rounded-xl shadow-md hover:bg-primary/90 focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link href="/auth/register" className="text-accent font-semibold hover:underline">Sign Up</Link>
          </div>

          {/* Quick Demo Logins */}
          <div className="mt-8 pt-6 border-t border-border">
            <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground text-center mb-3">Quick Demo Access</p>
            <div className="grid grid-cols-3 gap-2.5">
              <button type="button" onClick={() => quickLogin("smit.gamit@demo.caresync.local", "Patient@12345")}
                className="py-2.5 px-3 bg-emerald-100/80 hover:bg-emerald-200/90 dark:bg-emerald-950/50 dark:hover:bg-emerald-900/60 text-emerald-950 dark:text-emerald-200 border border-emerald-300 dark:border-emerald-700/80 text-xs font-bold rounded-xl transition-all shadow-2xs hover:shadow-xs flex flex-col items-center justify-center gap-1 focus:ring-2 focus:ring-emerald-400 focus:outline-none">
                <span className="text-base">👤</span>
                <span>Patient</span>
              </button>
              <button type="button" onClick={() => quickLogin("aarav.mehta@demo.caresync.local", "Doctor@12345")}
                className="py-2.5 px-3 bg-blue-100/80 hover:bg-blue-200/90 dark:bg-blue-950/50 dark:hover:bg-blue-900/60 text-blue-950 dark:text-blue-200 border border-blue-300 dark:border-blue-700/80 text-xs font-bold rounded-xl transition-all shadow-2xs hover:shadow-xs flex flex-col items-center justify-center gap-1 focus:ring-2 focus:ring-blue-400 focus:outline-none">
                <span className="text-base">🩺</span>
                <span>Doctor</span>
              </button>
              <button type="button" onClick={() => quickLogin("admin@demo.caresync.local", "Admin@12345")}
                className="py-2.5 px-3 bg-purple-100/80 hover:bg-purple-200/90 dark:bg-purple-950/50 dark:hover:bg-purple-900/60 text-purple-950 dark:text-purple-200 border border-purple-300 dark:border-purple-700/80 text-xs font-bold rounded-xl transition-all shadow-2xs hover:shadow-xs flex flex-col items-center justify-center gap-1 focus:ring-2 focus:ring-purple-400 focus:outline-none">
                <span className="text-base">⚡</span>
                <span>Admin</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
