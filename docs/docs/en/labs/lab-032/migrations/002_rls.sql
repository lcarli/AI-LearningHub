-- =============================================================================
-- Migration 002: Row Level Security (RLS) for Agent Data Protection
-- Lab 032: Row Level Security for Agents
-- =============================================================================
-- Run AFTER migration 001.
-- Adds multi-tenant RLS to restrict each agent/tenant to their own data.
-- =============================================================================

-- =============================================================================
-- TENANTS table
-- =============================================================================
CREATE TABLE IF NOT EXISTS tenants (
    id          TEXT PRIMARY KEY,           -- e.g. 'tenant_acme', 'tenant_outdoorgear'
    name        TEXT NOT NULL,
    plan        TEXT DEFAULT 'free',        -- 'free', 'pro', 'enterprise'
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- AGENT SESSIONS table (tenant-scoped)
-- =============================================================================
-- Tracks conversation sessions per tenant.
-- With RLS, tenants can only see their own sessions.
CREATE TABLE IF NOT EXISTS agent_sessions (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    session_token   TEXT NOT NULL UNIQUE,
    user_id         TEXT,                   -- optional: user within tenant
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    last_active     TIMESTAMPTZ DEFAULT NOW(),
    metadata        JSONB DEFAULT '{}'
);

-- =============================================================================
-- CONVERSATION HISTORY table (tenant-scoped)
-- =============================================================================
CREATE TABLE IF NOT EXISTS conversation_messages (
    id          BIGSERIAL PRIMARY KEY,
    tenant_id   TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    session_id  BIGINT NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant', 'tool')),
    content     TEXT NOT NULL,
    tool_calls  JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CUSTOM PRODUCT CATALOG table (tenant-scoped)
-- =============================================================================
-- Tenants can have their own products in addition to the shared catalog
CREATE TABLE IF NOT EXISTS tenant_products (
    id          BIGSERIAL PRIMARY KEY,
    tenant_id   TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    sku         TEXT NOT NULL,
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    embedding   vector(1536),
    price_usd   NUMERIC(10,2),
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tenant_id, sku)
);

-- =============================================================================
-- DATABASE ROLES for multi-tenant access
-- =============================================================================

-- Role for the agent application (used by the API server)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'agent_app') THEN
        CREATE ROLE agent_app LOGIN PASSWORD 'CHANGE_IN_PRODUCTION';
    END IF;
END $$;

-- Role for admin operations (migrations, backfill jobs)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'agent_admin') THEN
        CREATE ROLE agent_admin LOGIN PASSWORD 'CHANGE_IN_PRODUCTION';
    END IF;
END $$;

-- Grant schema access
GRANT USAGE ON SCHEMA public TO agent_app, agent_admin;
GRANT ALL ON ALL TABLES IN SCHEMA public TO agent_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO agent_admin;

-- agent_app: can read shared products, manage sessions and messages
GRANT SELECT ON products TO agent_app;
GRANT SELECT ON product_embeddings TO agent_app;
GRANT SELECT, INSERT, UPDATE ON agent_sessions TO agent_app;
GRANT SELECT, INSERT ON conversation_messages TO agent_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_products TO agent_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO agent_app;

-- =============================================================================
-- ROW LEVEL SECURITY: Enable on tenant-scoped tables
-- =============================================================================
ALTER TABLE agent_sessions        ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_products       ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- RLS POLICIES
-- =============================================================================
-- The application sets: SET app.current_tenant_id = 'tenant_acme';
-- before executing queries. RLS policies use this setting.

-- ---- agent_sessions policies ----

-- Agent app can only see sessions for the current tenant
CREATE POLICY sessions_tenant_isolation ON agent_sessions
    AS PERMISSIVE
    FOR ALL
    TO agent_app
    USING (tenant_id = current_setting('app.current_tenant_id', TRUE));

-- Admin can see all sessions (bypass RLS)
CREATE POLICY sessions_admin_all ON agent_sessions
    AS PERMISSIVE
    FOR ALL
    TO agent_admin
    USING (TRUE);

-- ---- conversation_messages policies ----

-- Agent app can only see messages for current tenant
CREATE POLICY messages_tenant_isolation ON conversation_messages
    AS PERMISSIVE
    FOR ALL
    TO agent_app
    USING (tenant_id = current_setting('app.current_tenant_id', TRUE));

-- Admin sees all messages
CREATE POLICY messages_admin_all ON conversation_messages
    AS PERMISSIVE
    FOR ALL
    TO agent_admin
    USING (TRUE);

-- ---- tenant_products policies ----

-- Agent app can only access their own tenant's products
CREATE POLICY tenant_products_isolation ON tenant_products
    AS PERMISSIVE
    FOR ALL
    TO agent_app
    USING (tenant_id = current_setting('app.current_tenant_id', TRUE));

-- Admin sees all tenant products
CREATE POLICY tenant_products_admin_all ON tenant_products
    AS PERMISSIVE
    FOR ALL
    TO agent_admin
    USING (TRUE);

-- =============================================================================
-- HELPER FUNCTION: set tenant context (call at start of each request)
-- =============================================================================
-- Usage in application code:
--   conn.execute("SELECT set_tenant_context(%s)", [tenant_id])
CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id TEXT)
RETURNS VOID
LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    -- Validate tenant exists before setting context
    IF NOT EXISTS (SELECT 1 FROM tenants WHERE id = p_tenant_id) THEN
        RAISE EXCEPTION 'Unknown tenant: %', p_tenant_id;
    END IF;
    PERFORM set_config('app.current_tenant_id', p_tenant_id, TRUE);
END;
$$;

-- Only agent_app can call set_tenant_context (not directly set session variable)
GRANT EXECUTE ON FUNCTION set_tenant_context(TEXT) TO agent_app;
REVOKE SET ON PARAMETER app.current_tenant_id FROM agent_app;

-- =============================================================================
-- SEED: Demo tenants
-- =============================================================================
INSERT INTO tenants (id, name, plan) VALUES
    ('tenant_outdoorgear', 'OutdoorGear Inc.', 'enterprise'),
    ('tenant_demo',        'Demo Company',     'free')
ON CONFLICT (id) DO NOTHING;

-- =============================================================================
-- VERIFY: RLS is active
-- =============================================================================
SELECT
    tablename,
    rowsecurity AS rls_enabled,
    forcerowsecurity AS rls_forced
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('agent_sessions', 'conversation_messages', 'tenant_products')
ORDER BY tablename;

SELECT 'Migration 002 (RLS) complete' AS status;
