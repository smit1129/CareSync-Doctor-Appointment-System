-- ============================================================================
-- Doctor Appointment Management System - Seed Data
-- ============================================================================

-- Passwords below are hashed using bcrypt for "Admin@12345", "Doctor@12345", "Patient@12345"
-- bcrypt hash for "Password@123": $2b$12$e8Yy8/m1T7v0Y7yXfQfJ.uFm75uQYV7n5QG4nQkZ1E1F8S2I6fAie
-- We will also have an automated python seeder that hashes dynamically.

-- 1. USERS
INSERT INTO users (id, email, password_hash, full_name, role, phone_number, is_active) VALUES
('usr-admin-01', 'admin@demo.caresync.local', '$2b$12$xvkM6IEMb62tKb3mK/nuROZqG2AUN23PwZ6mkp21PvATGI5wIfW3W', 'Hospital Admin', 'admin', '+91 90000 00001', TRUE),
('usr-doc-01', 'aarav.mehta@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Aarav Mehta', 'doctor', '+91 90000 10001', TRUE),
('usr-doc-02', 'ananya.patel@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Ananya Patel', 'doctor', '+91 90000 10002', TRUE),
('usr-doc-03', 'rohan.shah@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Rohan Shah', 'doctor', '+91 90000 10003', TRUE),
('usr-doc-04', 'neha.desai@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Neha Desai', 'doctor', '+91 90000 10004', TRUE),
('usr-pat-01', 'smit.gamit@demo.caresync.local', '$2b$12$OdpPKdaRxyURiFH4TOc3POkjqCZQ5RuY4cSHfV2VrLimpVqrP.BqC', 'Smit Gamit', 'patient', '+91 90000 20001', TRUE),
('usr-pat-02', 'rahul.patel@demo.caresync.local', '$2b$12$OdpPKdaRxyURiFH4TOc3POkjqCZQ5RuY4cSHfV2VrLimpVqrP.BqC', 'Rahul Patel', 'patient', '+91 90000 20002', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 2. DOCTORS
INSERT INTO doctors (id, user_id, specialization, qualification, experience_years, clinic_address, consultation_fee, bio, rating_avg, rating_count) VALUES
('doc-01', 'usr-doc-01', 'Cardiologist', 'MBBS, MD, DM', 14, 'Heart & Vascular Institute, SG Highway, Ahmedabad', 1200.00, 'Board-certified cardiologist specializing in non-invasive cardiovascular treatments, preventative care, and heart failure management.', 4.9, 28),
('doc-02', 'usr-doc-02', 'Dermatologist', 'MBBS, MD', 8, 'SkinCare Clinic, Vile Parle, Mumbai', 800.00, 'Expert in medical and cosmetic dermatology, treating severe acne, eczema, and providing advanced aesthetic procedures.', 4.7, 45),
('doc-03', 'usr-doc-03', 'Pediatrician', 'MBBS, MD, DNB', 11, 'Children''s Health Center, Kothrud, Pune', 700.00, 'Dedicated pediatrician with over a decade of experience in child growth and development, immunizations, and acute illness management.', 4.8, 62),
('doc-04', 'usr-doc-04', 'Neurologist', 'MBBS, MD, DM', 16, 'Neuro Spine Hospital, Whitefield, Bengaluru', 1500.00, 'Senior neurologist specializing in stroke management, epilepsy disorders, and chronic migraine therapies.', 5.0, 15)
ON CONFLICT (id) DO NOTHING;

-- 3. PATIENTS
INSERT INTO patients (id, user_id, contact_no, date_of_birth, gender, blood_group, medical_history) VALUES
('pat-01', 'usr-pat-01', '+91 90000 20001', '1988-04-12', 'Male', 'O+', 'Mild hypertension, no known drug allergies.'),
('pat-02', 'usr-pat-02', '+91 90000 20002', '1993-09-25', 'Female', 'A+', 'History of asthma, seasonal allergies.')
ON CONFLICT (id) DO NOTHING;

-- 4. DOCTOR AVAILABILITIES (Monday to Friday, 09:00 - 17:00)
INSERT INTO doctor_availabilities (id, doctor_id, day_of_week, start_time, end_time, slot_duration_minutes, is_active) VALUES
('avail-01', 'doc-01', 0, '09:00:00', '17:00:00', 30, TRUE),
('avail-02', 'doc-01', 1, '09:00:00', '17:00:00', 30, TRUE),
('avail-03', 'doc-01', 2, '09:00:00', '17:00:00', 30, TRUE),
('avail-04', 'doc-01', 3, '09:00:00', '17:00:00', 30, TRUE),
('avail-05', 'doc-01', 4, '09:00:00', '17:00:00', 30, TRUE),
('avail-06', 'doc-02', 0, '10:00:00', '16:00:00', 30, TRUE),
('avail-07', 'doc-02', 2, '10:00:00', '16:00:00', 30, TRUE),
('avail-08', 'doc-02', 4, '10:00:00', '16:00:00', 30, TRUE),
('avail-09', 'doc-03', 1, '09:00:00', '15:00:00', 30, TRUE),
('avail-10', 'doc-03', 3, '09:00:00', '15:00:00', 30, TRUE),
('avail-11', 'doc-04', 0, '11:00:00', '18:00:00', 30, TRUE),
('avail-12', 'doc-04', 4, '11:00:00', '18:00:00', 30, TRUE)
ON CONFLICT (id) DO NOTHING;

-- 5. SAMPLE APPOINTMENTS
INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, start_time, end_time, status, reason) VALUES
('apt-01', 'pat-01', 'doc-01', '2026-11-10', '10:00:00', '10:30:00', 'Confirmed', 'Routine cardiovascular follow-up'),
('apt-02', 'pat-02', 'doc-02', '2026-11-12', '11:00:00', '11:30:00', 'Confirmed', 'Annual skin checkup and rash consultation'),
('apt-03', 'pat-01', 'doc-01', '2026-10-01', '09:30:00', '10:00:00', 'Completed', 'Initial consultation for elevated resting BP')
ON CONFLICT (id) DO NOTHING;

-- 6. SAMPLE PAYMENTS
INSERT INTO payments (id, appointment_id, patient_id, amount, currency, payment_mode, transaction_id, status, receipt_number) VALUES
('pay-01', 'apt-01', 'pat-01', 1200.00, 'INR', 'card', 'TXN-CARD-99281', 'completed', 'REC-20260920-001'),
('pay-02', 'apt-02', 'pat-02', 900.00, 'INR', 'upi', 'TXN-UPI-48190', 'completed', 'REC-20260922-002'),
('pay-03', 'apt-03', 'pat-01', 1200.00, 'INR', 'card', 'TXN-CARD-11827', 'completed', 'REC-20260815-099')
ON CONFLICT (id) DO NOTHING;

-- 7. FEEDBACK & RATINGS
INSERT INTO feedback_ratings (id, appointment_id, patient_id, doctor_id, rating, comment) VALUES
('fb-01', 'apt-03', 'pat-01', 'doc-01', 5, 'Dr. Sarah was exceptionally attentive and explained the blood pressure management plan with great clarity.')
ON CONFLICT (id) DO NOTHING;

-- 8. NOTIFICATIONS
INSERT INTO notifications (id, user_id, title, message, type, is_read) VALUES
('notif-01', 'usr-pat-01', 'Appointment Confirmed', 'Your appointment with Dr. Sarah Jenkins on 2026-09-20 at 10:00 AM has been confirmed.', 'confirmation', FALSE),
('notif-02', 'usr-doc-01', 'New Appointment Scheduled', 'Patient John Doe booked a consultation for 2026-09-20 at 10:00 AM.', 'confirmation', FALSE)
ON CONFLICT (id) DO NOTHING;
