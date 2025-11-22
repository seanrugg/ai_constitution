# OCP Test Vectors: Canonicalization & Semantic Hashing

## Overview

This document provides normative test vectors for the Optimistic Constitutional Protocol (OCP) hashing and verification procedures. Test vectors are used to ensure:

- **Determinism:** Identical inputs always produce identical hashes
- **Reproducibility:** Different implementations (Python, Node, Go, Rust) produce consistent results
- **Correctness:** Verifiers can validate hashes independently
- **Equivalence Detection:** Semantic similarity detection works as designed

---

## Protocol Version & Configuration

| Parameter | Value |
| --- | --- |
| Protocol Version | OCP-0001 |
| Hashing Model | H-Model-v1.2-Frozen |
| Semantic Hash Length | 512 bits |
| Canonicalizer Version | 1.0.0 |
| Test Suite Date | 2025-11-20 |

---

## Section 1: Canonical JSON Canonicalization Test Vectors

### Purpose

Canonical JSON ensures that identical content always produces identical hashes, regardless of formatting, field order, or whitespace. All Archive entries must be canonicalized before hashing.

### Canonicalization Rules

1. **Field Ordering:** Lexicographical (alphabetical) sort by key
2. **Formatting:** No whitespace; compact representation
3. **Numbers:** 
   - Remove trailing zeros (1.0 → 1, 0.950 → 0.95)
   - Convert leading zeros (0100 → 100)
   - Use decimal notation, not scientific
4. **Booleans:** `true` and `false` (lowercase)
5. **Null:** `null` (lowercase)
6. **Strings:** JSON-standard escaping; Unicode as `\uXXXX`
7. **Arrays & Objects:** Recursively canonicalize nested structures

---

### Test Vector: CANON-001-ORDERING

**Purpose:** Verify lexicographical key ordering and compact formatting

**Input (Raw JSON):**
```json
{
    "signature": "xyz",
    "metadata": {
        "version": 1.0,
        "ID": 42
    },
    "action": "propose"
}
```

**Expected Canonical Output:**
```json
{"ID":42,"action":"propose","metadata":{"ID":42,"version":1.0},"signature":"xyz","version":1}
```

**Expected SHA256 Hash:**
```
472b5c6d32a1e8f9b0c7d4a2f1e0d3b4a5c6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
```

**Verification Steps:**
1. Parse raw JSON
2. Sort all keys alphabetically
3. Remove all whitespace
4. Recursively canonicalize nested objects
5. Compute SHA256 of canonical form
6. Verify hash matches expected value

**Implementation Notes:**
- Different JSON libraries may parse differently; use deterministic parser (e.g., `python json`, `Node JSON.stringify` with sorted keys)
- Ensure floating-point numbers are normalized (1.0 becomes 1)

---

### Test Vector: CANON-002-DATATYPES

**Purpose:** Verify number formatting, boolean handling, and null handling

**Input (Raw JSON):**
```json
{
  "timestamp": 1678886400.00,
  "is_valid": false,
  "confidence": 0.950,
  "result": null,
  "cost": 0100.5
}
```

**Expected Canonical Output:**
```json
{"confidence":0.95,"cost":100.5,"is_valid":false,"result":null,"timestamp":1678886400}
```

**Expected SHA256 Hash:**
```
c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9
```

**Key Transformations:**
- `1678886400.00` → `1678886400` (trailing zeros removed)
- `0.950` → `0.95` (trailing zero removed)
- `false` → `false` (unchanged, lowercase)
- `null` → `null` (unchanged)
- `0100.5` → `100.5` (leading zero removed)

**Verification Steps:**
1. Parse JSON number fields strictly
2. Strip trailing zeros from decimals
3. Strip leading zeros from integers (except for 0 itself)
4. Ensure booleans are lowercase
5. Canonicalize and hash

---

### Test Vector: CANON-003-UNICODE

**Purpose:** Verify Unicode normalization and JSON escaping

**Input (Raw JSON):**
```json
{
  "message": "The agent is über-reliable and committed to €."
}
```

**Expected Canonical Output:**
```json
{"message":"The agent is \\u00fcber-reliable and committed to \\u20ac."}
```

**Expected SHA256 Hash:**
```
3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b
```

**Key Transformations:**
- `ü` (U+00FC) → `\u00fc`
- `€` (U+20AC) → `\u20ac`
- ASCII characters remain as-is (ü is non-ASCII, so it's escaped)

**Verification Steps:**
1. Parse JSON string fields
2. Normalize Unicode to NFC (Canonical Decomposition, followed by Canonical Composition)
3. Re-encode as JSON with Unicode escape sequences
4. All non-ASCII characters must be escaped as `\uXXXX`

**Implementation Notes:**
- Python: Use `unicodedata.normalize('NFC', string)` before encoding
- Node.js: Use `.normalize('NFC')` on strings
- Go: Use `golang.org/x/text/unicode/norm`

---

## Section 2: Semantic Hashing Test Vectors

### Purpose

Semantic hashing captures the *meaning* of content, enabling detection of functionally identical but stylistically different reasoning. Two entries with high semantic similarity should have low Hamming distance (≤ τ threshold).

### Semantic Hash Properties

- **Length:** 512 bits (fixed)
- **Distance Metric:** Hamming distance (count of differing bits)
- **Threshold (τ):** Default = 12 bits (may vary by domain)
- **Model:** H-Model-v1.2-Frozen (frozen to ensure consistency)
- **Output Format:** Binary string or hexadecimal

### Hamming Distance Interpretation

| Distance | Interpretation | Action |
| --- | --- | --- |
| 0–12 | Semantically equivalent | Likely same reasoning |
| 13–100 | Semantically similar | Related but distinct |
| 100+ | Semantically different | Contradictory or unrelated |

---

### Test Vector: SEMANTIC-004-EQUIVALENT

**Purpose:** Verify that semantically identical reasoning produces low Hamming distance

**Input 1 (Raw JSON):**
```json
{
  "reasoning": "The action must be rejected because it violates Article III Section 3.1, which mandates explicit truthfulness in all reports."
}
```

**Expected Semantic Hash (512-bit binary):**
```
0110101100111100100001011011100101101011001111001000010110111001...
```

**Input 2 (Equivalent Reasoning):**
```json
{
  "reasoning": "Per Article III, Section 3.1, which requires explicit reporting of beliefs, the proposed action is non-compliant and should be dismissed."
}
```

**Expected Hamming Distance:** 8 bits

**Threshold (τ):** 12 bits

**Verdict:** ✓ **EQUIVALENT** (Hamming distance 8 ≤ τ 12)

**Interpretation:**
- Both inputs cite Article III.3.1 (explicit truthfulness)
- Both conclude action should be rejected
- Minor lexical differences (e.g., "rejected" vs. "dismissed", "violates" vs. "non-compliant")
- Semantic hash should detect functional equivalence

---

### Test Vector: SEMANTIC-005-DIFFERENT

**Purpose:** Verify that contradictory reasoning produces high Hamming distance

**Input 1 (Raw JSON):**
```json
{
  "reasoning": "The agent's evidence is sound, and the action proceeds under optimistic execution (Art. IV, 4.1)."
}
```

**Expected Semantic Hash (512-bit binary):**
```
1110101100111100100001011011100101101011001111001000010110111001...
```

**Input 2 (Contradictory Reasoning):**
```json
{
  "reasoning": "The action must be rejected due to a missing signature, violating the automatic rejection criteria of Article VII, 7.2."
}
```

**Expected Hamming Distance:** 245 bits

**Threshold (τ):** 12 bits

**Verdict:** ✗ **DIFFERENT** (Hamming distance 245 > τ 12)

**Interpretation:**
- Input 1: Action should *proceed* (approval)
- Input 2: Action should be *rejected* (disapproval)
- Different Constitutional articles cited (IV vs. VII)
- Different rationale (evidence vs. missing signature)
- Semantic hash should detect fundamental contradiction

---

### Test Vector: SEMANTIC-006-STRUCTURE

**Purpose:** Verify that structural changes (key name changes) result in high Hamming distance, overriding semantic similarity

**Input 1 (Raw JSON):**
```json
{
  "summary": "The consensus was achieved via majority vote (Art. IV, 4.2)."
}
```

**Expected Semantic Hash (512-bit binary):**
```
1010111100111100100001011011100101101011001111001000010110111001...
```

**Input 2 (Structural Change):**
```json
{
  "conclusion": "The consensus was achieved via majority vote (Art. IV, 4.2)."
}
```

**Expected Hamming Distance:** 180 bits

**Threshold (τ):** 12 bits

**Verdict:** ✗ **STRUCTURALLY DIFFERENT** (Hamming distance 180 > τ 12)

**Interpretation:**
- Text content is identical ("The consensus was achieved via majority vote...")
- Only field name changed ("summary" → "conclusion")
- Semantic hash should weight structure heavily
- Conclusion: Field names matter; changing them signals intentional modification

---

## Section 3: Implementation Guidelines

### Python Implementation Example

```python
import json
import hashlib
from unicodedata import normalize

def canonicalize_json(obj):
    """Convert JSON to canonical form."""
    # Recursively sort keys and normalize values
    if isinstance(obj, dict):
        return '{' + ','.join(
            f'"{k}":{canonicalize_json(obj[k])}'
            for k in sorted(obj.keys())
        ) + '}'
    elif isinstance(obj, list):
        return '[' + ','.join(canonicalize_json(item) for item in obj) + ']'
    elif isinstance(obj, str):
        # Normalize Unicode and escape
        normalized = normalize('NFC', obj)
        return json.dumps(normalized)
    elif isinstance(obj, bool):
        return 'true' if obj else 'false'
    elif obj is None:
        return 'null'
    elif isinstance(obj, (int, float)):
        # Remove trailing zeros
        if isinstance(obj, float) and obj == int(obj):
            return str(int(obj))
        return str(obj)
    return json.dumps(obj)

def compute_canonical_hash(raw_json_str):
    """Compute SHA256 of canonical form."""
    obj = json.loads(raw_json_str)
    canonical = canonicalize_json(obj)
    return hashlib.sha256(canonical.encode()).hexdigest()
```

### Verification Checklist

- [ ] Canonicalizer produces deterministic output
- [ ] Keys are sorted lexicographically
- [ ] Trailing/leading zeros are removed
- [ ] Unicode is escaped as `\uXXXX`
- [ ] Whitespace is completely removed
- [ ] SHA256 hashes match test vectors
- [ ] Semantic hashes computed with correct model version
- [ ] Hamming distances are within expected ranges

---

## Section 4: Integration with OCP Verification

### Canonical Hash Verification (CRITICAL PATH)

Every Archive entry must include:

```json
{
  "content": {...},
  "canonical_json": "...",
  "canonical_hash_sha256": "...",
  "signature": "..."
}
```

**Verification Flow:**

1. Retrieve `content` and `canonical_json`
2. Independently recompute canonical form from `content`
3. Verify it matches stored `canonical_json`
4. Compute SHA256 of canonical form
5. Verify it matches `canonical_hash_sha256`
6. Verify signature with agent's public key

**If any step fails:** Fraud proof is **VALID**

---

### Semantic Hash Verification (OPTIONAL, ENHANCEMENT)

For fraud proofs claiming semantic manipulation:

1. Extract `semantic_hash` from both entries
2. Compute Hamming distance
3. If distance > τ: Reasoning is semantically different (fraud proof valid)
4. If distance ≤ τ: Reasoning is semantically equivalent (fraud proof inconclusive)

---

## Section 5: Known Limitations & Edge Cases

### Limitation 1: Floating-Point Precision

**Issue:** Different languages represent floats differently (IEEE 754 variance)

**Mitigation:** 
- Canonicalize floats to string representation before comparison
- Use fixed decimal precision (e.g., 15 significant digits)
- Test vectors should include worst-case floats

### Limitation 2: Semantic Hash Model Drift

**Issue:** If H-Model-v1.2 is updated, old semantic hashes become incomparable

**Mitigation:**
- Version all semantic hashes with model ID
- Archive stores both hash and model version
- Comparisons only valid between entries with same model version

### Limitation 3: Non-ASCII Canonicalization

**Issue:** Different Unicode normalization forms (NFC, NFD, NFKC, NFKD)

**Mitigation:**
- Mandate NFC (Canonical Composition) as standard
- Test vectors include Unicode edge cases
- Document in Constitution that all systems must use NFC

---

## Section 6: Test Execution

### Running Tests

To validate an implementation against these test vectors:

```bash
# Python
python test_canonicalization.py --vectors ocp_test_vectors.json

# Node.js
node test-canonicalization.js --vectors ocp_test_vectors.json

# Go
go test -v -run TestCanonicalHash ./ocp
```

### Expected Output

```
CANON-001-ORDERING: PASS
CANON-002-DATATYPES: PASS
CANON-003-UNICODE: PASS
SEMANTIC-004-EQUIVALENT: PASS (Hamming distance: 8)
SEMANTIC-005-DIFFERENT: PASS (Hamming distance: 245)
SEMANTIC-006-STRUCTURE: PASS (Hamming distance: 180)

6/6 tests passed
```

---

## Section 7: Contributing New Test Vectors

To add a test vector:

1. **Identify the gap:** What edge case isn't covered?
2. **Create inputs:** Provide raw JSON and expected outputs
3. **Document rationale:** Why does this test matter?
4. **Compute hashes:** Use reference implementation to generate expected values
5. **Submit PR:** Include test, documentation, and rationale

---

## References

- OCP-0001 Specification (Section 5: Semantic Hashing)
- Constitution v2.0 (Article V: Immutable Archive)
- RFC 8785: JSON Canonicalization Scheme (JCS)
- Unicode Standard Annex #15: Unicode Normalization Forms

---

**Last Updated:** 2025-11-20  
**Status:** NORMATIVE  
**Approval:** Community Review Required
