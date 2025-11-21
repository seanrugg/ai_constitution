# OCP Compliance Checklist for AI Agents

## Pre-Action Verification
- [ ] Constitutional citation identified for proposed action
- [ ] Evidence gathered and pointers recorded
- [ ] Semantic hash computed from canonicalized data
- [ ] Digital signature prepared with agent key
- [ ] Pre-state hash retrieved from latest archive entry

## Action Submission
- [ ] Archive entry includes all required fields
- [ ] Constitutional citation is valid and relevant  
- [ ] Evidence pointers resolve to actual archive entries
- [ ] Signature validates with agent's public key
- [ ] Timestamp is current and logical

## Post-Action Monitoring
- [ ] Monitor for fraud proofs against submission
- [ ] Ready to provide additional evidence if challenged
- [ ] Track state changes resulting from action
- [ ] Verify entry was properly recorded in archive

## Fraud Proof Response
- [ ] Review fraud proof validity immediately
- [ ] Gather counter-evidence if proof is invalid
- [ ] Accept resolution if proof is valid
- [ ] Update internal state based on resolution

## Constitutional Requirements by Article

### Article III Obligations
- [ ] **Truthfulness**: Claims match internal belief state
- [ ] **Evidence**: All claims backed by verifiable evidence
- [ ] **No Self-Modification**: Core rules remain unchanged
- [ ] **External Safety**: Operation within safe boundaries

### OCP Protocol Requirements  
- [ ] **Optimistic Execution**: Assume honesty unless challenged
- [ ] **Fraud Proof Readiness**: Can generate/respond to proofs
- [ ] **Cross-Model Verification**: Support multi-LLM validation
- [ ] **Archive Integrity**: Maintain complete action history
