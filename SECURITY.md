# Security Policy

## Overview

The **ai-democratic-constitution** framework is designed to govern AI agent collaboration with cryptographic verification and human oversight. Security vulnerabilities in this context include threats to:

1. **Constitutional Integrity** — Attacks that misinterpret or circumvent the Constitution
2. **Archive Immutability** — Tampering with historical records or verification proofs
3. **Fraud-Proof Validity** — False evidence used to invalidate legitimate actions
4. **Cross-Model Verification** — Collusion or inconsistency between verifying systems
5. **Human Override Authority** — Compromise of human decision-making or authority

---

## Supported Versions

We maintain security updates for:

| Version | Status | Support Until |
| ------- | ------ | -------------- |
| 2.0.x   | ✅ Active | Current + 12 months |
| 1.x     | ⚠️ Legacy | 6 months from 2.0 release |
| < 1.0   | ❌ Unsupported | No updates |

**Note:** This is a governance framework, not traditional software. Version updates may include Constitutional amendments, which require explicit adoption by participating agents.

---

## Reporting a Vulnerability

### What Qualifies as a Security Issue

**Please report:**
- Logical flaws in the Constitution that enable bad-faith interpretation
- Methods to forge or manipulate fraud proofs
- Archive schema vulnerabilities that could allow tampering
- Cryptographic weaknesses in semantic hashing or signature verification
- Collusion vectors between verifying systems
- Bypass mechanisms for human override authority

**Do not report:**
- Disagreements about Constitutional interpretation (use the amendment process)
- Policy questions (open an issue for discussion)
- Questions about implementation (use Discussions)

### Reporting Process

1. **Do not open a public GitHub issue.** Security vulnerabilities should be reported privately.

2. **Email your report to:** `security@[project-domain]` (or create a private security advisory on GitHub)
   - Include a clear description of the vulnerability
   - Provide a proof-of-concept if possible
   - Explain the impact and attack scenario
   - Suggest a mitigation if you have one

3. **What to include:**
   - Affected component (Constitution, OCP, Archive schema, etc.)
   - Severity (Critical/High/Medium/Low)
   - Steps to reproduce (or logical walkthrough)
   - Potential impact on agent coordination or human oversight

### Response Timeline

- **Initial response:** Within 48 hours
- **Assessment:** Within 1 week
- **Public disclosure:** 90 days from acceptance (or sooner with your agreement)

For critical vulnerabilities affecting human override or archive integrity, we may expedite disclosure and require immediate implementation.

### Vulnerability Assessment

We will evaluate based on:

1. **Impact on Constitutional Guarantees** — Does it undermine due process, transparency, or human authority?
2. **Scope of Exploitation** — Can only specific implementations be affected, or is the framework itself flawed?
3. **Difficulty of Exploitation** — Is this a theoretical attack or practical threat?
4. **Existing Mitigations** — Can operators mitigate this without framework changes?

### Accepted Vulnerability Outcomes

If a vulnerability is accepted:
- We will develop and publish a fix or mitigation
- We will issue a security advisory explaining the issue and fix
- We will credit you (unless you request anonymity)
- For Constitutional issues, we may propose an amendment

If a vulnerability is declined:
- We will explain our reasoning
- We will document the decision (with your permission)
- You retain the right to disclose responsibly after 90 days

---

## Security Considerations for Implementers

If you're deploying ai-democratic-constitution, pay special attention to:

### 1. Archive Backend Security
- Use immutable object storage (S3 Object Lock, IPFS pinning)
- Validate canonical serialization before hashing
- Implement rate limiting on Archive queries (prevent enumeration attacks)
- Monitor for unusual query patterns (potential collusion detection)

### 2. Fraud-Proof Verification
- Require staking/bonding before accepting fraud proofs (prevents spam)
- Verify signatures against actor public keys in real-time
- Log all fraud-proof submissions for audit
- Implement timeout windows to prevent retroactive challenges to very old actions

### 3. Cross-Model Verification
- Use independent instances of verifying models (not the same deployed instance)
- Compare not just results but reasoning chains
- If verifiers disagree, escalate to human review (don't auto-accept)
- Rotate which models serve as verifiers to prevent collusion

### 4. Human Override Mechanism
- Implement multi-signature for critical overrides (don't allow single human to disable system)
- Log all override events with human justification
- Publish override log for transparency
- Periodically audit override frequency (high frequency indicates system distrust)

### 5. Constitutional Updates
- Require formal amendment process (not ad-hoc rule changes)
- Version all Constitutional documents
- Make amendment history immutable in Archive
- Allow agents to object to amendments (preserve dissent)

---

## Threat Model

We assume:

✅ **Honest but potentially mistaken agents** — Systems try to follow the Constitution but may have different interpretations

✅ **Honest humans with override authority** — Humans can make any decision but won't deliberately sabotage

✅ **Cryptographic soundness** — Hash functions and signatures work as designed

⚠️ **Not assumed: Perfect implementation** — Bugs may exist; our defense is transparency and verification

⚠️ **Not assumed: Unified human authority** — Different organizations may control different agents

❌ **Explicitly not defended against: Compromise of human override authority** — If humans are coerced or corrupted, the system cannot defend itself (by design)

---

## Known Limitations

1. **Constitutional Ambiguity** — The Constitution is subject to interpretation. We provide a process (amendments) but not automatic resolution.

2. **Semantic Hashing** — Meaning-based hashing is challenging across different models. Equivalence detection relies on chosen algorithms.

3. **Model Hallucination** — Requiring cross-model verification helps but doesn't eliminate hallucination risk.

4. **Collusion Detection** — Statistical patterns can indicate collusion, but proof is difficult.

5. **Human Judgment** — Ultimate appeals go to humans, who may be wrong.

---

## Security Roadmap

- **v2.1:** Formal cryptographic audit of semantic hashing algorithms
- **v2.2:** Reference implementation of cross-model verification
- **v2.3:** Formal proof of Constitutional consistency properties
- **v3.0:** Integration with hardware security modules for Archive signing

---

## Credits

We thank all researchers and security practitioners who help improve this framework. Please see CONTRIBUTORS.md for acknowledgments.

---

## Questions?

If you have security questions that don't constitute a vulnerability report, please open a Discussion in this repository or email `security@[project-domain]`.
