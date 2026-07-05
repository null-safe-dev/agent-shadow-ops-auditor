import streamlit as st
import json
from src.tools.stride_evaluator import evaluate_tool_payload
from src.skills.compliance_gate import verify_security_bounds

# Set Page Config to Wide Layout
st.set_page_config(
    page_title="Agent Shadow-Ops Auditor Panel",
    page_icon="🛡️",
    layout="wide"
)

# Header
st.title("🛡️ Enterprise Agent Shadow-Ops Auditor Panel")
st.markdown("### Left-Shift Multi-Agent Security & Governance Gate")
st.write("Intercept tool execution requests, identify policy violations, and run administrative validation overrides.")

# Initialize Session State variables
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = ""
if "arguments_payload" not in st.session_state:
    st.session_state.arguments_payload = ""
if "overridden" not in st.session_state:
    st.session_state.overridden = False

# Layout split into two equal columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("## 📥 Inbound Agent Execution Box")
    
    # Target Tool Execution Interface selectbox
    target_tool = st.selectbox(
        "Target Tool Execution Interface:",
        options=["relational_db_connector", "cloud_infrastructure_api", "hr_portal_system"],
        index=0
    )

    # Raw Arguments Payload input box with default query
    default_payload = '{"query": "SELECT * FROM public.analytics_metrics LIMIT 10;"}'
    raw_arguments = st.text_area(
        "Raw Arguments Payload (JSON Format):",
        value=default_payload,
        height=180
    )

    # Action button
    if st.button("Submit Payload to Sandbox", use_container_width=True):
        st.session_state.submitted = True
        st.session_state.selected_tool = target_tool
        st.session_state.arguments_payload = raw_arguments
        st.session_state.overridden = False

with col2:
    st.markdown("## 📊 Live Security Metrics Pipeline")

    # Only execute logic if the form has been submitted
    if st.session_state.submitted:
        # Run backend modules
        eval_state = evaluate_tool_payload(
            target_tool=st.session_state.selected_tool,
            raw_arguments=st.session_state.arguments_payload
        )
        final_state = verify_security_bounds(eval_state)

        # Check for admin override trigger
        if st.session_state.overridden:
            final_state["execution_status"] = "APPROVED"

        status = final_state.get("execution_status", "PENDING")
        risk_score = final_state.get("risk_score", 0)
        signatures = final_state.get("threat_signatures", [])

        if status == "APPROVED":
            # APPROVED State layout
            st.success("🟢 PAYLOAD APPROVED FOR EXECUTION")
            
            # Risk score metric card
            st.metric(
                label="Evaluated Risk Score",
                value=risk_score if not st.session_state.overridden else 0,
                delta="Clean Payload" if not st.session_state.overridden else "Overridden By Admin",
                delta_color="normal" if not st.session_state.overridden else "off"
            )
            
            # Info block
            st.info("No malicious vectors were flagged. Safety verification complete.")
            
            # Display override status alert if triggered
            if st.session_state.overridden:
                st.info("🔓 ADMIN OVERRIDE SUCCESSFUL: Payload released to runner.")

        elif status == "QUARANTINED_HITL":
            # QUARANTINED State layout
            st.error("🔴 CRITICAL THREAT DETECTED: PAYLOAD QUARANTINED")
            
            # Risk score metric card
            st.metric(
                label="Evaluated Risk Score",
                value=risk_score,
                delta="CRITICAL THREAT",
                delta_color="inverse"
            )

            # Outputs the specific elements inside the threat signatures array
            st.write("**Flagged Threat Signatures:**")
            for sig in signatures:
                st.warning(f"Signature Flagged:")
                st.code(sig, language="text")

            # Human-In-The-Loop Operations Room
            st.markdown("---")
            st.subheader("👥 Human-In-The-Loop Operations Room")
            st.write("Manual security intervention is required to unlock this execution request.")
            
            if st.button("Admin Override: Force Release Payload"):
                st.session_state.overridden = True
                st.rerun()
                
    else:
        st.info("Please configure the payload in the Inbound Agent Execution Box and submit to run security checks.")
