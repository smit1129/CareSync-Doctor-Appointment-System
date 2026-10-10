"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { adminAPI, AdminStats, doctorsAPI, DoctorInfo, PatientInfo, DailyReport, MonthlyReport } from "@/lib/api";

export default function AdminDashboard() {
  const router = useRouter();
  const { user, token, loading: authLoading, isAdmin } = useAuth();
  
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [doctors, setDoctors] = useState<DoctorInfo[]>([]);
  const [patients, setPatients] = useState<PatientInfo[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [tab, setTab] = useState<"overview" | "doctors" | "patients" | "reports">("overview");

  // New doctor state
  const [showAddDoctor, setShowAddDoctor] = useState(false);
  const [newDoc, setNewDoc] = useState({
    name: "",
    email: "",
    password: "",
    specialization: "",
    qualification: "",
    experience_years: 0,
    clinic_address: "",
    consultation_fee: 500,
  });
  const [addDocLoading, setAddDocLoading] = useState(false);
  const [msg, setMsg] = useState("");

  // Reports state
  const [dailyReport, setDailyReport] = useState<DailyReport | null>(null);
  const [monthlyReport, setMonthlyReport] = useState<MonthlyReport | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  
  const today = new Date();
  const [reportDate, setReportDate] = useState(today.toISOString().split("T")[0]);
  const [reportMonth, setReportMonth] = useState(today.getMonth() + 1);
  const [reportYear, setReportYear] = useState(today.getFullYear());

  const fetchData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [s, d, p] = await Promise.all([
        adminAPI.stats(token),
        doctorsAPI.list(),
        adminAPI.listPatients(token),
      ]);
      setStats(s);
      setDoctors(d);
      setPatients(p);
    } catch {
      // ignore
    }
    setLoading(false);
  }, [token]);

  const fetchReports = useCallback(async () => {
    if (!token) return;
    setReportLoading(true);
    try {
      const [daily, monthly] = await Promise.all([
        adminAPI.dailyReport(token, reportDate),
        adminAPI.monthlyReport(token, reportMonth, reportYear),
      ]);
      setDailyReport(daily);
      setMonthlyReport(monthly);
    } catch {
      // ignore
    }
    setReportLoading(false);
  }, [token, reportDate, reportMonth, reportYear]);

  useEffect(() => {
    if (authLoading) return;
    if (!user || !isAdmin) {
      router.push("/auth/login");
      return;
    }
    fetchData();
  }, [user, authLoading, isAdmin, router, fetchData]);

  useEffect(() => {
    if (tab === "reports") {
      fetchReports();
    }
  }, [tab, reportDate, reportMonth, reportYear, fetchReports]);

  const handleAddDoctor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setAddDocLoading(true);
    try {
      await adminAPI.addDoctor(token, newDoc);
      setMsg("Doctor added successfully");
      setShowAddDoctor(false);
      setNewDoc({
        name: "", email: "", password: "", specialization: "", qualification: "",
        experience_years: 0, clinic_address: "", consultation_fee: 500
      });
      fetchData();
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Failed to add doctor");
    }
    setAddDocLoading(false);
  };

  if (authLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="skeleton h-8 w-1/4 mb-4" />
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[1,2,3,4].map(i => <div key={i} className="skeleton h-32 rounded-xl" />)}
        </div>
        <div className="skeleton h-64 rounded-xl" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface hover:brightness-95 dark:hover:brightness-110 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Admin Dashboard</h1>
            <p className="text-foreground/60">System overview and management</p>
          </div>
          {tab === "doctors" && (
            <button onClick={() => setShowAddDoctor(true)} className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition font-medium">
              + Add Doctor
            </button>
          )}
        </div>

        {msg && (
          <div className="mb-6 p-4 bg-teal-50 border border-teal-200 text-teal-800 rounded-xl flex justify-between">
            {msg}
            <button onClick={() => setMsg("")} className="font-bold">✕</button>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {(["overview", "doctors", "patients", "reports"] as const).map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-5 py-2.5 rounded-lg text-sm font-medium capitalize transition-all whitespace-nowrap ${tab === t ? "bg-teal-600 text-white shadow" : "bg-surface text-foreground/70 border border-border hover:border-teal-300"}`}>
              {t}
            </button>
          ))}
        </div>

        {tab === "overview" && stats && (
          <div className="space-y-8">
            <h2 className="text-xl font-bold text-foreground">Statistics</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { label: "Total Doctors", value: stats.total_doctors, icon: "👨‍⚕️", color: "text-blue-600", bg: "bg-blue-50" },
                { label: "Total Patients", value: stats.total_patients, icon: "👤", color: "text-emerald-600", bg: "bg-emerald-50" },
                { label: "Total Appointments", value: stats.total_appointments, icon: "📅", color: "text-purple-600", bg: "bg-purple-50" },
                { label: "Total Revenue", value: `₹${stats.total_revenue}`, icon: "💰", color: "text-amber-600", bg: "bg-amber-50" },
              ].map(s => (
                <div key={s.label} className="bg-surface rounded-2xl p-6 border border-border shadow-sm flex items-center gap-4">
                  <div className={`w-14 h-14 rounded-xl ${s.bg} ${s.color} flex items-center justify-center text-2xl`}>
                    {s.icon}
                  </div>
                  <div>
                    <div className="text-sm text-foreground/60 font-medium">{s.label}</div>
                    <div className="text-2xl font-bold text-foreground">{s.value}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-surface rounded-2xl p-6 border border-border shadow-sm text-center">
                <div className="text-3xl font-bold text-green-600">{stats.confirmed_appointments}</div>
                <div className="text-sm text-foreground/60 mt-1">Confirmed</div>
              </div>
              <div className="bg-surface rounded-2xl p-6 border border-border shadow-sm text-center">
                <div className="text-3xl font-bold text-blue-600">{stats.completed_appointments}</div>
                <div className="text-sm text-foreground/60 mt-1">Completed</div>
              </div>
              <div className="bg-surface rounded-2xl p-6 border border-border shadow-sm text-center">
                <div className="text-3xl font-bold text-red-600">{stats.cancelled_appointments}</div>
                <div className="text-sm text-foreground/60 mt-1">Cancelled</div>
              </div>
            </div>
          </div>
        )}

        {tab === "doctors" && (
          <div className="bg-surface rounded-2xl border border-border shadow-sm overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-surface hover:brightness-95 dark:hover:brightness-110 border-b border-border">
                <tr>
                  <th className="px-6 py-4 font-semibold text-foreground/70">Name</th>
                  <th className="px-6 py-4 font-semibold text-foreground/70">Specialization</th>
                  <th className="px-6 py-4 font-semibold text-foreground/70">Experience</th>
                  <th className="px-6 py-4 font-semibold text-foreground/70">Fee</th>
                  <th className="px-6 py-4 font-semibold text-foreground/70">Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {doctors.map(d => (
                  <tr key={d.id} className="hover:bg-surface hover:brightness-95 dark:hover:brightness-110">
                    <td className="px-6 py-4 font-medium text-foreground">{d.name}</td>
                    <td className="px-6 py-4 text-foreground/70">{d.specialization}</td>
                    <td className="px-6 py-4 text-foreground/70">{d.experience_years} yrs</td>
                    <td className="px-6 py-4 text-foreground font-medium">₹{d.consultation_fee}</td>
                    <td className="px-6 py-4 text-amber-500 font-medium">★ {d.rating_avg}</td>
                  </tr>
                ))}
                {doctors.length === 0 && (
                  <tr><td colSpan={5} className="px-6 py-8 text-center text-foreground/60">No doctors found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {tab === "patients" && (
          <div className="bg-surface rounded-2xl border border-border shadow-sm overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-surface hover:brightness-95 dark:hover:brightness-110 border-b border-border">
                <tr>
                  <th className="px-6 py-4 font-semibold text-foreground/70">Name</th>
                  <th className="px-6 py-4 font-semibold text-foreground/70">Email</th>
                  <th className="px-6 py-4 font-semibold text-foreground/70">Contact</th>
                  <th className="px-6 py-4 font-semibold text-foreground/70">Joined</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {patients.map(p => (
                  <tr key={p.id} className="hover:bg-surface hover:brightness-95 dark:hover:brightness-110">
                    <td className="px-6 py-4 font-medium text-foreground">{p.name}</td>
                    <td className="px-6 py-4 text-foreground/70">{p.email}</td>
                    <td className="px-6 py-4 text-foreground/70">{p.contact_no || p.phone_number || "-"}</td>
                    <td className="px-6 py-4 text-foreground/60 text-sm">{new Date(p.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
                {patients.length === 0 && (
                  <tr><td colSpan={4} className="px-6 py-8 text-center text-foreground/60">No patients found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {tab === "reports" && (
          <div className="space-y-8">
            <div className="flex flex-col md:flex-row gap-6">
              
              {/* Daily Report */}
              <div className="flex-1 bg-surface rounded-2xl border border-border shadow-sm p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-bold text-foreground">Daily Report</h3>
                  <input type="date" value={reportDate} onChange={(e) => setReportDate(e.target.value)}
                    className="px-3 py-1.5 border border-border rounded-lg text-sm text-foreground/80 outline-none focus:ring-2 focus:ring-teal-500" />
                </div>
                {reportLoading ? (
                  <div className="skeleton h-40 rounded-xl"></div>
                ) : dailyReport ? (
                  <div>
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div className="bg-surface hover:brightness-95 dark:hover:brightness-110 p-4 rounded-xl border border-border text-center">
                        <div className="text-sm text-foreground/60">Total Appointments</div>
                        <div className="text-2xl font-bold text-foreground">{dailyReport.total_appointments}</div>
                      </div>
                      <div className="bg-amber-50 p-4 rounded-xl border border-amber-100 text-center">
                        <div className="text-sm text-amber-700">Total Revenue</div>
                        <div className="text-2xl font-bold text-amber-900">₹{dailyReport.total_revenue}</div>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <h4 className="text-sm font-semibold text-foreground/80 mb-3">Appointments Breakup</h4>
                      <div className="flex gap-2 text-sm text-center">
                        <div className="flex-1 bg-green-50 text-green-700 py-2 rounded-lg">Confirmed: {dailyReport.confirmed_count}</div>
                        <div className="flex-1 bg-blue-50 text-blue-700 py-2 rounded-lg">Completed: {dailyReport.completed_count}</div>
                        <div className="flex-1 bg-red-50 text-red-700 py-2 rounded-lg">Cancelled: {dailyReport.cancelled_count}</div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-foreground/60 text-sm">No report available for this date.</p>
                )}
              </div>

              {/* Monthly Report */}
              <div className="flex-1 bg-surface rounded-2xl border border-border shadow-sm p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-bold text-foreground">Monthly Report</h3>
                  <div className="flex gap-2">
                    <select value={reportMonth} onChange={(e) => setReportMonth(Number(e.target.value))}
                      className="px-3 py-1.5 border border-border rounded-lg text-sm text-foreground/80 outline-none focus:ring-2 focus:ring-teal-500">
                      {Array.from({length: 12}, (_, i) => i + 1).map(m => (
                        <option key={m} value={m}>{new Date(2000, m - 1).toLocaleString('default', { month: 'short' })}</option>
                      ))}
                    </select>
                    <input type="number" value={reportYear} onChange={(e) => setReportYear(Number(e.target.value))}
                      className="px-3 py-1.5 border border-border rounded-lg text-sm text-foreground/80 w-24 outline-none focus:ring-2 focus:ring-teal-500" min="2020" max="2035" />
                  </div>
                </div>
                {reportLoading ? (
                  <div className="skeleton h-40 rounded-xl"></div>
                ) : monthlyReport ? (
                  <div>
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div className="bg-surface hover:brightness-95 dark:hover:brightness-110 p-4 rounded-xl border border-border text-center">
                        <div className="text-sm text-foreground/60">Total Appointments ({monthlyReport.month_name})</div>
                        <div className="text-2xl font-bold text-foreground">{monthlyReport.total_appointments}</div>
                      </div>
                      <div className="bg-amber-50 p-4 rounded-xl border border-amber-100 text-center">
                        <div className="text-sm text-amber-700">Monthly Revenue</div>
                        <div className="text-2xl font-bold text-amber-900">₹{monthlyReport.total_revenue}</div>
                      </div>
                    </div>

                    <div className="mb-4">
                      <h4 className="text-sm font-semibold text-foreground/80 mb-3">Top Doctors</h4>
                      {monthlyReport.top_doctors.length > 0 ? (
                        <ul className="space-y-2">
                          {monthlyReport.top_doctors.map(d => (
                            <li key={d.doctor_id} className="flex justify-between items-center text-sm bg-surface hover:brightness-95 dark:hover:brightness-110 px-3 py-2 rounded-lg">
                              <div>
                                <span className="font-medium text-foreground/90">{d.doctor_name}</span>
                                <span className="text-foreground/60 ml-2">({d.specialization})</span>
                              </div>
                              <span className="bg-teal-100 text-teal-800 px-2 py-0.5 rounded font-medium">{d.appointment_count} apts</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-foreground/60 text-sm">No doctor statistics for this month.</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <p className="text-foreground/60 text-sm">No report available for this month.</p>
                )}
              </div>

            </div>
          </div>
        )}
      </div>

      {/* Add Doctor Modal */}
      {showAddDoctor && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-foreground">Add New Doctor</h2>
              <button onClick={() => setShowAddDoctor(false)} className="text-foreground/60 hover:bg-surface brightness-95 dark:brightness-125 p-2 rounded-lg">✕</button>
            </div>
            <form onSubmit={handleAddDoctor} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground/80 mb-1">Full Name</label>
                  <input type="text" required value={newDoc.name} onChange={e => setNewDoc({...newDoc, name: e.target.value})} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground/80 mb-1">Email</label>
                  <input type="email" required value={newDoc.email} onChange={e => setNewDoc({...newDoc, email: e.target.value})} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground/80 mb-1">Temporary Password</label>
                  <input type="text" required value={newDoc.password} onChange={e => setNewDoc({...newDoc, password: e.target.value})} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground/80 mb-1">Specialization</label>
                  <input type="text" required value={newDoc.specialization} onChange={e => setNewDoc({...newDoc, specialization: e.target.value})} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground/80 mb-1">Qualification</label>
                  <input type="text" required value={newDoc.qualification} onChange={e => setNewDoc({...newDoc, qualification: e.target.value})} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground/80 mb-1">Experience (Years)</label>
                  <input type="number" required min="0" value={newDoc.experience_years} onChange={e => setNewDoc({...newDoc, experience_years: parseInt(e.target.value)})} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground/80 mb-1">Consultation Fee (₹)</label>
                  <input type="number" required min="0" value={newDoc.consultation_fee} onChange={e => setNewDoc({...newDoc, consultation_fee: parseInt(e.target.value)})} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 outline-none" />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-foreground/80 mb-1">Clinic Address</label>
                  <input type="text" required value={newDoc.clinic_address} onChange={e => setNewDoc({...newDoc, clinic_address: e.target.value})} className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 outline-none" />
                </div>
              </div>
              <div className="mt-6 flex justify-end gap-3">
                <button type="button" onClick={() => setShowAddDoctor(false)} className="px-5 py-2 border rounded-lg font-medium">Cancel</button>
                <button type="submit" disabled={addDocLoading} className="px-5 py-2 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 disabled:opacity-50">
                  {addDocLoading ? "Saving..." : "Add Doctor"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
