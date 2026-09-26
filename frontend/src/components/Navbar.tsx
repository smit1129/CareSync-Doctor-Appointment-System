"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { notificationsAPI, NotificationInfo } from "@/lib/api";
import { Logo } from "@/components/Logo";

export default function Navbar() {
  const { user, token, logout, isDoctor, isAdmin, loading } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationInfo[]>([]);
  const notifRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (token) {
      notificationsAPI.list(token, true).then(setNotifications).catch(() => {});
    }
  }, [token]);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotifOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const markRead = async (id: string) => {
    if (!token) return;
    await notificationsAPI.markRead(token, id);
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const dashboardLink = isAdmin
    ? "/admin/dashboard"
    : isDoctor
    ? "/doctor/dashboard"
    : "/patient/dashboard";

  return (
    <nav className="bg-gradient-to-r from-teal-600 to-cyan-700 shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 text-white font-bold text-xl tracking-tight">
            <Logo className="w-8 h-8 text-white" />
          </Link>

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-1">
            <Link href="/doctors" className="text-white/90 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg text-sm font-medium transition-colors">
              Find Doctors
            </Link>

            {!loading && user && (
              <Link href={dashboardLink} className="text-white/90 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg text-sm font-medium transition-colors">
                Dashboard
              </Link>
            )}

            {!loading && user && isDoctor && (
              <Link href="/doctor/profile" className="text-white/90 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg text-sm font-medium transition-colors">
                Profile
              </Link>
            )}

            {!loading && user && (
              <div ref={notifRef} className="relative">
                <button
                  onClick={() => setNotifOpen(!notifOpen)}
                  className="text-white/90 hover:text-white hover:bg-white/10 p-2 rounded-lg transition-colors relative"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
                  {notifications.length > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                      {notifications.length > 9 ? "9+" : notifications.length}
                    </span>
                  )}
                </button>
                {notifOpen && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-2xl border border-gray-100 overflow-hidden z-50">
                    <div className="p-3 bg-gray-50 border-b font-semibold text-gray-700 text-sm">Notifications</div>
                    <div className="max-h-72 overflow-y-auto">
                      {notifications.length === 0 ? (
                        <p className="p-4 text-gray-400 text-sm text-center">All caught up!</p>
                      ) : (
                        notifications.map((n) => (
                          <div key={n.id} className="p-3 border-b border-gray-50 hover:bg-gray-50 cursor-pointer" onClick={() => markRead(n.id)}>
                            <p className="text-sm font-medium text-gray-800">{n.title}</p>
                            <p className="text-xs text-gray-500 mt-1 line-clamp-2">{n.message}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {!loading && !user && (
              <>
                <Link href="/auth/login" className="text-white/90 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg text-sm font-medium transition-colors">
                  Log In
                </Link>
                <Link href="/auth/register" className="bg-white text-teal-700 hover:bg-teal-50 px-4 py-2 rounded-lg text-sm font-semibold transition-colors shadow-sm">
                  Sign Up
                </Link>
              </>
            )}

            {!loading && user && (
              <div className="flex items-center gap-3 ml-2">
                <span className="text-white/80 text-sm">Hi, {user.name.split(" ")[0]}</span>
                <button onClick={logout} className="text-white/70 hover:text-white text-sm hover:bg-white/10 px-3 py-2 rounded-lg transition-colors">
                  Logout
                </button>
              </div>
            )}
          </div>

          {/* Mobile hamburger */}
          <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden text-white p-2">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {mobileOpen
                ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden bg-teal-700/95 backdrop-blur border-t border-white/10 px-4 pb-4 pt-2 space-y-1">
          <Link href="/doctors" onClick={() => setMobileOpen(false)} className="block text-white/90 hover:bg-white/10 px-3 py-2 rounded-lg text-sm">Find Doctors</Link>
          {user && <Link href={dashboardLink} onClick={() => setMobileOpen(false)} className="block text-white/90 hover:bg-white/10 px-3 py-2 rounded-lg text-sm">Dashboard</Link>}
          {user && isDoctor && <Link href="/doctor/profile" onClick={() => setMobileOpen(false)} className="block text-white/90 hover:bg-white/10 px-3 py-2 rounded-lg text-sm">Profile</Link>}
          {!user && (
            <>
              <Link href="/auth/login" onClick={() => setMobileOpen(false)} className="block text-white/90 hover:bg-white/10 px-3 py-2 rounded-lg text-sm">Log In</Link>
              <Link href="/auth/register" onClick={() => setMobileOpen(false)} className="block bg-white text-teal-700 px-3 py-2 rounded-lg text-sm font-semibold text-center">Sign Up</Link>
            </>
          )}
          {user && (
            <button onClick={() => { logout(); setMobileOpen(false); }} className="block w-full text-left text-white/70 hover:bg-white/10 px-3 py-2 rounded-lg text-sm">
              Logout
            </button>
          )}
        </div>
      )}
    </nav>
  );
}
