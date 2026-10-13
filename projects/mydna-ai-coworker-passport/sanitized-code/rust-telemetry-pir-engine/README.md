# Telemetry PIR Engine (Sanitized Reference)

Production-grade Rust implementation of on-device Privacy Information Redaction (PIR) and clipboard lineage hashing.

## Features
- **Zero-allocation reads:** Thread-safe pre-compiled regular expressions using `OnceLock`.
- **Fast Lineage Hashing:** 64-bit deterministic lineage hashing without keeping plain-text buffers.
- **Surface Classification:** Window classification for AI web surfaces and IDEs.

## Verification
```bash
cargo test
```
