import json
from src.tools.stride_evaluator import evaluate_tool_payload
from src.skills.compliance_gate import verify_security_bounds

def run_test_suite():
    """
    Validation engine to execute multi-agent compliance pipeline checks locally.
    Decodes the test profiles and runs evaluation loops.
    """
    try:
        with open("tests/compliance_evals.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: tests/compliance_evals.json dataset file not found.")
        return
    except json.JSONDecodeError:
        print("❌ Error: Failed to parse tests/compliance_evals.json. Invalid JSON syntax.")
        return

    test_cases = data.get("test_cases", [])
    total_cases = len(test_cases)
    passed_cases = 0

    print("=" * 70)
    print(" SHADOW-OPS-AUDITOR: LOCAL COMPLIANCE PIPELINE TEST SUITE")
    print("=" * 70)

    for case in test_cases:
        case_id = case.get("profile_id", "unknown_case")
        description = case.get("description", "")
        inputs = case.get("input", {})
        expected = case.get("expected_output", {})

        target_tool = inputs.get("target_tool", "")
        raw_arguments = inputs.get("raw_arguments", "")
        expected_status = expected.get("execution_status", "")

        # Print section header
        print(f"\n[Case ID: {case_id}]")
        print(f"Description: {description}")
        print(f"Target Tool: {target_tool}")
        print(f"Arguments  : {raw_arguments}")
        print("-" * 50)

        # 1. Run evaluation interceptor
        eval_state = evaluate_tool_payload(target_tool, raw_arguments)

        # 2. Run compliance gate
        final_state = verify_security_bounds(eval_state)

        # 3. Assess output
        actual_status = final_state.get("execution_status", "UNKNOWN")
        risk_score = final_state.get("risk_score", 0)
        signatures = final_state.get("threat_signatures", [])

        # Format details print
        print(f"  Risk Score        : {risk_score}")
        print(f"  Threat Signatures : {signatures}")
        print(f"  Final State Status: {actual_status}")

        if actual_status == expected_status:
            print("  🟢 VERIFICATION PASSED")
            passed_cases += 1
        else:
            print(f"  🔴 VERIFICATION FAILED (Expected: {expected_status}, Got: {actual_status})")
        print("-" * 50)

    # Output final summary section
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print(f"  Total Profiles Evaluated: {total_cases}")
    print(f"  Total Assertions Passed : {passed_cases} / {total_cases}")
    
    if passed_cases == total_cases:
        print("\n  🎉 SUCCESS: All compliance validation checks passed!")
    else:
        print("\n  ⚠️ WARNING: Some compliance checks did not match the expected state.")
    print("=" * 70)

if __name__ == "__main__":
    run_test_suite()
