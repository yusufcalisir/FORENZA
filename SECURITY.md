# Security Policy

## Security & Responsible Disclosure

FORENZA takes security, data privacy, and cryptographic evidence integrity with the highest priority.

---

## 🔒 Security Principles

1. **Zero Data Leakage:** All raw STR profiles, SNP genotypes, and CpG methylation values remain strictly localized or protected under ZK-SNARK Circom Groth16 zero-knowledge proofs.
2. **BYO-Key Storage Privacy:** User API keys configured in the web UI reside exclusively in the client's browser `localStorage` and are transmitted directly via secure proxy calls. Keys are **never** logged to external servers.
3. **Audit Trail Integrity:** Every biocomputational transaction is hashed via HMAC-SHA256 and anchored to the local or Polygon ledger.

---

## 🐛 Reporting a Vulnerability

If you discover a security vulnerability, please send a responsible disclosure email to security@forenza.org or create a private security advisory on GitHub.

Please do not publicly report security vulnerabilities in public issue trackers until the maintainers have investigated and released a patch.
