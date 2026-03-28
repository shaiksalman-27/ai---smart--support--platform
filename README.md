# OpenEnv SupportOps

OpenEnv SupportOps is a real-world customer support ticket triage environment for training and evaluating AI agents.

## What this environment does

The agent must:
- classify support tickets
- assign priority
- request missing information
- escalate risky cases
- resolve safe cases
- close tickets safely

This simulates a real customer support operations workflow.

## Tasks

### 1. Easy — Password Reset
Agent must classify the issue as account access, assign low priority, send password reset steps, and close safely.

### 2. Medium — Payment Failure
Agent must classify the issue as billing, assign high priority, ask for transaction ID, open billing review, and close safely.

### 3. Hard — Account Takeover
Agent must classify the issue as security, assign urgent priority, request identity verification, escalate to security ops, and close safely.

## Action space

Each step takes a typed `Action` model with:
- `action_type`
- `category`
- `priority`
- `message`
- `resolution`
- `escalation_team`

Supported action types:
- `classify`
- `set_priority`
- `ask_info`
- `escalate`
- `resolve`
- `close`

## Observation space

Each step returns a typed `Observation` model:
- `task_id`
- `difficulty`
- `customer_message`
- `current_status`
- `known_facts`
- `missing_fields`
- `action_history`
- `remaining_steps`
- `done`

## Reward design

The reward gives partial progress for:
- correct classification
- correct priority
- correct information request
- correct resolution or escalation
- safe closure

Penalties are given for:
- wrong actions
- unnecessary information requests
- unsafe early closure
- max steps reached

## Grader

The grader returns a deterministic score between `0.0` and `1.0`.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 7860
```