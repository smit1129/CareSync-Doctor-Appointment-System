-- ============================================================================
-- Migration: 001_enable_rls_and_secure_privileges.sql
-- Description: Enable Row Level Security (RLS) on all public tables and
--              revoke public/anon/authenticated access to all tables.
-- Resolves Supabase Security Advisor warnings:
--   1. RLS Disabled in Public (Check 0013)
--   2. Sensitive Columns Exposed (Check 0023)
-- Architecture:
--   - CareSync FastAPI connects via SQLAlchemy using the postgres role (which has BYPASSRLS).
--   - Enabling RLS + revoking anon/authenticated grants blocks all PostgREST access.
--   - All application data access goes through FastAPI (postgres role bypasses RLS).
--   - service_role policies are retained for Supabase Studio administration.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- STEP 1: Enable Row Level Security on all 9 tables in public schema
-- ----------------------------------------------------------------------------
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.doctor_availabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback_ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.password_resets ENABLE ROW LEVEL SECURITY;

-- ----------------------------------------------------------------------------
-- STEP 2: Revoke table-level access from anon and authenticated roles
-- (Prevents PostgREST / Supabase Data API from exposing sensitive data publicly)
-- ----------------------------------------------------------------------------
REVOKE ALL ON TABLE public.users FROM anon, authenticated;
REVOKE ALL ON TABLE public.doctors FROM anon, authenticated;
REVOKE ALL ON TABLE public.patients FROM anon, authenticated;
REVOKE ALL ON TABLE public.doctor_availabilities FROM anon, authenticated;
REVOKE ALL ON TABLE public.appointments FROM anon, authenticated;
REVOKE ALL ON TABLE public.payments FROM anon, authenticated;
REVOKE ALL ON TABLE public.notifications FROM anon, authenticated;
REVOKE ALL ON TABLE public.feedback_ratings FROM anon, authenticated;
REVOKE ALL ON TABLE public.password_resets FROM anon, authenticated;

-- Ensure future tables created in public do not grant default access to anon/authenticated
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;

-- ----------------------------------------------------------------------------
-- STEP 3: Drop any residual public/anon read policies
-- (Frontend accesses doctor listings via FastAPI, so PostgREST needs 0 access)
-- ----------------------------------------------------------------------------
DROP POLICY IF EXISTS "allow_anon_read_doctors" ON public.doctors;
DROP POLICY IF EXISTS "allow_anon_read_availabilities" ON public.doctor_availabilities;

-- ----------------------------------------------------------------------------
-- STEP 4: Full access policies for service_role / backend administration
-- ----------------------------------------------------------------------------
DROP POLICY IF EXISTS "service_role_all_users" ON public.users;
CREATE POLICY "service_role_all_users" ON public.users FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_doctors" ON public.doctors;
CREATE POLICY "service_role_all_doctors" ON public.doctors FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_patients" ON public.patients;
CREATE POLICY "service_role_all_patients" ON public.patients FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_availabilities" ON public.doctor_availabilities;
CREATE POLICY "service_role_all_availabilities" ON public.doctor_availabilities FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_appointments" ON public.appointments;
CREATE POLICY "service_role_all_appointments" ON public.appointments FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_payments" ON public.payments;
CREATE POLICY "service_role_all_payments" ON public.payments FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_notifications" ON public.notifications;
CREATE POLICY "service_role_all_notifications" ON public.notifications FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_feedback" ON public.feedback_ratings;
CREATE POLICY "service_role_all_feedback" ON public.feedback_ratings FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_password_resets" ON public.password_resets;
CREATE POLICY "service_role_all_password_resets" ON public.password_resets FOR ALL TO service_role USING (true) WITH CHECK (true);
