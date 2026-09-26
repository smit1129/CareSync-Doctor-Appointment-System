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
    <div>
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-teal-600 via-cyan-700 to-teal-800 text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-20 w-96 h-96 bg-cyan-300 rounded-full blur-3xl" />
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-12">
            <div className="max-w-3xl flex-1">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight">
                Your Health,{" "}
                <span className="text-cyan-300">Our Priority</span>
              </h1>
              <p className="mt-6 text-lg sm:text-xl text-white/80 leading-relaxed max-w-2xl">
                Book appointments with top healthcare specialists instantly. Search by specialization, choose your preferred time slot, and manage your healthcare journey seamlessly.
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                <Link href="/doctors" className="inline-flex items-center px-8 py-3.5 rounded-xl bg-white text-teal-700 font-semibold shadow-lg hover:shadow-xl hover:bg-teal-50 transition-all transform hover:-translate-y-0.5">
                  Find a Doctor →
                </Link>
                <Link href="/auth/register" className="inline-flex items-center px-8 py-3.5 rounded-xl border-2 border-white/30 text-white font-semibold hover:bg-white/10 transition-all">
                  Create Account
                </Link>
              </div>
            </div>
            
            {/* Hero SVG Illustration */}
            <div className="hidden lg:flex flex-1 justify-end">
              <div className="relative w-full max-w-md aspect-square bg-white/5 rounded-3xl backdrop-blur-sm border border-white/10 p-8 flex items-center justify-center shadow-2xl">
                <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full opacity-90 drop-shadow-2xl">
                  <circle cx="100" cy="100" r="80" fill="currentColor" className="text-teal-800/50" />
                  <rect x="60" y="55" width="80" height="90" rx="8" fill="white" className="shadow-lg" />
                  <line x1="75" y1="75" x2="125" y2="75" stroke="#0d9488" strokeWidth="4" strokeLinecap="round" />
                  <line x1="75" y1="95" x2="115" y2="95" stroke="#99f6e4" strokeWidth="4" strokeLinecap="round" />
                  <line x1="75" y1="115" x2="100" y2="115" stroke="#99f6e4" strokeWidth="4" strokeLinecap="round" />
                  <circle cx="140" cy="130" r="25" fill="#06b6d4" />
                  <path d="M130 130l6 6 12-12" stroke="white" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                {/* Floating Elements */}
                <div className="absolute -left-6 top-12 bg-white text-teal-700 px-4 py-3 rounded-2xl shadow-xl flex items-center gap-3 animate-bounce shadow-black/10" style={{ animationDuration: '3s' }}>
                  <span className="text-xl">🩺</span>
                  <div className="text-sm font-bold">Expert Doctors</div>
                </div>
                <div className="absolute -right-6 bottom-16 bg-white text-cyan-700 px-4 py-3 rounded-2xl shadow-xl flex items-center gap-3 animate-bounce shadow-black/10" style={{ animationDuration: '3.5s', animationDelay: '0.5s' }}>
                  <span className="text-xl">📅</span>
                  <div className="text-sm font-bold">Easy Booking</div>
                </div>
              </div>
            </div>
          </div>
          {/* Stats */}
          <div className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-6">
            {[
              { label: "User Roles", value: "3" },
              { label: "Appointment Booking", value: "24/7" },
              { label: "Demo Payments", value: "Secure" },
              { label: "Specializations", value: `${specializations.length || 5}+` },
            ].map((stat) => (
              <div key={stat.label} className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
                <div className="text-2xl sm:text-3xl font-bold">{stat.value}</div>
                <div className="text-sm text-white/70 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">How It Works</h2>
          <p className="text-center text-gray-500 mb-12 max-w-2xl mx-auto">Book your appointment in three simple steps</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: "1", icon: "🔍", title: "Search Doctor", desc: "Browse specialists by specialization, name, or clinic location." },
              { step: "2", icon: "📅", title: "Pick a Time Slot", desc: "Choose your preferred date and available time slot from the doctor's schedule." },
              { step: "3", icon: "✅", title: "Confirm & Pay", desc: "Complete secure payment and receive instant booking confirmation." },
            ].map((item) => (
              <div key={item.step} className="relative bg-gradient-to-b from-gray-50 to-white rounded-2xl p-8 text-center border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 bg-teal-600 text-white rounded-full flex items-center justify-center text-sm font-bold">{item.step}</div>
                <div className="text-4xl mb-4 mt-2">{item.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-500 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Specialization Filter + Doctors */}
      <section className="py-16 bg-gray-50" id="doctors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Our Specialists</h2>
          <p className="text-gray-500 mb-8">Filter by specialization and find the right doctor for you</p>

          {/* Search bar */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search by doctor name or clinic..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full max-w-md px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-800 shadow-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none transition-all"
            />
          </div>

          {/* Specialization pills */}
          <div className="flex flex-wrap gap-2 mb-8">
            <button
              onClick={() => setSelectedSpec("")}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                !selectedSpec ? "bg-teal-600 text-white shadow-md" : "bg-white text-gray-600 border border-gray-200 hover:border-teal-300"
              }`}
            >
              All
            </button>
            {specializations.map((spec) => (
              <button
                key={spec}
                onClick={() => setSelectedSpec(selectedSpec === spec ? "" : spec)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  selectedSpec === spec ? "bg-teal-600 text-white shadow-md" : "bg-white text-gray-600 border border-gray-200 hover:border-teal-300"
                }`}
              >
                {SPECIALIZATIONS_ICONS[spec] || "🏥"} {spec}
              </button>
            ))}
          </div>

          {/* Doctor Cards */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                  <div className="skeleton h-6 w-3/4 mb-3" />
                  <div className="skeleton h-4 w-1/2 mb-2" />
                  <div className="skeleton h-4 w-full mb-2" />
                  <div className="skeleton h-10 w-full mt-4" />
                </div>
              ))}
            </div>
          ) : doctors.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
              <div className="text-5xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No doctors found</h3>
              <p className="text-gray-400">Try adjusting your search or specialization filter.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {doctors.map((doc) => (
                <div key={doc.id} className="group bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-lg hover:border-teal-200 transition-all flex flex-col h-full">
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-full flex items-center justify-center text-white text-xl font-bold shrink-0 shadow-inner relative">
                      {doc.name.charAt(4) || "D"}
                      <div className="absolute -bottom-1 -right-1 bg-white rounded-full p-0.5" title="Verified Professional">
                        <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path></svg>
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-gray-900 group-hover:text-teal-700 transition-colors line-clamp-1">{doc.name}</h3>
                      <p className="text-sm text-teal-600 font-medium">{doc.specialization}</p>
                    </div>
                    <div className="flex items-center gap-1 bg-amber-50 px-2.5 py-1 rounded-lg shrink-0 border border-amber-100">
                      <span className="text-amber-500 text-sm">★</span>
                      <span className="text-sm font-semibold text-amber-700">{doc.rating_avg}</span>
                    </div>
                  </div>
                  
                  <div className="space-y-2 mb-6 flex-1">
                    <p className="text-sm text-gray-600 flex items-center gap-2">
                      <span className="text-gray-400">🎓</span> {doc.qualification}
                    </p>
                    <p className="text-sm text-gray-600 flex items-center gap-2">
                      <span className="text-gray-400">⏱️</span> {doc.experience_years} years experience
                    </p>
                    <p className="text-sm text-gray-600 flex items-center gap-2 line-clamp-1">
                      <span className="text-gray-400">📍</span> {doc.clinic_address}
                    </p>
                  </div>
                  
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100 mb-4">
                    <span className="text-sm text-gray-500">Consultation Fee</span>
                    <span className="text-lg font-bold text-gray-900">₹{doc.consultation_fee}</span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 mt-auto">
                    <Link href={`/doctors/${doc.id}`} className="py-2.5 px-2 text-center rounded-xl text-teal-700 font-medium bg-teal-50 hover:bg-teal-100 transition-colors text-sm">
                      View Profile
                    </Link>
                    <Link href={`/doctors/${doc.id}`} className="py-2.5 px-2 text-center rounded-xl text-white font-medium bg-teal-600 hover:bg-teal-700 shadow-sm transition-colors text-sm">
                      Book Now
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Demo Accounts */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">Quick Demo Access</h2>
          <p className="text-center text-gray-500 mb-8">Use these accounts to explore the system</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[
              { role: "Patient", desc: "Explore patient appointment features", email: "john.doe@gmail.com", pass: "Patient@12345", color: "from-emerald-500 to-teal-600", icon: "👤" },
              { role: "Doctor", desc: "Manage appointments and availability", email: "sarah.jenkins@hospital.com", pass: "Doctor@12345", color: "from-blue-500 to-indigo-600", icon: "🩺" },
              { role: "Admin", desc: "Manage the complete system", email: "admin@hospital.com", pass: "Admin@12345", color: "from-purple-500 to-pink-600", icon: "⚙️" },
            ].map((demo) => (
              <div key={demo.role} className={`bg-gradient-to-br ${demo.color} rounded-2xl p-6 text-white shadow-lg flex flex-col`}>
                <div className="text-4xl mb-4">{demo.icon}</div>
                <h3 className="text-xl font-bold mb-2">{demo.role} Account</h3>
                <p className="text-sm text-white/80 mb-6 flex-1">{demo.desc}</p>
                
                <button 
                  onClick={() => handleDemoLogin(demo.email, demo.pass)}
                  disabled={loginLoading}
                  className="w-full bg-white/20 hover:bg-white/30 backdrop-blur py-3 px-4 rounded-xl text-sm font-semibold transition-all border border-white/20 shadow-sm disabled:opacity-50"
                >
                  {loginLoading ? "Loading..." : `Login as ${demo.role}`}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
