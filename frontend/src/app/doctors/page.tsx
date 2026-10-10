"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { doctorsAPI, DoctorInfo } from "@/lib/api";

export default function DoctorsPage() {
  const [doctors, setDoctors] = useState<DoctorInfo[]>([]);
  const [specializations, setSpecializations] = useState<string[]>([]);
  const [selectedSpec, setSelectedSpec] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    doctorsAPI.getSpecializations().then(setSpecializations).catch(() => {});
  }, []);

  useEffect(() => {
    let active = true;
    const fetchDocs = async () => {
      setLoading(true);
      try {
        const docs = await doctorsAPI.list({
          specialization: selectedSpec || undefined,
          search: search || undefined,
        });
        if (active) setDoctors(docs);
      } catch { /* empty */ }
      if (active) setLoading(false);
    };
    fetchDocs();
    return () => { active = false; };
  }, [selectedSpec, search]);

  return (
    <div className="min-h-screen bg-surface hover:brightness-95 dark:hover:brightness-110">
      <div className="bg-primary text-primary-foreground py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold">Find a Doctor</h1>
          <p className="mt-2 text-white/80">Browse our network of specialist doctors and book your appointment</p>
          <div className="mt-6">
            <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, specialization, or clinic..."
              className="w-full max-w-xl px-5 py-3.5 rounded-xl bg-surface/10 backdrop-blur border border-white/20 text-white placeholder-white/50 focus:bg-surface/20 focus:ring-2 focus:ring-white/30 outline-none transition-all" />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filter pills */}
        <div className="flex flex-wrap gap-2 mb-8">
          <button onClick={() => setSelectedSpec("")}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${!selectedSpec ? "bg-teal-600 text-white shadow" : "bg-surface text-foreground/70 border border-border hover:border-teal-300"}`}>
            All Specialists
          </button>
          {specializations.map((s) => (
            <button key={s} onClick={() => setSelectedSpec(selectedSpec === s ? "" : s)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${selectedSpec === s ? "bg-teal-600 text-white shadow" : "bg-surface text-foreground/70 border border-border hover:border-teal-300"}`}>
              {s}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="bg-surface rounded-2xl p-6 border border-border">
                <div className="skeleton h-6 w-3/4 mb-3" /><div className="skeleton h-4 w-1/2 mb-2" /><div className="skeleton h-4 w-full mb-2" /><div className="skeleton h-10 w-full mt-4" />
              </div>
            ))}
          </div>
        ) : doctors.length === 0 ? (
          <div className="text-center py-20 bg-surface rounded-2xl border border-border">
            <div className="text-5xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-foreground/80 mb-2">No doctors found</h3>
            <p className="text-gray-400">Try adjusting your search or filter.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {doctors.map((doc) => (
              <Link key={doc.id} href={`/doctors/${doc.id}`} className="group">
                <div className="bg-surface rounded-2xl p-6 border border-border hover:shadow-lg hover:border-teal-200 transition-all transform hover:-translate-y-1">
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-12 h-12 bg-primary text-primary-foreground rounded-xl flex items-center justify-center text-white text-lg font-bold">
                      {doc.name.charAt(4) || doc.name.charAt(0)}
                    </div>
                    <div className="flex items-center gap-1 bg-amber-50 px-2.5 py-1 rounded-lg">
                      <span className="text-amber-500 text-sm">★</span>
                      <span className="text-sm font-semibold text-amber-700">{doc.rating_avg}</span>
                      <span className="text-xs text-amber-500">({doc.rating_count})</span>
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-foreground group-hover:text-teal-700 transition-colors">{doc.name}</h3>
                  <p className="text-sm text-teal-600 font-medium">{doc.specialization}</p>
                  <p className="text-sm text-foreground/60 mt-1">{doc.qualification}</p>
                  <p className="text-xs text-gray-400 mt-1">📍 {doc.clinic_address}</p>
                  <p className="text-xs text-gray-400">{doc.experience_years} yrs experience</p>
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
                    <span className="text-lg font-bold text-foreground">₹{doc.consultation_fee}</span>
                    <span className="text-sm text-teal-600 font-medium group-hover:translate-x-1 transition-transform">Book Now →</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
