"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { doctorsAPI, DoctorInfo } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";

const SPECIALIZATIONS_ICONS: Record<string, string> = {
  Cardiologist: "❤️",
  Dermatologist: "🧴",
  Pediatrician: "👶",
  Neurologist: "🧠",
  "General Physician": "🩺",
  Endocrinologist: "💉",
  Orthopedic: "🦴",
  Ophthalmology: "👁️",
};

export default function HomePage() {
  const [doctors, setDoctors] = useState<DoctorInfo[]>([]);
  const [specializations, setSpecializations] = useState<string[]>([]);
  const [selectedSpec, setSelectedSpec] = useState<string>("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [loginLoading, setLoginLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleDemoLogin = async (email: string, pass: string) => {
    setLoginLoading(true);
    try {
      await login(email, pass);
      router.push("/");
    } catch (err) {
      console.error("Demo login failed", err);
    } finally {
      setLoginLoading(false);
    }
  };

  useEffect(() => {
    Promise.all([
      doctorsAPI.list(),
      doctorsAPI.getSpecializations(),
    ]).then(([docs, specs]) => {
      setDoctors(docs);
      setSpecializations(specs);
    }).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    let active = true;
    const fetchDocs = async () => {
      setLoading(true);
      try {
        const docs = await doctorsAPI.list({ specialization: selectedSpec || undefined, search: search || undefined });
        if (active) setDoctors(docs);
      } catch { /* empty */ }
      if (active) setLoading(false);
    };
    fetchDocs();
    return () => { active = false; };
  }, [selectedSpec, search]);

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-teal-600 via-cyan-700 to-teal-800 dark:from-teal-800 dark:via-cyan-900 dark:to-teal-950 text-white overflow-hidden">
        {/* Subtle decorative atmospheric glows */}
        <div className="absolute inset-0 pointer-events-none opacity-20" aria-hidden="true">
          <div className="absolute -top-24 -left-24 w-96 h-96 bg-emerald-400 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-10 w-[30rem] h-[30rem] bg-teal-300 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-12 lg:gap-16">
            <div className="max-w-2xl flex-1 text-left">
              {/* Trust Badge */}
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-xs font-medium text-emerald-100 mb-6">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Next-Generation Healthcare • 24/7 Verified Specialists</span>
              </div>

              {/* Headline */}
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.15]">
                Your Health,{" "}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-300 to-emerald-200">
                  Our Priority
                </span>
              </h1>

              {/* Subtitle */}
              <p className="mt-5 text-base sm:text-lg lg:text-xl text-emerald-50/90 leading-relaxed font-normal">
                Book appointments with certified healthcare specialists instantly. Search by clinical expertise, choose real-time consultation slots, and manage your family’s healthcare journey with seamless confidence.
              </p>

              {/* CTA Buttons */}
              <div className="mt-8 flex flex-wrap items-center gap-4">
                <Link
                  href="/doctors"
                  className="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-white text-emerald-950 font-semibold shadow-lg hover:shadow-xl hover:bg-emerald-50 transition-all transform hover:-translate-y-0.5 text-sm sm:text-base"
                >
                  <span>Find a Doctor</span>
                  <span className="text-emerald-700 font-bold">→</span>
                </Link>
                <Link
                  href="/auth/register"
                  className="inline-flex items-center justify-center px-7 py-3.5 rounded-xl border border-white/30 text-white font-semibold hover:bg-white/10 transition-all text-sm sm:text-base backdrop-blur-sm"
                >
                  Create Account
                </Link>
              </div>
            </div>

            {/* Hero Medical Visual Card */}
            <div className="hidden lg:flex flex-1 justify-end">
              <div className="relative w-full max-w-md">
                {/* Subtle aura behind card */}
                <div className="absolute -inset-1 bg-gradient-to-r from-teal-400/20 to-emerald-500/20 rounded-3xl blur-xl opacity-60" />

                {/* Main Glass Consultation Preview */}
                <div className="relative bg-white/10 backdrop-blur-xl rounded-3xl border border-white/20 p-7 shadow-2xl text-white">
                  {/* Doctor Profile Header */}
                  <div className="flex items-center justify-between pb-5 border-b border-white/15">
                    <div className="flex items-center gap-3.5">
                      <div className="w-13 h-13 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-xl font-bold text-white shadow-md">
                        AM
                      </div>
                      <div>
                        <div className="flex items-center gap-1.5">
                          <h4 className="font-bold text-base text-white tracking-tight">Dr. Aarav Mehta</h4>
                          <svg className="w-4 h-4 text-teal-300 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <p className="text-xs text-emerald-200 font-medium">Senior Cardiologist • MD</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 bg-white/15 px-2.5 py-1 rounded-lg text-xs font-semibold text-white">
                      <span className="text-amber-300">★</span> 4.9
                    </div>
                  </div>

                  {/* Real-time schedule preview */}
                  <div className="my-5 space-y-3">
                    <div className="flex items-center justify-between text-xs text-emerald-100 font-medium">
                      <span>Next Available Slot</span>
                      <span className="text-teal-300 font-semibold">Today • Instant Booking</span>
                    </div>
                    <div className="bg-white/10 border border-white/15 rounded-xl p-3.5 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-teal-400/20 flex items-center justify-center text-teal-300 text-sm">
                          📅
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-white">10:30 AM – 11:00 AM</p>
                          <p className="text-[11px] text-emerald-200/80">Apollo Clinic, Bandra</p>
                        </div>
                      </div>
                      <span className="text-xs font-bold text-white bg-emerald-500/30 px-2.5 py-1 rounded-md border border-emerald-400/30">
                        ₹600
                      </span>
                    </div>
                  </div>

                  {/* Card bottom credentials */}
                  <div className="pt-2 flex items-center justify-between text-xs text-emerald-100/90">
                    <span className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      Instant Confirmation
                    </span>
                    <span className="font-medium text-teal-300">CareSync Verified ✓</span>
                  </div>

                  {/* Floating Badges */}
                  <div className="absolute -left-6 -bottom-4 bg-surface text-foreground px-4 py-2.5 rounded-2xl shadow-xl border border-border flex items-center gap-3 transform -rotate-1">
                    <span className="text-xl">🩺</span>
                    <div>
                      <p className="text-xs font-bold text-foreground">Verified Doctors</p>
                      <p className="text-[10px] text-muted-foreground">Certified Medical Council</p>
                    </div>
                  </div>

                  <div className="absolute -right-4 -top-3 bg-surface text-foreground px-4 py-2 rounded-2xl shadow-xl border border-border flex items-center gap-2 transform rotate-1">
                    <span className="w-2 h-2 rounded-full bg-teal-500 animate-pulse" />
                    <p className="text-xs font-bold text-foreground">Live Availability</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Statistics Grid */}
          <div className="mt-14 sm:mt-16 grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6">
            {[
              { label: "User Roles", value: "3", desc: "Patient • Doctor • Admin" },
              { label: "Appointment Booking", value: "24/7", desc: "Real-time calendar" },
              { label: "Verified Specialists", value: "100%", desc: "Direct doctor access" },
              { label: "Medical Disciplines", value: `${specializations.length || 8}+`, desc: "Comprehensive care" },
            ].map((stat) => (
              <div key={stat.label} className="bg-white/10 backdrop-blur-md rounded-2xl p-4 sm:p-5 border border-white/15 text-left">
                <div className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">{stat.value}</div>
                <div className="text-sm font-semibold text-emerald-100 mt-1">{stat.label}</div>
                <div className="text-[11px] text-emerald-200/70 mt-0.5">{stat.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 sm:py-20 bg-background border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-xl mx-auto mb-12 sm:mb-14">
            <span className="text-xs font-bold uppercase tracking-wider text-teal-600 dark:text-teal-400">Streamlined Process</span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground tracking-tight mt-1">How CareSync Works</h2>
            <p className="text-muted-foreground mt-2 text-sm sm:text-base">Book your medical consultation in three intuitive steps without queues or delays.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
            {[
              { step: "01", icon: "🔍", title: "Find Specialists", desc: "Browse qualified practitioners by medical discipline, experience, patient ratings, and consultation fee." },
              { step: "02", icon: "📅", title: "Select a Time Slot", desc: "Choose your preferred appointment date and convenient time slot directly from real-time doctor schedules." },
              { step: "03", icon: "✅", title: "Instant Confirmation", desc: "Complete demo payment securely to receive instant booking receipts and manage appointments in your portal." },
            ].map((item) => (
              <div key={item.step} className="relative bg-surface rounded-2xl p-7 sm:p-8 border border-border shadow-sm hover:shadow-md hover:border-teal-500/40 transition-all flex flex-col h-full">
                <div className="flex items-center justify-between mb-5">
                  <div className="w-12 h-12 rounded-xl bg-teal-50 dark:bg-teal-950/40 border border-teal-100 dark:border-teal-900/50 flex items-center justify-center text-2xl">
                    {item.icon}
                  </div>
                  <span className="text-xs font-bold tracking-widest text-muted-foreground/60 uppercase">Step {item.step}</span>
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Specialization Filter + Doctors */}
      <section className="py-16 sm:py-20 bg-surface-subtle/50 border-b border-border" id="doctors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-teal-600 dark:text-teal-400">Certified Network</span>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground tracking-tight mt-1">Our Medical Specialists</h2>
              <p className="text-muted-foreground text-sm sm:text-base mt-1">Filter by clinical specialization and book with certified healthcare professionals.</p>
            </div>

            {/* Search bar */}
            <div className="relative max-w-sm w-full">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-muted-foreground">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search doctor or clinic..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-border bg-surface text-foreground placeholder:text-muted-foreground/60 shadow-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none transition-all text-sm"
              />
            </div>
          </div>

          {/* Specialization pills */}
          <div className="flex flex-wrap gap-2 mb-8">
            <button
              onClick={() => setSelectedSpec("")}
              className={`px-4 py-2 rounded-full text-xs sm:text-sm font-semibold transition-all ${!selectedSpec
                ? "bg-primary text-primary-foreground shadow-sm"
                : "bg-surface text-foreground/80 border border-border hover:border-teal-500/50 hover:text-foreground"
                }`}
            >
              All Specialists
            </button>
            {specializations.map((spec) => (
              <button
                key={spec}
                onClick={() => setSelectedSpec(selectedSpec === spec ? "" : spec)}
                className={`px-4 py-2 rounded-full text-xs sm:text-sm font-semibold transition-all ${selectedSpec === spec
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "bg-surface text-foreground/80 border border-border hover:border-teal-500/50 hover:text-foreground"
                  }`}
              >
                {SPECIALIZATIONS_ICONS[spec] || "🏥"} {spec}
              </button>
            ))}
          </div>

          {/* Doctor Cards Grid */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-surface rounded-2xl p-6 shadow-sm border border-border">
                  <div className="skeleton h-6 w-3/4 mb-3" />
                  <div className="skeleton h-4 w-1/2 mb-2" />
                  <div className="skeleton h-4 w-full mb-2" />
                  <div className="skeleton h-10 w-full mt-4" />
                </div>
              ))}
            </div>
          ) : doctors.length === 0 ? (
            <div className="text-center py-16 bg-surface rounded-2xl border border-border">
              <div className="text-5xl mb-4">🔍</div>
              <h3 className="text-xl font-bold text-foreground mb-2">No doctors found</h3>
              <p className="text-muted-foreground text-sm">Try adjusting your search criteria or specialization filter.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {doctors.map((doc) => (
                <div
                  key={doc.id}
                  className="group bg-surface rounded-2xl p-6 border border-border shadow-sm hover:shadow-xl hover:border-teal-500/40 transition-all flex flex-col h-full duration-200"
                >
                  {/* Card Header: Avatar, Name, Specialization & Rating */}
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-emerald-800 to-teal-900 text-white rounded-2xl flex items-center justify-center text-xl font-bold shrink-0 shadow-sm relative">
                      {doc.name.replace(/^Dr\.?\s*/i, "").charAt(0) || "D"}
                      <div className="absolute -bottom-1 -right-1 bg-surface rounded-full p-0.5 shadow-sm" title="Verified Practitioner">
                        <svg className="w-4 h-4 text-teal-600 dark:text-teal-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-bold text-foreground group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors truncate">
                        {doc.name}
                      </h3>
                      <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-teal-50 dark:bg-teal-950/60 text-teal-800 dark:text-teal-300 mt-1">
                        {doc.specialization}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 bg-amber-50 dark:bg-amber-950/40 border border-amber-200/60 dark:border-amber-800/50 px-2.5 py-1 rounded-lg shrink-0">
                      <span className="text-amber-500 text-xs">★</span>
                      <span className="text-xs font-bold text-amber-800 dark:text-amber-300">{doc.rating_avg}</span>
                    </div>
                  </div>

                  {/* Metadata Info */}
                  <div className="space-y-2 mb-6 flex-1 text-xs sm:text-sm text-muted-foreground">
                    <p className="flex items-center gap-2">
                      <span className="text-base">🎓</span>
                      <span className="truncate">{doc.qualification}</span>
                    </p>
                    <p className="flex items-center gap-2">
                      <span className="text-base">⏱️</span>
                      <span>{doc.experience_years} years clinical experience</span>
                    </p>
                    <p className="flex items-center gap-2">
                      <span className="text-base">📍</span>
                      <span className="truncate">{doc.clinic_address}</span>
                    </p>
                  </div>

                  {/* Consultation Fee */}
                  <div className="flex items-center justify-between pt-4 border-t border-border mb-4">
                    <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Consultation Fee</span>
                    <span className="text-xl font-bold text-foreground">₹{doc.consultation_fee}</span>
                  </div>

                  {/* Booking Actions */}
                  <div className="grid grid-cols-2 gap-2 mt-auto">
                    <Link
                      href={`/doctors/${doc.id}`}
                      className="py-2.5 px-2 text-center rounded-xl border border-border text-foreground hover:bg-surface-subtle font-medium text-xs sm:text-sm transition-colors"
                    >
                      View Profile
                    </Link>
                    <Link
                      href={`/doctors/${doc.id}`}
                      className="py-2.5 px-2 text-center rounded-xl bg-primary text-primary-foreground hover:opacity-90 font-medium text-xs sm:text-sm shadow-sm transition-all"
                    >
                      Book Now →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Quick Demo Access */}
      <section className="py-16 sm:py-20 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Sandbox Evaluation</span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-foreground tracking-tight mt-1">Quick Demo Access</h2>
            <p className="text-muted-foreground text-sm mt-2">Instantly sign in with pre-configured role credentials to evaluate workflows.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[
              {
                role: "Patient",
                badge: "Appointments & History",
                desc: "Explore search, schedule consultation slots, and verify instant demo payment workflows.",
                email: "smit.gamit@demo.caresync.local",
                pass: "Patient@12345",
                icon: "👤",
                btnTheme: "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 hover:bg-emerald-100 dark:hover:bg-emerald-900/50 border border-emerald-200/60 dark:border-emerald-800/50",
              },
              {
                role: "Doctor",
                badge: "Schedule Management",
                desc: "Review booked appointments, adjust availability slots, and manage practitioner profile settings.",
                email: "aarav.mehta@demo.caresync.local",
                pass: "Doctor@12345",
                icon: "🩺",
                btnTheme: "bg-teal-50 dark:bg-teal-950/40 text-teal-800 dark:text-teal-300 hover:bg-teal-100 dark:hover:bg-teal-900/50 border border-teal-200/60 dark:border-teal-800/50",
              },
              {
                role: "Admin",
                badge: "System Administration",
                desc: "Audit hospital registrations, verify doctor credentials, and oversee platform activity.",
                email: "admin@demo.caresync.local",
                pass: "Admin@12345",
                icon: "⚙️",
                btnTheme: "bg-slate-100 dark:bg-slate-800/60 text-slate-800 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700/60 border border-slate-300/60 dark:border-slate-700/60",
              },
            ].map((demo) => (
              <div key={demo.role} className="bg-surface rounded-2xl p-6 border border-border shadow-sm hover:shadow-md transition-all flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-surface-subtle border border-border flex items-center justify-center text-2xl">
                    {demo.icon}
                  </div>
                  <span className="text-[11px] font-semibold text-muted-foreground bg-surface-subtle px-2.5 py-1 rounded-full border border-border">
                    {demo.badge}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-foreground mb-1">{demo.role} Portal</h3>
                <p className="text-xs text-muted-foreground leading-relaxed mb-4 flex-1">{demo.desc}</p>
                <div className="bg-surface-subtle border border-border/70 rounded-xl p-2.5 mb-4 text-[11px] text-muted-foreground font-mono">
                  <p className="truncate">Email: {demo.email}</p>
                </div>
                <button
                  onClick={() => handleDemoLogin(demo.email, demo.pass)}
                  disabled={loginLoading}
                  className="w-full py-2.5 px-4 rounded-xl text-xs font-semibold bg-primary text-primary-foreground border border-primary hover:brightness-110 active:scale-[0.98] transition-all shadow-sm disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {loginLoading ? "Authenticating..." : `Login as ${demo.role} →`}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
