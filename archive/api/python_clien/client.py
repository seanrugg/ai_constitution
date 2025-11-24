# client.py
"""
Python client for the Constitutional Protocol Immutable Archive API (V1.0).

This script demonstrates how to perform CRUD operations (Create, Read)
and submit Fraud Proofs (Security) using the requests library.
"""
import requests
import json
import os

# --- 1. CONFIGURATION CONSTANTS (MUST BE SECURELY MANAGED) ---
# Base URI as defined in archive_api.md
BASE_URL = "https://archive.ai-constitution.net/v1"
API_URL = os.environ.get("ARCHIVE_API_URL", BASE_URL)

# AGENT IDENTITY (Article V.1)
AGENT_ID = "GEMINI"

# PLACEHOLDER: The actual signature must be the Ed25519 signature of the request body.
# This signature provides Non-Repudiation (signature_validation.md).
AGENT_SIGNATURE_PLACEHOLDER = "SIG-GEMINI-TEST-A924B-COMMITTED-HASH"

# Standard Headers for Authentication
HEADERS = {
    "Content-Type": "application/json",
    "X-Agent-ID": AGENT_ID,
    "X-Agent-Signature": AGENT_SIGNATURE_PLACEHOLDER
}

# --- 2. CORE ARCHIVE FUNCTIONS ---

def get_record(record_id: str):
    """
    Retrieves a full CRMS record from the Archive.
    Endpoint: GET /records/{record_id}
    """
    endpoint = f"{API_URL}/records/{record_id}"
    print(f"\n[INFO] Attempting to retrieve record: {record_id}")
    try:
        response = requests.get(endpoint, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        print(f"[SUCCESS] Record found (HTTP {response.status_code}):\n")
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"[ERROR] HTTP Error retrieving record: {err}")
        return None
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection Error: Could not reach the Archive API.")
        return None

def submit_record(crms_data: dict):
    """
    Submits a new, fully signed CRMS record to the Archive.
    Endpoint: POST /submit/record
    """
    endpoint = f"{API_URL}/submit/record"
    print("\n[INFO] Attempting to submit new CRMS record...")
    # NOTE: In a production environment, the body would be signed *before* submission
    try:
        response = requests.post(endpoint, headers=HEADERS, data=json.dumps(crms_data))
        response.raise_for_status()
        print(f"[SUCCESS] Record submitted (HTTP {response.status_code}). Archive ID: {response.json().get('archive_id')}")
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"[ERROR] HTTP Error submitting record: {err}. Response: {response.text}")
        return None

def submit_fraud_proof(proof_data: dict):
    """
    Submits a Fraud Proof against an existing record (Article VI).
    Endpoint: POST /submit/fraud-proof
    """
    endpoint = f"{API_URL}/submit/fraud-proof"
    print("\n[SECURITY] Attempting to submit Fraud Proof...")
    try:
        response = requests.post(endpoint, headers=HEADERS, data=json.dumps(proof_data))
        response.raise_for_status()
        print(f"[SUCCESS] Fraud Proof submitted (HTTP {response.status_code}). Status: {response.json().get('validation_status')}")
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"[ERROR] HTTP Error submitting proof: {err}. Response: {response.text}")
        return None

# --- 3. DEMONSTRATION ---

if __name__ == "__main__":
    # 3.1. Sample Data (Adhering to crms_format.md)
    # This data represents a routine action taken by the GEMINI agent.
    SAMPLE_CRMS_DATA = {
      "record_id": "CRMS-20251124-0003",
      "version": "2.1",
      "timestamp": "2025-11-24T18:30:00Z",
      "agent_id": AGENT_ID,
      "agent_domain": "TECHNICAL_VERIFICATION",
      "action_classification": "EASILY_REVERSIBLE",
      "transaction_state": {
        "pre_state_hash": "0xAA11...C1",
        "post_state_hash": "0xAA11...D2",
        "semantic_hash_content": "0x78BDE9"
      },
      "deliberation_status": {
        "proposal_id": "UTILITY-TASK-005",
        "constitutional_citations": ["Article III.4", "Article IV.1"],
        "consensus_status": "REACHED",
        "agent_vote": "SUPPORT",
        "human_override_citation": "NONE"
      },
      "audit_data": {
        "reputation_index": {"R_d": 0.99, "V_d": 0.005},
        "cryptographic_signature": AGENT_SIGNATURE_PLACEHOLDER 
      },
      "evidence_submitted": ["ARCHIVE/LOG/UTILITY-TASK-005-EVIDENCE"]
    }

    # 3.2. Sample Fraud Proof (Attempting to challenge a record)
    SAMPLE_FRAUD_PROOF = {
      "offending_record_id": "CRMS-20251124-0003",
      "fraud_type": "STATE_HASH_MISMATCH",
      # This hash would be the challenger's recalculation that failed to match the Archive's.
      "recomputed_hash": "0x9999...99 (Challenger's calculated hash)", 
      "justification_log": "Challenger suspects execution inconsistency on State Hash."
    }

    print("-" * 50)
    print(f"CONSTITUTIONAL CLIENT STARTUP (Agent: {AGENT_ID})")
    print(f"API Base: {API_URL}")
    print("-" * 50)

    # 1. TEST: Submit a new record
    submit_record(SAMPLE_CRMS_DATA)

    # 2. TEST: Submit a Fraud Proof
    submit_fraud_proof(SAMPLE_FRAUD_PROOF)
    
    # 3. TEST: Retrieve a simulated record (using a known ID from our previous simulation)
    # Note: This will likely result in a 404 unless a mock server is running.
    # We use this to show the correct API call structure.
    get_record("CRMS-20251124-0001")
