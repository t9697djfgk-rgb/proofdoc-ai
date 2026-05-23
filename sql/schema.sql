-- ================================================================
-- ProofDoc AI  –  Full PostgreSQL schema for Supabase
-- Run this once in Supabase SQL Editor (Dashboard → SQL Editor)
-- ================================================================

-- UUID extension (already enabled in Supabase, but safe to re-run)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Organizations (Law Firms) ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS organizations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    slug                TEXT UNIQUE NOT NULL,
    email               TEXT,
    phone               TEXT,
    address             TEXT,
    country             TEXT DEFAULT 'Rwanda',
    subscription_plan   TEXT DEFAULT 'starter',   -- starter|professional|firm
    subscription_status TEXT DEFAULT 'active',
    stripe_customer_id  TEXT,
    settings            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ── Profiles (extends Supabase auth.users) ─────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    email           TEXT NOT NULL,
    full_name       TEXT NOT NULL DEFAULT '',
    role            TEXT NOT NULL CHECK (role IN ('admin','lawyer','staff','client','intern')),
    title           TEXT,          -- e.g. "Senior Associate"
    phone           TEXT,
    avatar_url      TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Clients ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clients (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    profile_id      UUID REFERENCES profiles(id) ON DELETE SET NULL,
    name            TEXT NOT NULL,
    email           TEXT,
    phone           TEXT,
    address         TEXT,
    client_type     TEXT DEFAULT 'individual',   -- individual|company
    company_name    TEXT,
    notes           TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Matters ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS matters (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    ref             TEXT NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT,
    matter_type     TEXT,
    status          TEXT DEFAULT 'Active',   -- Active|On Hold|Closed|Archived
    priority        TEXT DEFAULT 'medium',
    open_date       DATE DEFAULT CURRENT_DATE,
    close_date      DATE,
    jurisdiction    TEXT DEFAULT 'Rwanda',
    court_reference TEXT,
    opposing_party  TEXT,
    created_by      UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, ref)
);

-- ── Matter Members (lawyer ↔ client ↔ matter) ──────────────────────
CREATE TABLE IF NOT EXISTS matter_members (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matter_id   UUID NOT NULL REFERENCES matters(id) ON DELETE CASCADE,
    profile_id  UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    role        TEXT NOT NULL DEFAULT 'lawyer',  -- lead_lawyer|lawyer|staff|client
    added_by    UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(matter_id, profile_id)
);

-- ── Documents ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    matter_id       UUID REFERENCES matters(id) ON DELETE SET NULL,
    uploaded_by     UUID REFERENCES profiles(id) ON DELETE SET NULL,
    name            TEXT NOT NULL,
    file_path       TEXT,    -- Supabase Storage path
    file_type       TEXT,
    file_size       INTEGER,
    visibility      TEXT DEFAULT 'internal',  -- internal|shared_with_client|client_upload|final|draft
    description     TEXT,
    tags            TEXT[],
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Messages (Matter Discussions) ─────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    matter_id       UUID NOT NULL REFERENCES matters(id) ON DELETE CASCADE,
    sender_id       UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    sender_role     TEXT NOT NULL,
    message_type    TEXT NOT NULL DEFAULT 'client_visible',  -- client_visible|internal_note
    body            TEXT NOT NULL,
    is_edited       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Message Attachments ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS message_attachments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id  UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    file_name   TEXT NOT NULL,
    file_type   TEXT,
    file_size   INTEGER,
    file_path   TEXT,
    uploaded_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ── Message Read Receipts ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS message_reads (
    message_id  UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    profile_id  UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    read_at     TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (message_id, profile_id)
);

-- ── Tasks ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    matter_id       UUID REFERENCES matters(id) ON DELETE SET NULL,
    assigned_to     UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_by      UUID REFERENCES profiles(id) ON DELETE SET NULL,
    title           TEXT NOT NULL,
    description     TEXT,
    status          TEXT DEFAULT 'pending',   -- pending|in_progress|completed|cancelled
    priority        TEXT DEFAULT 'medium',
    due_date        DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Notes (internal, law-firm only) ───────────────────────────────
CREATE TABLE IF NOT EXISTS notes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    matter_id       UUID REFERENCES matters(id) ON DELETE SET NULL,
    author_id       UUID REFERENCES profiles(id) ON DELETE SET NULL,
    title           TEXT,
    body            TEXT NOT NULL,
    is_private      BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Time Entries ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS time_entries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    matter_id       UUID REFERENCES matters(id) ON DELETE SET NULL,
    lawyer_id       UUID REFERENCES profiles(id) ON DELETE SET NULL,
    description     TEXT NOT NULL,
    hours           NUMERIC(6,2) NOT NULL,
    rate            NUMERIC(10,2),
    entry_date      DATE DEFAULT CURRENT_DATE,
    billed          BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Invoices ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS invoices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    matter_id       UUID REFERENCES matters(id) ON DELETE SET NULL,
    client_id       UUID REFERENCES clients(id) ON DELETE SET NULL,
    invoice_number  TEXT NOT NULL,
    status          TEXT DEFAULT 'draft',  -- draft|sent|paid|overdue
    subtotal        NUMERIC(12,2),
    vat_rate        NUMERIC(5,2) DEFAULT 20.0,
    vat_amount      NUMERIC(12,2),
    total           NUMERIC(12,2),
    due_date        DATE,
    paid_date       DATE,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Notifications ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    recipient_id    UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    type            TEXT NOT NULL,   -- new_message|document_shared|deadline|draft_shared|etc
    title           TEXT NOT NULL,
    body            TEXT,
    matter_id       UUID REFERENCES matters(id) ON DELETE SET NULL,
    related_id      TEXT,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Rwanda Laws Database ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS laws (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title            TEXT NOT NULL,
    law_number       TEXT,
    category         TEXT,   -- criminal|civil|commercial|constitutional|labour|tax|other
    status           TEXT DEFAULT 'in_force',  -- in_force|pending_review|repealed
    summary          TEXT,
    source_url       TEXT,
    official_gazette TEXT,
    enactment_date   DATE,
    in_force_date    DATE,
    last_checked     TIMESTAMPTZ DEFAULT NOW(),
    raw_content      TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS law_articles (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    law_id         UUID NOT NULL REFERENCES laws(id) ON DELETE CASCADE,
    article_number TEXT,
    title          TEXT,
    content        TEXT NOT NULL,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ── Audit Log ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    actor_id        UUID REFERENCES profiles(id) ON DELETE SET NULL,
    actor_name      TEXT,
    action          TEXT NOT NULL,   -- MESSAGE_SENT|DOCUMENT_SHARED|MATTER_CREATED|etc
    resource_type   TEXT,
    resource_id     TEXT,
    details         JSONB DEFAULT '{}',
    ip_address      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- updated_at auto-trigger
-- ================================================================
CREATE OR REPLACE FUNCTION _set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$;

DO $$ DECLARE t TEXT;
BEGIN
  FOR t IN SELECT unnest(ARRAY[
    'organizations','profiles','clients','matters',
    'documents','messages','tasks','notes','invoices','laws'
  ]) LOOP
    EXECUTE format(
      'DROP TRIGGER IF EXISTS trg_%s_updated ON %s;
       CREATE TRIGGER trg_%s_updated BEFORE UPDATE ON %s
       FOR EACH ROW EXECUTE FUNCTION _set_updated_at();', t,t,t,t);
  END LOOP;
END $$;

-- ================================================================
-- Indexes
-- ================================================================
CREATE INDEX IF NOT EXISTS idx_profiles_org      ON profiles(organization_id);
CREATE INDEX IF NOT EXISTS idx_profiles_role     ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_matters_org       ON matters(organization_id);
CREATE INDEX IF NOT EXISTS idx_matters_status    ON matters(status);
CREATE INDEX IF NOT EXISTS idx_mm_matter         ON matter_members(matter_id);
CREATE INDEX IF NOT EXISTS idx_mm_profile        ON matter_members(profile_id);
CREATE INDEX IF NOT EXISTS idx_docs_matter       ON documents(matter_id);
CREATE INDEX IF NOT EXISTS idx_docs_org          ON documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_docs_visibility   ON documents(visibility);
CREATE INDEX IF NOT EXISTS idx_msgs_matter       ON messages(matter_id);
CREATE INDEX IF NOT EXISTS idx_msgs_org          ON messages(organization_id);
CREATE INDEX IF NOT EXISTS idx_msgs_type         ON messages(message_type);
CREATE INDEX IF NOT EXISTS idx_msgs_created      ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_org         ON tasks(organization_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned    ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_due         ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_notif_recipient   ON notifications(recipient_id);
CREATE INDEX IF NOT EXISTS idx_notif_unread      ON notifications(recipient_id, is_read);
CREATE INDEX IF NOT EXISTS idx_audit_org         ON audit_logs(organization_id);
CREATE INDEX IF NOT EXISTS idx_audit_created     ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_laws_status       ON laws(status);
CREATE INDEX IF NOT EXISTS idx_law_articles_law  ON law_articles(law_id);
CREATE INDEX IF NOT EXISTS idx_time_org          ON time_entries(organization_id);
CREATE INDEX IF NOT EXISTS idx_time_matter       ON time_entries(matter_id);
