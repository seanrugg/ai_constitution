flowchart TD
    A[Start Audit: Archive Entry] --> B[Retrieve AE Metadata]
    B --> C{Signature Valid?}
    C -->|No| D[Generate Fraud Proof<br/>SIGNATURE_FAIL]
    D --> E[Archive Entry INVALIDATED]
    C -->|Yes| F[Re-Canonicalize Action Data]
    F --> G[Re-Hash Canonical Data]
    G --> H{Hashes Match?}
    H -->|No| I[Generate Fraud Proof<br/>HASH_MISMATCH]
    I --> E
    H -->|Yes| J[AE VALIDATED]
    
    style A fill:#bbdefb
    style E fill:#ffcdd2
    style J fill:#c8e6c9
    style C fill:#fff9c4
    style H fill:#fff9c4
