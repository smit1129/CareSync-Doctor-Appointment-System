"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { appointmentsAPI, feedbackAPI, doctorsAPI, AppointmentInfo, TimeSlot } from "@/lib/api";
import Link from "next/link";

const STATUS_BADGES: Record<string, string> = {
  Confirmed: "badge-confirmed",
  Completed: "badge-completed",
  Cancelled: "badge-cancelled",
  Rejected: "badge-rejected",
  Requested: "badge-requested",
  "Payment Pending": "badge-requested",
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
  const [msgType, setMsgType] = useState<"success" | "error">("success");

  // Reschedule modal state
  const [rescheduleApt, setRescheduleApt] = useState<AppointmentInfo | null>(null);
  const [newDate, setNewDate] = useState("");
  const [slots, setSlots] = useState<TimeSlot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState("");
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [rescheduling, setRescheduling] = useState(false);

  const showMsg = (text: string, type: "success" | "error" = "success") => {
    setMsg(text);
    setMsgType(type);
    setTimeout(() => setMsg(""), 5000);
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "Requested": return "Awaiting Doctor Approval";
      case "Payment Pending": return "Request Accepted — Complete Payment";
      case "Confirmed": return "Appointment Confirmed";
      case "Rejected": return "Appointment Rejected";
      default: return status;
    }
  };

  // Payment modal state
  const [payApt, setPayApt] = useState<AppointmentInfo | null>(null);
  const [paymentMode, setPaymentMode] = useState("card");
  const [paying, setPaying] = useState(false);

  const fetchAppointments = async () => {
    if (!token) return;
    try {
      const apts = await appointmentsAPI.patientHistory(token);
      setAppointments(apts);
    } catch { /* empty */ }
  };

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

  const handleCancel = async (id: string) => {
    if (!token) return;
    if (!window.confirm("Are you sure you want to cancel this appointment?")) return;
    setCancellingId(id);
    try {
      await appointmentsAPI.cancel(token, id, "Cancelled by patient");
      showMsg("Appointment cancelled successfully. Refund will be processed if applicable.");
      fetchAppointments();
    } catch (err: unknown) {
      showMsg(err instanceof Error ? err.message : "Cancel failed", "error");
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
      showMsg("Thank you for your feedback!");
    } catch (err: unknown) {
      showMsg(err instanceof Error ? err.message : "Feedback failed", "error");
    }
    setFeedbackSubmitting(false);
  };

  // --- Reschedule handlers ---
  const openReschedule = (apt: AppointmentInfo) => {
    setRescheduleApt(apt);
    setNewDate("");
    setSlots([]);
    setSelectedSlot("");
  };

  const closeReschedule = () => {
    setRescheduleApt(null);
    setNewDate("");
    setSlots([]);
    setSelectedSlot("");
  };

  const loadSlots = async (doctorId: string, date: string) => {
    if (!date) return;
    setSlotsLoading(true);
    setSelectedSlot("");
    try {
      const available = await doctorsAPI.getSlots(doctorId, date);
      setSlots(available);
    } catch {
      setSlots([]);
    }
    setSlotsLoading(false);
  };

  const handleNewDateChange = (date: string) => {
    setNewDate(date);
    if (rescheduleApt) {
      loadSlots(rescheduleApt.doctor_id, date);
    }
  };

  const handleReschedule = async () => {
    if (!token || !rescheduleApt || !newDate || !selectedSlot) return;
    setRescheduling(true);
    try {
      await appointmentsAPI.reschedule(token, rescheduleApt.id, {
        new_date: newDate,
        new_start_time: selectedSlot,
      });
      showMsg("Appointment rescheduled successfully!");
      closeReschedule();
      fetchAppointments();
    } catch (err: unknown) {
      showMsg(err instanceof Error ? err.message : "Reschedule failed", "error");
    }
    setRescheduling(false);
  };

  const handlePayment = async () => {
    if (!token || !payApt) return;
    setPaying(true);
    try {
      // Use existing payment API
      const { paymentsAPI } = await import("@/lib/api");
      await paymentsAPI.process(token, {
        appointment_id: payApt.id,
        amount: 500, // Fallback, could fetch doc fee if available
        payment_mode: paymentMode,
      });
      showMsg("Payment successful! Your appointment is now confirmed.");
      setPayApt(null);
      fetchAppointments();
    } catch (err: unknown) {
      showMsg(err instanceof Error ? err.message : "Payment failed", "error");
    }
    setPaying(false);
  };

  const todayStr = new Date().toISOString().split("T")[0];
  const upcoming = appointments.filter(a => ["Confirmed", "Requested", "Payment Pending"].includes(a.status));
  const past = appointments.filter(a => !["Confirmed", "Requested", "Payment Pending"].includes(a.status));
  const rescheduleEligible = (apt: AppointmentInfo) =>
    ["Confirmed", "Requested", "Payment Pending"].includes(apt.status);

  if (authLoading || loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="skeleton h-8 w-1/2 mb-4" />
        <div className="skeleton h-40 w-full" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Patient Dashboard</h1>
            <p className="text-muted-foreground mt-1">Welcome back, {user?.name}</p>
          </div>
          <Link href="/doctors" className="px-5 py-2.5 bg-primary text-primary-foreground font-semibold rounded-xl hover:bg-primary/90 transition-all shadow-sm">
            + Book Appointment
          </Link>
        </div>

        {msg && (
          <div className={`mb-6 p-4 rounded-xl text-sm flex items-center justify-between border ${
            msgType === "success"
              ? "bg-teal-50 dark:bg-teal-950/50 border-teal-300 dark:border-teal-800 text-teal-900 dark:text-teal-200 font-medium"
              : "bg-rose-50 dark:bg-rose-950/50 border-rose-300 dark:border-rose-800 text-rose-900 dark:text-rose-200 font-medium"
          }`}>
            <span>{msg}</span>
            <button onClick={() => setMsg("")} className="ml-4 font-bold opacity-60 hover:opacity-100">✕</button>
          </div>
        )}

        {/* Upcoming */}
        <div className="mb-10">
          <h2 className="text-xl font-bold text-foreground mb-4">Upcoming Appointments ({upcoming.length})</h2>
          {upcoming.length === 0 ? (
            <div className="bg-surface rounded-2xl border border-border p-8 text-center">
              <div className="text-4xl mb-3">📅</div>
              <p className="text-muted-foreground">No upcoming appointments</p>
              <Link href="/doctors" className="inline-block mt-4 text-accent font-semibold hover:underline">Find a Doctor →</Link>
            </div>
          ) : (
            <div className="space-y-4">
              {upcoming.map((apt) => (
                <div key={apt.id} className="bg-surface rounded-2xl border border-border p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:shadow-md transition-shadow">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-semibold text-foreground">{apt.doctor_name}</h3>
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${STATUS_BADGES[apt.status] || ""}`}>
                        {getStatusText(apt.status)}
                      </span>
                    </div>
                    <p className="text-sm text-accent font-medium">{apt.doctor_specialization}</p>
                    <p className="text-sm text-muted-foreground mt-1">📅 {apt.appointment_date} at {apt.start_time} – {apt.end_time}</p>
                    {apt.reason && <p className="text-sm text-muted-foreground mt-1">Reason: {apt.reason}</p>}
                  </div>
                  <div className="flex gap-2 shrink-0">
                    {rescheduleEligible(apt) && (
                      <button
                        onClick={() => openReschedule(apt)}
                        className="px-4 py-2 bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/60 dark:hover:bg-blue-900/70 text-blue-800 dark:text-blue-200 border border-blue-300 dark:border-blue-700 text-sm font-semibold rounded-lg transition-colors focus:ring-2 focus:ring-blue-400 focus:outline-none"
                      >
                        🔄 Reschedule
                      </button>
                    )}
                    {apt.status === "Payment Pending" && (
                      <button
                        onClick={() => setPayApt(apt)}
                        className="px-4 py-2 bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-950/60 dark:hover:bg-emerald-900/70 text-emerald-800 dark:text-emerald-200 border border-emerald-300 dark:border-emerald-700 text-sm font-semibold rounded-lg transition-colors shadow-xs focus:ring-2 focus:ring-emerald-400 focus:outline-none"
                      >
                        💳 Complete Payment
                      </button>
                    )}
                    <button
                      onClick={() => handleCancel(apt.id)}
                      disabled={cancellingId === apt.id}
                      className="px-4 py-2 bg-red-50 hover:bg-red-100 dark:bg-red-950/60 dark:hover:bg-red-900/70 text-red-800 dark:text-red-200 border border-red-300 dark:border-red-700 text-sm font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-red-400 focus:outline-none"
                    >
                      {cancellingId === apt.id ? "Cancelling..." : "Cancel"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Past */}
        <div>
          <h2 className="text-xl font-bold text-foreground mb-4">Past Appointments ({past.length})</h2>
          {past.length === 0 ? (
            <div className="bg-surface rounded-2xl border border-border p-8 text-center text-muted-foreground">No past appointments</div>
          ) : (
            <div className="space-y-3">
              {past.map((apt) => (
                <div key={apt.id} className="bg-surface rounded-xl border border-border p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-foreground">{apt.doctor_name}</h4>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_BADGES[apt.status] || ""}`}>
                        {getStatusText(apt.status)}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">{apt.appointment_date} at {apt.start_time} • {apt.doctor_specialization}</p>
                    {apt.cancellation_reason && (
                      <p className="text-xs text-muted-foreground mt-0.5">Reason: {apt.cancellation_reason}</p>
                    )}
                  </div>
                  {apt.status === "Completed" && !feedbackDone.has(apt.id) && (
                    <button onClick={() => setFeedbackAptId(apt.id)}
                      className="px-4 py-2 bg-amber-100 hover:bg-amber-200 text-amber-950 border border-amber-300 text-sm font-semibold rounded-lg transition-colors focus:ring-2 focus:ring-amber-400 focus:outline-none dark:bg-amber-950/60 dark:hover:bg-amber-900/70 dark:text-amber-200 dark:border-amber-700">
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
          <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <div className="bg-surface rounded-2xl shadow-2xl max-w-md w-full p-6 border border-border">
              <h3 className="text-xl font-bold text-foreground mb-4">Rate Your Experience</h3>
              <div className="flex gap-2 mb-4">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button key={star} onClick={() => setRating(star)} className={`text-3xl transition-colors ${star <= rating ? "text-amber-400" : "text-border"}`}>★</button>
                ))}
              </div>
              <textarea value={comment} onChange={(e) => setComment(e.target.value)} rows={3} placeholder="Share your experience..."
                className="w-full px-4 py-3 rounded-xl border border-border bg-surface text-foreground focus:ring-2 focus:ring-accent outline-none mb-4" />
              <div className="flex gap-3">
                <button onClick={() => setFeedbackAptId("")} className="flex-1 py-2.5 border border-border text-foreground/70 rounded-xl hover:bg-surface-subtle font-medium">Cancel</button>
                <button onClick={handleFeedback} disabled={feedbackSubmitting}
                  className="flex-1 py-2.5 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 font-semibold disabled:opacity-50 transition-colors">
                  {feedbackSubmitting ? "Submitting..." : "Submit Review"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Reschedule Modal */}
        {rescheduleApt && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <div className="bg-surface rounded-2xl shadow-2xl max-w-md w-full p-6 border border-border">
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-xl font-bold text-foreground">Reschedule Appointment</h3>
                <button onClick={closeReschedule} className="text-muted-foreground hover:text-foreground text-xl font-bold">✕</button>
              </div>

              <div className="bg-surface-subtle border border-border rounded-xl p-4 mb-5 text-sm">
                <p className="font-semibold text-foreground">{rescheduleApt.doctor_name}</p>
                <p className="text-accent font-medium">{rescheduleApt.doctor_specialization}</p>
                <p className="text-muted-foreground mt-1">Current: {rescheduleApt.appointment_date} at {rescheduleApt.start_time}</p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-foreground/80 mb-1.5">Select New Date</label>
                <input
                  type="date"
                  min={todayStr}
                  value={newDate}
                  onChange={(e) => handleNewDateChange(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-border bg-surface text-foreground focus:ring-2 focus:ring-accent outline-none"
                />
              </div>

              {newDate && (
                <div className="mb-5">
                  <label className="block text-sm font-medium text-foreground/80 mb-2">Available Time Slots</label>
                  {slotsLoading ? (
                    <div className="text-center py-4 text-muted-foreground text-sm">Loading slots...</div>
                  ) : slots.length === 0 ? (
                    <div className="text-center py-4 text-muted-foreground text-sm bg-surface-subtle border border-border rounded-xl">
                      No available slots on this date. Please choose a different day.
                    </div>
                  ) : (
                    <div className="grid grid-cols-3 gap-2 max-h-48 overflow-y-auto">
                      {slots.map((slot) => (
                        <button
                          key={slot.start_time}
                          disabled={!slot.is_available}
                          onClick={() => setSelectedSlot(slot.start_time)}
                          className={`py-2 px-1 text-xs rounded-lg text-center transition-all ${
                            !slot.is_available
                              ? "bg-surface-subtle text-muted-foreground/40 border border-border/60 cursor-not-allowed line-through font-normal"
                              : selectedSlot === slot.start_time
                              ? "bg-primary text-primary-foreground shadow-sm font-bold border border-primary"
                              : "bg-teal-50/70 hover:bg-teal-100/90 dark:bg-surface dark:hover:bg-surface-subtle border border-teal-200/80 dark:border-border text-teal-950 dark:text-foreground font-semibold"
                          }`}
                        >
                          {slot.start_time}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <div className="flex gap-3">
                <button onClick={closeReschedule} className="flex-1 py-2.5 border border-border text-foreground/70 rounded-xl hover:bg-surface-subtle font-medium">
                  Cancel
                </button>
                <button
                  onClick={handleReschedule}
                  disabled={!newDate || !selectedSlot || rescheduling}
                  className="flex-1 py-2.5 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 font-semibold disabled:opacity-50 transition-colors"
                >
                  {rescheduling ? "Rescheduling..." : "Confirm Reschedule"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Payment Modal */}
        {payApt && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <div className="bg-surface rounded-2xl shadow-2xl max-w-md w-full p-6 border border-border">
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-xl font-bold text-foreground">Complete Payment</h3>
                <button onClick={() => setPayApt(null)} className="text-muted-foreground hover:text-foreground text-xl font-bold">✕</button>
              </div>

              <div className="bg-surface-subtle border border-border rounded-xl p-4 mb-5 text-sm text-center">
                <p className="font-semibold text-foreground mb-1">Appointment with {payApt.doctor_name}</p>
                <p className="text-muted-foreground">{payApt.appointment_date} at {payApt.start_time}</p>
                <div className="mt-3 text-2xl font-bold text-foreground">₹500</div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-foreground/80 mb-3">Select Payment Method</label>
                <div className="flex gap-2">
                  {[
                    { key: "card", label: "💳 Card" },
                    { key: "upi", label: "📱 UPI" },
                    { key: "netbanking", label: "🏦 Net" },
                  ].map(m => (
                    <button key={m.key} onClick={() => setPaymentMode(m.key)}
                      className={`flex-1 py-2.5 rounded-xl text-sm transition-all ${paymentMode === m.key ? "bg-teal-50/90 dark:bg-accent/15 border-2 border-teal-600 dark:border-accent text-teal-950 dark:text-accent font-semibold" : "bg-surface hover:bg-surface-subtle border border-border text-foreground/80 hover:border-teal-400 font-medium"}`}>
                      {m.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-3">
                <button onClick={() => setPayApt(null)} className="flex-1 py-3 border border-border text-foreground/70 rounded-xl hover:bg-surface-subtle font-medium">
                  Cancel
                </button>
                <button
                  onClick={handlePayment}
                  disabled={paying}
                  className="flex-1 py-3 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 font-semibold disabled:opacity-50 transition-all shadow-md"
                >
                  {paying ? "Processing..." : "Pay Securely"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
