"""
canonicalizer.py - Core canonicalization and semantic hashing for OCP

This module is the linchpin of the Optimistic Constitutional Protocol (OCP), 
ensuring deterministic representation of all constitutional objects for 
cryptographic hashing and verification.
"""

import json
import hashlib
import decimal
import datetime
from typing import Dict, Any, Union, Optional
from dataclasses import asdict, is_dataclass
import uuid

# --- Constants ---
HASH_ALGORITHM = 'sha256'
ENCODING = 'utf-8'

class ConstitutionalError(Exception):
    """Base exception for constitutional protocol violations."""
    pass

class CanonicalizationError(ConstitutionalError):
    """Raised when data cannot be properly canonicalized."""
    pass

class OCPJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles OCP-specific data types:
    - Decimal -> str (to avoid floating point precision issues)
    - UUID -> str
    - datetime -> ISO format string
    - dataclasses -> dict
    """
    
    def default(self, obj):
        # Handle decimal for financial/mathematical precision
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        
        # Handle UUIDs
        if isinstance(obj, uuid.UUID):
            return str(obj)
        
        # Handle datetime objects
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        
        # Handle dataclasses
        if is_dataclass(obj):
            return asdict(obj)
        
        # Let the base class default method raise the TypeError
        return super().default(obj)

def _deep_sort(obj: Any) -> Any:
    """
    Recursively sort all dictionaries by keys and sort lists where appropriate.
    This ensures complete deterministic ordering of nested structures.
    """
    if isinstance(obj, dict):
        # Sort dictionary by keys and recursively process values
        return {k: _deep_sort(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        # For lists, we need to be careful - only sort if all elements are comparable
        # and of the same basic type. For mixed types or complex objects, we maintain order.
        if all(isinstance(x, (str, int, float, bool)) for x in obj):
            return sorted(_deep_sort(x) for x in obj)
        else:
            return [_deep_sort(x) for x in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        # For other types, convert to string representation for consistency
        return str(obj)

def canonicalize(data: Dict[str, Any], strict: bool = True) -> str:
    """
    Convert a Python dictionary to a deterministically ordered, canonical JSON string.
    
    Args:
        data: Input dictionary to canonicalize
        strict: If True, raises CanonicalizationError on non-canonicalizable data
        
    Returns:
        Canonical JSON string
        
    Raises:
        CanonicalizationError: If data cannot be properly canonicalized
    """
    if not isinstance(data, dict):
        if strict:
            raise CanonicalizationError(f"Input must be a dictionary, got {type(data)}")
        else:
            # Attempt to convert to dict for dataclasses and other objects
            if is_dataclass(data):
                data = asdict(data)
            elif hasattr(data, '__dict__'):
                data = data.__dict__
            else:
                raise CanonicalizationError(f"Cannot convert {type(data)} to dictionary")
    
    try:
        # Deep sort the entire structure
        sorted_data = _deep_sort(data)
        
        # Convert to canonical JSON
        canonical_json = json.dumps(
            sorted_data,
            cls=OCPJSONEncoder,
            sort_keys=True,  # Redundant with _deep_sort but added for safety
            separators=(',', ':'),
            ensure_ascii=False,
            allow_nan=False  # Important for cryptographic consistency
        )
        
        return canonical_json
        
    except (TypeError, ValueError) as e:
        if strict:
            raise CanonicalizationError(f"Failed to canonicalize data: {e}") from e
        else:
            # Fallback: convert all values to string and retry
            try:
                stringified_data = {k: str(v) for k, v in data.items()}
                return canonicalize(stringified_data, strict=False)
            except Exception:
                raise CanonicalizationError(f"Data cannot be canonicalized even with fallback: {e}")

def semantic_hash(data: Dict[str, Any], algorithm: str = HASH_ALGORITHM) -> str:
    """
    Calculate the cryptographic hash of canonicalized data.
    
    Args:
        data: Input dictionary to hash
        algorithm: Hash algorithm to use (default: sha256)
        
    Returns:
        Hexadecimal string of the semantic hash
    """
    canonical_string = canonicalize(data)
    canonical_bytes = canonical_string.encode(ENCODING)
    
    hasher = hashlib.new(algorithm)
    hasher.update(canonical_bytes)
    
    return hasher.hexdigest()

def verify_semantic_hash(data: Dict[str, Any], expected_hash: str, 
                        algorithm: str = HASH_ALGORITHM) -> bool:
    """
    Verify that data produces the expected semantic hash.
    
    Args:
        data: Input dictionary to verify
        expected_hash: Expected hash value
        algorithm: Hash algorithm used
        
    Returns:
        True if hash matches, False otherwise
    """
    actual_hash = semantic_hash(data, algorithm)
    return actual_hash == expected_hash

# --- OCP Data Models ---

class ArchiveEntry:
    """Example dataclass representing an Immutable Archive entry."""
    
    def __init__(self, entry_id: str, agent_id: str, action_type: str, 
                 content: Dict[str, Any], pre_state_hash: str, 
                 post_state_hash: str, timestamp: datetime.datetime,
                 constitutional_citation: Optional[str] = None):
        self.entry_id = entry_id
        self.agent_id = agent_id
        self.action_type = action_type
        self.content = content
        self.pre_state_hash = pre_state_hash
        self.post_state_hash = post_state_hash
        self.timestamp = timestamp
        self.constitutional_citation = constitutional_citation

# --- Comprehensive Test Suite ---

if __name__ == "__main__":
    import unittest
    
    class TestCanonicalizer(unittest.TestCase):
        
        def test_basic_canonicalization(self):
            """Test that different key orders produce same canonical form."""
            dict_a = {"a": 1, "b": 2, "c": 3}
            dict_b = {"c": 3, "a": 1, "b": 2}
            
            canonical_a = canonicalize(dict_a)
            canonical_b = canonicalize(dict_b)
            
            self.assertEqual(canonical_a, canonical_b)
            self.assertEqual(semantic_hash(dict_a), semantic_hash(dict_b))
        
        def test_nested_structures(self):
            """Test canonicalization of nested dictionaries and lists."""
            complex_dict = {
                "z": [3, 1, 2],
                "a": {
                    "c": 3,
                    "a": 1,
                    "b": {"f": 6, "d": 4, "e": 5}
                },
                "b": 2
            }
            
            # This should always produce the same canonical form
            canonical = canonicalize(complex_dict)
            expected_start = '{"a":{"a":1,"b":{"d":4,"e":5,"f":6},"c":3},"b":2,"z":[1,2,3]}'
            self.assertEqual(canonical, expected_start)
        
        def test_decimal_precision(self):
            """Test that decimal values are handled with precision."""
            from decimal import Decimal
            
            financial_data = {
                "amount": Decimal("123.45"),
                "precision_matters": True
            }
            
            hash1 = semantic_hash(financial_data)
            
            # Same value as float should produce different hash (due to precision)
            float_data = {
                "amount": 123.45,  # Float representation
                "precision_matters": True
            }
            
            hash2 = semantic_hash(float_data)
            self.assertNotEqual(hash1, hash2, "Decimal and float should have different hashes")
        
        def test_uuid_handling(self):
            """Test that UUIDs are properly canonicalized."""
            test_uuid = uuid.uuid4()
            data_with_uuid = {
                "id": test_uuid,
                "name": "test_agent"
            }
            
            # Should not raise an exception
            canonical = canonicalize(data_with_uuid)
            self.assertIn(str(test_uuid), canonical)
        
        def test_verify_hash(self):
            """Test hash verification function."""
            test_data = {"action": "propose", "value": 42}
            test_hash = semantic_hash(test_data)
            
            self.assertTrue(verify_semantic_hash(test_data, test_hash))
            
            # Tampered data should fail verification
            tampered_data = {"action": "propose", "value": 43}  # Changed value
            self.assertFalse(verify_semantic_hash(tampered_data, test_hash))
        
        def test_archive_entry_canonicalization(self):
            """Test canonicalization of complex OCP objects."""
            entry = ArchiveEntry(
                entry_id="entry_001",
                agent_id="agent_claude",
                action_type="contract_proposal",
                content={"claim": "The sky is blue", "evidence": "observation"},
                pre_state_hash="0xabc123",
                post_state_hash="0xdef456",
                timestamp=datetime.datetime(2024, 1, 1, 12, 0, 0),
                constitutional_citation="Article III, Section 3.1"
            )
            
            # Should work with dataclass conversion
            canonical = canonicalize(entry)
            self.assertIn("entry_001", canonical)
            self.assertIn("Article III", canonical)
    
    # Run the tests
    print("🧪 Running Canonicalizer Test Suite...")
    
    # Basic functionality tests
    print("\n--- Basic Canonicalization Tests ---")
    
    # Test 1: Order independence
    action_a = {
        "action_id": "001-XYZ",
        "agent": "Claude-3",
        "claim": "The initial cost is $500",
        "evidence_ptr": "archive://0000001",
        "timestamp": 1700000000
    }
    
    action_b = {
        "agent": "Claude-3", 
        "timestamp": 1700000000,
        "claim": "The initial cost is $500",
        "action_id": "001-XYZ",
        "evidence_ptr": "archive://0000001"
    }

    canonical_a = canonicalize(action_a)
    canonical_b = canonicalize(action_b)
    
    print(f"✓ Canonical Forms Match: {canonical_a == canonical_b}")
    print(f"✓ Semantic Hashes Match: {semantic_hash(action_a) == semantic_hash(action_b)}")
    
    # Test 2: Sensitivity to changes
    action_c = action_a.copy()
    action_c["claim"] = "The initial cost is $501"  # Single character change
    
    print(f"✓ Hash Changes with Content: {semantic_hash(action_a) != semantic_hash(action_c)}")
    
    # Test 3: Complex nested structure
    complex_action = {
        "proposal": {
            "financials": {
                "amount": 1000,
                "currency": "USD"
            },
            "timeline": [2024, 2025, 2026],
            "parties": ["agent_a", "agent_b"]
        },
        "metadata": {
            "created_by": "Claude-3",
            "constitutional_basis": "Article IV, Section 2"
        }
    }
    
    complex_hash = semantic_hash(complex_action)
    print(f"✓ Complex Structure Hash: {complex_hash}")
    
    # Run unit tests
    print("\n--- Running Unit Tests ---")
    unittest.main(argv=[''], verbosity=2, exit=False)
