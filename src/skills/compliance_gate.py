def verify_security_bounds(state: dict) -> dict:
    """
    Enforces compliance policy checks on the current execution state.
    Pauses execution and flags status to QUARANTINED_HITL if threats are detected.

    Args:
        state: A state dictionary containing compliance analysis results.

    Returns:
        dict: The updated state dictionary with finalized execution_status.
    """
    risk_score = state.get("risk_score", 0)
    threat_signatures = state.get("threat_signatures", [])

    # Validate that threat_signatures is a list
    if not isinstance(threat_signatures, list):
        threat_signatures = [threat_signatures] if threat_signatures else []

    # Enforce security gates: Quarantine if risk score >= 60 or threat signatures detected
    if risk_score >= 60 or len(threat_signatures) > 0:
        state["execution_status"] = "QUARANTINED_HITL"
    else:
        state["execution_status"] = "APPROVED"

    return state
