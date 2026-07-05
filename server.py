from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from src.tools.stride_evaluator import evaluate_tool_payload
from src.skills.compliance_gate import verify_security_bounds

app = FastAPI(
    title="Shadow Ops Auditor compliance API",
    description="HTTP server wrapper exposing the multi-agent compliance pipeline for security checks.",
    version="1.0.0"
)

class AuditPayload(BaseModel):
    target_tool: str
    raw_arguments: str

@app.post("/api/audit", summary="Audit a tool payload", response_description="The final validated execution state")
async def audit_endpoint(payload: AuditPayload):
    """
    Exposes a compliance evaluation endpoint.
    Runs the payload through the stride threat evaluator and the compliance gate.
    """
    try:
        # Step 1: Run through evaluation interceptor tool
        initial_state = evaluate_tool_payload(
            target_tool=payload.target_tool,
            raw_arguments=payload.raw_arguments
        )
        
        # Step 2: Run through deterministic compliance skill gate
        final_state = verify_security_bounds(initial_state)
        
        return final_state
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred within the compliance pipeline: {str(e)}"
        )

@app.get("/health", summary="Health check endpoint")
async def health_check():
    """Simple API health check endpoint."""
    return {"status": "HEALTHY", "engine": "shadow-ops-auditor"}

if __name__ == "__main__":
    # Start the server on host 0.0.0.0 and port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
