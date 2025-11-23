package ocp

import (
	"fmt"
	"testing"
)

// TestBasicCanonicalizer tests basic canonicalization with order independence
func TestBasicCanonicalizer(t *testing.T) {
	dictA := map[string]interface{}{
		"a": float64(1),
		"b": float64(2),
		"c": float64(3),
	}

	dictB := map[string]interface{}{
		"c": float64(3),
		"a": float64(1),
		"b": float64(2),
	}

	canonicalA, err := Canonicalize(dictA, true)
	if err != nil {
		t.Fatalf("Failed to canonicalize dictA: %v", err)
	}

	canonicalB, err := Canonicalize(dictB, true)
	if err != nil {
		t.Fatalf("Failed to canonicalize dictB: %v", err)
	}

	if canonicalA != canonicalB {
		t.Errorf("Canonical forms should match:\n  A: %s\n  B: %s", canonicalA, canonicalB)
	}

	hashA, err := SemanticHash(dictA)
	if err != nil {
		t.Fatalf("Failed to hash dictA: %v", err)
	}

	hashB, err := SemanticHash(dictB)
	if err != nil {
		t.Fatalf("Failed to hash dictB: %v", err)
	}

	if hashA != hashB {
		t.Errorf("Hashes should match:\n  A: %s\n  B: %s", hashA, hashB)
	}

	t.Logf("✓ Canonical forms match: %s", canonicalA)
	t.Logf("✓ Hashes match: %s", hashA)
}

// TestNestedStructures tests canonicalization of nested maps and arrays
func TestNestedStructures(t *testing.T) {
	complexDict := map[string]interface{}{
		"z": []interface{}{float64(3), float64(1), float64(2)},
		"a": map[string]interface{}{
			"c": float64(3),
			"a": float64(1),
			"b": map[string]interface{}{
				"f": float64(6),
				"d": float64(4),
				"e": float64(5),
			},
		},
		"b": float64(2),
	}

	canonical, err := Canonicalize(complexDict, true)
	if err != nil {
		t.Fatalf("Failed to canonicalize: %v", err)
	}

	expected := `{"a":{"a":1,"b":{"d":4,"e":5,"f":6},"c":3},"b":2,"z":[1,2,3]}`
	if canonical != expected {
		t.Errorf("Canonical form mismatch:\n  Expected: %s\n  Got:      %s", expected, canonical)
	}

	t.Logf("✓ Nested structure canonicalized correctly: %s", canonical)
}

// TestHashSensitivity tests that hashes change with content
func TestHashSensitivity(t *testing.T) {
	actionA := map[string]interface{}{
		"action_id":    "001-XYZ",
		"agent":        "Claude-3",
		"claim":        "The initial cost is $500",
		"evidence_ptr": "archive://0000001",
		"timestamp":    float64(1700000000),
	}

	actionB := map[string]interface{}{
		"action_id":    "001-XYZ",
		"agent":        "Claude-3",
		"claim":        "The initial cost is $501", // Changed value
		"evidence_ptr": "archive://0000001",
		"timestamp":    float64(1700000000),
	}

	hashA, err := SemanticHash(actionA)
	if err != nil {
		t.Fatalf("Failed to hash actionA: %v", err)
	}

	hashB, err := SemanticHash(actionB)
	if err != nil {
		t.Fatalf("Failed to hash actionB: %v", err)
	}

	if hashA == hashB {
		t.Errorf("Hashes should differ with content change")
	}

	t.Logf("✓ Hash A: %s", hashA)
	t.Logf("✓ Hash B: %s", hashB)
	t.Logf("✓ Hashes correctly differ")
}

// TestVerifyHash tests hash verification
func TestVerifyHash(t *testing.T) {
	testData := map[string]interface{}{
		"action": "propose",
		"value":  float64(42),
	}

	testHash, err := SemanticHash(testData)
	if err != nil {
		t.Fatalf("Failed to generate hash: %v", err)
	}

	// Verify valid hash
	valid, err := VerifySemanticHash(testData, testHash)
	if err != nil {
		t.Fatalf("Failed to verify hash: %v", err)
	}

	if !valid {
		t.Errorf("Valid hash should verify")
	}

	// Verify invalid hash
	tamperedData := map[string]interface{}{
		"action": "propose",
		"value":  float64(43),
	}

	invalid, err := VerifySemanticHash(tamperedData, testHash)
	if err != nil {
		t.Fatalf("Failed to verify tampered hash: %v", err)
	}

	if invalid {
		t.Errorf("Tampered data should fail verification")
	}

	t.Logf("✓ Valid hash verifies: %s", testHash)
	t.Logf("✓ Tampered data fails verification")
}

// TestCanonicalEquality tests structural equality
func TestCanonicalEquality(t *testing.T) {
	obj1 := map[string]interface{}{
		"z": float64(1),
		"a": float64(2),
	}

	obj2 := map[string]interface{}{
		"a": float64(2),
		"z": float64(1),
	}

	if !CanonicallyEqual(obj1, obj2) {
		t.Errorf("Reordered objects should be canonically equal")
	}

	obj3 := map[string]interface{}{
		"a": float64(2),
		"z": float64(2), // Different value
	}

	if CanonicallyEqual(obj1, obj3) {
		t.Errorf("Different objects should not be canonically equal")
	}

	t.Logf("✓ Canonical equality works correctly")
}

// TestArraySorting tests that arrays are sorted correctly
func TestArraySorting(t *testing.T) {
	withUnsorted := map[string]interface{}{
		"numbers": []interface{}{float64(5), float64(3), float64(1), float64(4), float64(2)},
	}

	withSorted := map[string]interface{}{
		"numbers": []interface{}{float64(1), float64(2), float64(3), float64(4), float64(5)},
	}

	hashUnsorted, err := SemanticHash(withUnsorted)
	if err != nil {
		t.Fatalf("Failed to hash unsorted: %v", err)
	}

	hashSorted, err := SemanticHash(withSorted)
	if err != nil {
		t.Fatalf("Failed to hash sorted: %v", err)
	}

	if hashUnsorted != hashSorted {
		t.Errorf("Sorted and unsorted arrays should have same hash")
	}

	t.Logf("✓ Array sorting produces consistent hashes")
}

// TestComplexContract tests a complex contract structure
func TestComplexContract(t *testing.T) {
	contract := map[string]interface{}{
		"id":               "550e8400-e29b-41d4-a716-446655440000",
		"proposer_agent":   "Claude",
		"action_type":      "amend",
		"action": map[string]interface{}{
			"target":    "amendment-article-3",
			"operation": "modify",
		},
		"evidence": []map[string]string{
			{
				"type":    "archive_reference",
				"pointer": "sha256:abc123def456",
			},
		},
		"reasoning": map[string]interface{}{
			"rationale":  "Clarifies Article III.1",
			"confidence": float64(0.87),
		},
		"timestamp": "2025-11-20T14:30:00Z",
	}

	hash, err := SemanticHash(contract)
	if err != nil {
		t.Fatalf("Failed to hash complex contract: %v", err)
	}

	if len(hash) != 64 {
		t.Errorf("SHA256 hash should be 64 hex characters, got %d", len(hash))
	}

	valid, err := VerifySemanticHash(contract, hash)
	if err != nil {
		t.Fatalf("Failed to verify contract hash: %v", err)
	}

	if !valid {
		t.Errorf("Contract hash should verify")
	}

	t.Logf("✓ Complex contract hash: %s", hash)
	t.Logf("✓ Contract hash verifies")
}

// TestCrossLanguageVector tests cross-language validation
func TestCrossLanguageVector(t *testing.T) {
	pythonTestVector := map[string]interface{}{
		"action":      "propose",
		"agent":       "Claude",
		"confidence":  float64(0.88),
		"timestamp":   "2025-11-20T14:30:00Z",
	}

	hash, err := SemanticHash(pythonTestVector)
	if err != nil {
		t.Fatalf("Failed to generate test vector hash: %v", err)
	}

	if len(hash) != 64 {
		t.Errorf("Hash should be 64 characters, got %d", len(hash))
	}

	t.Logf("✓ Go hash: %s", hash)
	t.Logf("✓ Compare with Python/JavaScript/Rust for validation")
}

// TestContractProposalType tests the ContractProposal helper type
func TestContractProposalType(t *testing.T) {
	proposal := &ContractProposal{
		ID:                 "550e8400-e29b-41d4-a716-446655440000",
		ProposerAgent:      "Claude",
		ActionType:         "amend",
		Action: map[string]interface{}{
			"target":    "amendment-article-3",
			"operation": "modify",
		},
		Evidence: []map[string]string{
			{
				"type":    "archive_reference",
				"pointer": "sha256:abc123def456",
			},
		},
		Reasoning: map[string]interface{}{
			"rationale":  "Clarifies Article III.1",
			"confidence": float64(0.87),
		},
		ReversibilityClass:  "partially_reversible",
		PreStateHash:        "sha256:1234567890abcdef",
		PostStateHash:       "sha256:fedcba0987654321",
		CanonicalSerialized: "{...}",
		Timestamp:           "2025-11-20T14:30:00Z",
		ProposerSignature: map[string]string{
			"algorithm": "ed25519",
			"value":     "3a4b5c6d7e8f9a0b",
		},
		ReputationStake: 60,
	}

	hash, err := proposal.GetHash()
	if err != nil {
		t.Fatalf("Failed to get proposal hash: %v", err)
	}

	if len(hash) != 64 {
		t.Errorf("Hash should be 64 hex characters")
	}

	valid, err := proposal.VerifyHash(hash)
	if err != nil {
		t.Fatalf("Failed to verify proposal hash: %v", err)
	}

	if !valid {
		t.Errorf("Proposal hash should verify")
	}

	t.Logf("✓ ContractProposal hash: %s", hash)
	t.Logf("✓ ContractProposal hash verifies")
}

// BenchmarkCanonicalHash benchmarks canonical hash computation
func BenchmarkCanonicalHash(b *testing.B) {
	testData := map[string]interface{}{
		"action":      "propose",
		"agent":       "Claude",
		"confidence":  float64(0.88),
		"timestamp":   "2025-11-20T14:30:00Z",
		"evidence_ptr": "archive://0000001",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = SemanticHash(testData)
	}
}

// BenchmarkCanonicalize benchmarks canonicalization
func BenchmarkCanonicalize(b *testing.B) {
	testData := map[string]interface{}{
		"action":      "propose",
		"agent":       "Claude",
		"confidence":  float64(0.88),
		"timestamp":   "2025-11-20T14:30:00Z",
		"evidence_ptr": "archive://0000001",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = Canonicalize(testData, true)
	}
}

// ExampleCanonicalize demonstrates canonicalization
func ExampleCanonicalize() {
	data := map[string]interface{}{
		"action": "propose",
		"agent":  "Claude",
		"value":  float64(42),
	}

	canonical, err := Canonicalize(data, true)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}

	fmt.Printf("Canonical: %s\n", canonical)
}

// ExampleSemanticHash demonstrates hash computation
func ExampleSemanticHash() {
	data := map[string]interface{}{
		"action": "propose",
		"agent":  "Claude",
		"value":  float64(42),
	}

	hash, err := SemanticHash(data)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}

	fmt.Printf("Hash: %s\n", hash)
}

// ExampleVerifySemanticHash demonstrates hash verification
func ExampleVerifySemanticHash() {
	data := map[string]interface{}{
		"action": "propose",
		"value":  float64(42),
	}

	hash, err := SemanticHash(data)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}

	valid, err := VerifySemanticHash(data, hash)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}

	fmt.Printf("Valid: %v\n", valid)
}
