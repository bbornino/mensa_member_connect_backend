-- Enable Row Level Security (RLS) on all tables in the public schema
-- This script fixes Supabase security linter errors
-- Since Django handles authentication, we'll create restrictive policies
-- that deny all access through PostgREST API

-- Django system tables
ALTER TABLE public.django_migrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.django_content_type ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.django_admin_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.django_session ENABLE ROW LEVEL SECURITY;

-- Django auth tables
ALTER TABLE public.auth_permission ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.auth_group ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.auth_group_permissions ENABLE ROW LEVEL SECURITY;

-- Application tables
ALTER TABLE public.mensa_member_connect_localgroup ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mensa_member_connect_customuser_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mensa_member_connect_customuser_user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mensa_member_connect_adminaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mensa_member_connect_connectionrequest ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mensa_member_connect_expertise ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mensa_member_connect_industry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mensa_member_connect_customuser ENABLE ROW LEVEL SECURITY;

-- Token blacklist tables
ALTER TABLE public.token_blacklist_outstandingtoken ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.token_blacklist_blacklistedtoken ENABLE ROW LEVEL SECURITY;

-- Create restrictive policies that deny all access through PostgREST
-- Since Django handles authentication through its own system, we want to
-- prevent direct API access to these tables. Django will still work because
-- it uses direct database connections with the postgres user, not PostgREST.

-- Apply deny-all policies to all tables
-- This ensures that even if someone has the Supabase API key,
-- they cannot access data directly through PostgREST
-- 
-- Note: We drop existing policies first to make this script idempotent

-- Django system tables
DROP POLICY IF EXISTS deny_all_django_migrations ON public.django_migrations;
CREATE POLICY deny_all_django_migrations ON public.django_migrations
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_django_content_type ON public.django_content_type;
CREATE POLICY deny_all_django_content_type ON public.django_content_type
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_django_admin_log ON public.django_admin_log;
CREATE POLICY deny_all_django_admin_log ON public.django_admin_log
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_django_session ON public.django_session;
CREATE POLICY deny_all_django_session ON public.django_session
    FOR ALL USING (false);

-- Django auth tables
DROP POLICY IF EXISTS deny_all_auth_permission ON public.auth_permission;
CREATE POLICY deny_all_auth_permission ON public.auth_permission
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_auth_group ON public.auth_group;
CREATE POLICY deny_all_auth_group ON public.auth_group
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_auth_group_permissions ON public.auth_group_permissions;
CREATE POLICY deny_all_auth_group_permissions ON public.auth_group_permissions
    FOR ALL USING (false);

-- Application tables
DROP POLICY IF EXISTS deny_all_localgroup ON public.mensa_member_connect_localgroup;
CREATE POLICY deny_all_localgroup ON public.mensa_member_connect_localgroup
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_customuser_groups ON public.mensa_member_connect_customuser_groups;
CREATE POLICY deny_all_customuser_groups ON public.mensa_member_connect_customuser_groups
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_customuser_user_permissions ON public.mensa_member_connect_customuser_user_permissions;
CREATE POLICY deny_all_customuser_user_permissions ON public.mensa_member_connect_customuser_user_permissions
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_adminaction ON public.mensa_member_connect_adminaction;
CREATE POLICY deny_all_adminaction ON public.mensa_member_connect_adminaction
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_connectionrequest ON public.mensa_member_connect_connectionrequest;
CREATE POLICY deny_all_connectionrequest ON public.mensa_member_connect_connectionrequest
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_expertise ON public.mensa_member_connect_expertise;
CREATE POLICY deny_all_expertise ON public.mensa_member_connect_expertise
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_industry ON public.mensa_member_connect_industry;
CREATE POLICY deny_all_industry ON public.mensa_member_connect_industry
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_customuser ON public.mensa_member_connect_customuser;
CREATE POLICY deny_all_customuser ON public.mensa_member_connect_customuser
    FOR ALL USING (false);

-- Token blacklist tables
DROP POLICY IF EXISTS deny_all_outstandingtoken ON public.token_blacklist_outstandingtoken;
CREATE POLICY deny_all_outstandingtoken ON public.token_blacklist_outstandingtoken
    FOR ALL USING (false);

DROP POLICY IF EXISTS deny_all_blacklistedtoken ON public.token_blacklist_blacklistedtoken;
CREATE POLICY deny_all_blacklistedtoken ON public.token_blacklist_blacklistedtoken
    FOR ALL USING (false);

-- Note: These policies only affect access through Supabase's PostgREST API.
-- Django will continue to work normally because it uses direct database connections
-- with the postgres user credentials, which bypass RLS policies.

