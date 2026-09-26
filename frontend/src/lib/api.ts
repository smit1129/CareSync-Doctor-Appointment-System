const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string | null;
  headers?: Record<string, string>;
}

export async function apiFetch<T = unknown>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = "GET", body, token, headers: extraHeaders } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...extraHeaders,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    const error = new Error(errorData.detail || `Request failed with status ${res.status}`) as Error & { status: number; data: unknown };
    error.status = res.status;
    error.data = errorData;
    throw error;
  }

  return res.json() as Promise<T>;
}

// Auth API
export const authAPI = {
  register: (data: { name: string; email: string; phone?: string; password: string; role?: string }) =>
    apiFetch("/auth/register", { method: "POST", body: data }),

  login: (data: { email: string; password: string }) =>
    apiFetch<{ access_token: string; user_id: string; role: string; name: string; email: string }>(
      "/auth/login",
      { method: "POST", body: data }
    ),

  forgotPassword: (email: string) =>
    apiFetch("/auth/forgot-password", { method: "POST", body: { email } }),

  getMe: (token: string) =>
    apiFetch<{ id: string; email: string; full_name: string; role: string; patient_id?: string; doctor_id?: string }>(
      "/auth/me",
      { token }
    ),
};

// Doctors API
export const doctorsAPI = {
  list: (params?: { specialization?: string; search?: string }) => {
    const qs = new URLSearchParams();
    if (params?.specialization) qs.set("specialization", params.specialization);
    if (params?.search) qs.set("search", params.search);
    const query = qs.toString();
    return apiFetch<DoctorInfo[]>(`/doctors${query ? `?${query}` : ""}`);
  },

  getById: (id: string) => apiFetch<DoctorInfo>(`/doctors/${id}`),

  getSlots: (doctorId: string, targetDate: string) =>
    apiFetch<TimeSlot[]>(`/doctors/${doctorId}/slots?target_date=${targetDate}`),

  getSpecializations: () => apiFetch<string[]>("/doctors/specializations"),

  updateAvailability: (token: string, schedules: AvailabilityInput[]) =>
    apiFetch("/doctors/me/availability", { method: "POST", body: schedules, token }),

  getMyAvailability: (token: string) =>
    apiFetch<AvailabilityInfo[]>("/doctors/me/availability", { token }),

  updateProfile: (token: string, data: Partial<DoctorInfo>) =>
    apiFetch("/doctors/me/profile", { method: "PUT", body: data, token }),
};

// Appointments API
export const appointmentsAPI = {
  book: (token: string, data: { doctor_id: string; appointment_date: string; start_time: string; reason?: string; initial_status?: string }) =>
    apiFetch<AppointmentInfo>("/appointments/book", { method: "POST", body: data, token }),

  cancel: (token: string, id: string, reason?: string) =>
    apiFetch<AppointmentInfo>(`/appointments/${id}/cancel`, {
      method: "POST",
      body: { cancellation_reason: reason || "Cancelled by patient" },
      token,
    }),

  reschedule: (token: string, id: string, data: { new_date: string; new_start_time: string }) =>
    apiFetch<AppointmentInfo>(`/appointments/${id}/reschedule`, { method: "POST", body: data, token }),

  patientHistory: (token: string) =>
    apiFetch<AppointmentInfo[]>("/appointments/patient/history", { token }),

  doctorList: (token: string, dateFilter?: string) => {
    const qs = dateFilter ? `?date_filter=${dateFilter}` : "";
    return apiFetch<AppointmentInfo[]>(`/appointments/doctor/list${qs}`, { token });
  },

  doctorAction: (token: string, id: string, action: string) =>
    apiFetch<AppointmentInfo>(`/appointments/${id}/doctor-action`, {
      method: "POST",
      body: { action },
      token,
    }),

  complete: (token: string, id: string) =>
    apiFetch<AppointmentInfo>(`/appointments/${id}/complete`, { method: "POST", token }),

  getById: (token: string, id: string) =>
    apiFetch<AppointmentInfo>(`/appointments/${id}`, { token }),
};

// Payments API
export const paymentsAPI = {
  process: (token: string, data: { appointment_id: string; amount: number; payment_mode: string; card_number?: string; simulate_failure?: boolean }) =>
    apiFetch<PaymentInfo>("/payments/process", { method: "POST", body: data, token }),

  refund: (token: string, paymentId: string, reason?: string) =>
    apiFetch<PaymentInfo>(`/payments/${paymentId}/refund`, {
      method: "POST",
      body: { reason },
      token,
    }),

  receipt: (receiptNumber: string) =>
    apiFetch<ReceiptInfo>(`/payments/receipt/${receiptNumber}`),
};

// Notifications API
export const notificationsAPI = {
  list: (token: string, unreadOnly?: boolean) =>
    apiFetch<NotificationInfo[]>(`/notifications${unreadOnly ? "?unread_only=true" : ""}`, { token }),

  markRead: (token: string, id: string) =>
    apiFetch<NotificationInfo>(`/notifications/${id}/read`, { method: "PUT", token }),
};

// Feedback API
export const feedbackAPI = {
  submit: (token: string, data: { appointment_id: string; rating: number; comment?: string }) =>
    apiFetch("/feedback", { method: "POST", body: data, token }),

  getDoctorFeedbacks: (doctorId: string) =>
    apiFetch<FeedbackInfo[]>(`/feedback/doctor/${doctorId}`),
};

// Admin API
export const adminAPI = {
  addDoctor: (token: string, data: DoctorCreateInput) =>
    apiFetch("/admin/doctors", { method: "POST", body: data, token }),

  updateDoctor: (token: string, id: string, data: Partial<DoctorInfo>) =>
    apiFetch(`/admin/doctors/${id}`, { method: "PUT", body: data, token }),

  deleteDoctor: (token: string, id: string) =>
    apiFetch(`/admin/doctors/${id}`, { method: "DELETE", token }),

  listPatients: (token: string) =>
    apiFetch<PatientInfo[]>("/admin/patients", { token }),

  stats: (token: string) =>
    apiFetch<AdminStats>("/admin/stats", { token }),

  monthlyReport: (token: string, month: number, year: number) =>
    apiFetch<MonthlyReport>(`/reports/monthly?month=${month}&year=${year}`, { token }),

  dailyReport: (token: string, reportDate?: string) => {
    const qs = reportDate ? `?report_date=${reportDate}` : "";
    return apiFetch<DailyReport>(`/reports/daily${qs}`, { token });
  },
};

// Types
export interface DoctorInfo {
  id: string;
  user_id: string;
  name: string;
  email: string;
  phone_number?: string;
  specialization: string;
  qualification: string;
  experience_years: number;
  clinic_address: string;
  consultation_fee: number;
  bio?: string;
  rating_avg: number;
  rating_count: number;
  availabilities: AvailabilityInfo[];
}

export interface AvailabilityInfo {
  id: string;
  doctor_id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  slot_duration_minutes: number;
  is_active: boolean;
}

export interface AvailabilityInput {
  day_of_week: number;
  start_time: string;
  end_time: string;
  slot_duration_minutes: number;
  is_active: boolean;
}

export interface TimeSlot {
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export interface AppointmentInfo {
  id: string;
  patient_id: string;
  doctor_id: string;
  doctor_name?: string;
  doctor_specialization?: string;
  patient_name?: string;
  appointment_date: string;
  start_time: string;
  end_time: string;
  status: string;
  reason?: string;
  cancellation_reason?: string;
  rescheduled_from_id?: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentInfo {
  id: string;
  appointment_id: string;
  patient_id: string;
  amount: number;
  currency: string;
  payment_mode: string;
  transaction_id: string;
  status: string;
  receipt_number: string;
  refund_amount: number;
  refund_status?: string;
  created_at: string;
}

export interface ReceiptInfo {
  receipt_number: string;
  transaction_id: string;
  appointment_id: string;
  doctor_name: string;
  patient_name: string;
  appointment_date: string;
  appointment_time: string;
  amount: number;
  currency: string;
  payment_mode: string;
  status: string;
  payment_date: string;
}

export interface NotificationInfo {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
}

export interface FeedbackInfo {
  id: string;
  appointment_id: string;
  patient_id: string;
  patient_name?: string;
  doctor_id: string;
  rating: number;
  comment?: string;
  created_at: string;
}

export interface PatientInfo {
  id: string;
  user_id: string;
  name: string;
  email: string;
  phone_number?: string;
  contact_no?: string;
  date_of_birth?: string;
  gender?: string;
  blood_group?: string;
  medical_history?: string;
  created_at: string;
}

export interface DoctorCreateInput {
  name: string;
  email: string;
  password: string;
  phone_number?: string;
  specialization: string;
  qualification: string;
  experience_years: number;
  clinic_address: string;
  consultation_fee: number;
  bio?: string;
}

export interface AdminStats {
  total_doctors: number;
  total_patients: number;
  total_appointments: number;
  confirmed_appointments: number;
  completed_appointments: number;
  cancelled_appointments: number;
  total_revenue: number;
}

export interface MonthlyReport {
  month: number;
  year: number;
  month_name: string;
  total_appointments: number;
  completed_count: number;
  cancelled_count: number;
  confirmed_count: number;
  total_revenue: number;
  specialization_breakdown: Record<string, number>;
  top_doctors: { doctor_id: string; doctor_name: string; specialization: string; appointment_count: number }[];
}

export interface DailyReport {
  date: string;
  total_appointments: number;
  confirmed_count: number;
  completed_count: number;
  cancelled_count: number;
  total_revenue: number;
  appointments: { appointment_id: string; patient_name: string; doctor_name: string; specialization: string; time: string; status: string; fee: number }[];
}
