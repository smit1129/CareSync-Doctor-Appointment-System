"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { doctorsAPI, appointmentsAPI, paymentsAPI, feedbackAPI, DoctorInfo, TimeSlot, FeedbackInfo } from "@/lib/api";

const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export default function DoctorDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user, token } = useAuth();
  const doctorId = params.id as string;

  const [doctor, setDoctor] = useState<DoctorInfo | null>(null);
  const [reviews, setReviews] = useState<FeedbackInfo[]>([]);
  const [slots, setSlots] = useState<TimeSlot[]>([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedSlot, setSelectedSlot] = useState("");
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(true);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [bookingStatus, setBookingStatus] = useState<"idle" | "booking" | "paying" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const [paymentMode, setPaymentMode] = useState("card");

  // Generate next 14 days
  const dateOptions = React.useMemo(() => {
    const options: { label: string; value: string; dayName: string }[] = [];
    for (let i = 0; i < 14; i++) {
      const d = new Date();
      d.setDate(d.getDate() + i);
      const iso = d.toISOString().split("T")[0];
      const dayName = DAY_NAMES[d.getDay() === 0 ? 6 : d.getDay() - 1];
      const label = d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
      options.push({ label, value: iso, dayName });
    }
    return options;
  }, []);

  useEffect(() => {
    let active = true;
    const fetchDoc = async () => {
      try {
        const [doc, fb] = await Promise.all([
          doctorsAPI.getById(doctorId),
          feedbackAPI.getDoctorFeedbacks(doctorId),
        ]);
        if (active) {
          setDoctor(doc);
          setReviews(fb);
        }
      } catch {
        if (active) setErrorMsg("Failed to load doctor details");
      }
      if (active) setLoading(false);
    };
    fetchDoc();
    return () => { active = false; };
  }, [doctorId]);

  useEffect(() => {
    if (!selectedDate || !doctorId) return;
    let active = true;
    const fetchSlots = async () => {
      setSlotsLoading(true);
      try {
        const slotsData = await doctorsAPI.getSlots(doctorId, selectedDate);
        if (active) {
          setSlots(slotsData);
          setSelectedSlot("");
        }
      } catch {
        if (active) setSlots([]);
      }
      if (active) setSlotsLoading(false);
    };
    fetchSlots();
    return () => { active = false; };
  }, [selectedDate, doctorId]);

  useEffect(() => {
    if (!loading && !selectedDate && dateOptions.length > 0) {
      Promise.resolve().then(() => setSelectedDate(dateOptions[0].value));
    }
  }, [loading, selectedDate, dateOptions]);

  const handleBook = async () => {
    if (!token || !user) {
      router.push("/auth/login");
      return;
    }
    if (!selectedSlot || !selectedDate) return;
    setBookingStatus("booking");
    setErrorMsg("");
    try {
      const apt = await appointmentsAPI.book(token, {
        doctor_id: doctorId,
        appointment_date: selectedDate,
        start_time: selectedSlot,
        reason: reason || "General Consultation",
      });
      // Process payment
      setBookingStatus("paying");
      await paymentsAPI.process(token, {
        appointment_id: apt.id,
        amount: doctor?.consultation_fee || 500,
        payment_mode: paymentMode,
      });
      setBookingStatus("success");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Booking failed";
      setErrorMsg(message);
      setBookingStatus("error");
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="skeleton h-8 w-1/2 mb-4" />
        <div className="skeleton h-6 w-1/3 mb-3" />
        <div className="skeleton h-40 w-full mb-4" />
        <div className="skeleton h-32 w-full" />
      </div>
    );
  }

  if (!doctor) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <div className="text-5xl mb-4">😔</div>
        <h2 className="text-2xl font-bold text-gray-700">Doctor not found</h2>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Doctor Profile Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8 mb-8">
          <div className="flex flex-col sm:flex-row gap-6">
            <div className="w-20 h-20 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-2xl flex items-center justify-center text-white text-2xl font-bold shrink-0">
              {doctor.name.charAt(4) || "D"}
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900">{doctor.name}</h1>
              <p className="text-teal-600 font-semibold">{doctor.specialization}</p>
              <p className="text-sm text-gray-500 mt-1">{doctor.qualification} • {doctor.experience_years} years experience</p>
              <p className="text-sm text-gray-400 mt-1">📍 {doctor.clinic_address}</p>
              {doctor.bio && <p className="text-sm text-gray-600 mt-3 leading-relaxed">{doctor.bio}</p>}
              <div className="flex items-center gap-4 mt-4">
                <div className="flex items-center gap-1 bg-amber-50 px-3 py-1.5 rounded-lg">
                  <span className="text-amber-500">★</span>
                  <span className="font-semibold text-amber-700">{doctor.rating_avg}</span>
                  <span className="text-sm text-amber-500">({doctor.rating_count} reviews)</span>
                </div>
                <div className="text-xl font-bold text-gray-900">₹{doctor.consultation_fee}</div>
              </div>
            </div>
          </div>

          {/* Schedule info */}
          {doctor.availabilities && doctor.availabilities.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-100">
              <h3 className="font-semibold text-gray-700 mb-3">Schedule</h3>
              <div className="flex flex-wrap gap-2">
                {doctor.availabilities.filter(a => a.is_active).map((a) => (
                  <span key={a.id} className="text-xs bg-teal-50 text-teal-700 px-3 py-1.5 rounded-lg">
                    {DAY_NAMES[a.day_of_week]} {a.start_time}–{a.end_time}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Booking Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Book Appointment</h2>

              {bookingStatus === "success" ? (
                <div className="text-center py-8">
                  <div className="text-5xl mb-4">🎉</div>
                  <h3 className="text-xl font-bold text-green-700 mb-2">Appointment Booked Successfully!</h3>
                  <p className="text-gray-500 mb-6">Payment processed. You will receive a confirmation notification.</p>
                  <button onClick={() => router.push("/patient/dashboard")}
                    className="px-6 py-3 bg-teal-600 text-white font-semibold rounded-xl hover:bg-teal-700 transition-colors">
                    View My Appointments
                  </button>
                </div>
              ) : (
                <>
                  {/* Date Picker */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-3">Select Date</label>
                    <div className="flex overflow-x-auto gap-2 pb-2">
                      {dateOptions.map((d) => (
                        <button key={d.value} onClick={() => setSelectedDate(d.value)}
                          className={`shrink-0 px-4 py-3 rounded-xl text-sm font-medium transition-all ${selectedDate === d.value ? "bg-teal-600 text-white shadow" : "bg-gray-50 text-gray-600 border border-gray-200 hover:border-teal-300"}`}>
                          <div className="text-xs opacity-70">{d.dayName.slice(0, 3)}</div>
                          <div>{d.label.split(", ")[0]?.split(" ").pop()}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Slot Picker */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-3">Select Time Slot</label>
                    {slotsLoading ? (
                      <div className="grid grid-cols-4 sm:grid-cols-6 gap-2">
                        {[1,2,3,4,5,6,7,8].map(i => <div key={i} className="skeleton h-10 rounded-lg" />)}
                      </div>
                    ) : slots.length === 0 ? (
                      <div className="text-center py-8 bg-gray-50 rounded-xl text-gray-400">
                        <p>No slots available for this date</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-6 gap-2">
                        {slots.map((s) => (
                          <button key={s.start_time} disabled={!s.is_available}
                            onClick={() => setSelectedSlot(s.start_time)}
                            className={`py-2.5 px-2 rounded-lg text-sm font-medium transition-all ${!s.is_available ? "bg-gray-100 text-gray-300 cursor-not-allowed line-through" : selectedSlot === s.start_time ? "bg-teal-600 text-white shadow" : "bg-white border border-gray-200 text-gray-700 hover:border-teal-400"}`}>
                            {s.start_time}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Reason */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Reason for Visit</label>
                    <input type="text" value={reason} onChange={(e) => setReason(e.target.value)}
                      placeholder="Describe your symptoms or consultation purpose"
                      className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-800 focus:ring-2 focus:ring-teal-500 outline-none" />
                  </div>

                  {/* Payment Mode */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-3">Payment Method</label>
                    <div className="flex gap-3">
                      {[
                        { key: "card", label: "💳 Card", },
                        { key: "upi", label: "📱 UPI", },
                        { key: "netbanking", label: "🏦 Netbanking", },
                      ].map(m => (
                        <button key={m.key} onClick={() => setPaymentMode(m.key)}
                          className={`flex-1 py-3 rounded-xl text-sm font-medium transition-all ${paymentMode === m.key ? "bg-teal-50 border-2 border-teal-500 text-teal-700" : "bg-gray-50 border border-gray-200 text-gray-600 hover:border-teal-300"}`}>
                          {m.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {errorMsg && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{errorMsg}</div>}

                  <button onClick={handleBook} disabled={!selectedSlot || !selectedDate || bookingStatus === "booking" || bookingStatus === "paying"}
                    className="w-full py-3.5 bg-gradient-to-r from-teal-600 to-cyan-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                    {bookingStatus === "booking" ? "Booking..." : bookingStatus === "paying" ? "Processing Payment..." : `Book & Pay ₹${doctor.consultation_fee}`}
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Reviews Sidebar */}
          <div>
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="font-bold text-gray-900 mb-4">Patient Reviews ({reviews.length})</h3>
              {reviews.length === 0 ? (
                <p className="text-sm text-gray-400">No reviews yet</p>
              ) : (
                <div className="space-y-4">
                  {reviews.slice(0, 5).map((r) => (
                    <div key={r.id} className="pb-4 border-b border-gray-50 last:border-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-amber-500 text-sm">{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</span>
                      </div>
                      <p className="text-sm text-gray-600">{r.comment || "Great experience!"}</p>
                      <p className="text-xs text-gray-400 mt-1">— {r.patient_name}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
