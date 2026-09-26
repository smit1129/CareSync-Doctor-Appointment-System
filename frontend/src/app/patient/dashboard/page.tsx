"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { appointmentsAPI, feedbackAPI, AppointmentInfo } from "@/lib/api";
import Link from "next/link";

const STATUS_BADGES: Record<string, string> = {
  Confirmed: "badge-confirmed",
  Completed: "badge-completed",
  Cancelled: "badge-cancelled",
  Rejected: "badge-rejected",
  Requested: "badge-requested",
  Rescheduled: "badge-rescheduled",
};

export default function PatientDashboard() {
  const router = useRouter();
  const { user, token, loading: authLoading, isPatient } = useAuth();
  const [appointments, setAppointments] = useState<AppointmentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState("");
  const [feedbackAptId, setFeedbackAptId] = useState("");
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);
  const [feedbackDone, setFeedbackDone] = useState<Set<string>>(new Set());
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (authLoading) return;
    if (!user || !isPatient) { router.push("/auth/login"); return; }
    
    let active = true;
    const fetchApts = async () => {
      if (!token) return;
      setLoading(true);
      try {
        const apts = await appointmentsAPI.patientHistory(token);
        if (active) setAppointments(apts);
      } catch { /* empty */ }
      if (active) setLoading(false);
    };
    fetchApts();
    
    return () => { active = false; };
  }, [user, authLoading, isPatient, router, token]);

  const fetchAppointments = async () => {
    if (!token) return;
    try {
      const apts = await appointmentsAPI.patientHistory(token);
      setAppointments(apts);
    } catch { /* empty */ }
  };

  const handleCancel = async (id: string) => {
    if (!token) return;
    setCancellingId(id);
    try {
      await appointmentsAPI.cancel(token, id, "Cancelled by patient");
      setMsg("Appointment cancelled successfully. Refund will be processed if applicable.");
      fetchAppointments();
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Cancel failed");
    }
    setCancellingId("");
  };

  const handleFeedback = async () => {
    if (!token || !feedbackAptId) return;
    setFeedbackSubmitting(true);
    try {
      await feedbackAPI.submit(token, { appointment_id: feedbackAptId, rating, comment });
      setFeedbackDone(prev => new Set(prev).add(feedbackAptId));
      setFeedbackAptId("");
      setComment("");
      setRating(5);
      setMsg("Thank you for your feedback!");
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Feedback failed");
    }
    setFeedbackSubmitting(false);
  };

  const upcoming = appointments.filter(a => ["Confirmed", "Requested"].includes(a.status));
  const past = appointments.filter(a => !["Confirmed", "Requested"].includes(a.status));

  if (authLoading || loading) {
    return <div className="max-w-5xl mx-auto px-4 py-12"><div className="skeleton h-8 w-1/2 mb-4" /><div className="skeleton h-40 w-full" /></div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Patient Dashboard</h1>
            <p className="text-gray-500">Welcome back, {user?.name}</p>
          </div>
          <Link href="/doctors" className="px-5 py-2.5 bg-teal-600 text-white font-semibold rounded-xl hover:bg-teal-700 transition-colors shadow">
            + Book Appointment
          </Link>
        </div>

        {msg && (
          <div className="mb-6 p-4 bg-teal-50 border border-teal-200 rounded-xl text-teal-800 text-sm flex items-center justify-between">
            {msg}
            <button onClick={() => setMsg("")} className="text-teal-600 hover:text-teal-800">✕</button>
          </div>
        )}

        {/* Upcoming */}
        <div className="mb-10">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Upcoming Appointments ({upcoming.length})</h2>
          {upcoming.length === 0 ? (
            <div className="bg-white rounded-2xl border border-gray-100 p-8 text-center">
              <div className="text-4xl mb-3">📅</div>
              <p className="text-gray-500">No upcoming appointments</p>
              <Link href="/doctors" className="inline-block mt-4 text-teal-600 font-semibold hover:text-teal-700">Find a Doctor →</Link>
            </div>
          ) : (
            <div className="space-y-4">
              {upcoming.map((apt) => (
                <div key={apt.id} className="bg-white rounded-2xl border border-gray-100 p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:shadow-sm transition-shadow">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-semibold text-gray-900">{apt.doctor_name}</h3>
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${STATUS_BADGES[apt.status] || ""}`}>{apt.status}</span>
                    </div>
                    <p className="text-sm text-teal-600">{apt.doctor_specialization}</p>
                    <p className="text-sm text-gray-500 mt-1">📅 {apt.appointment_date} at {apt.start_time} – {apt.end_time}</p>
                    {apt.reason && <p className="text-sm text-gray-400 mt-1">Reason: {apt.reason}</p>}
                  </div>
                  <button onClick={() => handleCancel(apt.id)} disabled={cancellingId === apt.id}
                    className="px-4 py-2 bg-red-50 text-red-600 text-sm font-medium rounded-lg hover:bg-red-100 transition-colors disabled:opacity-50">
                    {cancellingId === apt.id ? "Cancelling..." : "Cancel"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Past */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Past Appointments ({past.length})</h2>
          {past.length === 0 ? (
            <div className="bg-white rounded-2xl border border-gray-100 p-8 text-center text-gray-400">No past appointments</div>
          ) : (
            <div className="space-y-3">
              {past.map((apt) => (
                <div key={apt.id} className="bg-white rounded-xl border border-gray-100 p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-gray-800">{apt.doctor_name}</h4>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_BADGES[apt.status] || ""}`}>{apt.status}</span>
                    </div>
                    <p className="text-xs text-gray-500">{apt.appointment_date} at {apt.start_time} • {apt.doctor_specialization}</p>
                  </div>
                  {apt.status === "Completed" && !feedbackDone.has(apt.id) && (
                    <button onClick={() => setFeedbackAptId(apt.id)}
                      className="px-4 py-2 bg-amber-50 text-amber-700 text-sm font-medium rounded-lg hover:bg-amber-100 transition-colors">
                      ⭐ Rate
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Feedback Modal */}
        {feedbackAptId && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Rate Your Experience</h3>
              <div className="flex gap-2 mb-4">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button key={star} onClick={() => setRating(star)} className={`text-3xl transition-colors ${star <= rating ? "text-amber-400" : "text-gray-200"}`}>
                    ★
                  </button>
                ))}
              </div>
              <textarea value={comment} onChange={(e) => setComment(e.target.value)} rows={3} placeholder="Share your experience..."
                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-800 focus:ring-2 focus:ring-teal-500 outline-none mb-4" />
              <div className="flex gap-3">
                <button onClick={() => setFeedbackAptId("")} className="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 font-medium">Cancel</button>
                <button onClick={handleFeedback} disabled={feedbackSubmitting}
                  className="flex-1 py-2.5 bg-teal-600 text-white rounded-xl hover:bg-teal-700 font-semibold disabled:opacity-50">
                  {feedbackSubmitting ? "Submitting..." : "Submit Review"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
