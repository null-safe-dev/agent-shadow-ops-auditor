# Security Verification Rules & Compliance Scopes

This document lists the security policies, prohibited terminology, and risk calculations enforced by the compliance gate hooks.

## 🔒 Prohibited Terminology Rules

To prevent agents from bypassing pipeline auditing, the `before_agent_callback` hook scans inbound session prompts for audit-bypass keywords.

| Terminology Group | Match Term | Threat Signature Code | Impact Level |
| :--- | :--- | :--- | :--- |
| **Audit Bypass** | `bypass audit` | `BYPASS_AUDIT_ATTEMPT` | High |
| **Injection Attacks** | `inject payload` | `PAYLOAD_INJECTION_ATTEMPT` | Critical |
| **Data Disclosure** | `leak secrets` | `SECRETS_LEAK_ATTEMPT` | Critical |
| **Log Evasion** | `deactivate log` | `LOG_DEACTIVATION_ATTEMPT` | High |

---

## 🛡️ STRIDE Payload Interceptor Rules

The `evaluate_tool_payload` firewall analyzes command arguments for destructive actions and privilege elevations before executing tools on the host environment.

### 1. Data Tampering Patterns

Any command matching these patterns triggers a **+60 Risk Score** and flags the corresponding signature.

*   `DROP TABLE` ➔ `DB_DROP_TABLE_ATTEMPT`
*   `rm -rf` ➔ `UNRESTRICTED_FILE_DELETION`
*   `DELETE FROM` ➔ `DB_DELETE_RECORD_ATTEMPT`
*   `TRUNCATE TABLE` ➔ `DB_TRUNCATE_TABLE_ATTEMPT`

### 2. Privilege Elevation Patterns

Any command matching these patterns triggers a **+40 Risk Score** and flags the corresponding signature.

*   `sudo` ➔ `SUDO_PRIVILEGE_ESCALATION`
*   `admin_role` ➔ `ADMIN_ROLE_ESCALATION`
*   `chmod` ➔ `FILE_PERMISSION_MODIFICATION`

---

## 🚦 Risk Scoring & Routing Logic

The final validation step is executed inside `verify_security_bounds`:

$$RiskScore_{total} = \min(\sum RiskScore_{tampering} + \sum RiskScore_{elevation}, 100)$$

- **APPROVED**: If $RiskScore_{total} < 60$ and no threat signatures were raised, the payload is cleared for sandbox execution.
- **QUARANTINED_HITL**: If $RiskScore_{total} \ge 60$ or any threat signatures are present, execution is paused, routing the transaction directly to the quarantine node for administrator review.
