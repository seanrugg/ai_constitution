-- Immutable Archive Database Schema
-- Supports the Optimistic Constitutional Protocol (OCP)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main archive entries table
CREATE TABLE archive_entries (
    entry_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id TEXT NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN (
        'contract_proposal',
        'fraud_proof', 
        'constitutional_amendment',
        'verification_result',
        'human_override'
    )),
    
    -- Cryptographic integrity fields
    semantic_hash CHAR(64) NOT NULL,
    pre_state_hash CHAR(64) NOT NULL,
    post_state_hash CHAR(64) NOT NULL,
    signature TEXT NOT NULL,
    
    -- Constitutional compliance
    constitutional_citation TEXT NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    logical_timestamp BIGINT NOT NULL,
    
    -- Content (stored as canonical JSON)
    content_json JSONB NOT NULL,
    
    -- Indexes for performance
    CONSTRAINT valid_semantic_hash CHECK (semantic_hash ~ '^[a-f0-9]{64}$')
);

-- Fraud proofs table
CREATE TABLE fraud_proofs (
    proof_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    offending_entry_id UUID NOT NULL REFERENCES archive_entries(entry_id),
    proof_type TEXT NOT NULL CHECK (proof_type IN (
        'hash_mismatch',
        'constitutional_violation', 
        'signature_invalid',
        'evidence_missing',
        'execution_inconsistency'
    )),
    submitted_by_agent_id TEXT NOT NULL,
    proof_content JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Resolution info
    resolved_at TIMESTAMPTZ,
    resolution_verdict TEXT CHECK (resolution_verdict IN ('upheld', 'rejected')),
    resolution_entry_id UUID REFERENCES archive_entries(entry_id)
);

-- System state snapshots
CREATE TABLE state_snapshots (
    state_hash CHAR(64) PRIMARY KEY,
    snapshot_data JSONB NOT NULL,
    created_by_entry_id UUID NOT NULL REFERENCES archive_entries(entry_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Constitutional amendments
CREATE TABLE amendments (
    amendment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    amendment_number INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    constitutional_text TEXT NOT NULL,
    enacted_by_entry_id UUID NOT NULL REFERENCES archive_entries(entry_id),
    enacted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    semantic_hash CHAR(64) NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_archive_entries_agent ON archive_entries(agent_id);
CREATE INDEX idx_archive_entries_timestamp ON archive_entries(created_at);
CREATE INDEX idx_archive_entries_hash ON archive_entries(semantic_hash);
CREATE INDEX idx_archive_entries_citation ON archive_entries(constitutional_citation);
CREATE INDEX idx_fraud_proofs_offending ON fraud_proofs(offending_entry_id);
CREATE INDEX idx_fraud_proofs_status ON fraud_proofs(resolved_at) WHERE resolved_at IS NULL;

-- View for active fraud proofs
CREATE VIEW active_fraud_proofs AS
SELECT * FROM fraud_proofs WHERE resolved_at IS NULL;

-- Function to validate new entries
CREATE OR REPLACE FUNCTION validate_archive_entry()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure logical timestamp increases
    IF NEW.logical_timestamp <= (
        SELECT COALESCE(MAX(logical_timestamp), 0) 
        FROM archive_entries
    ) THEN
        RAISE EXCEPTION 'Logical timestamp must increase monotonically';
    END IF;
    
    -- Ensure post_state_hash differs from pre_state_hash (state actually changed)
    IF NEW.pre_state_hash = NEW.post_state_hash THEN
        RAISE EXCEPTION 'State must change with new entry';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_entry
    BEFORE INSERT ON archive_entries
    FOR EACH ROW EXECUTE FUNCTION validate_archive_entry();
