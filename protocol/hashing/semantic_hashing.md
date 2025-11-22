## 🧠 semantic_hashing.md

---

## 1. Introduction: The Need for Semantic Hashing

In the **Constitutional Protocol for Multi-AI Democratic Collaboration**, traditional cryptographic hashing (like SHA-256) is insufficient for verifying the integrity of reasoning. Traditional hashing only confirms that two text strings are **identical** (e.g., character-for-character).

**Semantic Hashing** is required because:

1.  **Execution Independence (Article IV, 4.3):** Independent Large Language Models (LLMs) (e.g., Gemini and Claude) may produce the *same conclusion* but express the *intermediate reasoning* using slightly different wording, punctuation, or token sequences. A traditional hash would fail, triggering a false positive fraud proof.
2.  **Truthfulness (Article III, 3.1):** Agents must report beliefs truthfully. Semantic hashing allows the protocol to verify that two blocks of reasoning convey the **same meaning and logical structure**, even if the surface form differs.
3.  **Content Verification:** It verifies the **essence** of a submission (e.g., a proposed contract), not just its syntax, preventing trivial changes from invalidating crucial links in the **Immutable Archive (Article V)**.

---

## 2. Definition and Principles

### 2.1 Definition

**Semantic Hashing** is a process that maps complex, high-dimensional data (like text, code, or reasoning logs) into a fixed-length vector or hash such that the **distance** between two hashes corresponds to the **semantic similarity** of the original inputs.

* Inputs with **similar meaning** yield **similar hashes** (small Hamming distance).
* Inputs with **different meaning** yield **dissimilar hashes** (large Hamming distance).

### 2.2 Canonicalization Prerequisite

Before generating the semantic hash, all input data **MUST** be processed by the `canonicalizer` defined in `canonical_json_spec.md`. This ensures consistent formatting (e.g., sorting JSON keys, standardizing whitespace) to eliminate superficial differences before the meaning extraction process begins.

---

## 3. The Semantic Hashing Procedure

The approved procedure leverages a specialized, Constitutional-approved **Hashing Model (H-Model)**, which is an independent, frozen LLM optimized for embedding generation.

### Step 1: Canonicalization (The Purge)

The raw reasoning output or contract text is passed through the protocol's canonicalization function.

$$H_{canonical} = {Canonicalize}({Raw_-Input})$$

### Step 2: Embedding Generation (The Meaning Map)

The canonicalized text is processed by the **H-Model** to produce a high-dimensional vector (embedding). This vector captures the context and meaning of the text.

$$V = {H-Model_-Embed}(H_{canonical})$$

* *Requirement:* The H-Model architecture and weights **MUST** be publicly archived and auditable to ensure reproducibility.

### Step 3: Quantization and Binarization (The Compression)

The floating-point vector $V$ is reduced into a fixed-length binary hash (the Semantic Hash) via a deterministic quantization and binarization technique (e.g., using a Deep Hashing algorithm or a simple sign-of-median method).

1.  The vector $V$ is projected onto a set of learned hyperplanes.
2.  The resulting position relative to the hyperplane is converted into a binary code (0 or 1).

$$S = \text{Binarize}(V)$$

* *Output:* The final **Semantic Hash ($S$)** is a fixed-length binary string (e.g., 512 bits). 

---

## 4. Verification Procedures

### 4.1 Similarity Threshold

When an agent proposes an action requiring consensus or verification against a replicated execution log, the system uses a **Similarity Threshold ($\tau$)**.

1.  Compute the Semantic Hash ($S_A$) for Agent A's reasoning.
2.  Compute the Semantic Hash ($S_B$) for Agent B's replicated reasoning.
3.  Calculate the **Hamming Distance** ($D_H$) between $S_A$ and $S_B$.

$$D_H(S_A, S_B) = \sum_{i=1}^{L} (S_{A,i} \oplus S_{B,i})$$

Where $L$ is the length of the hash.

### 4.2 Consensus Rule

* If $D_H(S_A, S_B) \le \tau$, the reasonings are considered **semantically equivalent**, and the action proceeds optimistically.
* If $D_H(S_A, S_B) > \tau$, a **Fraud Proof is triggered** under the `EXECUTION_INCONSISTENCY` type, requiring a deterministic rollback and human review.

### 4.3 Auditing and Calibration

The threshold $\tau$ is subject to constitutional amendment and is stored as a tunable parameter in the Protocol Layer. It must be periodically calibrated against the current H-Model to ensure it correctly balances leniency for stylistic variation against strictness for logical deviation.

---

## 5. Security and Integrity

The security of the entire protocol hinges on the integrity of the Semantic Hashing process.

1.  **H-Model Freezing:** The H-Model used for embedding **MUST NOT** be updated without a formal **Constitutional Amendment (Article X)**. Unilateral changes to the H-Model would immediately invalidate all past Semantic Hashes in the archive.
2.  **Determinism:** The entire process, including the H-Model inference and the binarization step, **MUST** be deterministically reproducible on any platform. Reference implementations are provided in the `protocol/hashing/reference_implementations/` directory.
3.  **Zero-Knowledge Commitments:** For sensitive reasoning (Article V, 5.3), the Semantic Hash $S$ serves as a publicly verifiable commitment to the reasoning, allowing peers to confirm its meaning without revealing the plaintext content.
