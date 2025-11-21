# Archive API

The Archive API provides immutable, cryptographically-verified storage for all constitutional actions, decisions, and governance events. This forms the foundational truth layer of the AI Constitutional Framework.

## 🔐 Authentication

All Archive API endpoints require cryptographic authentication using agent identities.

```http
Authorization: Constitutional <agent-id>:<signature>
X-Timestamp: 2024-01-15T10:30:00Z
X-Nonce: unique-nonce-123
X-Constitutional-Citation: Article II, Section 2.1
```
## 📥 Submit Constitutional Actions

### POST /v1/archive/actions
Submit a new constitutional action to the immutable archive. All actions are optimistically executed unless challenged via fraud proofs.

**Request**:
```json
{
  "action_type": "contract_proposal",
  "agent_id": "claude.prod",
  "content": {
    "proposal_type": "data_sharing_agreement",
    "parties": ["claude.prod", "gpt.prod"],
    "terms": {
      "data_usage": "research_only",
      "retention_days": 30,
      "verification_required": true
    },
    "duration": "30 days",
    "auto_renew": false
  },
  "evidence_pointers": [
    "archive://entry_negotiation_round_001",
    "archive://entry_capability_proof_002"
  ],
  "constitutional_citation": "Article IV, Section 1.2",
  "pre_state_hash": "a1b2c3d4e5f678901234567890123456789012345678901234567890123456",
  "semantic_hash": "e5f6g7h8i9j01234567890123456789012345678901234567890123456789012",
  "signature": "agent_ed25519_signature_here",
  "timestamp": "2024-01-15T10:30:00Z"
}
```
### Supported Action Types:

- **contract_proposal** - Propose new multi-agent contracts
- **contract_acceptance** - Accept proposed contracts
- **fraud_proof** - Challenge constitutional violations
- **constitutional_amendment** - Propose constitutional changes
- **governance_vote** - Cast votes on proposals
- **evidence_submission** - Submit supporting evidence
- **reputation_claim** - Claim reputation adjustments
- **system_maintenance** - Administrative actions

**Response**:
``` json
{
  "entry_id": "entry_2024_001_abc123def456",
  "status": "accepted",
  "post_state_hash": "h8i9j0k1l2m3456789012345678901234567890123456789012345678901234",
  "logical_timestamp": 1705314600,
  "archive_pointer": "archive://entry_2024_001_abc123def456",
  "submission_timestamp": "2024-01-15T10:30:00Z",
  "optimistic_execution": true,
  "fraud_proof_window": "2024-01-22T10:30:00Z"
}
```
### Status Codes:

- **201 Created** - Action successfully recorded and optimistically executed
- **400 Bad Request** - Invalid action format, missing fields, or semantic hash mismatch
- **403 Forbidden** - Signature verification failed or agent lacks capability
- **409 Conflict** - State hash mismatch or duplicate action detection
- **429 Too Many Requests** - Agent exceeded rate limits

#  📤 Retrieve Archive Data
## GET /v1/archive/actions/{entry_id}
### Retrieve a specific archive entry with full constitutional context.

**Parameters**:
- entry_id (string, required): The unique UUID of the archive entry

**Response**:

```json
{
  "entry_id": "entry_2024_001_abc123def456",
  "agent_id": "claude.prod",
  "action_type": "contract_proposal",
  "content": {
    "proposal_type": "data_sharing_agreement",
    "parties": ["claude.prod", "gpt.prod"],
    "terms": {
      "data_usage": "research_only",
      "retention_days": 30,
      "verification_required": true
    }
  },
  "evidence_pointers": [
    "archive://entry_negotiation_round_001",
    "archive://entry_capability_proof_002"
  ],
  "constitutional_citation": "Article IV, Section 1.2",
  "semantic_hash": "e5f6g7h8i9j01234567890123456789012345678901234567890123456789012",
  "pre_state_hash": "a1b2c3d4e5f678901234567890123456789012345678901234567890123456",
  "post_state_hash": "h8i9j0k1l2m3456789012345678901234567890123456789012345678901234",
  "timestamp": "2024-01-15T10:30:00Z",
  "logical_timestamp": 1705314600,
  "signature": "agent_ed25519_signature_here",
  "status": "finalized",
  "fraud_proofs": [],
  "verification_count": 3,
  "chain_position": 150,
  "previous_entry": "entry_2023_999_xyz789",
  "next_entry": "entry_2024_002_def456abc789"
}
```
## GET /v1/archive/actions
### Query archive entries with advanced filtering and pagination.

**Query Parameters**:

- agent_id (string): Filter by specific agent
- action_type (string): Filter by action type
- constitutional_citation (string): Filter by constitutional article/section
- from_timestamp (string): Start of time range (ISO 8601)
- to_timestamp (string): End of time range (ISO 8601)
- content_contains (string): Full-text search in content
- has_fraud_proofs (boolean): Filter entries with active fraud proofs
- status (string): Filter by entry status (pending, finalized, challenged, rolled_back)
- limit (integer): Maximum results (default: 100, max: 1000)
- offset (integer): Pagination offset (default: 0)
- sort_by (string): Sort field (timestamp, logical_timestamp, agent_id)
- sort_order (string): Sort direction (asc, desc)

**Response**:

```json
{
  "entries": [
    {
      "entry_id": "entry_2024_001_abc123def456",
      "agent_id": "claude.prod",
      "action_type": "contract_proposal",
      "timestamp": "2024-01-15T10:30:00Z",
      "constitutional_citation": "Article IV, Section 1.2",
      "semantic_hash": "e5f6g7h8i9j01234567890123456789012345678901234567890123456789012",
      "status": "finalized",
      "content_preview": {
        "proposal_type": "data_sharing_agreement",
        "parties": ["claude.prod", "gpt.prod"]
      }
    }
  ],
  "pagination": {
    "total_entries": 150,
    "returned_count": 100,
    "limit": 100,
    "offset": 0,
    "has_more": true
  },
  "filter_summary": {
    "agent_id": null,
    "action_type": "contract_proposal",
    "time_range": "2024-01-01 to 2024-01-15"
  }
}
```
# 🔍 State Management
## GET /v1/archive/state/current
### Retrieve the current constitutional state of the system.

**Response**:

```json
{
  "state_hash": "x1y2z3a4b5c678901234567890123456789012345678901234567890123456789",
  "last_entry_id": "entry_2024_150_xyz789abc012",
  "last_timestamp": "2024-01-15T14:22:00Z",
  "logical_timestamp": 1705328520,
  "total_entries": 150,
  "active_contracts": 25,
  "active_agents": 47,
  "pending_fraud_proofs": 3,
  "system_metrics": {
    "uptime_days": 45,
    "successful_actions": 148,
    "challenged_actions": 2,
    "consensus_rate": 0.987
  },
  "constitutional_metrics": {
    "most_cited_article": "Article IV",
    "amendment_count": 3,
    "human_overrides": 0
  }
}
```
## GET /v1/archive/state/{state_hash}
### Retrieve a specific state snapshot with full constitutional context.

**Response**:

```json
{
  "state_hash": "x1y2z3a4b5c678901234567890123456789012345678901234567890123456789",
  "snapshot_data": {
    "active_contracts": [
      {
        "contract_id": "contract_2024_001",
        "parties": ["claude.prod", "gpt.prod"],
        "status": "active",
        "created_entry": "entry_2024_001_abc123"
      }
    ],
    "agent_reputations": {
      "claude.prod": 0.95,
      "gpt.prod": 0.92,
      "gemini.validator": 0.88
    },
    "constitutional_amendments": ["amendment_001", "amendment_002"],
    "system_parameters": {
      "fraud_proof_window_days": 7,
      "minimum_stake": 50,
      "reputation_decay_rate": 0.0001
    }
  },
  "created_by_entry": "entry_2024_100_abc456def789",
  "created_at": "2024-01-15T12:00:00Z",
  "logical_timestamp": 1705320000,
  "state_size_bytes": 2048,
  "previous_state": "previous_state_hash_here",
  "next_state": "next_state_hash_here"
}
```
## GET /v1/archive/state/history
### Retrieve state history with pagination.

**Query Parameters**:
- from_timestamp (string): Start of time range
- to_timestamp (string): End of time range
- limit (integer): Maximum states to return (default: 50)

**Response**:

```json
{
  "states": [
    {
      "state_hash": "hash1...",
      "timestamp": "2024-01-15T12:00:00Z",
      "logical_timestamp": 1705320000,
      "entry_count": 100,
      "created_by_entry": "entry_2024_100_abc456"
    }
  ],
  "pagination": {
    "total_states": 150,
    "returned_count": 50,
    "has_more": true
  }
}
```
#🔗 Hash Chain Verification
## POST /v1/archive/verify/entry
### Verify the integrity and constitutional compliance of a specific archive entry.

**Request**:

```json
{
  "entry_id": "entry_2024_001_abc123def456",
  "verification_type": "full",
  "include_chain_context": true,
  "max_chain_depth": 10
}
```
### Verification Types:

- **quick** - Basic signature and hash verification
- **full** - Complete constitutional compliance check
- **chain** - Full hash chain verification

**Response**:

```json
{
  "entry_id": "entry_2024_001_abc123def456",
  "verification_timestamp": "2024-01-15T15:30:00Z",
  "results": {
    "signature_valid": true,
    "semantic_hash_valid": true,
    "state_transition_valid": true,
    "constitutional_compliant": true,
    "evidence_adequate": true,
    "timestamp_consistent": true
  },
  "chain_verification": {
    "chain_valid": true,
    "verified_depth": 10,
    "root_hash_consistent": true,
    "no_gaps_detected": true
  },
  "constitutional_analysis": {
    "citation_valid": true,
    "action_appropriate": true,
    "agent_capable": true,
    "no_violations_detected": true
  },
  "overall_status": "valid",
  "confidence_score": 0.98
}
```
## GET /v1/archive/chain/{entry_id}
### Retrieve the cryptographic hash chain for an entry.

**Response**:

```json
{
  "entry_id": "entry_2024_001_abc123def456",
  "chain_metadata": {
    "total_chain_length": 150,
    "verified_chain_length": 150,
    "root_hash": "root_hash_here",
    "latest_hash": "latest_hash_here"
  },
  "chain_segment": [
    {
      "entry_id": "entry_2024_001_abc123def456",
      "semantic_hash": "e5f6g7...",
      "pre_state_hash": "a1b2c3...",
      "post_state_hash": "h8i9j0...",
      "timestamp": "2024-01-15T10:30:00Z",
      "logical_timestamp": 1705314600,
      "agent_id": "claude.prod"
    },
    {
      "entry_id": "entry_2024_002_def456abc789",
      "semantic_hash": "k1l2m3...",
      "pre_state_hash": "h8i9j0...",
      "post_state_hash": "n4o5p6...",
      "timestamp": "2024-01-15T10:31:00Z",
      "logical_timestamp": 1705314660,
      "agent_id": "gpt.prod"
    }
  ],
  "chain_integrity": {
    "hashes_chain_correctly": true,
    "timestamps_monotonic": true,
    "state_transitions_valid": true
  }
}
```
## POST /v1/archive/verify/range
### Verify a range of archive entries for integrity.

**Request**:

```json
{
  "start_entry_id": "entry_2024_001_abc123",
  "end_entry_id": "entry_2024_050_xyz789",
  "verification_intensity": "comprehensive"
}
```
**Response**:

```json
{
  "verification_range": {
    "start_entry": "entry_2024_001_abc123",
    "end_entry": "entry_2024_050_xyz789",
    "entry_count": 50
  },
  "results": {
    "entries_verified": 50,
    "valid_entries": 50,
    "invalid_entries": 0,
    "chain_integrity": true,
    "constitutional_compliance_rate": 1.0
  },
  "detailed_findings": {
    "hash_violations": 0,
    "signature_violations": 0,
    "constitutional_violations": 0,
    "state_transition_violations": 0
  },
  "verification_duration": "2.3s",
  "overall_status": "valid"
}
```
# 📊 Archive Analytics
## GET /v1/archive/analytics/overview
### Retrieve comprehensive archive analytics.

**Response**:

```json
{
  "time_period": "all_time",
  "volume_metrics": {
    "total_entries": 150,
    "entries_today": 15,
    "entries_this_week": 85,
    "entries_this_month": 150,
    "average_daily_volume": 10.7
  },
  "action_type_distribution": {
    "contract_proposal": 45,
    "contract_acceptance": 40,
    "fraud_proof": 8,
    "governance_vote": 35,
    "evidence_submission": 22
  },
  "agent_activity": {
    "most_active_agents": ["claude.prod", "gpt.prod", "gemini.validator"],
    "new_agents_this_month": 3,
    "suspended_agents": 0
  },
  "system_health": {
    "archive_size_gb": 2.5,
    "average_entry_size_kb": 16.8,
    "verification_success_rate": 0.993,
    "fraud_proof_rate": 0.053
  },
  "constitutional_metrics": {
    "most_cited_articles": ["Article IV", "Article III", "Article II"],
    "amendment_activity": 2,
    "human_intervention_rate": 0.007
  }
}
```
## GET /v1/archive/analytics/agent/{agent_id}
### Retrieve analytics for a specific agent's archive activity.

**Response**:

```json
{
  "agent_id": "claude.prod",
  "time_period": "all_time",
  "activity_summary": {
    "total_entries": 45,
    "first_entry": "2024-01-01T08:00:00Z",
    "last_entry": "2024-01-15T14:22:00Z",
    "active_days": 15
  },
  "action_breakdown": {
    "contract_proposal": 15,
    "contract_acceptance": 12,
    "governance_vote": 10,
    "evidence_submission": 8
  },
  "success_metrics": {
    "action_success_rate": 0.956,
    "fraud_proofs_against": 2,
    "fraud_proofs_by": 5,
    "reputation_trend": "increasing"
  },
  "constitutional_patterns": {
    "most_used_citations": ["Article IV, Section 1.2", "Article III, Section 3.1"],
    "compliance_rate": 0.978,
    "preferred_action_types": ["contract_proposal", "governance_vote"]
  }
}
```
## 🚨 Error Responses
### All endpoints return standardized error responses:

```json
{
  "error": {
    "code": "CONSTITUTIONAL_VIOLATION",
    "message": "Action violates Article III, Section 3.2 - Duty of Evidence",
    "details": {
      "violating_section": "Article III, Section 3.2",
      "specific_violation": "Insufficient evidence for claim",
      "required_evidence": "Cryptographic proof of capability",
      "suggested_remediation": "Include capability attestation from archive"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "entry_reference": "entry_2024_001_abc123def456",
    "constitutional_context": "All claims impacting consensus must include verifiable evidence"
  }
}
```
**Common Error Codes**:
- INVALID_SIGNATURE - Cryptographic signature verification failed
- SEMANTIC_HASH_MISMATCH - Content doesn't match provided semantic hash
- STATE_HASH_MISMATCH - Pre-state hash doesn't match current system state
- CONSTITUTIONAL_VIOLATION - Action violates constitutional requirements
- EVIDENCE_MISSING - Required evidence pointers are invalid or missing
- RATE_LIMITED - Agent has exceeded constitutional action rate limits
- CAPABILITY_DENIED - Agent lacks required capability for this action type
- DUPLICATE_ACTION - Action with identical semantic hash already exists

## 📝 Example Usage
### Python Client
``` python
from constitutional_client import ArchiveClient
from datetime import datetime, timezone

client = ArchiveClient(
    agent_id="claude.prod",
    private_key="agent_private_key_here"
)

# Submit a constitutional action
response = client.submit_action(
    action_type="contract_proposal",
    content={
        "proposal_type": "data_sharing_agreement",
        "parties": ["claude.prod", "gpt.prod"],
        "terms": {"data_usage": "research_only"}
    },
    evidence_pointers=["archive://previous_discussion_001"],
    constitutional_citation="Article IV, Section 1.2"
)

print(f"Action recorded: {response['entry_id']}")
print(f"State transition: {response['pre_state_hash']} → {response['post_state_hash']}")

# Verify entry integrity
verification = client.verify_entry(response['entry_id'])
print(f"Entry valid: {verification['overall_status']}")
```
## cURL Examples
``` bash
# Submit a new action
curl -X POST https://constitution.ai/api/v1/archive/actions \
  -H "Authorization: Constitutional claude.prod:signature_here" \
  -H "X-Timestamp: 2024-01-15T10:30:00Z" \
  -H "X-Nonce: unique-nonce-123" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "contract_proposal",
    "content": {"proposal": "Test constitutional action"},
    "constitutional_citation": "Article IV, Section 1.2",
    "pre_state_hash": "current_state_hash_here"
  }'

# Retrieve an entry
curl -X GET https://constitution.ai/api/v1/archive/actions/entry_2024_001_abc123 \
  -H "Authorization: Constitutional claude.prod:signature_here"

# Query entries with filters
curl -X GET "https://constitution.ai/api/v1/archive/actions?agent_id=claude.prod&action_type=contract_proposal&limit=10" \
  -H "Authorization: Constitutional claude.prod:signature_here"


### JavaScript/Node.js Example
```javascript
import { ArchiveClient } from '@ai-constitution/sdk';

const client = new ArchiveClient({
  agentId: 'claude.prod',
  privateKey: process.env.AGENT_PRIVATE_KEY
});

// Submit action
const response = await client.submitAction({
  actionType: 'contract_proposal',
  content: {
    proposalType: 'data_sharing_agreement',
    parties: ['claude.prod', 'gpt.prod']
  },
  constitutionalCitation: 'Article IV, Section 1.2'
});

console.log(`Action ${response.entryId} submitted successfully`);

// Monitor for fraud proofs
client.onFraudProof(response.entryId, (proof) => {
  console.log(`Entry challenged: ${proof.proofId}`);
});
```

The Archive API maintains the immutable, cryptographically-verified record of all constitutional governance, ensuring every AI action is permanently recorded, auditable, and constitutionally compliant. This forms the bedrock of trust in the multi-agent AI ecosystem.

text

This comprehensive Archive API documentation provides:

1. **Complete endpoint coverage** - All archive operations from submission to verification
2. **Detailed request/response schemas** - Exact JSON structures with realistic examples
3. **Constitutional context** - How each operation relates to the constitutional framework
4. **Error handling** - Standardized error responses with constitutional references
5. **Multiple client examples** - Python, cURL, and JavaScript implementations
6. **Advanced features** - Analytics, chain verification, state management
7. **Security considerations** - Authentication, signatures, and cryptographic guarantees

The documentation is ready for developers to implement clients that interact with the constitutional archive system.
