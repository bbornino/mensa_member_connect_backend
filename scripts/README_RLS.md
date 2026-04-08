# Row Level Security (RLS) Setup for Supabase

## What is RLS?

Row Level Security (RLS) is a PostgreSQL feature that restricts access to rows in a table based on policies. Supabase requires RLS to be enabled on all tables in the `public` schema that are exposed to PostgREST (Supabase's auto-generated REST API).

## Why Do We Need This?

Without RLS enabled, anyone with your Supabase API key could potentially access or modify your database directly through the PostgREST API, bypassing Django's authentication and authorization system.

## How to Apply the Fix

### Option 1: Using Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `enable_rls.sql`
4. Click **Run** to execute the script

### Option 2: Using psql Command Line

```bash
# Connect to your Supabase database
psql "postgresql://<db_user>:<db_password>@<db_host>:5432/postgres?sslmode=require"

# Run the script
\i scripts/enable_rls.sql
```

### Option 3: Using Django Management Command

You can also create a Django management command to run this, but using the Supabase dashboard is the simplest approach.

## What This Script Does

1. **Enables RLS** on all affected tables
2. **Creates restrictive policies** that deny all access through PostgREST API
3. **Preserves Django functionality** - Django uses direct database connections, so it's not affected by these policies

## Important Notes

- ✅ **Django will continue to work normally** - These policies only affect access through Supabase's PostgREST API
- ✅ **Your application is now more secure** - Even if someone gets your Supabase API key, they can't access your data
- ⚠️ **If you plan to use Supabase's PostgREST API in the future**, you'll need to modify these policies to allow appropriate access

## Verifying the Fix

After running the script, you can verify RLS is enabled by:

1. Running the Supabase linter again (see "How to Run the Supabase Linter" below)
2. Checking that all RLS errors are resolved
3. Testing that your Django application still works correctly

## How to Run the Supabase Linter

The Supabase Database Linter checks your database for security and performance issues. Here are the ways to run it:

### Option 1: Using Supabase Dashboard (Easiest)

1. Go to your Supabase project dashboard: https://supabase.com/dashboard
2. Select your project
3. Navigate to **Database** → **Linter** (or look for "Database Linter" in the sidebar)
4. The linter will automatically run and show you any issues
5. You can export the results as CSV (which is how you got the original error list)

### Option 2: Using Supabase CLI

1. **Install the Supabase CLI** (if not already installed):
   ```bash
   npm install -g supabase
   # or
   brew install supabase/tap/supabase
   ```

2. **Login to Supabase**:
   ```bash
   supabase login
   ```

3. **Link your project** (if not already linked):
   ```bash
   supabase link --project-ref xbqekpsyfldqajcefsjv
   ```

4. **Run the linter**:
   ```bash
   supabase db lint
   ```
   
   To see only errors (not warnings):
   ```bash
   supabase db lint --level error
   ```

The CLI will show you the same issues that appear in the dashboard.

## Future Considerations

If you ever want to use Supabase's PostgREST API directly (instead of just using it as a database), you'll need to:

1. Modify the policies to allow appropriate access
2. Use Supabase Auth for authentication
3. Create policies that check user permissions

For now, since you're using Django's authentication system, the deny-all policies are the safest approach.

