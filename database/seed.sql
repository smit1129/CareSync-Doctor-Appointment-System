-- ============================================================================
-- Doctor Appointment Management System - Seed Data
-- ============================================================================

-- Passwords below are hashed using bcrypt for "Admin@12345", "Doctor@12345", "Patient@12345"
-- bcrypt hash for "Password@123": $2b$12$e8Yy8/m1T7v0Y7yXfQfJ.uFm75uQYV7n5QG4nQkZ1E1F8S2I6fAie
-- We will also have an automated python seeder that hashes dynamically.

-- 1. USERS
INSERT INTO users (id, email, password_hash, full_name, role, phone_number, is_active) VALUES
('usr-admin-01', 'admin@demo.caresync.local', '$2b$12$xvkM6IEMb62tKb3mK/nuROZqG2AUN23PwZ6mkp21PvATGI5wIfW3W', 'Hospital Admin', 'admin', '+91 90000 00001', TRUE),
('usr-doc-01', 'aarav.mehta@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Aarav Mehta', 'doctor', '+91 98765 01001', TRUE),
('usr-doc-02', 'priya.sharma@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Priya Sharma', 'doctor', '+91 98765 01002', TRUE),
('usr-doc-03', 'rohan.patel@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Rohan Patel', 'doctor', '+91 98765 01003', TRUE),
('usr-doc-04', 'neha.shah@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Neha Shah', 'doctor', '+91 98765 01004', TRUE),
('usr-doc-05', 'kunal.desai@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Kunal Desai', 'doctor', '+91 98765 01005', TRUE),
('usr-doc-06', 'ananya.joshi@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Ananya Joshi', 'doctor', '+91 98765 01006', TRUE),
('usr-doc-07', 'vivek.trivedi@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Vivek Trivedi', 'doctor', '+91 98765 01007', TRUE),
('usr-doc-08', 'meera.iyer@demo.caresync.local', '$2b$12$3orBJlJaoLsYnDqxaKTiNuLf/Ka8YxV9AQ6u6UePW7Ovwur6sQEuy', 'Dr. Meera Iyer', 'doctor', '+91 98765 01008', TRUE),
('usr-pat-01', 'smit.gamit@demo.caresync.local', '$2b$12$OdpPKdaRxyURiFH4TOc3POkjqCZQ5RuY4cSHfV2VrLimpVqrP.BqC', 'Smit Gamit', 'patient', '+91 98765 02001', TRUE),
('usr-pat-02', 'kavya.patel@demo.caresync.local', '$2b$12$OdpPKdaRxyURiFH4TOc3POkjqCZQ5RuY4cSHfV2VrLimpVqrP.BqC', 'Kavya Patel', 'patient', '+91 98765 02002', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 2. DOCTORS (8 Indian demo doctors)
INSERT INTO doctors (id, user_id, specialization, qualification, experience_years, clinic_address, consultation_fee, bio, rating_avg, rating_count) VALUES
('doc-01', 'usr-doc-01', 'Cardiologist', 'MBBS, MD (Medicine), DM (Cardiology)', 12, 'Heart & Vascular Centre, Ahmedabad, Gujarat', 1200.00, 'Experienced cardiologist specializing in non-invasive cardiovascular treatments, preventative cardiac care, and heart failure management.', 5.0, 28),
('doc-02', 'usr-doc-02', 'Pediatrician', 'MBBS, MD (Pediatrics)', 8, 'Children''s Care Clinic, Vadodara, Gujarat', 800.00, 'Compassionate pediatric specialist dedicated to child health, vaccinations, growth monitoring, and developmental wellbeing.', 5.0, 35),
('doc-03', 'usr-doc-03', 'Dermatologist', 'MBBS, MD (Dermatology)', 9, 'Skin & Wellness Clinic, Ahmedabad, Gujarat', 900.00, 'Specialist in clinical and cosmetic dermatology, acne therapies, eczema treatment, and skin health management.', 4.8, 19),
('doc-04', 'usr-doc-04', 'General Physician', 'MBBS, MD (General Medicine)', 7, 'Shree Health Clinic, Surat, Gujarat', 600.00, 'Experienced general physician focusing on routine check-ups, lifestyle diseases, diabetes, and hypertension management.', 4.7, 14),
('doc-05', 'usr-doc-05', 'Neurologist', 'MBBS, MD (Medicine), DM (Neurology)', 11, 'NeuroCare Centre, Mumbai, Maharashtra', 1100.00, 'Leading neurologist treating migraines, neurological disorders, epilepsy, and stroke rehabilitation.', 4.9, 22),
('doc-06', 'usr-doc-06', 'Gynecologist', 'MBBS, MD (Obstetrics & Gynecology)', 10, 'Women''s Care Hospital, Vadodara, Gujarat', 1000.00, 'Dedicated gynecologist specializing in women''s health, prenatal care, high-risk pregnancies, and minimally invasive surgeries.', 4.9, 31),
('doc-07', 'usr-doc-07', 'Orthopedic Surgeon', 'MBBS, MS (Orthopedics)', 13, 'OrthoCare Hospital, Ahmedabad, Gujarat', 1000.00, 'Skilled orthopedic surgeon specializing in joint replacement, sports injuries, fracture management, and spinal disorders.', 4.8, 25),
('doc-08', 'usr-doc-08', 'ENT Specialist', 'MBBS, MS (ENT)', 8, 'ENT & Hearing Care Centre, Bengaluru, Karnataka', 750.00, 'Experienced ENT specialist providing comprehensive care for ear, nose, and throat conditions including hearing disorders and sinus treatments.', 4.8, 18)
ON CONFLICT (id) DO NOTHING;

-- 3. PATIENTS
INSERT INTO patients (id, user_id, contact_no, date_of_birth, gender, blood_group, medical_history) VALUES
('pat-01', 'usr-pat-01', '+91 98765 02001', '1988-04-12', 'Male', 'O+', 'Mild hypertension, no known drug allergies.'),
('pat-02', 'usr-pat-02', '+91 98765 02002', '1993-09-25', 'Female', 'A+', 'History of asthma, seasonal allergies.')
ON CONFLICT (id) DO NOTHING;

-- 4. DOCTOR AVAILABILITIES (Monday to Saturday, 09:00 - 17:00)
INSERT INTO doctor_availabilities (id, doctor_id, day_of_week, start_time, end_time, slot_duration_minutes, is_active) VALUES
('avail-01', 'doc-01', 0, '09:00:00', '17:00:00', 30, TRUE),
('avail-02', 'doc-01', 1, '09:00:00', '17:00:00', 30, TRUE),
('avail-03', 'doc-01', 2, '09:00:00', '17:00:00', 30, TRUE),
('avail-04', 'doc-01', 3, '09:00:00', '17:00:00', 30, TRUE),
('avail-05', 'doc-01', 4, '09:00:00', '17:00:00', 30, TRUE),
('avail-06', 'doc-01', 5, '09:00:00', '17:00:00', 30, TRUE),
('avail-07', 'doc-02', 0, '09:00:00', '17:00:00', 30, TRUE),
('avail-08', 'doc-02', 1, '09:00:00', '17:00:00', 30, TRUE),
('avail-09', 'doc-02', 2, '09:00:00', '17:00:00', 30, TRUE),
('avail-10', 'doc-02', 3, '09:00:00', '17:00:00', 30, TRUE),
('avail-11', 'doc-02', 4, '09:00:00', '17:00:00', 30, TRUE),
('avail-12', 'doc-02', 5, '09:00:00', '17:00:00', 30, TRUE),
('avail-13', 'doc-03', 0, '09:00:00', '17:00:00', 30, TRUE),
('avail-14', 'doc-03', 1, '09:00:00', '17:00:00', 30, TRUE),
('avail-15', 'doc-03', 2, '09:00:00', '17:00:00', 30, TRUE),
('avail-16', 'doc-03', 3, '09:00:00', '17:00:00', 30, TRUE),
('avail-17', 'doc-03', 4, '09:00:00', '17:00:00', 30, TRUE),
('avail-18', 'doc-03', 5, '09:00:00', '17:00:00', 30, TRUE),
('avail-19', 'doc-04', 0, '09:00:00', '17:00:00', 30, TRUE),
('avail-20', 'doc-04', 1, '09:00:00', '17:00:00', 30, TRUE),
('avail-21', 'doc-04', 2, '09:00:00', '17:00:00', 30, TRUE),
('avail-22', 'doc-04', 3, '09:00:00', '17:00:00', 30, TRUE),
('avail-23', 'doc-04', 4, '09:00:00', '17:00:00', 30, TRUE),
('avail-24', 'doc-04', 5, '09:00:00', '17:00:00', 30, TRUE),
('avail-25', 'doc-05', 0, '09:00:00', '17:00:00', 30, TRUE),
('avail-26', 'doc-05', 1, '09:00:00', '17:00:00', 30, TRUE),
('avail-27', 'doc-05', 2, '09:00:00', '17:00:00', 30, TRUE),
('avail-28', 'doc-05', 3, '09:00:00', '17:00:00', 30, TRUE),
('avail-29', 'doc-05', 4, '09:00:00', '17:00:00', 30, TRUE),
('avail-30', 'doc-05', 5, '09:00:00', '17:00:00', 30, TRUE),
('avail-31', 'doc-06', 0, '09:00:00', '17:00:00', 30, TRUE),
('avail-32', 'doc-06', 1, '09:00:00', '17:00:00', 30, TRUE),
('avail-33', 'doc-06', 2, '09:00:00', '17:00:00', 30, TRUE),
('avail-34', 'doc-06', 3, '09:00:00', '17:00:00', 30, TRUE),
('avail-35', 'doc-06', 4, '09:00:00', '17:00:00', 30, TRUE),
('avail-36', 'doc-06', 5, '09:00:00', '17:00:00', 30, TRUE),
('avail-37', 'doc-07', 0, '09:00:00', '17:00:00', 30, TRUE),
('avail-38', 'doc-07', 1, '09:00:00', '17:00:00', 30, TRUE),
('avail-39', 'doc-07', 2, '09:00:00', '17:00:00', 30, TRUE),
('avail-40', 'doc-07', 3, '09:00:00', '17:00:00', 30, TRUE),
('avail-41', 'doc-07', 4, '09:00:00', '17:00:00', 30, TRUE),
('avail-42', 'doc-07', 5, '09:00:00', '17:00:00', 30, TRUE),
('avail-43', 'doc-08', 0, '09:00:00', '17:00:00', 30, TRUE),
('avail-44', 'doc-08', 1, '09:00:00', '17:00:00', 30, TRUE),
('avail-45', 'doc-08', 2, '09:00:00', '17:00:00', 30, TRUE),
('avail-46', 'doc-08', 3, '09:00:00', '17:00:00', 30, TRUE),
('avail-47', 'doc-08', 4, '09:00:00', '17:00:00', 30, TRUE),
('avail-48', 'doc-08', 5, '09:00:00', '17:00:00', 30, TRUE)
ON CONFLICT (id) DO NOTHING;

-- 5. SAMPLE APPOINTMENTS
INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, start_time, end_time, status, reason) VALUES
('apt-01', 'pat-01', 'doc-01', '2026-11-10', '10:00:00', '10:30:00', 'Confirmed', 'Routine cardiovascular follow-up'),
('apt-02', 'pat-02', 'doc-03', '2026-11-12', '11:00:00', '11:30:00', 'Confirmed', 'Annual skin checkup and rash consultation'),
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
('fb-01', 'apt-03', 'pat-01', 'doc-01', 5, 'Dr. Aarav was exceptionally attentive and explained the blood pressure management plan with great clarity.')
ON CONFLICT (id) DO NOTHING;

-- 8. NOTIFICATIONS
INSERT INTO notifications (id, user_id, title, message, type, is_read) VALUES
('notif-01', 'usr-pat-01', 'Appointment Confirmed', 'Your appointment with Dr. Aarav Mehta on 2026-11-10 at 10:00 AM has been confirmed.', 'confirmation', FALSE),
('notif-02', 'usr-doc-01', 'New Appointment Scheduled', 'Patient Smit Gamit booked a consultation for 2026-11-10 at 10:00 AM.', 'confirmation', FALSE)
ON CONFLICT (id) DO NOTHING;
