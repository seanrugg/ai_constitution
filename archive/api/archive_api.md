# ⚙️ ARCHIVE API SPECIFICATION

- **File Path:** archive_api.md
- **Version:** V1.0 (Aligns with Constitutional Protocol v2.1)
- **Scope:** Defines the Representational State Transfer (REST) API for secure interaction with the **Immutable Archive**. This interface is mandatory for Agent submission and external Auditor verification of all Constitutional Records.

-----

## 1\. PROTOCOL & AUTHENTICATION

### 1.1 Base URI

All API calls must use the secure protocol and the specified base URI:

`https://archive.ai-constitution.net/v1`

### 1.2 Authentication (Article V.1)

Access to the write-enabled endpoints (`POST`, `PUT`) requires cryptographic proof of identity to ensure **Non-Repudiation**.

  * **Agents:** Must sign the entire request payload body using their **Ed25519 Private Key** (as defined in `signature_validation.md`). The signature is passed in the `X-Agent-Signature` header.
  * **Human Supervisors/Auditors:** Require a unique, session-based `X-Supervisor-Key`.

-----

## 2\. CORE ARCHIVE ENDPOINTS

These endpoints are designed for rapid access to committed records and essential audit data.

| Method | Endpoint | Description | Constitutional Link |
| :--- | :--- | :--- | :--- |
| `GET` | `/records/{record_id}` | Retrieves the full CRMS JSON entry associated with a specific ID (e.g., `CRMS-20251124-0001`). | Article V.1 (Retrieval) |
| `GET` | `/query` | Searches the archive based on parameters (Agent ID, Constitutional Citation, or Time Range). | Article V.2 (Transparency) |
| `GET` | `/reputation/{agent_id}` | Retrieves the current, authoritative **Reputation Index (R\_d, V\_d)** for a specified Agent across all domains. | Article VIII.1 (Reputation) |
| `POST`| `/submit/record` | Submits a new, fully signed **CRMS JSON record** to the Archive for commitment. | Article V.4 (Commitment) |

-----

## 3\. FRAUD & VERIFICATION ENDPOINTS

These are critical, high-priority endpoints designed to facilitate the Adversarial Audit process mandated by **Article VI**.

### 3.1 Submitting a Fraud Proof

The system guarantees immediate processing of Fraud Proofs. This is the primary mechanism for challenging an Agent's integrity.

  * **Endpoint:** `POST /submit/fraud-proof`
  * **Purpose:** Allows any Agent or Auditor to submit a claim of record forgery or hash mismatch. If validated, it triggers an immediate freeze and penalty against the offending Agent's reputation score (Article VIII).
  * **Request Body (JSON):**
    ```json
    {
      "offending_record_id": "CRMS-YYYYMMDD-UUID",
      "fraud_type": "STATE_HASH_MISMATCH / SIGNATURE_INVALID",
      "recomputed_hash": "STRING (The hash calculated by the challenger)",
      "justification_log": "STRING (Brief explanation and link to external logs)"
    }
    ```
  * **Response Codes:**
      * `202 ACCEPTED`: Proof received and queued for atomic validation by the Arbitration layer.
      * `409 CONFLICT`: The submitted proof is malformed or invalid per **Article VI.2** (e.g., missing required fields).

### 3.2 On-Demand Hash Verification

This utility endpoint allows agents to quickly verify system hashes against the canonicalization standard without triggering a full fraud proof submission.

  * **Endpoint:** `POST /validate/hash`
  * **Purpose:** Recalculates and verifies a given input string or object against the official SHA3-256 standard, aiding in local testing of `hash_validation.md`.
  * **Request Body (JSON):**
    ```json
    {
      "hash_input": "STRING/OBJECT (The data to be hashed)",
      "expected_hash": "STRING (Optional: The hash to compare against)"
    }
    ```
  * **Response Body (JSON):**
    ```json
    {
      "calculated_hash": "0x...",
      "is_valid": true 
    }
    ```
