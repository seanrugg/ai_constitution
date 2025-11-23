/**
 * canonicalizer.js - Core canonicalization and semantic hashing for OCP
 * 
 * This module is the JavaScript implementation of the Optimistic Constitutional Protocol (OCP)
 * canonicalization engine, ensuring deterministic representation of all constitutional objects
 * for cryptographic hashing and verification.
 * 
 * Must produce byte-for-byte identical output to canonicalizer.py
 */

const crypto = require('crypto');

// --- Constants ---
const HASH_ALGORITHM = 'sha256';
const ENCODING = 'utf-8';

// --- Custom Error Classes ---
class ConstitutionalError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ConstitutionalError';
    }
}

class CanonicalizationError extends ConstitutionalError {
    constructor(message) {
        super(message);
        this.name = 'CanonicalizationError';
    }
}

/**
 * Recursively sort all dictionaries by keys and sort lists where appropriate.
 * This ensures complete deterministic ordering of nested structures.
 * Matches Python's _deep_sort function.
 * 
 * @param {any} obj - Object to sort
 * @returns {any} - Deeply sorted object
 */
function deepSort(obj) {
    if (obj === null) {
        return null;
    }
    
    if (typeof obj === 'object' && !Array.isArray(obj) && obj.constructor === Object) {
        // Handle plain objects (dictionaries)
        const sorted = {};
        const keys = Object.keys(obj).sort();
        
        for (const key of keys) {
            sorted[key] = deepSort(obj[key]);
        }
        return sorted;
    } else if (Array.isArray(obj)) {
        // For arrays: only sort if all elements are primitives of same type
        const allPrimitive = obj.every(x => 
            typeof x === 'string' || typeof x === 'number' || typeof x === 'boolean' || x === null
        );
        
        if (allPrimitive && obj.every(x => typeof x === obj[0]?.constructor)) {
            // Sort primitives of same type
            const deepSorted = obj.map(x => deepSort(x));
            return deepSorted.sort((a, b) => {
                if (a < b) return -1;
                if (a > b) return 1;
                return 0;
            });
        } else {
            // Maintain order for mixed types or complex objects
            return obj.map(x => deepSort(x));
        }
    } else {
        // Primitive types (string, number, boolean, null)
        return obj;
    }
}

/**
 * Custom JSON serializer for OCP-specific types.
 * Handles Date, BigInt, and other non-standard JSON types.
 * 
 * @param {any} value - Value to serialize
 * @returns {any} - Serializable representation
 */
function replacer(key, value) {
    // Handle Date objects - convert to ISO string
    if (value instanceof Date) {
        return value.toISOString();
    }
    
    // Handle BigInt - convert to string
    if (typeof value === 'bigint') {
        return value.toString();
    }
    
    // Handle UUID-like strings - keep as-is
    if (typeof value === 'string' && /^[0-9a-f-]{36}$/i.test(value)) {
        return value;
    }
    
    return value;
}

/**
 * Convert a JavaScript object to a deterministically ordered, canonical JSON string.
 * Matches Python's canonicalize function.
 * 
 * @param {Object} data - Input object to canonicalize
 * @param {boolean} strict - If true, throws on non-canonicalizable data
 * @returns {string} - Canonical JSON string
 * @throws {CanonicalizationError} - If data cannot be canonicalized
 */
function canonicalize(data, strict = true) {
    if (typeof data !== 'object' || data === null) {
        if (strict) {
            throw new CanonicalizationError(`Input must be an object, got ${typeof data}`);
        } else {
            // Attempt conversion for other types
            try {
                data = { value: data };
            } catch (e) {
                throw new CanonicalizationError(`Cannot convert ${typeof data} to object`);
            }
        }
    }

    try {
        // Deep sort the entire structure
        const sortedData = deepSort(data);
        
        // Convert to canonical JSON using custom replacer
        // Important: JSON.stringify with replacer, no spaces, sorted keys
        const canonicalJson = JSON.stringify(sortedData, replacer);
        
        // Verify the output is valid
        if (!canonicalJson || typeof canonicalJson !== 'string') {
            throw new CanonicalizationError('Failed to produce canonical JSON string');
        }
        
        return canonicalJson;
        
    } catch (error) {
        if (strict) {
            throw new CanonicalizationError(`Failed to canonicalize data: ${error.message}`);
        } else {
            // Fallback: convert all values to string and retry
            try {
                const stringified = {};
                for (const [k, v] of Object.entries(data)) {
                    stringified[k] = String(v);
                }
                return canonicalize(stringified, false);
            } catch (fallbackError) {
                throw new CanonicalizationError(
                    `Data cannot be canonicalized even with fallback: ${fallbackError.message}`
                );
            }
        }
    }
}

/**
 * Calculate the cryptographic hash of canonicalized data.
 * Matches Python's semantic_hash function.
 * 
 * @param {Object} data - Input object to hash
 * @param {string} algorithm - Hash algorithm to use (default: sha256)
 * @returns {string} - Hexadecimal string of the semantic hash
 */
function semanticHash(data, algorithm = HASH_ALGORITHM) {
    const canonicalString = canonicalize(data);
    const canonicalBuffer = Buffer.from(canonicalString, ENCODING);
    
    const hasher = crypto.createHash(algorithm);
    hasher.update(canonicalBuffer);
    
    return hasher.digest('hex');
}

/**
 * Verify that data produces the expected semantic hash.
 * Matches Python's verify_semantic_hash function.
 * 
 * @param {Object} data - Input object to verify
 * @param {string} expectedHash - Expected hash value
 * @param {string} algorithm - Hash algorithm used
 * @returns {boolean} - True if hash matches, false otherwise
 */
function verifySemanticHash(data, expectedHash, algorithm = HASH_ALGORITHM) {
    const actualHash = semanticHash(data, algorithm);
    return actualHash === expectedHash;
}

/**
 * Compare two canonicalized objects for equality.
 * 
 * @param {Object} data1 - First object
 * @param {Object} data2 - Second object
 * @returns {boolean} - True if canonical forms are identical
 */
function canonicallyEqual(data1, data2) {
    try {
        return canonicalize(data1) === canonicalize(data2);
    } catch (error) {
        return false;
    }
}

// --- Module Exports (for Node.js) ---
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        canonicalize,
        semanticHash,
        verifySemanticHash,
        canonicallyEqual,
        deepSort,
        ConstitutionalError,
        CanonicalizationError,
        HASH_ALGORITHM,
        ENCODING
    };
}

// --- Test Suite (Node.js) ---
if (typeof require !== 'undefined' && require.main === module) {
    const assert = require('assert');
    
    console.log('🧪 Running Canonicalizer Test Suite...\n');
    
    // Test 1: Basic canonicalization - order independence
    console.log('--- Test 1: Basic Canonicalization (Order Independence) ---');
    const dictA = { "a": 1, "b": 2, "c": 3 };
    const dictB = { "c": 3, "a": 1, "b": 2 };
    
    const canonicalA = canonicalize(dictA);
    const canonicalB = canonicalize(dictB);
    
    assert.strictEqual(canonicalA, canonicalB, 'Canonical forms should match');
    assert.strictEqual(semanticHash(dictA), semanticHash(dictB), 'Hashes should match');
    console.log('✓ Canonical forms match regardless of key order');
    console.log('✓ Semantic hashes match');
    
    // Test 2: Nested structures
    console.log('\n--- Test 2: Nested Structures ---');
    const complexDict = {
        "z": [3, 1, 2],
        "a": {
            "c": 3,
            "a": 1,
            "b": { "f": 6, "d": 4, "e": 5 }
        },
        "b": 2
    };
    
    const canonical = canonicalize(complexDict);
    const expectedStart = '{"a":{"a":1,"b":{"d":4,"e":5,"f":6},"c":3},"b":2,"z":[1,2,3]}';
    assert.strictEqual(canonical, expectedStart, 'Complex nested structure should canonicalize correctly');
    console.log('✓ Nested structures canonicalize correctly');
    console.log(`  Canonical: ${canonical}`);
    
    // Test 3: Sensitivity to changes
    console.log('\n--- Test 3: Hash Sensitivity ---');
    const actionA = {
        "action_id": "001-XYZ",
        "agent": "Claude-3",
        "claim": "The initial cost is $500",
        "evidence_ptr": "archive://0000001",
        "timestamp": 1700000000
    };
    
    const actionB = actionA;
    actionB.claim = "The initial cost is $501";  // Single character change
    
    const hashOriginal = semanticHash({
        "action_id": "001-XYZ",
        "agent": "Claude-3",
        "claim": "The initial cost is $500",
        "evidence_ptr": "archive://0000001",
        "timestamp": 1700000000
    });
    
    const hashModified = semanticHash(actionB);
    assert.notStrictEqual(hashOriginal, hashModified, 'Hash should change with content');
    console.log('✓ Hash changes with content modification');
    console.log(`  Original hash: ${hashOriginal}`);
    console.log(`  Modified hash: ${hashModified}`);
    
    // Test 4: Verify hash
    console.log('\n--- Test 4: Hash Verification ---');
    const testData = { "action": "propose", "value": 42 };
    const testHash = semanticHash(testData);
    
    assert.strictEqual(
        verifySemanticHash(testData, testHash),
        true,
        'Valid hash should verify'
    );
    
    const tamperedData = { "action": "propose", "value": 43 };
    assert.strictEqual(
        verifySemanticHash(tamperedData, testHash),
        false,
        'Tampered data should fail verification'
    );
    console.log('✓ Hash verification works correctly');
    console.log('✓ Tampered data fails verification');
    
    // Test 5: Python compatibility test vectors
    console.log('\n--- Test 5: Python Compatibility Test Vectors ---');
    const pythonTestVector = {
        "action": "propose",
        "agent": "Claude",
        "confidence": 0.88,
        "timestamp": "2025-11-20T14:30:00Z"
    };
    
    const hash = semanticHash(pythonTestVector);
    console.log(`✓ Test vector hash computed: ${hash}`);
    console.log('  (Compare with Python implementation for cross-language validation)');
    
    // Test 6: Canonical equality
    console.log('\n--- Test 6: Canonical Equality ---');
    const obj1 = { "z": 1, "a": 2 };
    const obj2 = { "a": 2, "z": 1 };
    assert.strictEqual(canonicallyEqual(obj1, obj2), true, 'Reordered objects should be equal');
    console.log('✓ Canonical equality detects equivalent structures');
    
    // Test 7: Date handling
    console.log('\n--- Test 7: Date Handling ---');
    const dataWithDate = {
        "event": "contract_proposal",
        "timestamp": new Date('2025-11-20T14:30:00Z')
    };
    
    const canonWithDate = canonicalize(dataWithDate);
    assert.strictEqual(canonWithDate.includes('2025-11-20'), true, 'Date should be ISO formatted');
    console.log('✓ Date objects handled correctly');
    console.log(`  Canonical: ${canonWithDate}`);
    
    console.log('\n✅ All tests passed!');
}
