"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { appointmentsAPI, AppointmentInfo } from "@/lib/api";

const STATUS_BADGES: Record<string, string> = {
  Confirmed: "badge-confirmed",
  Completed: "badge-completed",
  Cancelled: "badge-cancelled",
  Rejected: "badge-rejected",
  Requested: "badge-requested",
  "Payment Pending": "badge-requested",
  Rescheduled: "badge-rescheduled",
};

export default function DoctorDashboard() {
  const router = useRouter();
  const { user, token, loading: authLoading, isDoctor } = useAuth();
  const [appointments, setAppointments] = useState<AppointmentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState("");
  const [msg, setMsg] = useState("");
  const [tab, setTab] = useState<"upcoming" | "all">("upcoming");

  useEffect(() => {
    if (authLoading) return;
    if (!user || !isDoctor) { router.push("/auth/login"); return; }
    
    let active = true;
    const fetchApts = async () => {
      if (!token) return;
      setLoading(true);
      try {
        const apts = await appointmentsAPI.doctorList(token);
        if (active) setAppointments(apts);
      } catch { /* empty */ }
      if (active) setLoading(false);
    };
    fetchApts();
    return () => { active = false; };
  }, [user, authLoading, isDoctor, router, token]);

  const fetchAppointments = async () => {
    if (!token) return;
    try {
      const apts = await appointmentsAPI.doctorList(token);
      setAppointments(apts);
    } catch { /* empty */ }
  };

  const handleAction = async (id: string, action: string) => {
    if (!token) return;
    setActionId(id);
    try {
      await appointmentsAPI.doctorAction(token, id, action);
      setMsg(`Appointment ${action.toLowerCase()}ed successfully`);
      fetchAppointments();
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Action failed");
    }
    setActionId("");
  };

  const handleComplete = async (id: string) => {
    if (!token) return;
    setActionId(id);
    try {
      await appointmentsAPI.complete(token, id);
      setMsg("Appointment marked as completed");
      fetchAppointments();
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Failed");
    }
    setActionId("");
  };

  const today = new Date().toISOString().split("T")[0];
  const upcoming = appointments.filter(a => ["Confirmed", "Requested", "Pending", "Payment Pending"].includes(a.status) && a.appointment_date >= today);
  const displayList = tab === "upcoming" ? upcoming : appointments;

  if (authLoading || loading) {
    return <div className="max-w-5xl mx-auto px-4 py-12"><div className="skeleton h-8 w-1/2 mb-4" /><div className="skeleton h-40 w-full" /></div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Doctor Dashboard</h1>
          <p className="text-gray-500 mt-1">Welcome, {user?.name}</p>
        </div>

        {msg && (
          <div className="mb-6 p-4 bg-teal-50 border border-teal-200 rounded-xl text-teal-800 text-sm flex justify-between">
            {msg}
            <button onClick={() => setMsg("")} className="text-teal-600">✕</button>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Total", value: appointments.length, color: "bg-gray-50 text-gray-800" },
            { label: "Upcoming", value: upcoming.length, color: "bg-teal-50 text-teal-800" },
            { label: "Completed", value: appointments.filter(a => a.status === "Completed").length, color: "bg-blue-50 text-blue-800" },
            { label: "Pending", value: appointments.filter(a => ["Requested", "Pending"].includes(a.status)).length, color: "bg-purple-50 text-purple-800" },
          ].map((s) => (
            <div key={s.label} className={`${s.color} rounded-2xl p-5 text-center border border-gray-100`}>
              <div className="text-2xl font-bold">{s.value}</div>
              <div className="text-sm opacity-70">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button onClick={() => setTab("upcoming")} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === "upcoming" ? "bg-teal-600 text-white" : "bg-white text-gray-600 border border-gray-200"}`}>
            Upcoming
          </button>
          <button onClick={() => setTab("all")} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === "all" ? "bg-teal-600 text-white" : "bg-white text-gray-600 border border-gray-200"}`}>
            All Appointments
          </button>
        </div>

        {displayList.length === 0 ? (
          <div className="bg-white rounded-2xl border border-gray-100 p-12 text-center">
            <div className="text-4xl mb-3">📋</div>
            <p className="text-gray-500">No appointments to display</p>
          </div>
        ) : (
          <div className="space-y-4">
            {displayList.map((apt) => (
              <div key={apt.id} className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-semibold text-gray-900">{apt.patient_name}</h3>
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${STATUS_BADGES[apt.status] || ""}`}>{apt.status}</span>
                    </div>
                    <p className="text-sm text-gray-500">📅 {apt.appointment_date} at {apt.start_time} – {apt.end_time}</p>
                    {apt.reason && <p className="text-sm text-gray-400 mt-1">Reason: {apt.reason}</p>}
                  </div>
                  <div className="flex gap-2">
                    {["Requested", "Pending"].includes(apt.status) && (
                      <>
                        <button onClick={() => handleAction(apt.id, "Accept")} disabled={actionId === apt.id}
                          className="px-4 py-2 bg-green-50 text-green-700 text-sm font-medium rounded-lg hover:bg-green-100 transition-colors disabled:opacity-50">
                          Accept
                        </button>
                        <button onClick={() => handleAction(apt.id, "Reject")} disabled={actionId === apt.id}
                          className="px-4 py-2 bg-red-50 text-red-600 text-sm font-medium rounded-lg hover:bg-red-100 transition-colors disabled:opacity-50">
                          Reject
                        </button>
                      </>
                    )}
                    {apt.status === "Payment Pending" && (
                      <span className="text-sm font-medium text-amber-600 bg-amber-50 px-3 py-1.5 rounded-lg">Awaiting patient payment</span>
                    )}
                    {apt.status === "Confirmed" && (
                      <button onClick={() => handleComplete(apt.id)} disabled={actionId === apt.id}
                        className="px-4 py-2 bg-blue-50 text-blue-700 text-sm font-medium rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50">
                        Mark Complete
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
