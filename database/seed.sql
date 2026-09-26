-- ============================================================================
-- Doctor Appointment Management System - Seed Data
-- ============================================================================

-- Passwords below are hashed using bcrypt for "Admin@12345", "Doctor@12345", "Patient@12345"
-- bcrypt hash for "Password@123": $2b$12$e8Yy8/m1T7v0Y7yXfQfJ.uFm75uQYV7n5QG4nQkZ1E1F8S2I6fAie
-- We will also have an automated python seeder that hashes dynamically.

-- 1. USERS
INSERT INTO users (id, email, password_hash, full_name, role, phone_number, is_active) VALUES
('usr-admin-01', 'admin@hospital.com', '$2b$12$L8gWlqH9c0JomBvy3vGq9.T6oKzLw89B9d6nI4C2VbJg6n5m1N0qe', 'Hospital Admin', 'admin', '+1-555-0100', TRUE),
('usr-doc-01', 'sarah.jenkins@hospital.com', '$2b$12$L8gWlqH9c0JomBvy3vGq9.T6oKzLw89B9d6nI4C2VbJg6n5m1N0qe', 'Dr. Sarah Jenkins', 'doctor', '+1-555-0101', TRUE),
('usr-doc-02', 'marcus.vance@hospital.com', '$2b$12$L8gWlqH9c0JomBvy3vGq9.T6oKzLw89B9d6nI4C2VbJg6n5m1N0qe', 'Dr. Marcus Vance', 'doctor', '+1-555-0102', TRUE),
('usr-doc-03', 'priya.sharma@hospital.com', '$2b$12$L8gWlqH9c0JomBvy3vGq9.T6oKzLw89B9d6nI4C2VbJg6n5m1N0qe', 'Dr. Priya Sharma', 'doctor', '+1-555-0103', TRUE),
('usr-doc-04', 'alex.mercer@hospital.com', '$2b$12$L8gWlqH9c0JomBvy3vGq9.T6oKzLw89B9d6nI4C2VbJg6n5m1N0qe', 'Dr. Alex Mercer', 'doctor', '+1-555-0104', TRUE),
('usr-pat-01', 'john.doe@gmail.com', '$2b$12$L8gWlqH9c0JomBvy3vGq9.T6oKzLw89B9d6nI4C2VbJg6n5m1N0qe', 'John Doe', 'patient', '+1-555-0150', TRUE),
('usr-pat-02', 'alice.smith@gmail.com', '$2b$12$L8gWlqH9c0JomBvy3vGq9.T6oKzLw89B9d6nI4C2VbJg6n5m1N0qe', 'Alice Smith', 'patient', '+1-555-0151', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 2. DOCTORS
INSERT INTO doctors (id, user_id, specialization, qualification, experience_years, clinic_address, consultation_fee, bio, rating_avg, rating_count) VALUES
('doc-01', 'usr-doc-01', 'Cardiologist', 'MD, FACC, Harvard Medical', 14, 'Heart & Vascular Suite 402, Metro Health Center', 1200.00, 'Board-certified cardiologist specializing in non-invasive cardiovascular treatments, preventative care, and heart failure management.', 4.9, 28),
('doc-02', 'usr-doc-02', 'Dermatologist', 'MD, American Board of Dermatology', 10, 'Skin & Wellness Center, Level 2', 900.00, 'Specialist in clinical and cosmetic dermatology, acne therapies, eczema, and skin cancer screenings.', 4.8, 19),
('doc-03', 'usr-doc-03', 'Pediatrician', 'MBBS, MD Pediatrics, Johns Hopkins', 8, 'Childrens Care Wing, Room 108', 800.00, 'Compassionate pediatric specialist dedicated to child health, vaccinations, growth monitoring, and developmental wellbeing.', 5.0, 35),
('doc-04', 'usr-doc-04', 'Neurologist', 'MD, PhD Neuroscience, Oxford', 16, 'Brain & Nerve Institute, 6th Floor', 1500.00, 'Leading neurologist treating migraines, neurological disorders, cognitive disorders, and stroke rehabilitation.', 4.9, 22)
ON CONFLICT (id) DO NOTHING;

-- 3. PATIENTS
INSERT INTO patients (id, user_id, contact_no, date_of_birth, gender, blood_group, medical_history) VALUES
('pat-01', 'usr-pat-01', '+1-555-0150', '1988-04-12', 'Male', 'O+', 'Mild hypertension, no known drug allergies.'),
('pat-02', 'usr-pat-02', '+1-555-0151', '1993-09-25', 'Female', 'A+', 'History of asthma, seasonal allergies.')
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
('apt-01', 'pat-01', 'doc-01', '2026-09-20', '10:00:00', '10:30:00', 'Confirmed', 'Routine cardiovascular follow-up'),
('apt-02', 'pat-02', 'doc-02', '2026-09-22', '11:00:00', '11:30:00', 'Confirmed', 'Annual skin checkup and rash consultation'),
('apt-03', 'pat-01', 'doc-01', '2026-08-15', '09:30:00', '10:00:00', 'Completed', 'Initial consultation for elevated resting BP')
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
