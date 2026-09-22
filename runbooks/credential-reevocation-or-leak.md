# Credential Revocation or Leak

## Severity
High / Critical

## Overview
A credential (API key, password, token, certificate, or private key) has been leaked, exposed, or must be revoked immediately.

## Detection
- Secret scanning alert (e.g., git history, CI logs)
- Unauthorized access or anomalous authentication activity
- Report from an employee or third party

## Response

### 1. Contain
- Identify the affected credential and its scope (user, service, system)
- Block the credential at the auth provider / secrets manager immediately

### 2. Revoke & Rotate
- Revoke the exposed credential
- Generate a new credential and distribute it only through a secure channel
- Update all services and integrations that depend on the old credential

### 3. Investigate
- Review access logs for misuse during the exposure window
- Determine how the leak occurred (repo commit, log dump, phishing, etc.)
- Remove the secret from git history if committed (`git filter-repo` or BFG)

### 4. Prevent
- Enforce secret scanning in CI and pre-commit hooks
- Store all secrets in a secrets manager (never in code or config files)
- Enable short-lived tokens where possible
- Rotate credentials on a regular schedule

## Post-Incident
- Document the timeline and root cause
- Add preventive controls to the backlog
- Notify affected stakeholders if required
