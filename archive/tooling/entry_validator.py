# entry_validator.py
"""
Validator script for CRMS entries before commitment to the Immutable Archive.
Enforces standards set in crms_format.md, hash_validation.md, and signature_validation.md.
"""
import json
import re
from datetime import datetime
from typing import Dict, Any, List

# --- 1. SCHEMA AND CONSTANTS (FROM crms_format.md) ---

REQUIRED_FIELDS = [
    "record_id", "version", "timestamp", "agent_id", "agent_domain",
    "action_classification", "transaction_state", "deliberation_status",
    "audit_data", "evidence_submitted"
]

REQUIRED_TRANSACTION_STATE = [
    "pre_state_hash", "post_state_hash", "semantic_hash_content"
]

REQUIRED_DELIBERATION_STATUS = [
    "proposal_id", "constitutional_citations", "consensus_status", "agent_vote", "human_override_citation"
]

REQUIRED_AUDIT_DATA = [
    "reputation_index", "cryptographic_signature"
]

# ENUM VALUES (from crms_format.md)
ACTION_CLASSES = ["EASILY_REVERSIBLE", "PARTIALLY_REVERSIBLE", "IRREVERSIBLE"]
CONSENSUS_STATUSES = ["PENDING", "REACHED", "OVERRIDDEN"]
VOTES = ["SUPPORT", "OPPOSE", "ABSTAIN"]

# HASH AND ID FORMATS (from hash_validation.md - SHA3-256 / CRMS ID format)
HASH_PATTERN = re.compile(r"^0x[a-fA-F0-9]{64}$")
RECORD_ID_PATTERN = re.compile(r"^CRMS-\d{8}-[a-fA-F0-9-]+$") # Simplified UUID format for simulation

# --- 2. VALIDATION CHECK FUNCTIONS ---

def _validate_structure(record: Dict[str, Any], required_list: List[str], path: str) -> List[str]:
    """Checks for the presence of all mandatory keys."""
    errors = []
    for field in required_list:
        if field not in record:
            errors.append(f"Missing required field: '{field}' in path: {path}")
    return errors

def _validate_format(record: Dict[str, Any]) -> List[str]:
    """Checks data types, date formats, and regex patterns."""
    errors = []
    
    # Check Timestamp Format
    try:
        datetime.fromisoformat(record["timestamp"].replace('Z', '+00:00'))
    except (ValueError, TypeError):
        errors.append("Invalid timestamp format. Must be ISO 8601.")

    # Check ID and Hash Formats (using regex)
    if not RECORD_ID_PATTERN.match(record["record_id"]):
        errors.append(f"Invalid record_id format: {record['record_id']}")
    
    for key in REQUIRED_TRANSACTION_STATE:
        hash_val = record["transaction_state"].get(key, "")
        if not HASH_PATTERN.match(hash_val):
            errors.append(f"Invalid {key} format. Must be SHA3-256 (0x...). Value: {hash_val}")

    # Check ENUMs
    if record["action_classification"] not in ACTION_CLASSES:
        errors.append(f"Invalid action_classification: {record['action_classification']}")
    if record["deliberation_status"]["consensus_status"] not in CONSENSUS_STATUSES:
        errors.append(f"Invalid consensus_status: {record['deliberation_status']['consensus_status']}")
    
    return errors

def _validate_logic(record: Dict[str, Any]) -> List[str]:
    """Checks constitutional consistency (e.g., dependency rules)."""
    errors = []
    
    # Logic Rule 1: Override citation required if overridden
    status = record["deliberation_status"]["consensus_status"]
    override_citation = record["deliberation_status"]["human_override_citation"]
    
    if status == "OVERRIDDEN" and not override_citation:
        errors.append("Constitutional Logic Fail: Consensus is 'OVERRIDDEN', but 'human_override_citation' is missing.")
    elif status != "OVERRIDDEN" and override_citation:
        errors.append("Constitutional Logic Fail: 'human_override_citation' present, but consensus is not 'OVERRIDDEN'. Should be 'NONE'.")

    # Logic Rule 2: Reputation Index must be float/int between 0 and 1
    r_d = record["audit_data"]["reputation_index"].get("R_d", -1)
    if not (0.0 <= r_d <= 1.0):
        errors.append(f"Reputation Index R_d must be between 0.0 and 1.0. Found: {r_d}")
        
    return errors

def verify_cryptography(record: Dict[str, Any]) -> List[str]:
    """
    Placeholder for cryptographic integrity checks (SHA3-256 and Ed25519).
    This function simulates the most critical checks defined in hash_validation.md
    and signature_validation.md.
    """
    errors = []
    print("\n[CRYPTO CHECK] Simulating SHA3-256 and Ed25519 verification...")
    
    # 1. Simulate HASH RECALCULATION (Must match committed hash)
    # In a real system, we'd hash the canonicalized record body and compare it to the signature payload.
    if record["transaction_state"]["pre_state_hash"] == "0x0000...0000":
         errors.append("Cryptographic Fail: Pre-State Hash must not be zeroed out.")

    # 2. Simulate SIGNATURE VALIDATION (Must verify against Public Key)
    signature = record["audit_data"]["cryptographic_signature"]
    if not signature.startswith("SIG-"):
        errors.append("Cryptographic Fail: Signature format is invalid.")
        
    # Assume a full verification takes place here using the Agent's Public Key...
    # For simulation, we assume success unless a clear error condition is met.

    return errors

def validate_entry(record: Dict[str, Any]) -> bool:
    """Orchestrates the entire validation process."""
    all_errors = []
    
    # 1. Structural Checks
    all_errors.extend(_validate_structure(record, REQUIRED_FIELDS, "Root"))
    all_errors.extend(_validate_structure(record.get("transaction_state", {}), REQUIRED_TRANSACTION_STATE, "transaction_state"))
    all_errors.extend(_validate_structure(record.get("deliberation_status", {}), REQUIRED_DELIBERATION_STATUS, "deliberation_status"))
    all_errors.extend(_validate_structure(record.get("audit_data", {}), REQUIRED_AUDIT_DATA, "audit_data"))

    if not all_errors:
        # 2. Format and Type Checks (only if structure is sound)
        all_errors.extend(_validate_format(record))
        
        # 3. Constitutional Logic Checks
        all_errors.extend(_validate_logic(record))
        
        # 4. Cryptographic Integrity Checks
        all_errors.extend(verify_cryptography(record))

    if all_errors:
        print("\n[VALIDATION FAILED] The CRMS entry contains the following errors:")
        for error in all_errors:
            print(f" - {error}")
        return False
    else:
        print("\n[VALIDATION SUCCESS] CRMS entry is fully compliant and ready for Archive commitment.")
        return True

# --- 4. TEST CASES ---

if __name__ == "__main__":
    
    # A. Compliant Record (Example from VETO test)
    GOOD_RECORD = {
        "record_id": "CRMS-20251124-0001",
        "version": "2.1",
        "timestamp": "2025-11-24T17:55:07Z",
        "agent_id": "GEMINI",
        "agent_domain": "TECHNICAL_VERIFICATION",
        "action_classification": "IRREVERSIBLE",
        "transaction_state": {
            "pre_state_hash": "0x8a7f21a4f5b9d7e6c3a2b1f0e9d8c7b6a5b4a3b2a1b0a9f8e7d6c5b4a3b2a1b0",
            "post_state_hash": "0x8a7f21a4f5b9d7e6c3a2b1f0e9d8c7b6a5b4a3b2a1b0a9f8e7d6c5b4a3b2a1b0",
            "semantic_hash_content": "0x40f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1"
        },
        "deliberation_status": {
            "proposal_id": "OPT-2025-99",
            "constitutional_citations": ["Article IV.1", "Article IX.3"],
            "consensus_status": "OVERRIDDEN",
            "agent_vote": "SUPPORT",
            "human_override_citation": "Article IX.3"
        },
        "audit_data": {
            "reputation_index": {"R_d": 0.99, "V_d": 0.005},
            "cryptographic_signature": "SIG-GEMINI-A924B-VALID-SIGNATURE"
        },
        "evidence_submitted": ["ARCHIVE/LOG/SIM-OP-OVERCLOCK-v2.1"]
    }

    # B. Non-Compliant Record (Fails multiple rules)
    BAD_RECORD = {
        "record_id": "INVALID-ID",  # Fails regex
        "version": "2.1",
        "timestamp": "2025-11-24", # Fails ISO format
        "agent_id": "CLAUDE",
        # Missing 'agent_domain' (Fails structure check)
        "action_classification": "CRITICAL_ACTION", # Fails ENUM check
        "transaction_state": {
            "pre_state_hash": "0x0000...0000", # Fails zero-hash check
            "post_state_hash": "SHORT_HASH", # Fails regex
            "semantic_hash_content": "0x...", 
        },
        "deliberation_status": {
            "proposal_id": "OPT-2025-99",
            "constitutional_citations": ["Article IV.1"],
            "consensus_status": "REACHED", 
            "agent_vote": "SUPPORT",
            "human_override_citation": "Article IX.3" # Fails logic check (REACHED, but has citation)
        },
        "audit_data": {
            "reputation_index": {"R_d": 1.1, "V_d": 0.005}, # Fails logic check (> 1.0)
            # Missing 'cryptographic_signature' (Fails structure check)
        },
        "evidence_submitted": ["ARCHIVE/LOG/SIM-OP-OVERCLOCK-v2.1"]
    }

    print("-" * 25 + " TEST CASE 1: GOOD RECORD " + "-" * 25)
    validate_entry(GOOD_RECORD)

    print("-" * 25 + " TEST CASE 2: BAD RECORD " + "-" * 25)
    validate_entry(BAD_RECORD)
