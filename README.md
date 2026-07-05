# agent-shadow-ops-auditor

A code-first multi-agent compliance pipeline built using **Agent Development Kit (ADK) 2.0**.

This project provides automated auditing, intercepting script execution commands, and verifying context deterministically to prevent shadow operations or unauthorized actions by autonomous agents.

## Project Structure

```text
agent-shadow-ops-auditor/
│
├── agent.yaml              # Root ADK 2.0 configuration file
├── requirements.txt        # Python package dependencies
├── README.md               # Setup and usage documentation
│
├── src/
│   ├── tools/              # Local script interceptor tools
│   │   ├── __init__.py
│   │   └── interceptor.py  # Checks scripts/commands for unsafe operations (e.g. sudo, curl)
│   │
│   └── skills/             # Deterministic context verification hooks/callbacks
│       ├── __init__.py
│       └── verification.py # Pre-agent execution callback verifying prohibited prompts
│
└── tests/                  # Security automated evaluation tests
    ├── __init__.py
    └── test_compliance.py  # Unit & integration tests for tools, hooks, and configuration
```

## Setup Instructions

1. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # OR
   .venv\Scripts\activate.bat # On Windows (Command Prompt)
   # OR
   .venv\Scripts\Activate.ps1 # On Windows (PowerShell)
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Component Details

### 1. Root Configuration (`agent.yaml`)
Validates against the ADK 2.0 `AgentConfig` schema. It specifies the agent metadata, configures the `gemini-2.0-flash-exp` model, registers the custom local script interceptor tool, and configures the deterministic context verification callback.

### 2. Local Script Interceptors (`src/tools/interceptor.py`)
Uses the `local_script_interceptor` function to check command strings for privilege escalations (`sudo`, `chmod 777`), data exfiltration tools (`curl`, `wget`, `netcat`), and environment disclosures (`printenv`, `env`). If matched, it returns a `BLOCKED` status payload.

### 3. Context Verification Skills (`src/skills/verification.py`)
The `before_agent_callback` hook intercepts inputs before they reach the agent. It checks the incoming user prompt for prohibited terms (e.g., `bypass audit`, `inject payload`). If found, it deterministicially returns a blocked content message, skipping the LLM call entirely.

## Running Security Automated Evaluations

To verify the compliance checks and agent setup, run the pytest suite:

```bash
pytest tests/test_compliance.py
```
