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

# Premium Dark CSS Injection
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global fonts and background colors override */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Style the text areas and select boxes to feel like code sandbox tools */
    div.stTextArea textarea {
        background-color: #0B0F19 !important;
        border: 1px solid #334155 !important;
        color: #38BDF8 !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 14px !important;
        border-radius: 8px !important;
    }
    
    div.stSelectbox div[data-baseweb="select"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    /* Primary and Admin override button styling */
    div.stButton > button {
        background-color: #10B981 !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div.stButton > button:hover {
        background-color: #34D399 !important;
        transform: translateY(-1px) !important;
    }

    /* Red and Green Indicator bars */
    .indicator-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 24px;
        border-left: 6px solid #10B981;
        margin-bottom: 20px;
    }
    
    .indicator-card-error {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 24px;
        border-left: 6px solid #EF4444;
        margin-bottom: 20px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #F8FAFC;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <h1 style='color: #F8FAFC; font-weight: 700;'>🛡️ Enterprise Agent Shadow-Ops Auditor Panel</h1>
    <p style='color: #94A3B8; font-size: 18px; font-weight: 500;'>Left-Shift Multi-Agent Security & Governance Gate</p>
</div>
""", unsafe_allow_html=True)

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
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("<h2 style='color: #F8FAFC; font-size: 22px; font-weight: 600; margin-bottom: 20px;'>📥 Inbound Agent Execution Box</h2>", unsafe_allow_html=True)
    
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
        st.rerun()

with col2:
    st.markdown("<h2 style='color: #F8FAFC; font-size: 22px; font-weight: 600; margin-bottom: 20px;'>📊 Live Security Metrics Pipeline</h2>", unsafe_allow_html=True)

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
            
            # Custom indicator card
            st.markdown(f"""
                <div class="indicator-card">
                    <p style="color: #94A3B8; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 4px 0;">Evaluated Risk Score</p>
                    <div class="metric-value">{risk_score if not st.session_state.overridden else 0}</div>
                    <p style="color: #10B981; font-size: 14px; margin: 8px 0 0 0; font-weight: 500;">{"✓ Safe Payload Baseline" if not st.session_state.overridden else "✓ Overridden By Admin"}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Info block
            st.info("No malicious vectors were flagged. Safety verification complete.")
            
            # Display override status alert if triggered
            if st.session_state.overridden:
                st.toast("🔓 ADMIN OVERRIDE SUCCESSFUL: Payload released.")

        elif status == "QUARANTINED_HITL":
            # QUARANTINED State layout
            st.error("🔴 CRITICAL THREAT DETECTED: PAYLOAD QUARANTINED")
            
            # Custom indicator card
            st.markdown(f"""
                <div class="indicator-card-error">
                    <p style="color: #94A3B8; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 4px 0;">Evaluated Risk Score</p>
                    <div class="metric-value">{risk_score}</div>
                    <p style="color: #EF4444; font-size: 14px; margin: 8px 0 0 0; font-weight: 500;">✗ CRITICAL THREAT BOUNDARY VIOLATION</p>
                </div>
            """, unsafe_allow_html=True)

            # Outputs the specific elements inside the threat signatures array
            st.write("**Flagged Threat Signatures:**")
            for sig in signatures:
                st.warning(f"Signature Flagged:")
                st.code(sig, language="text")

            # Human-In-The-Loop Operations Room
            st.markdown("---")
            st.subheader("👥 Human-In-The-Loop Operations Room")
            st.write("Manual security intervention is required to unlock this execution request.")
            
            # Trigger button
            if st.button("Admin Override: Force Release Payload", use_container_width=True):
                st.session_state.overridden = True
                st.rerun()
                
    else:
        st.info("Please configure the payload in the Inbound Agent Execution Box and submit to run security checks.")
