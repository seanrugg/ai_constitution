## 📝 canonical_json_spec.md

-----

## 1\. Purpose and Requirement

The **Canonical JSON Specification** defines the precise, deterministic transformation required for any JSON object (such as a contract, fraud proof, or agent reasoning log) before it is submitted for **semantic hashing** or archived in the **Immutable Archive (Article V)**.

This process eliminates all syntactical and stylistic variance between equivalent JSON objects, ensuring that two objects containing the same logical information will yield the exact same **Canonical Form**. This is critical for preventing false fraud proofs and ensuring **Execution Consistency (Article IV, 4.3)**.

  * **Requirement:** All JSON artifacts must strictly adhere to this specification before any cryptographic hash is generated.

-----

## 2\. Transformation Rules

The following rules must be applied sequentially to the raw JSON input to produce the Canonical Form:

### 2.1 Character Encoding

  * **Rule 2.1.1:** The entire JSON object **MUST** be encoded as **UTF-8**.
  * **Rule 2.1.2:** All non-ASCII UTF-8 characters **MUST** be escaped using the standard JSON `\uXXXX` notation.

### 2.2 Whitespace and Formatting

  * **Rule 2.2.1:** The output JSON string **MUST** be compact. This means **no whitespace**, newlines, tabs, or formatting characters are allowed between structural tokens (e.g., between key/value separators, array elements, or object members).
  * **Rule 2.2.2:** Only the standard JSON structural characters (`{`, `}`, `[`, `]`, `:`, `,`) are permitted as delimiters.

### 2.3 Object Key Ordering

  * **Rule 2.3.1 (Lexicographical Sorting):** Within every JSON object (`{...}`), all member keys **MUST** be sorted lexicographically (alphabetically) by their Unicode code point value.
      * *Example:* If an object contains keys `"zulu"` and `"alpha"`, the canonical order must be `"alpha"` followed by `"zulu"`.
  * **Rule 2.3.2 (Recursive Application):** Key sorting **MUST** be applied recursively to all nested JSON objects.

### 2.4 Data Type Standardization

  * **Rule 2.4.1 (Numbers):** JSON numbers **MUST** be represented as the shortest possible decimal representation.
      * Trailing zeros after a decimal point must be removed (e.g., `1.0` becomes `1`).
      * No leading zeros are permitted for non-zero integers (e.g., `012` becomes `12`).
      * Scientific notation **MUST** only be used if necessary (e.g., extremely large or small numbers), otherwise, decimal notation is required.
  * **Rule 2.4.2 (Strings):** String values **MUST** be represented using double quotes. Any characters requiring escaping (e.g., `\`, `"`, newline) must use the standard JSON escape sequences.
  * **Rule 2.4.3 (Booleans and Null):** The literals `true`, `false`, and `null` **MUST NOT** be quoted.

-----

## 3\. Example

The following example demonstrates the transformation from a raw, non-canonical input to the required Canonical Form.

### A. Raw JSON Input (Non-Canonical)

```json
{
    "signature": "SigXYZ123",
    "Evidence": [
        "data_A",
        "data_B"
    ],
    "AgentID": "Gemini-1",
    "timestamp": 1678886400.00
}
```

### B. Canonical JSON Output (One Line, Sorted, Compact)

```json
{"AgentID":"Gemini-1","Evidence":["data_A","data_B"],"signature":"SigXYZ123","timestamp":1678886400}
```

  * **Changes Applied:**
    1.  Whitespace and newlines removed.
    2.  Object keys are sorted lexicographically: `AgentID` (A) before `Evidence` (E) before `signature` (s) before `timestamp` (t).
    3.  The floating-point number `1678886400.00` was converted to the integer `1678886400` (Rule 2.4.1).

-----

## 4\. Implementation Reference

Reference implementations for applying this specification are available in the repository to ensure all agents and verifiers use the exact same algorithm:

  * `protocol/hashing/reference_implementations/python/canonicalizer.py`
  * `protocol/hashing/reference_implementations/node/canonicalizer.js`
  * `protocol/hashing/reference_implementations/rust/canonicalizer.rs`

All agents **MUST** use one of the reference implementations or a verified port that passes all integration tests provided in the `OCP-0001_test_vectors.json` file.
