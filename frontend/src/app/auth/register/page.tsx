"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }
    setLoading(true);
    try {
      await register(name, email, password, phone || undefined);
      router.push("/patient/dashboard");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Registration failed";
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
            <h1 className="text-3xl font-bold text-foreground">Create Account</h1>
            <p className="text-muted-foreground mt-2 text-sm">Join CareSync to book appointments instantly</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-rose-50 dark:bg-rose-950/50 border border-rose-300 dark:border-rose-800 rounded-xl text-rose-950 dark:text-rose-200 text-sm font-medium">{error}</div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-foreground mb-1.5">Full Name</label>
              <input type="text" required value={name} onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-border hover:border-gray-400 dark:hover:border-teal-700 bg-surface-subtle/60 dark:bg-surface-subtle/40 text-foreground placeholder:text-muted-foreground/70 focus:bg-surface focus:ring-2 focus:ring-accent focus:border-accent outline-none transition-all shadow-xs"
                placeholder="John Doe" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-foreground mb-1.5">Email Address</label>
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-border hover:border-gray-400 dark:hover:border-teal-700 bg-surface-subtle/60 dark:bg-surface-subtle/40 text-foreground placeholder:text-muted-foreground/70 focus:bg-surface focus:ring-2 focus:ring-accent focus:border-accent outline-none transition-all shadow-xs"
                placeholder="you@example.com" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-foreground mb-1.5">Phone (Optional)</label>
              <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-border hover:border-gray-400 dark:hover:border-teal-700 bg-surface-subtle/60 dark:bg-surface-subtle/40 text-foreground placeholder:text-muted-foreground/70 focus:bg-surface focus:ring-2 focus:ring-accent focus:border-accent outline-none transition-all shadow-xs"
                placeholder="+1-555-0000" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-foreground mb-1.5">Password</label>
              <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-border hover:border-gray-400 dark:hover:border-teal-700 bg-surface-subtle/60 dark:bg-surface-subtle/40 text-foreground placeholder:text-muted-foreground/70 focus:bg-surface focus:ring-2 focus:ring-accent focus:border-accent outline-none transition-all shadow-xs"
                placeholder="Min 6 characters" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-foreground mb-1.5">Confirm Password</label>
              <input type="password" required value={confirm} onChange={(e) => setConfirm(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-border hover:border-gray-400 dark:hover:border-teal-700 bg-surface-subtle/60 dark:bg-surface-subtle/40 text-foreground placeholder:text-muted-foreground/70 focus:bg-surface focus:ring-2 focus:ring-accent focus:border-accent outline-none transition-all shadow-xs"
                placeholder="Re-enter password" />
            </div>
            <button type="submit" disabled={loading}
              className="w-full py-3 bg-primary text-primary-foreground font-semibold rounded-xl shadow-md hover:bg-primary/90 focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? "Creating Account..." : "Create Account"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link href="/auth/login" className="text-accent font-semibold hover:underline">Sign In</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
