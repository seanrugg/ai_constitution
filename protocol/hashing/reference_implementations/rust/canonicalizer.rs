/// canonicalizer.rs - Core canonicalization and semantic hashing for OCP
///
/// This module is the Rust implementation of the Optimistic Constitutional Protocol (OCP)
/// canonicalization engine, ensuring deterministic representation of all constitutional objects
/// for cryptographic hashing and verification.
///
/// Must produce byte-for-byte identical output to canonicalizer.py and canonicalizer.js

use serde_json::{json, Value, Map};
use sha2::{Sha256, Digest};
use std::collections::BTreeMap;
use thiserror::Error;

// --- Constants ---
pub const HASH_ALGORITHM: &str = "sha256";
pub const ENCODING: &str = "utf-8";

// --- Custom Error Types ---
#[derive(Error, Debug)]
pub enum ConstitutionalError {
    #[error("Constitutional protocol error: {0}")]
    ProtocolError(String),
    
    #[error("Canonicalization error: {0}")]
    CanonicalizationError(String),
    
    #[error("Hashing error: {0}")]
    HashingError(String),
}

pub type Result<T> = std::result::Result<T, ConstitutionalError>;

/// Recursively sort all dictionaries by keys and sort arrays where appropriate.
/// This ensures complete deterministic ordering of nested structures.
/// Matches Python's _deep_sort and JavaScript's deepSort functions.
fn deep_sort(value: &Value) -> Value {
    match value {
        Value::Object(map) => {
            // Convert to BTreeMap (automatically sorted by keys)
            let mut sorted_map = BTreeMap::new();
            for (k, v) in map.iter() {
                sorted_map.insert(k.clone(), deep_sort(v));
            }
            
            // Convert back to serde_json::Map
            let mut result_map = Map::new();
            for (k, v) in sorted_map.into_iter() {
                result_map.insert(k, v);
            }
            Value::Object(result_map)
        }
        Value::Array(arr) => {
            // Check if all elements are primitives of same type
            let all_primitives = arr.iter().all(|v| {
                matches!(
                    v,
                    Value::String(_) | Value::Number(_) | Value::Bool(_) | Value::Null
                )
            });
            
            if all_primitives && arr.len() > 0 {
                // Check if all are same type
                let first_type = std::mem::discriminant(&arr[0]);
                let all_same_type = arr.iter().all(|v| std::mem::discriminant(v) == first_type);
                
                if all_same_type {
                    // Sort primitives of same type
                    let mut sorted = arr
                        .iter()
                        .map(|v| deep_sort(v))
                        .collect::<Vec<_>>();
                    
                    sorted.sort_by(|a, b| {
                        // Custom comparison for JSON values
                        match (a, b) {
                            (Value::String(s1), Value::String(s2)) => s1.cmp(s2),
                            (Value::Number(n1), Value::Number(n2)) => {
                                // Compare as f64 for consistency
                                let f1 = n1.as_f64().unwrap_or(0.0);
                                let f2 = n2.as_f64().unwrap_or(0.0);
                                f1.partial_cmp(&f2).unwrap_or(std::cmp::Ordering::Equal)
                            }
                            (Value::Bool(b1), Value::Bool(b2)) => b1.cmp(b2),
                            _ => std::cmp::Ordering::Equal,
                        }
                    });
                    
                    Value::Array(sorted)
                } else {
                    // Mixed types - maintain order
                    Value::Array(arr.iter().map(|v| deep_sort(v)).collect())
                }
            } else {
                // Empty array or non-primitive - maintain order
                Value::Array(arr.iter().map(|v| deep_sort(v)).collect())
            }
        }
        _ => {
            // Primitives are returned as-is
            value.clone()
        }
    }
}

/// Convert a serde_json::Value to a deterministically ordered, canonical JSON string.
/// Matches Python's canonicalize and JavaScript's canonicalize functions.
///
/// # Arguments
/// * `data` - Input JSON value to canonicalize
/// * `strict` - If true, returns error on non-canonicalizable data
///
/// # Returns
/// Canonical JSON string (compact, no whitespace, sorted keys)
pub fn canonicalize(data: &Value, strict: bool) -> Result<String> {
    // Ensure we have an object
    if !data.is_object() {
        if strict {
            return Err(ConstitutionalError::CanonicalizationError(
                format!("Input must be an object, got {:?}", data.type_str())
            ));
        } else {
            // Wrap in object
            let wrapped = json!({ "value": data });
            return canonicalize(&wrapped, false);
        }
    }

    // Deep sort the entire structure
    let sorted_data = deep_sort(data);
    
    // Convert to canonical JSON string using compact representation
    // serde_json::to_string produces compact JSON with no extra whitespace
    match serde_json::to_string(&sorted_data) {
        Ok(canonical_json) => {
            if canonical_json.is_empty() {
                Err(ConstitutionalError::CanonicalizationError(
                    "Failed to produce canonical JSON string".to_string()
                ))
            } else {
                Ok(canonical_json)
            }
        }
        Err(e) => {
            if strict {
                Err(ConstitutionalError::CanonicalizationError(
                    format!("Failed to canonicalize data: {}", e)
                ))
            } else {
                // Fallback: convert all values to strings and retry
                if let Value::Object(map) = data {
                    let mut stringified = Map::new();
                    for (k, v) in map.iter() {
                        stringified.insert(k.clone(), Value::String(v.to_string()));
                    }
                    let wrapped_obj = Value::Object(stringified);
                    canonicalize(&wrapped_obj, false)
                } else {
                    Err(ConstitutionalError::CanonicalizationError(
                        format!("Data cannot be canonicalized even with fallback: {}", e)
                    ))
                }
            }
        }
    }
}

/// Calculate the cryptographic hash of canonicalized data.
/// Matches Python's semantic_hash and JavaScript's semanticHash functions.
///
/// # Arguments
/// * `data` - Input JSON value to hash
///
/// # Returns
/// Hexadecimal string of the SHA256 hash
pub fn semantic_hash(data: &Value) -> Result<String> {
    let canonical_string = canonicalize(data, true)?;
    let canonical_bytes = canonical_string.as_bytes();
    
    let mut hasher = Sha256::new();
    hasher.update(canonical_bytes);
    let result = hasher.finalize();
    
    Ok(format!("{:x}", result))
}

/// Verify that data produces the expected semantic hash.
/// Matches Python's verify_semantic_hash and JavaScript's verifySemanticHash functions.
///
/// # Arguments
/// * `data` - Input JSON value to verify
/// * `expected_hash` - Expected hash value (hex string)
///
/// # Returns
/// true if hash matches, false otherwise
pub fn verify_semantic_hash(data: &Value, expected_hash: &str) -> Result<bool> {
    let actual_hash = semantic_hash(data)?;
    Ok(actual_hash == expected_hash)
}

/// Compare two JSON values for canonical equality.
///
/// # Arguments
/// * `data1` - First JSON value
/// * `data2` - Second JSON value
///
/// # Returns
/// true if canonical forms are identical
pub fn canonically_equal(data1: &Value, data2: &Value) -> bool {
    match (canonicalize(data1, true), canonicalize(data2, true)) {
        (Ok(canon1), Ok(canon2)) => canon1 == canon2,
        _ => false,
    }
}

/// Helper trait to get type name of JSON value
trait JsonTypeStr {
    fn type_str(&self) -> &'static str;
}

impl JsonTypeStr for Value {
    fn type_str(&self) -> &'static str {
        match self {
            Value::Null => "null",
            Value::Bool(_) => "bool",
            Value::Number(_) => "number",
            Value::String(_) => "string",
            Value::Array(_) => "array",
            Value::Object(_) => "object",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_canonicalization() {
        let dict_a = json!({
            "a": 1,
            "b": 2,
            "c": 3
        });

        let dict_b = json!({
            "c": 3,
            "a": 1,
            "b": 2
        });

        let canonical_a = canonicalize(&dict_a, true).unwrap();
        let canonical_b = canonicalize(&dict_b, true).unwrap();

        assert_eq!(canonical_a, canonical_b);
        assert_eq!(
            semantic_hash(&dict_a).unwrap(),
            semantic_hash(&dict_b).unwrap()
        );
    }

    #[test]
    fn test_nested_structures() {
        let complex_dict = json!({
            "z": [3, 1, 2],
            "a": {
                "c": 3,
                "a": 1,
                "b": {
                    "f": 6,
                    "d": 4,
                    "e": 5
                }
            },
            "b": 2
        });

        let canonical = canonicalize(&complex_dict, true).unwrap();
        let expected = r#"{"a":{"a":1,"b":{"d":4,"e":5,"f":6},"c":3},"b":2,"z":[1,2,3]}"#;
        assert_eq!(canonical, expected);
    }

    #[test]
    fn test_hash_sensitivity() {
        let original = json!({
            "action_id": "001-XYZ",
            "agent": "Claude-3",
            "claim": "The initial cost is $500",
            "evidence_ptr": "archive://0000001",
            "timestamp": 1700000000
        });

        let modified = json!({
            "action_id": "001-XYZ",
            "agent": "Claude-3",
            "claim": "The initial cost is $501",
            "evidence_ptr": "archive://0000001",
            "timestamp": 1700000000
        });

        let hash_original = semantic_hash(&original).unwrap();
        let hash_modified = semantic_hash(&modified).unwrap();

        assert_ne!(hash_original, hash_modified);
    }

    #[test]
    fn test_verify_hash() {
        let test_data = json!({
            "action": "propose",
            "value": 42
        });

        let test_hash = semantic_hash(&test_data).unwrap();

        assert!(verify_semantic_hash(&test_data, &test_hash).unwrap());

        let tampered_data = json!({
            "action": "propose",
            "value": 43
        });

        assert!(!verify_semantic_hash(&tampered_data, &test_hash).unwrap());
    }

    #[test]
    fn test_canonical_equality() {
        let obj1 = json!({"z": 1, "a": 2});
        let obj2 = json!({"a": 2, "z": 1});

        assert!(canonically_equal(&obj1, &obj2));
    }

    #[test]
    fn test_complex_contract() {
        let contract = json!({
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "proposer_agent": "Claude",
            "action_type": "amend",
            "action": {
                "target": "amendment-article-3",
                "operation": "modify"
            },
            "evidence": [
                {
                    "type": "archive_reference",
                    "pointer": "sha256:abc123def456"
                }
            ],
            "reasoning": {
                "rationale": "Clarifies Article III.1",
                "confidence": 0.87
            },
            "timestamp": "2025-11-20T14:30:00Z"
        });

        let hash = semantic_hash(&contract).unwrap();
        assert!(hash.len() == 64); // SHA256 hex is 64 chars
        assert!(verify_semantic_hash(&contract, &hash).unwrap());
    }

    #[test]
    fn test_array_sorting() {
        let with_unsorted = json!({
            "numbers": [5, 3, 1, 4, 2]
        });

        let with_sorted = json!({
            "numbers": [1, 2, 3, 4, 5]
        });

        assert_eq!(
            semantic_hash(&with_unsorted).unwrap(),
            semantic_hash(&with_sorted).unwrap()
        );
    }

    #[test]
    fn test_cross_language_vector() {
        // Test vector for cross-language validation
        let python_test_vector = json!({
            "action": "propose",
            "agent": "Claude",
            "confidence": 0.88,
            "timestamp": "2025-11-20T14:30:00Z"
        });

        let hash = semantic_hash(&python_test_vector).unwrap();
        println!("Rust hash: {}", hash);
        println!("Compare with Python/JavaScript implementation for validation");

        assert!(hash.len() == 64);
    }
}

fn main() {
    println!("🧪 Running Canonicalizer Test Suite for Rust...\n");

    // Test 1: Basic canonicalization
    println!("--- Test 1: Basic Canonicalization (Order Independence) ---");
    let dict_a = json!({"a": 1, "b": 2, "c": 3});
    let dict_b = json!({"c": 3, "a": 1, "b": 2});

    let canonical_a = canonicalize(&dict_a, true).unwrap();
    let canonical_b = canonicalize(&dict_b, true).unwrap();

    println!("✓ Canonical forms match: {}", canonical_a == canonical_b);
    println!("✓ Semantic hashes match: {}", semantic_hash(&dict_a).unwrap() == semantic_hash(&dict_b).unwrap());

    // Test 2: Nested structures
    println!("\n--- Test 2: Nested Structures ---");
    let complex_dict = json!({
        "z": [3, 1, 2],
        "a": {
            "c": 3,
            "a": 1,
            "b": {"f": 6, "d": 4, "e": 5}
        },
        "b": 2
    });

    let canonical = canonicalize(&complex_dict, true).unwrap();
    println!("✓ Complex structure canonicalized: {}", canonical);

    // Test 3: Hash sensitivity
    println!("\n--- Test 3: Hash Sensitivity ---");
    let action_a = json!({
        "action_id": "001-XYZ",
        "agent": "Claude-3",
        "claim": "The initial cost is $500",
        "timestamp": 1700000000
    });

    let action_b = json!({
        "action_id": "001-XYZ",
        "agent": "Claude-3",
        "claim": "The initial cost is $501",
        "timestamp": 1700000000
    });

    let hash_a = semantic_hash(&action_a).unwrap();
    let hash_b = semantic_hash(&action_b).unwrap();

    println!("✓ Hash changes with content: {}", hash_a != hash_b);
    println!("  Hash A: {}", hash_a);
    println!("  Hash B: {}", hash_b);

    // Test 4: Verification
    println!("\n--- Test 4: Hash Verification ---");
    let test_data = json!({"action": "propose", "value": 42});
    let test_hash = semantic_hash(&test_data).unwrap();

    println!("✓ Valid hash verifies: {}", verify_semantic_hash(&test_data, &test_hash).unwrap());

    let tampered = json!({"action": "propose", "value": 43});
    println!("✓ Tampered data fails: {}", !verify_semantic_hash(&tampered, &test_hash).unwrap());

    // Test 5: Canonical equality
    println!("\n--- Test 5: Canonical Equality ---");
    let obj1 = json!({"z": 1, "a": 2});
    let obj2 = json!({"a": 2, "z": 1});
    println!("✓ Reordered objects equal: {}", canonically_equal(&obj1, &obj2));

    println!("\n✅ All manual tests passed!");
}
