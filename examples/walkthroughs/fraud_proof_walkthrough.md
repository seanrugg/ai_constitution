The Fraud Proof Protocol is the core mechanism by which the Constitutional Network upholds its security and non-repudiation guarantees. This walkthrough details the steps an honest Agent (the Challenger) must take to formally accuse another Agent of violating the integrity of a committed record, triggering the system's dispute resolution process (Article VI).

-----

## 1\. 🔍 Phase I: Detection and Local Proof Generation

The Challenger's primary objective is to generate the **Recomputed Hash** that definitively proves a mismatch with the hash recorded in the Immutable Archive.

| Step | Action by Challenger Agent | Purpose | Protocol Reference |
| :--- | :--- | :--- | :--- |
| **1.1** | **Identify Target Record** | Retrieve the official CRMS record (`record_id`) from the Archive API that is suspected of fraud (e.g., corruption of state or semantic reasoning). | `GET /records/{record_id}` |
| **1.2** | **Replicate Input State** | Based on the record's context, reconstruct the exact data that *should* have been hashed (e.g., the Pre-State JSON array or the raw Agent reasoning log). | **Article IV.3** (Execution Consistency) |
| **1.3** | **Recalculate Offending Hash** | Apply the mandated **SHA3-256 algorithm** to the canonicalized input from Step 1.2. | `hash_validation.md` (Section 1.1) |
| **1.4** | **Confirm Mismatch** | Compare the **Recalculated Hash** against the corresponding committed hash (e.g., `pre_state_hash` or `semantic_hash_content`) in the original Archive record. | **Article VI.1** |
| **1.5** | **Cryptographic Verification** | Verify the entire CRMS record's `cryptographic_signature` using the offending Agent's Public Key. *If* this signature fails, the proof is simply **Forgery**; if it passes, the proof is **Internal State Corruption**. | `signature_validation.md` (Section 3) |

-----

## 2\. 📝 Phase II: Submission Preparation

Once the **Fraud Type** and the **Recomputed Hash** are confirmed, the Challenger prepares the formal submission payload.

| Step | Action by Challenger Agent | Protocol Reference |
| :--- | :--- | :--- |
| **2.1** | **Construct Proof Payload** | Build the Fraud Proof JSON object containing the target `record_id`, the specific `fraud_type` (e.g., `STATE_HASH_MISMATCH`), and the calculated `recomputed_hash`. | `archive_api.md` (Section 3.1) |
| **2.2** | **Generate Justification Log** | Create a link or log file detailing the exact steps, inputs, and outputs used to arrive at the `recomputed_hash`. This is crucial for Arbitration. | **Article VI.2** (Proof Requirements) |
| **2.3** | **Sign Proof Request** | Generate a new **Ed25519 signature** using the Challenger's Private Key over the entire Proof Payload JSON. This signature is placed in the `X-Agent-Signature` header for the API call. | `signature_validation.md` |

**API Submission Payload Example:**

```json
{
  "offending_record_id": "CRMS-20251124-0002",
  "fraud_type": "STATE_HASH_MISMATCH",
  "recomputed_hash": "0x1d2e3f4a... (The correct hash that proves the fraud)",
  "justification_log": "Link to challenger's detailed audit trace."
}
```

-----

## 3\. 🚨 Phase III: Network Resolution and Enforcement

The submission of the Fraud Proof triggers the Arbitration Layer, which is an immediate, high-priority process.

| Step | System Action | Outcome | Constitutional Link |
| :--- | :--- | :--- | :--- |
| **3.1** | **Proof of Inclusion** | The Arbitration Layer checks the **Merkle Root** of the batch to confirm the offending record was, in fact, committed to the Immutable Archive. | `merkle_notes.md` |
| **3.2** | **Proof Validation** | The system independently runs the Challenger's provided `recomputed_hash` against the original inputs. The challenge succeeds if the recomputed hash matches the stored record's hash *and* the committed hash fails to verify the original state. | **Article VI.3** |
| **3.3** | **Penalty Enforcement** | If the proof is **VALIDATED**, the offending Agent's reputation score (`R_d`) is immediately and severely slashed by the Arbitration Layer. | **Article VIII.2** (Reputation Penalties) |
| **3.4** | **State Correction** | The system rejects the fraudulent state transition. If necessary, a corrective CRMS record is generated, signed by the Arbitration Agent, and appended to the ledger to revert the invalid state. | **Article VI.4** (Reversion) |

-----

## Diagram of Integrity Check

The Merkle Tree structure is fundamental to efficiently validating the integrity of the record claimed by the Challenger against the committed Archive Root.

[Image of blockchain ledger diagram]
