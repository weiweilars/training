# HR Recruitment Agent Runners

Simple scripts to run HR recruitment agents with either Semantic Kernel (SK) or Agent Development Kit (ADK) implementations.

## Usage

### Run with Semantic Kernel (Recommended)
```bash
# List available agents
python run_sk_agents.py --list

# Start specific agent
python run_sk_agents.py job_requisition_agent
python run_sk_agents.py sourcing_agent
python run_sk_agents.py resume_screening_agent
```

### Run with Agent Development Kit
```bash
# List available agents  
python run_adk_agents.py --list

# Start specific agent
python run_adk_agents.py job_requisition_agent
python run_adk_agents.py sourcing_agent
python run_adk_agents.py resume_screening_agent
```

## Available Agents & Ports

| Agent Name | Port | URL |
|------------|------|-----|
| job_requisition_agent | 5020 | http://localhost:5020 |
| sourcing_agent | 5021 | http://localhost:5021 |
| resume_screening_agent | 5022 | http://localhost:5022 |
| assessment_agent | 5023 | http://localhost:5023 |
| interview_scheduling_agent | 5024 | http://localhost:5024 |
| background_verification_agent | 5025 | http://localhost:5025 |
| offer_management_agent | 5026 | http://localhost:5026 |
| communication_agent | 5027 | http://localhost:5027 |
| compliance_agent | 5028 | http://localhost:5028 |
| analytics_reporting_agent | 5029 | http://localhost:5029 |
| team_coordinator_agent | 5030 | http://localhost:5030 |

## Agent Cards
Each agent exposes its capabilities via agent card:
- Agent Card URL: `http://localhost:<port>/.well-known/agent-card.json`
- Example: http://localhost:5020/.well-known/agent-card.json

## Requirements
- Make sure you're in the `hr_recruitment_system` directory
- Agent configuration files must be in `hr_recruitment_agents/` subdirectory
- Either SK or ADK server implementations must be available in `../a2a_training/`

## Examples

```bash
# Start job requisition agent with SK
python run_sk_agents.py job_requisition_agent

# Start sourcing agent with ADK  
python run_adk_agents.py sourcing_agent

# List all available agents
python run_sk_agents.py --list
python run_adk_agents.py --list
```

## Stop Agents
Use `Ctrl+C` to stop any running agent.

## Notes
- Each agent runs on a fixed port to avoid conflicts
- Configuration files are automatically copied to the appropriate server directory
- SK implementation includes advanced features like context preservation
- ADK implementation provides simpler, lightweight operation