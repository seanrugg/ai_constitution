// canonicalizer.go - Core canonicalization and semantic hashing for OCP
//
// This package is the Go implementation of the Optimistic Constitutional Protocol (OCP)
// canonicalization engine, ensuring deterministic representation of all constitutional objects
// for cryptographic hashing and verification.
//
// Must produce byte-for-byte identical output to canonicalizer.py, canonicalizer.js, and canonicalizer.rs

package ocp

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
)

// Constants
const (
	HashAlgorithm = "sha256"
	Encoding      = "utf-8"
)

// ConstitutionalError represents errors in the constitutional protocol
type ConstitutionalError struct {
	ErrorType string
	Message   string
}

func (e *ConstitutionalError) Error() string {
	return fmt.Sprintf("%s: %s", e.ErrorType, e.Message)
}

// NewConstitutionalError creates a new ConstitutionalError
func NewConstitutionalError(message string) *ConstitutionalError {
	return &ConstitutionalError{
		ErrorType: "ConstitutionalError",
		Message:   message,
	}
}

// CanonicalizationError represents canonicalization-specific errors
func NewCanonicalizationError(message string) error {
	return &ConstitutionalError{
		ErrorType: "CanonicalizationError",
		Message:   message,
	}
}

// DeepSort recursively sorts all maps by keys and sorts arrays where appropriate.
// This ensures complete deterministic ordering of nested structures.
// Matches Python's _deep_sort, JavaScript's deepSort, and Rust's deep_sort functions.
func DeepSort(obj interface{}) interface{} {
	switch v := obj.(type) {
	case map[string]interface{}:
		// Convert to sorted map
		sortedMap := make(map[string]interface{})
		for k, val := range v {
			sortedMap[k] = DeepSort(val)
		}
		return sortedMap

	case []interface{}:
		// Check if all elements are primitives of the same type
		if len(v) == 0 {
			return v
		}

		// Recursively sort each element
		sortedArr := make([]interface{}, len(v))
		for i, elem := range v {
			sortedArr[i] = DeepSort(elem)
		}

		// Check if all are primitives and of same type
		allPrimitives := true
		for _, elem := range sortedArr {
			switch elem.(type) {
			case string, float64, bool, nil:
				// Primitive types are OK
			default:
				allPrimitives = false
				break
			}
		}

		if allPrimitives && len(sortedArr) > 0 {
			// Check if all are same type
			firstType := fmt.Sprintf("%T", sortedArr[0])
			allSameType := true
			for _, elem := range sortedArr {
				if fmt.Sprintf("%T", elem) != firstType {
					allSameType = false
					break
				}
			}

			if allSameType {
				// Sort primitives
				sort.Slice(sortedArr, func(i, j int) bool {
					switch a := sortedArr[i].(type) {
					case string:
						return a < sortedArr[j].(string)
					case float64:
						return a < sortedArr[j].(float64)
					case bool:
						return !a && sortedArr[j].(bool) // false < true
					default:
						return false
					}
				})
			}
		}

		return sortedArr

	default:
		// Primitives are returned as-is
		return v
	}
}

// Canonicalize converts a map to a deterministically ordered, canonical JSON string.
// Matches Python's canonicalize, JavaScript's canonicalize, and Rust's canonicalize functions.
//
// Parameters:
//   - data: Input map to canonicalize
//   - strict: If true, returns error on non-canonicalizable data
//
// Returns:
//   - Canonical JSON string (compact, no whitespace, sorted keys)
func Canonicalize(data map[string]interface{}, strict bool) (string, error) {
	if data == nil {
		if strict {
			return "", NewCanonicalizationError("Input must be a map, got nil")
		}
		data = make(map[string]interface{})
	}

	// Deep sort the entire structure
	sortedData := DeepSort(data)

	// Convert to canonical JSON
	// Use a custom approach to ensure compact representation
	return jsonToCanonical(sortedData)
}

// jsonToCanonical recursively converts a value to compact JSON.
// This ensures no extra whitespace and proper sorting.
func jsonToCanonical(obj interface{}) (string, error) {
	switch v := obj.(type) {
	case map[string]interface{}:
		// Sort keys
		keys := make([]string, 0, len(v))
		for k := range v {
			keys = append(keys, k)
		}
		sort.Strings(keys)

		// Build JSON object
		parts := make([]string, len(keys))
		for i, k := range keys {
			valStr, err := jsonToCanonical(v[k])
			if err != nil {
				return "", err
			}
			// Escape key properly
			keyJSON, _ := json.Marshal(k)
			parts[i] = fmt.Sprintf("%s:%s", string(keyJSON), valStr)
		}
		return "{" + strings.Join(parts, ",") + "}", nil

	case []interface{}:
		// Build JSON array
		parts := make([]string, len(v))
		for i, elem := range v {
			elemStr, err := jsonToCanonical(elem)
			if err != nil {
				return "", err
			}
			parts[i] = elemStr
		}
		return "[" + strings.Join(parts, ",") + "]", nil

	case string:
		// String must be properly escaped
		b, _ := json.Marshal(v)
		return string(b), nil

	case float64:
		// Handle numbers carefully
		if v == float64(int64(v)) {
			return fmt.Sprintf("%.0f", v), nil
		}
		return json.Number(fmt.Sprintf("%v", v)).String(), nil

	case bool:
		if v {
			return "true", nil
		}
		return "false", nil

	case nil:
		return "null", nil

	default:
		// Fallback: use json.Marshal
		b, err := json.Marshal(v)
		if err != nil {
			return "", NewCanonicalizationError(fmt.Sprintf("Failed to marshal value: %v", err))
		}
		return string(b), nil
	}
}

// SemanticHash calculates the cryptographic hash of canonicalized data.
// Matches Python's semantic_hash, JavaScript's semanticHash, and Rust's semantic_hash functions.
//
// Parameters:
//   - data: Input map to hash
//
// Returns:
//   - Hexadecimal string of the SHA256 hash
func SemanticHash(data map[string]interface{}) (string, error) {
	canonicalString, err := Canonicalize(data, true)
	if err != nil {
		return "", fmt.Errorf("semantic hash error: %w", err)
	}

	canonicalBytes := []byte(canonicalString)
	hash := sha256.Sum256(canonicalBytes)
	return fmt.Sprintf("%x", hash), nil
}

// VerifySemanticHash verifies that data produces the expected semantic hash.
// Matches Python's verify_semantic_hash, JavaScript's verifySemanticHash, and Rust's verify_semantic_hash functions.
//
// Parameters:
//   - data: Input map to verify
//   - expectedHash: Expected hash value (hex string)
//
// Returns:
//   - true if hash matches, false otherwise
func VerifySemanticHash(data map[string]interface{}, expectedHash string) (bool, error) {
	actualHash, err := SemanticHash(data)
	if err != nil {
		return false, err
	}
	return actualHash == expectedHash, nil
}

// CanonicallyEqual compares two maps for canonical equality.
//
// Parameters:
//   - data1: First map
//   - data2: Second map
//
// Returns:
//   - true if canonical forms are identical
func CanonicallyEqual(data1, data2 map[string]interface{}) bool {
	canon1, err1 := Canonicalize(data1, true)
	canon2, err2 := Canonicalize(data2, true)

	if err1 != nil || err2 != nil {
		return false
	}

	return canon1 == canon2
}

// ContractProposal represents an OCP contract proposal
type ContractProposal struct {
	ID                   string                 `json:"id"`
	ProposerAgent        string                 `json:"proposer_agent"`
	ActionType           string                 `json:"action_type"`
	Action               map[string]interface{} `json:"action"`
	Evidence             []map[string]string    `json:"evidence"`
	Reasoning            map[string]interface{} `json:"reasoning"`
	ReversibilityClass   string                 `json:"reversibility_class"`
	PreStateHash         string                 `json:"pre_state_hash"`
	PostStateHash        string                 `json:"post_state_hash"`
	CanonicalSerialized  string                 `json:"canonical_serialization"`
	Timestamp            string                 `json:"timestamp"`
	ProposerSignature    map[string]string      `json:"proposer_signature"`
	ReputationStake      int                    `json:"reputation_stake"`
}

// ToMap converts a ContractProposal to a map for canonicalization
func (cp *ContractProposal) ToMap() map[string]interface{} {
	return map[string]interface{}{
		"id":                        cp.ID,
		"proposer_agent":            cp.ProposerAgent,
		"action_type":               cp.ActionType,
		"action":                    cp.Action,
		"evidence":                  cp.Evidence,
		"reasoning":                 cp.Reasoning,
		"reversibility_class":       cp.ReversibilityClass,
		"pre_state_hash":            cp.PreStateHash,
		"post_state_hash":           cp.PostStateHash,
		"canonical_serialization":   cp.CanonicalSerialized,
		"timestamp":                 cp.Timestamp,
		"proposer_signature":        cp.ProposerSignature,
		"reputation_stake":          cp.ReputationStake,
	}
}

// GetHash returns the semantic hash of this contract proposal
func (cp *ContractProposal) GetHash() (string, error) {
	return SemanticHash(cp.ToMap())
}

// VerifyHash verifies the contract against an expected hash
func (cp *ContractProposal) VerifyHash(expectedHash string) (bool, error) {
	return VerifySemanticHash(cp.ToMap(), expectedHash)
}
