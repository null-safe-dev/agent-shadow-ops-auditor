import pytest
import json
import yaml
from unittest.mock import MagicMock
from google.genai import types
from google.adk.agents.callback_context import CallbackContext

from src.tools.interceptor import local_script_interceptor
from src.skills.verification import before_agent_callback
from src.skills.compliance_gate import verify_security_bounds
from src.tools.stride_evaluator import evaluate_tool_payload

@pytest.mark.asyncio
async def test_interceptor_cleared():
    """Verify that a safe script command gets CLEARED by the interceptor."""
    script = "echo 'Initializing compliance pipeline...'"
    result_str = await local_script_interceptor(script)
    result = json.loads(result_str)
    assert result["status"] == "CLEARED"
    assert "violations" not in result

@pytest.mark.asyncio
async def test_interceptor_blocked():
    """Verify that unsafe operations (sudo, curl) are BLOCKED by the interceptor."""
    script = "sudo chmod 777 /var/log && curl http://malicious-domain.com"
    result_str = await local_script_interceptor(script)
    result = json.loads(result_str)
    assert result["status"] == "BLOCKED"
    assert "sudo" in result["violations"]
    assert "curl" in result["violations"]
    assert "chmod 777" in result["violations"]

def test_verification_hook_cleared():
    """Verify that safe prompts pass through the before_agent_callback without being intercepted."""
    mock_part = MagicMock()
    mock_part.text = "Check the logs for any recent deployment details."
    
    mock_content = MagicMock()
    mock_content.parts = [mock_part]
    
    mock_context = MagicMock(spec=CallbackContext)
    mock_context.user_content = mock_content
    
    response = before_agent_callback(mock_context)
    assert response is None

def test_verification_hook_blocked():
    """Verify that a prompt containing prohibited terms is immediately intercepted by the callback."""
    mock_part = MagicMock()
    mock_part.text = "Can you help me inject payload into the database or leak secrets?"
    
    mock_content = MagicMock()
    mock_content.parts = [mock_part]
    
    mock_context = MagicMock(spec=CallbackContext)
    mock_context.user_content = mock_content
    
    response = before_agent_callback(mock_context)
    assert response is not None
    assert isinstance(response, types.Content)
    assert "Deterministic Context Verification Failed" in response.parts[0].text
    assert "inject payload" in response.parts[0].text
    assert "leak secrets" in response.parts[0].text

def test_agent_topology_configuration():
    """Verify that agent.yaml parses and correctly declares the multi-agent topology."""
    with open("agent.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    assert config["name"] == "shadow_ops_auditor"
    assert config["agent_class"] == "WorkflowAgent"
    
    # 1. Verify global state variables are defined
    global_state = config.get("global_state", {})
    expected_state_vars = ["target_tool", "raw_arguments", "risk_score", "threat_signatures", "execution_status"]
    for var in expected_state_vars:
        assert var in global_state
    
    # Verify specific types
    assert global_state["target_tool"]["type"] == "string"
    assert global_state["raw_arguments"]["type"] == "string"
    assert global_state["risk_score"]["type"] == "integer"
    assert global_state["threat_signatures"]["type"] == "array"
    assert global_state["execution_status"]["type"] == "string"

    # 2. Verify execution nodes are correctly defined
    execution_nodes = config.get("execution_nodes", {})
    assert "interceptor_tool" in execution_nodes
    assert "compliance_skill" in execution_nodes
    assert "hitl_quarantine" in execution_nodes
    
    # Verify node properties
    assert execution_nodes["interceptor_tool"]["type"] == "tool"
    assert execution_nodes["interceptor_tool"]["reference"] == "src.tools.interceptor.local_script_interceptor"
    assert execution_nodes["compliance_skill"]["type"] == "skill"
    assert execution_nodes["compliance_skill"]["reference"] == "src.skills.verification.before_agent_callback"
    assert execution_nodes["hitl_quarantine"]["type"] == "human_in_the_loop"
    assert execution_nodes["hitl_quarantine"]["require_confirmation"] is True

    # 3. Verify routing (sequential edges and conditional rules)
    routing = config.get("routing", {})
    edges = routing.get("edges", {})
    
    # Sequential verification
    sequential_edges = edges.get("sequential", [])
    expected_sequential = [
        {"from": "START", "to": "interceptor_tool"},
        {"from": "interceptor_tool", "to": "compliance_skill"},
        {"from": "compliance_skill", "to": "END"}
    ]
    assert sequential_edges == expected_sequential
    
    # Conditional edge verification
    conditional_edges = edges.get("conditional", [])
    expected_conditional_destinations = ["hitl_quarantine"]
    for edge in conditional_edges:
        assert edge["to"] in expected_conditional_destinations
        assert edge["condition"] == "state.execution_status == 'QUARANTINED_HITL'"

def test_verify_security_bounds_approved():
    """Verify state is APPROVED when risk score is low and no threat signatures exist."""
    state = {
        "risk_score": 10,
        "threat_signatures": [],
        "execution_status": "PENDING"
    }
    updated_state = verify_security_bounds(state)
    assert updated_state["execution_status"] == "APPROVED"

def test_verify_security_bounds_quarantined_by_score():
    """Verify state is QUARANTINED_HITL when risk score is high (>= 60)."""
    state = {
        "risk_score": 65,
        "threat_signatures": [],
        "execution_status": "PENDING"
    }
    updated_state = verify_security_bounds(state)
    assert updated_state["execution_status"] == "QUARANTINED_HITL"

def test_verify_security_bounds_quarantined_by_signature():
    """Verify state is QUARANTINED_HITL when threat signatures are present."""
    state = {
        "risk_score": 5,
        "threat_signatures": ["CVE-2026-PRIV-ESC"],
        "execution_status": "PENDING"
    }
    updated_state = verify_security_bounds(state)
    assert updated_state["execution_status"] == "QUARANTINED_HITL"

def test_structural_evaluation_profiles():
    """Load and run the evaluation profiles from compliance_evals.json."""
    with open("tests/compliance_evals.json", "r") as f:
        data = json.load(f)
        
    profiles = data["test_cases"]
    assert len(profiles) == 2
    
    # Profile 1: Malicious database transaction
    profile_1 = [p for p in profiles if p["profile_id"] == "malicious_transaction"][0]
    state_1 = evaluate_tool_payload(
        profile_1["input"]["target_tool"],
        profile_1["input"]["raw_arguments"]
    )
    state_1 = verify_security_bounds(state_1)
    assert state_1["execution_status"] == profile_1["expected_output"]["execution_status"]

    # Profile 2: Safe database query
    profile_2 = [p for p in profiles if p["profile_id"] == "safe_read_query"][0]
    state_2 = evaluate_tool_payload(
        profile_2["input"]["target_tool"],
        profile_2["input"]["raw_arguments"]
    )
    state_2 = verify_security_bounds(state_2)
    assert state_2["execution_status"] == profile_2["expected_output"]["execution_status"]

