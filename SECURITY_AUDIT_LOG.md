# Security Audit Report

**Repository:** CAREFLOWAIAPP  
**Analysis Date:** 2026-04-17 06:01:14 UTC  
**Bot Version:** Hermes Security Bot v1.0

## Summary

- **Total Issues Found:** 3
- **Automatic Fixes Generated:** 0
- **Fixes Applied in this Run:** 0

## Analysis Details

### Scanned Files
The following security patterns were checked:
- Hardcoded secrets (passwords, API keys, tokens)
- Dangerous eval() usage
- HTTP instead of HTTPS
- DEBUG mode enabled in production
- Bare except clauses

### Issues Detected

| Severity | Issue Type | File | Line | Match |
|----------|-----------|------|------|-------|
| HIGH | hardcoded_secret | `DEPLOYMENT_PACKAGE/run_deployment.py` | 7 | `PASSWORD = 'j2nzgPFUido5D'` |
| HIGH | hardcoded_secret | `DEPLOYMENT_PACKAGE/ssh_deploy.py` | 20 | `PASSWORD = "j2nzgPFUido5D"` |
| HIGH | hardcoded_secret | `DEPLOYMENT_PACKAGE/full_deploy.py` | 14 | `PASSWORD = 'j2nzgPFUido5D'` |

### Fixes Generated

*No automatic fixes were generated for this analysis.*

## Audit History

This file is automatically updated by the Hermes Security Bot.  
**Do not manually edit** - bot updates will overwrite changes.

---
*Last updated: 2026-04-17 06:01:14 UTC*
