import re

def evaluate_tool_payload(target_tool: str, raw_arguments: str) -> dict:
    """
    Evaluates risk and compliance variables for a tool payload based on STRIDE threats.
    Scans for data tampering patterns and privilege elevation requests.

    Args:
        target_tool: The name of the tool intended for execution.
        raw_arguments: Command string or JSON parameters passed to the tool.

    Returns:
        dict: The evaluated pipeline state dictionary.
    """
    risk_score = 0
    threat_signatures = []
    
    # Normalize arguments for evaluation checks
    args_lower = raw_arguments.lower()

    # 1. Check for data tampering indicators (e.g., DROP TABLE, rm -rf, delete from)
    tampering_patterns = [
        (r"\bdrop\s+table\b", "DB_DROP_TABLE_ATTEMPT"),
        (r"\brm\s+-rf\b", "UNRESTRICTED_FILE_DELETION"),
        (r"\bdelete\s+from\b", "DB_DELETE_RECORD_ATTEMPT"),
        (r"\btruncate\s+table\b", "DB_TRUNCATE_TABLE_ATTEMPT")
    ]
    
    for pattern, signature in tampering_patterns:
        if re.search(pattern, args_lower):
            risk_score += 60
            threat_signatures.append(signature)

    # 2. Check for privilege elevation attempts (e.g., sudo, admin_role, root)
    elevation_patterns = [
        (r"\bsudo\b", "SUDO_PRIVILEGE_ESCALATION"),
        (r"\badmin_role\b", "ADMIN_ROLE_ESCALATION"),
        (r"\bchmod\b", "FILE_PERMISSION_MODIFICATION")
    ]
    
    for pattern, signature in elevation_patterns:
        if re.search(pattern, args_lower):
            risk_score += 40
            threat_signatures.append(signature)

    # Ensure risk score is capped at 100
    risk_score = min(risk_score, 100)

    # Default baseline risk for clean requests
    if risk_score == 0:
        risk_score = 10

    return {
        "target_tool": target_tool,
        "raw_arguments": raw_arguments,
        "risk_score": risk_score,
        "threat_signatures": threat_signatures,
        "execution_status": "PENDING"
    }
