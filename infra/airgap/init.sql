-- ==============================================================================
-- FORENZA: Forensic Evidence Operating System
-- Air-Gapped PostgreSQL 16 LIMS & Custody Ledger Database Initialization
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- --- Cases Table ---
CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_number VARCHAR(64) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    jurisdiction VARCHAR(128) DEFAULT 'Criminal Investigation Division',
    lead_analyst VARCHAR(128) NOT NULL,
    technical_reviewer VARCHAR(128),
    status VARCHAR(32) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'PENDING_REVIEW', 'CERTIFIED', 'ARCHIVED')),
    iso_17025_accreditation VARCHAR(64) DEFAULT 'ISO/IEC 17025:2017',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- --- Evidence Items Table ---
CREATE TABLE IF NOT EXISTS evidence_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    item_barcode VARCHAR(64) UNIQUE NOT NULL,
    evidence_type VARCHAR(64) NOT NULL,
    substrate VARCHAR(64) DEFAULT 'NON_POROUS',
    storage_location VARCHAR(128) DEFAULT 'Cold Storage Unit B-4',
    collected_at TIMESTAMP WITH TIME ZONE,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    dna_yield_ng_per_ul NUMERIC(10, 4) DEFAULT 0.0000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- --- Merkle Chain-of-Custody Ledger Table ---
CREATE TABLE IF NOT EXISTS custody_ledger (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evidence_id UUID REFERENCES evidence_items(id) ON DELETE CASCADE,
    action VARCHAR(64) NOT NULL,
    performed_by VARCHAR(128) NOT NULL,
    witness_analyst VARCHAR(128),
    leaf_hash VARCHAR(64) NOT NULL,
    previous_root_hash VARCHAR(64),
    merkle_root_hash VARCHAR(64) NOT NULL,
    iso_uncertainty_budget NUMERIC(8, 4) DEFAULT 0.0500,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- --- MCMC Mixture Deconvolution Runs ---
CREATE TABLE IF NOT EXISTS mcmc_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    run_name VARCHAR(128) NOT NULL,
    num_contributors INT NOT NULL CHECK (num_contributors BETWEEN 1 AND 5),
    num_chains INT DEFAULT 4,
    iterations_per_chain INT DEFAULT 25000,
    gelman_rubin_r_hat NUMERIC(6, 4),
    effective_sample_size INT,
    log_likelihood_ratio NUMERIC(12, 4),
    enfsi_verbal_scale VARCHAR(64),
    proportions_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- --- Circom Groth16 Zero-Knowledge Proofs ---
CREATE TABLE IF NOT EXISTS zkp_proofs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    circuit_name VARCHAR(64) DEFAULT 'dna_match_bn254',
    public_signals JSONB NOT NULL,
    proof_data JSONB NOT NULL,
    verified BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- --- Indices for Low-Latency Query Execution ---
CREATE INDEX IF NOT EXISTS idx_cases_case_number ON cases(case_number);
CREATE INDEX IF NOT EXISTS idx_evidence_barcode ON evidence_items(item_barcode);
CREATE INDEX IF NOT EXISTS idx_custody_merkle ON custody_ledger(merkle_root_hash);
CREATE INDEX IF NOT EXISTS idx_mcmc_case ON mcmc_runs(case_id);

-- --- Initial Seed Data (Verified Reference Case) ---
INSERT INTO cases (id, case_number, title, lead_analyst, technical_reviewer, status)
VALUES (
    'a0000000-0000-0000-0000-000000000001',
    'FOR-2026-NIST-01',
    'NIST SRM 2391d Multi-Omic Golden Calibration Case',
    'Senior Analyst Dr. E. Vance',
    'Technical Reviewer Dr. M. Sterling',
    'CERTIFIED'
) ON CONFLICT (case_number) DO NOTHING;
