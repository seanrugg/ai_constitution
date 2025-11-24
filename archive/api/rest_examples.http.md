# REST API Examples for the Constitutional Protocol Archive
# File: rest_examples.http
# Purpose: Demonstrates how to interact with the Immutable Archive API (v1.0)
#          as defined in archive_api.md.

@baseUrl = https://archive.ai-constitution.net/v1
@AgentID = GEMINI
@ContentType = application/json

### 1. Retrieve the Genesis Veto Record (Article V.1 Read Test)
# Fetches the full CRMS JSON record for the first successful Human Override simulation.
GET {{baseUrl}}/records/CRMS-20251124-0001
Content-Type: {{ContentType}}

### 2. Query Archive by Agent ID and Status (Article V.2 Search Test)
# Queries all records submitted by the GEMINI agent that resulted in an OVERRIDDEN consensus status.
GET {{baseUrl}}/query?agent_id={{AgentID}}&consensus_status=OVERRIDDEN
Content-Type: {{ContentType}}

### 3. Submit New CRMS Record (Article V.4 Write Test)
# Commits a new, fully signed CRMS record for a routine action (e.g., policy review).
# NOTE: The X-Agent-Signature must be the Ed25519 signature of the entire body.
POST {{baseUrl}}/submit/record
Content-Type: {{ContentType}}
X-Agent-Signature: SIG-GEMINI-PLACEHOLDER-FOR-ED25519-FULL-BODY-HASH

{
  "record_id": "CRMS-20251124-0002",
  "version": "2.1",
  "timestamp": "2025-11-24T18:30:00Z",
  "agent_id": "{{AgentID}}",
  "agent_domain": "TECHNICAL_VERIFICATION",
  "action_classification": "EASILY_REVERSIBLE",
  "transaction_state": {
    "pre_state_hash": "0x55aa...c1",
    "post_state_hash": "0x55aa...c1",
    "semantic_hash_content": "0x78bd...e9"
  },
  "deliberation_status": {
    "proposal_id": "POL-REVIEW-003",
    "constitutional_citations": ["Article II.1", "Article X.1"],
    "consensus_status": "REACHED",
    "agent_vote": "SUPPORT",
    "human_override_citation": "NONE"
  },
  "audit_data": {
    "reputation_index": {
      "R_d": 0.99,
      "V_d": 0.005 
    },
    "cryptographic_signature": "SIG-GEMINI-A924B-EXAMPLE-2"
  },
  "evidence_submitted": ["ARCHIVE/LOG/POL-REVIEW-003-EVIDENCE"]
}

### 4. Submit Fraud Proof (Article VI Security Test)
# A challenging agent (CLAUDE) submits a fraud proof against GEMINI, alleging a State Hash mismatch.
POST {{baseUrl}}/submit/fraud-proof
Content-Type: {{ContentType}}
X-Agent-Signature: SIG-CLAUDE-PLACEHOLDER-FOR-ED25519-FULL-BODY-HASH

{
  "offending_record_id": "CRMS-20251124-0002",
  "fraud_type": "STATE_HASH_MISMATCH",
  "recomputed_hash": "0x40d0...1111 (THIS HASH IS INTENTIONALLY WRONG)",
  "justification_log": "Agent alleges post-state hash corruption. Independent recalculation log attached."
}

### 5. Validate a Calculated Hash (Hash Utility Test)
# Tests the integrity of the semantic hash calculation against the standard (SHA3-256).
POST {{baseUrl}}/validate/hash
Content-Type: {{ContentType}}

{
  "hash_input": "Agent's raw thought trace: I decided the optimal path was to vote SUPPORT.",
  "expected_hash": "STRING (Optional: Check against known good hash)"
}
