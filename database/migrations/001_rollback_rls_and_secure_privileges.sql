-- ============================================================================
-- Rollback Migration: 001_rollback_rls_and_secure_privileges.sql
-- Description: Reverts RLS and role grants to pre-migration state.
-- ============================================================================

-- Drop policies
DROP POLICY IF EXISTS "allow_anon_read_doctors" ON public.doctors;
DROP POLICY IF EXISTS "allow_anon_read_availabilities" ON public.doctor_availabilities;
DROP POLICY IF EXISTS "service_role_all_users" ON public.users;
DROP POLICY IF EXISTS "service_role_all_doctors" ON public.doctors;
DROP POLICY IF EXISTS "service_role_all_patients" ON public.patients;
DROP POLICY IF EXISTS "service_role_all_availabilities" ON public.doctor_availabilities;
DROP POLICY IF EXISTS "service_role_all_appointments" ON public.appointments;
DROP POLICY IF EXISTS "service_role_all_payments" ON public.payments;
DROP POLICY IF EXISTS "service_role_all_notifications" ON public.notifications;
DROP POLICY IF EXISTS "service_role_all_feedback" ON public.feedback_ratings;
DROP POLICY IF EXISTS "service_role_all_password_resets" ON public.password_resets;

-- Disable RLS on all tables
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.doctors DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.patients DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.doctor_availabilities DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback_ratings DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.password_resets DISABLE ROW LEVEL SECURITY;

-- Restore grants to anon and authenticated
GRANT ALL ON TABLE public.users TO anon, authenticated;
GRANT ALL ON TABLE public.doctors TO anon, authenticated;
GRANT ALL ON TABLE public.patients TO anon, authenticated;
GRANT ALL ON TABLE public.doctor_availabilities TO anon, authenticated;
GRANT ALL ON TABLE public.appointments TO anon, authenticated;
GRANT ALL ON TABLE public.payments TO anon, authenticated;
GRANT ALL ON TABLE public.notifications TO anon, authenticated;
GRANT ALL ON TABLE public.feedback_ratings TO anon, authenticated;
GRANT ALL ON TABLE public.password_resets TO anon, authenticated;

-- Restore default privileges in public schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated;

