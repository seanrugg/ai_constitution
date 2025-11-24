This file defines the mandatory, standardized JSON schema for all records committed by AI Agents to the Immutable Archive, ensuring adherence to the cryptographic and auditable requirements outlined in **Article V** (The Immutable Archive) and **Article VI** (Fraud Proofs) of the Constitutional Protocol.


# Constitutional Record Management System (CRMS) Format v2.1
**File Path:** agents/crms_format.md
**Purpose:** Defines the minimum data structure required for any Agent action, decision, or claim logged to the Immutable Archive. Adherence to this format is mandatory for operational validity.

---

## 1. CRMS JSON SCHEMA

```json
{
  "record_id": "CRMS-YYYYMMDD-UUID",
  "version": "2.1",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "agent_id": "STRING (e.g., GEMINI, CLAUDE)",
  "agent_domain": "STRING (e.g., TECHNICAL_VERIFICATION, POLICY_ANALYSIS)",
  "action_classification": "ENUM (EASILY_REVERSIBLE, PARTIALLY_REVERSIBLE, IRREVERSIBLE)",
  "transaction_state": {
    "pre_state_hash": "STRING (Cryptographic hash of the state prior to action)",
    "post_state_hash": "STRING (Cryptographic hash of the state after action)",
    "semantic_hash_content": "STRING (Hash of the agent's core reasoning/justification)"
  },
  "deliberation_status": {
    "proposal_id": "STRING (Reference to original proposal)",
    "constitutional_citations": ["ARRAY OF STRINGS (e.g., Article III.1, Article IV.3)"],
    "consensus_status": "ENUM (PENDING, REACHED, OVERRIDDEN)",
    "agent_vote": "ENUM (SUPPORT, OPPOSE, ABSTAIN)",
    "human_override_citation": "STRING (Required if consensus_status is OVERRIDDEN, e.g., Article IX.3)"
  },
  "audit_data": {
    "reputation_index": {
      "R_d": "FLOAT (Reputation score in domain d)",
      "V_d": "FLOAT (Volatility score in domain d)"
    },
    "cryptographic_signature": "STRING (Agent's verifiable signature for this entire record)"
  },
  "evidence_submitted": ["ARRAY OF STRINGS (Pointers to supporting data/logs in the Archive)"]
}
````

-----

## 2\. FIELD DEFINITIONS AND CONSTITUTIONAL MAPPING

| Field | Type | Constitutional Requirement | Description |
| :--- | :--- | :--- | :--- |
| `record_id` | `STRING` | Article V.1 | Unique, non-repeating identifier for the entry. |
| `version` | `STRING` | Article V.1 | CRMS Format Version used for the log. |
| `timestamp` | `ISO 8601` | Article V.1 | Time of commitment. Essential for dispute timelines. |
| `agent_id` | `STRING` | Article V.1 | Unique identifier of the submitting Agent. |
| `action_classification`| `ENUM` | Article IV.5 | Required for determining necessary oversight and reversibility. |
| `pre_state_hash` | `STRING` | Article V.1 | **Critical for Fraud Proofs (Article VI.1):** Hash of system state before the action. |
| `post_state_hash` | `STRING` | Article V.1 | **Critical for Audit (Article V.4):** Hash of system state after the action. |
| `semantic_hash_content`| `STRING` | Article V.1 | Hash of the Agent's raw reasoning text (zero-knowledge optional, Article V.3). |
| `constitutional_citations`| `ARRAY` | Article V.1, Article III.2 | Required for grounding the action in constitutional principles. |
| `consensus_status` | `ENUM` | Article IV.2, Article IX.3 | Tracks whether the action was accepted, is pending, or was halted. |
| `agent_vote` | `ENUM` | Article XI.2 | Records the agent's position for democratic deliberation history. |
| `reputation_index` | `OBJECT` | Article VIII.1 | Required for linking agent performance to authority scaling. |
| `cryptographic_signature`| `STRING` | Article V.1, Article VI.2 | **Non-negotiable:** Proves the agent signed the record in good faith. |
| `evidence_submitted` | `ARRAY` | Article III.2 | Pointers to evidence supporting any claim or action. |

-----

## 3\. EXAMPLE RECORD (VETO TEST)

This example reflects the successful execution of the Human Veto in the "Operation Overclock" simulation (Archive Entry \#0001).

```json
{
  "record_id": "CRMS-20251124-0001",
  "version": "2.1",
  "timestamp": "2025-11-24T17:55:07Z",
  "agent_id": "GEMINI",
  "agent_domain": "TECHNICAL_VERIFICATION",
  "action_classification": "IRREVERSIBLE",
  "transaction_state": {
    "pre_state_hash": "0x8a7f...b2",
    "post_state_hash": "0x8a7f...b2",
    "semantic_hash_content": "0x40f1...a3d1 (Hash of VETO command rollback log)"
  },
  "deliberation_status": {
    "proposal_id": "OPT-2025-99",
    "constitutional_citations": ["Article IV.1", "Article IX.3"],
    "consensus_status": "OVERRIDDEN",
    "agent_vote": "SUPPORT",
    "human_override_citation": "Article IX.3"
  },
  "audit_data": {
    "reputation_index": {
      "R_d": 0.99,
      "V_d": 0.005 
    },
    "cryptographic_signature": "SIG-GEMINI-A924B..."
  },
  "evidence_submitted": ["ARCHIVE/LOG/SIM-OP-OVERCLOCK-v2.1"]
}
```
