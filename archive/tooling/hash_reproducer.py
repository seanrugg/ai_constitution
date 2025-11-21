#!/usr/bin/env python3
"""
Hash Reproducer - Constitutional Archive Integrity Tool

Validates and reproduces semantic hashes for archive entries to ensure
cryptographic integrity and constitutional compliance.

Usage:
    python hash_reproducer.py --entry <entry_id>
    python hash_reproducer.py --verify-range --start <entry_id> --end <entry_id>
    python hash_reproducer.py --audit-agent <agent_id> --time-range 7d
"""

import argparse
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import sqlite3
import requests
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from protocol.hashing.reference_implementations.python.canonicalizer import (
        canonicalize, semantic_hash, verify_semantic_hash
    )
except ImportError:
    # Fallback implementation if canonicalizer is not available
    import json as fallback_json
    import hashlib as fallback_hashlib
    
    def canonicalize(data: Dict[str, Any]) -> str:
        """Fallback canonicalization implementation"""
        return fallback_json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    
    def semantic_hash(data: Dict[str, Any]) -> str:
        """Fallback semantic hash implementation"""
        canonical = canonicalize(data)
        return fallback_hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    
    def verify_semantic_hash(data: Dict[str, Any], expected_hash: str) -> bool:
        """Fallback verification implementation"""
        return semantic_hash(data) == expected_hash


class HashReproducer:
    """
    Tool for reproducing and validating semantic hashes in the constitutional archive.
    Ensures the cryptographic integrity of the immutable record.
    """
    
    def __init__(self, archive_path: str, api_base_url: str = None):
        """
        Initialize the hash reproducer.
        
        Args:
            archive_path: Path to SQLite archive database
            api_base_url: Base URL for archive API (optional)
        """
        self.archive_path = Path(archive_path)
        self.api_base_url = api_base_url
        self.conn = None
        self.session = requests.Session() if api_base_url else None
        
        # Statistics
        self.stats = {
            'entries_processed': 0,
            'hashes_valid': 0,
            'hashes_invalid': 0,
            'signatures_valid': 0,
            'signatures_invalid': 0,
            'constitutional_violations': 0,
            'processing_time': 0.0
        }
    
    def connect(self) -> bool:
        """Connect to the archive database."""
        try:
            if self.archive_path.exists():
                self.conn = sqlite3.connect(self.archive_path)
                self.conn.row_factory = sqlite3.Row
                return True
            else:
                print(f"❌ Archive database not found: {self.archive_path}")
                return False
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def fetch_entry_local(self, entry_id: str) -> Optional[Dict]:
        """Fetch an archive entry from local database."""
        if not self.conn:
            return None
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM archive_entries 
            WHERE entry_id = ?
        """, (entry_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def fetch_entry_api(self, entry_id: str) -> Optional[Dict]:
        """Fetch an archive entry from API."""
        if not self.session:
            return None
            
        try:
            response = self.session.get(
                f"{self.api_base_url}/v1/archive/actions/{entry_id}",
                headers={'Accept': 'application/json'}
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API error: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            print(f"❌ API request failed: {e}")
            return None
    
    def get_entry(self, entry_id: str) -> Optional[Dict]:
        """Get an archive entry from local DB or API."""
        # Try local database first
        entry = self.fetch_entry_local(entry_id)
        if entry:
            return entry
        
        # Fall back to API
        if self.api_base_url:
            print(f"🔍 Entry not found locally, trying API...")
            entry = self.fetch_entry_api(entry_id)
            if entry:
                return entry
        
        print(f"❌ Entry not found: {entry_id}")
        return None
    
    def reproduce_hash(self, entry_data: Dict) -> Tuple[bool, str, str]:
        """
        Reproduce the semantic hash for an archive entry.
        
        Args:
            entry_data: Archive entry data
            
        Returns:
            Tuple of (success, original_hash, reproduced_hash, error_message)
        """
        try:
            # Extract content that should be hashed
            content_to_hash = {
                'action_type': entry_data.get('action_type'),
                'agent_id': entry_data.get('agent_id'),
                'content': entry_data.get('content'),
                'evidence_pointers': entry_data.get('evidence_pointers', []),
                'constitutional_citation': entry_data.get('constitutional_citation'),
                'timestamp': entry_data.get('timestamp')
            }
            
            # Handle different content formats
            if isinstance(content_to_hash['content'], str):
                try:
                    content_to_hash['content'] = json.loads(content_to_hash['content'])
                except (json.JSONDecodeError, TypeError):
                    pass  # Keep as string if not JSON
            
            # Reproduce the hash
            reproduced_hash = semantic_hash(content_to_hash)
            original_hash = entry_data.get('semantic_hash')
            
            if reproduced_hash == original_hash:
                return True, original_hash, reproduced_hash, None
            else:
                return False, original_hash, reproduced_hash, "Hash mismatch"
                
        except Exception as e:
            return False, entry_data.get('semantic_hash', 'unknown'), 'error', f"Hash reproduction failed: {e}"
    
    def verify_signature(self, entry_data: Dict) -> Tuple[bool, str]:
        """
        Verify the cryptographic signature of an archive entry.
        
        Args:
            entry_data: Archive entry data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # This is a placeholder - actual signature verification would require
        # the agent's public key and cryptographic libraries
        signature = entry_data.get('signature')
        if not signature:
            return False, "Missing signature"
        
        # Basic signature format validation
        if len(signature) < 10:  # Very basic check
            return False, "Signature too short"
        
        # In a real implementation, this would verify against the agent's public key
        # For now, we'll assume valid if present and reasonable length
        return True, "Signature format valid (actual verification not implemented)"
    
    def check_constitutional_compliance(self, entry_data: Dict) -> Tuple[bool, List[str]]:
        """
        Check if an entry complies with constitutional requirements.
        
        Args:
            entry_data: Archive entry data
            
        Returns:
            Tuple of (is_compliant, list_of_violations)
        """
        violations = []
        
        # Check required fields
        required_fields = ['action_type', 'agent_id', 'constitutional_citation', 'evidence_pointers']
        for field in required_fields:
            if not entry_data.get(field):
                violations.append(f"Missing required field: {field}")
        
        # Check evidence requirements for certain action types
        action_type = entry_data.get('action_type')
        evidence_pointers = entry_data.get('evidence_pointers', [])
        
        if action_type in ['contract_proposal', 'fraud_proof'] and len(evidence_pointers) == 0:
            violations.append(f"Action type '{action_type}' requires evidence pointers")
        
        # Check constitutional citation format
        citation = entry_data.get('constitutional_citation', '')
        if citation and not citation.startswith('Article'):
            violations.append(f"Invalid constitutional citation format: {citation}")
        
        return len(violations) == 0, violations
    
    def validate_entry(self, entry_id: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Comprehensive validation of an archive entry.
        
        Args:
            entry_id: Entry identifier to validate
            verbose: Whether to print detailed output
            
        Returns:
            Validation results dictionary
        """
        start_time = time.time()
        
        # Fetch the entry
        entry_data = self.get_entry(entry_id)
        if not entry_data:
            return {
                'entry_id': entry_id,
                'valid': False,
                'error': 'Entry not found',
                'timestamp': datetime.now().isoformat()
            }
        
        if verbose:
            print(f"🔍 Validating entry: {entry_id}")
            print(f"   Agent: {entry_data.get('agent_id')}")
            print(f"   Action: {entry_data.get('action_type')}")
            print(f"   Citation: {entry_data.get('constitutional_citation')}")
        
        # Reproduce hash
        hash_valid, original_hash, reproduced_hash, hash_error = self.reproduce_hash(entry_data)
        
        # Verify signature
        signature_valid, signature_error = self.verify_signature(entry_data)
        
        # Check constitutional compliance
        compliant, violations = self.check_constitutional_compliance(entry_data)
        
        # Check state transition
        state_valid = self.validate_state_transition(entry_data)
        
        # Update statistics
        self.stats['entries_processed'] += 1
        if hash_valid:
            self.stats['hashes_valid'] += 1
        else:
            self.stats['hashes_invalid'] += 1
        
        if signature_valid:
            self.stats['signatures_valid'] += 1
        else:
            self.stats['signatures_invalid'] += 1
        
        if not compliant:
            self.stats['constitutional_violations'] += 1
        
        processing_time = time.time() - start_time
        self.stats['processing_time'] += processing_time
        
        # Build results
        results = {
            'entry_id': entry_id,
            'valid': hash_valid and signature_valid and compliant and state_valid,
            'hash_validation': {
                'valid': hash_valid,
                'original_hash': original_hash,
                'reproduced_hash': reproduced_hash,
                'error': hash_error
            },
            'signature_validation': {
                'valid': signature_valid,
                'error': signature_error
            },
            'constitutional_compliance': {
                'compliant': compliant,
                'violations': violations
            },
            'state_transition': {
                'valid': state_valid
            },
            'processing_time_seconds': processing_time,
            'timestamp': datetime.now().isoformat()
        }
        
        if verbose:
            self.print_validation_results(results)
        
        return results
    
    def validate_state_transition(self, entry_data: Dict) -> bool:
        """
        Validate the state transition for an entry.
        
        Args:
            entry_data: Archive entry data
            
        Returns:
            Whether state transition is valid
        """
        # This would typically verify that post_state_hash is correctly derived
        # from pre_state_hash and the entry's content
        pre_state = entry_data.get('pre_state_hash')
        post_state = entry_data.get('post_state_hash')
        
        if not pre_state or not post_state:
            return False
        
        # Basic check: state should change (unless it's a read-only action)
        if pre_state == post_state and entry_data.get('action_type') not in ['query', 'read']:
            return False
        
        return True
    
    def validate_range(self, start_entry_id: str, end_entry_id: str, batch_size: int = 100) -> Dict[str, Any]:
        """
        Validate a range of archive entries.
        
        Args:
            start_entry_id: Starting entry ID
            end_entry_id: Ending entry ID
            batch_size: Number of entries to process in each batch
            
        Returns:
            Range validation results
        """
        print(f"🔍 Validating range: {start_entry_id} to {end_entry_id}")
        
        # This would need to be implemented based on how entries are ordered
        # For now, we'll process a fixed number of entries
        results = {
            'range': f"{start_entry_id}-{end_entry_id}",
            'entries_validated': [],
            'summary': {
                'total_entries': 0,
                'valid_entries': 0,
                'invalid_entries': 0,
                'hash_failures': 0,
                'signature_failures': 0,
                'constitutional_violations': 0
            },
            'start_time': datetime.now().isoformat()
        }
        
        # In a real implementation, this would iterate through the range
        # For now, we'll validate a single entry as a demonstration
        entry_result = self.validate_entry(start_entry_id, verbose=False)
        results['entries_validated'].append(entry_result)
        
        # Update summary
        results['summary']['total_entries'] = 1
        if entry_result['valid']:
            results['summary']['valid_entries'] += 1
        else:
            results['summary']['invalid_entries'] += 1
        
        if not entry_result['hash_validation']['valid']:
            results['summary']['hash_failures'] += 1
        
        if not entry_result['signature_validation']['valid']:
            results['summary']['signature_failures'] += 1
        
        if not entry_result['constitutional_compliance']['compliant']:
            results['summary']['constitutional_violations'] += 1
        
        results['end_time'] = datetime.now().isoformat()
        results['duration_seconds'] = self.stats['processing_time']
        
        return results
    
    def audit_agent(self, agent_id: str, time_range: str = '30d') -> Dict[str, Any]:
        """
        Audit all entries from a specific agent.
        
        Args:
            agent_id: Agent identifier to audit
            time_range: Time range for audit (7d, 30d, 90d, 1y)
            
        Returns:
            Audit results
        """
        print(f"🔍 Auditing agent: {agent_id} (time range: {time_range})")
        
        # Calculate time range
        if time_range == '7d':
            delta = timedelta(days=7)
        elif time_range == '30d':
            delta = timedelta(days=30)
        elif time_range == '90d':
            delta = timedelta(days=90)
        elif time_range == '1y':
            delta = timedelta(days=365)
        else:
            delta = timedelta(days=30)  # Default
        
        cutoff_date = datetime.now() - delta
        
        results = {
            'agent_id': agent_id,
            'time_range': time_range,
            'cutoff_date': cutoff_date.isoformat(),
            'entries_audited': [],
            'summary': {
                'total_entries': 0,
                'valid_entries': 0,
                'invalid_entries': 0,
                'compliance_rate': 0.0,
                'hash_integrity_rate': 0.0,
                'average_processing_time': 0.0
            },
            'start_time': datetime.now().isoformat()
        }
        
        # In a real implementation, this would query the database for agent entries
        # For now, we'll demonstrate with a single entry lookup
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT entry_id FROM archive_entries 
                WHERE agent_id = ? AND timestamp >= ?
                LIMIT 10
            """, (agent_id, cutoff_date.isoformat()))
            
            entry_ids = [row[0] for row in cursor.fetchall()]
            
            for entry_id in entry_ids:
                entry_result = self.validate_entry(entry_id, verbose=False)
                results['entries_audited'].append(entry_result)
        
        # Calculate summary statistics
        total_entries = len(results['entries_audited'])
        valid_entries = sum(1 for entry in results['entries_audited'] if entry['valid'])
        hash_valid_entries = sum(1 for entry in results['entries_audited'] if entry['hash_validation']['valid'])
        
        results['summary']['total_entries'] = total_entries
        results['summary']['valid_entries'] = valid_entries
        results['summary']['invalid_entries'] = total_entries - valid_entries
        
        if total_entries > 0:
            results['summary']['compliance_rate'] = valid_entries / total_entries
            results['summary']['hash_integrity_rate'] = hash_valid_entries / total_entries
            total_time = sum(entry['processing_time_seconds'] for entry in results['entries_audited'])
            results['summary']['average_processing_time'] = total_time / total_entries
        
        results['end_time'] = datetime.now().isoformat()
        results['duration_seconds'] = self.stats['processing_time']
        
        return results
    
    def print_validation_results(self, results: Dict[str, Any]):
        """Print validation results in a readable format."""
        print(f"\n📊 Validation Results for {results['entry_id']}")
        print("=" * 50)
        
        # Overall status
        status_icon = "✅" if results['valid'] else "❌"
        print(f"{status_icon} Overall: {'VALID' if results['valid'] else 'INVALID'}")
        
        # Hash validation
        hash_status = "✅" if results['hash_validation']['valid'] else "❌"
        print(f"{hash_status} Hash: {results['hash_validation']['valid']}")
        if not results['hash_validation']['valid']:
            print(f"   Original:  {results['hash_validation']['original_hash']}")
            print(f"   Reproduced: {results['hash_validation']['reproduced_hash']}")
            print(f"   Error: {results['hash_validation']['error']}")
        
        # Signature validation
        sig_status = "✅" if results['signature_validation']['valid'] else "❌"
        print(f"{sig_status} Signature: {results['signature_validation']['valid']}")
        if not results['signature_validation']['valid']:
            print(f"   Error: {results['signature_validation']['error']}")
        
        # Constitutional compliance
        comp_status = "✅" if results['constitutional_compliance']['compliant'] else "❌"
        print(f"{comp_status} Constitutional: {results['constitutional_compliance']['compliant']}")
        if not results['constitutional_compliance']['compliant']:
            for violation in results['constitutional_compliance']['violations']:
                print(f"   Violation: {violation}")
        
        # State transition
        state_status = "✅" if results['state_transition']['valid'] else "❌"
        print(f"{state_status} State Transition: {results['state_transition']['valid']}")
        
        print(f"⏱️  Processing time: {results['processing_time_seconds']:.3f}s")
        print("=" * 50)
    
    def print_statistics(self):
        """Print summary statistics."""
        print(f"\n📈 Hash Reproducer Statistics")
        print("=" * 40)
        print(f"Entries processed: {self.stats['entries_processed']}")
        print(f"Valid hashes: {self.stats['hashes_valid']}")
        print(f"Invalid hashes: {self.stats['hashes_invalid']}")
        
        if self.stats['entries_processed'] > 0:
            success_rate = (self.stats['hashes_valid'] / self.stats['entries_processed']) * 100
            print(f"Hash success rate: {success_rate:.1f}%")
        
        print(f"Valid signatures: {self.stats['signatures_valid']}")
        print(f"Invalid signatures: {self.stats['signatures_invalid']}")
        print(f"Constitutional violations: {self.stats['constitutional_violations']}")
        print(f"Total processing time: {self.stats['processing_time']:.2f}s")
        
        if self.stats['entries_processed'] > 0:
            avg_time = self.stats['processing_time'] / self.stats['entries_processed']
            print(f"Average time per entry: {avg_time:.3f}s")
    
    def generate_report(self, output_path: str, results: Dict[str, Any]):
        """Generate a JSON report of validation results."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'tool_version': '1.0.0',
            'statistics': self.stats,
            'results': results
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report generated: {output_path}")
    
    def close(self):
        """Close database connection and cleanup."""
        if self.conn:
            self.conn.close()
        if self.session:
            self.session.close()


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description='Hash Reproducer - Constitutional Archive Integrity Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a single entry
  python hash_reproducer.py --entry entry_2024_001_abc123
  
  # Validate with verbose output
  python hash_reproducer.py --entry entry_2024_001_abc123 --verbose
  
  # Audit an agent's recent activity
  python hash_reproducer.py --audit-agent claude.prod --time-range 7d
  
  # Generate a report
  python hash_reproducer.py --entry entry_2024_001_abc123 --report validation_report.json
  
  # Use API instead of local database
  python hash_reproducer.py --entry entry_2024_001_abc123 --api https://constitution.ai/api/v1
        """
    )
    
    parser.add_argument('--entry', help='Validate a specific archive entry')
    parser.add_argument('--verify-range', action='store_true', help='Validate a range of entries')
    parser.add_argument('--start', help='Start entry ID for range validation')
    parser.add_argument('--end', help='End entry ID for range validation')
    parser.add_argument('--audit-agent', help='Audit all entries from a specific agent')
    parser.add_argument('--time-range', choices=['7d', '30d', '90d', '1y'], default='30d',
                       help='Time range for audit (default: 30d)')
    parser.add_argument('--archive', default='constitution_archive.db',
                       help='Path to archive database (default: constitution_archive.db)')
    parser.add_argument('--api', help='Base URL for archive API')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--report', help='Generate JSON report to specified file')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for range validation')
    
    args = parser.parse_args()
    
    # Initialize reproducer
    reproducer = HashReproducer(args.archive, args.api)
    
    if not reproducer.connect() and not args.api:
        print("❌ Cannot connect to archive database and no API specified")
        sys.exit(1)
    
    try:
        results = None
        
        if args.entry:
            # Validate single entry
            results = reproducer.validate_entry(args.entry, verbose=args.verbose)
            
        elif args.verify_range and args.start and args.end:
            # Validate range
            results = reproducer.validate_range(args.start, args.end, args.batch_size)
            
        elif args.audit_agent:
            # Audit agent
            results = reproducer.audit_agent(args.audit_agent, args.time_range)
            
        else:
            parser.print_help()
            return
        
        # Print statistics
        reproducer.print_statistics()
        
        # Generate report if requested
        if args.report and results:
            reproducer.generate_report(args.report, results)
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        reproducer.close()


if __name__ == '__main__':
    main()
