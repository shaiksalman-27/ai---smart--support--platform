from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.env import SupportOpsEnv
from app.graders import grade_episode
from app.models import Action
from app.recovery_logic import get_recovery_steps
from app.security_logic import analyze_security_risk
from app.support_logic import analyze_support_issue
from app.tasks import list_tasks

app = FastAPI(title="AI Smart Support & Cybersecurity Assistant")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

env = SupportOpsEnv()


class IssueRequest(BaseModel):
    issue: str


class ResetRequest(BaseModel):
    task_id: Optional[str] = None


class StepRequest(BaseModel):
    action_type: str
    content: Optional[str] = ""


def action_from_request(req: StepRequest) -> Action:
    action_type = req.action_type.lower().strip()
    content = (req.content or "").strip()

    payload = {
        "action_type": action_type,
        "category": None,
        "priority": None,
        "message": None,
        "resolution": None,
        "escalation_team": None,
    }

    if action_type == "classify":
        payload["category"] = content.lower().replace(" ", "_")
    elif action_type in ["prioritize", "set_priority"]:
        payload["action_type"] = "set_priority"
        payload["priority"] = content.lower()
    elif action_type == "ask_info":
        payload["message"] = content
    elif action_type == "respond":
        payload["message"] = content
    elif action_type == "resolve":
        payload["resolution"] = content.lower().replace(" ", "_")
    elif action_type == "escalate":
        payload["escalation_team"] = content.lower().replace(" ", "_")
    elif action_type == "close":
        payload["action_type"] = "close"
    else:
        payload["message"] = content

    return Action(**payload)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok", "message": "Application is running"}


@app.post("/analyze")
def analyze_issue(data: IssueRequest):
    issue = data.issue.strip()

    if not issue:
        return JSONResponse(status_code=400, content={"error": "Issue text is required."})

    support = analyze_support_issue(issue)
    security = analyze_security_risk(issue)
    steps = get_recovery_steps(security["risk_level"])

    return {
        "issue": issue,
        "category": support["category"],
        "priority": support["priority"],
        "support_response": support["response"],
        "support_confidence": support.get("confidence", 80),
        "support_reasons": support.get("reasons", []),
        "risk_level": security["risk_level"],
        "risk_score": security["risk_score"],
        "security_confidence": security.get("confidence", 75),
        "security_summary": security.get("security_summary", "Security analysis completed."),
        "detected_signals": security["detected_signals"],
        "recovery_steps": steps,
    }


@app.post("/auto-recover")
def auto_recover(data: IssueRequest):
    issue = data.issue.lower().strip()

    if not issue:
        return JSONResponse(status_code=400, content={"error": "Issue text is required."})

    actions = []
    status = "Optimized"

    if "login" in issue or "password" in issue or "sign in" in issue:
        actions = [
            "Password reset workflow recommended",
            "Session refresh suggested",
            "Re-login guidance prepared",
            "Account access support response generated",
        ]
        status = "Recovered"

    elif "payment" in issue or "billing" in issue or "refund" in issue:
        actions = [
            "Transaction verification suggested",
            "Billing escalation path prepared",
            "Retry payment only after status check",
            "Customer safety note generated",
        ]
        status = "Partially Recovered"

    elif any(word in issue for word in ["hack", "hacked", "virus", "malware", "popup", "suspicious"]):
        actions = [
            "Internet disconnect recommended",
            "Suspicious apps review suggested",
            "Permission audit initiated conceptually",
            "Security scan guidance prepared",
            "Password change from safe device recommended",
        ]
        status = "Security Stabilized"

    elif any(word in issue for word in ["crash", "freeze", "stuck", "bug", "error"]):
        actions = [
            "Restart application suggested",
            "Cache clearing recommended",
            "Update check suggested",
            "Issue reproduction note prepared",
        ]
        status = "Partially Recovered"

    elif any(word in issue for word in ["slow", "lag", "performance", "overheating"]):
        actions = [
            "Background app cleanup suggested",
            "Storage cleanup recommended",
            "Restart device recommended",
            "Pending updates check suggested",
        ]
        status = "Optimized"

    else:
        actions = [
            "General troubleshooting guidance prepared",
            "Basic recovery recommendations generated",
            "Manual review may still be needed",
        ]
        status = "Reviewed"

    return {
        "status": status,
        "actions": actions,
        "note": "Automatic safe recovery guidance has been generated. Some cases may still need manual action.",
    }


@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {
                "task_id": item.task_id,
                "difficulty": item.difficulty,
                "title": item.title,
                "objective": item.objective,
            }
            for item in list_tasks()
        ]
    }


@app.post("/reset")
def reset_env(data: Optional[ResetRequest] = None):
    tasks = list_tasks()
    task_id = data.task_id if data and data.task_id else tasks[0].task_id

    observation = env.reset(task_id)

    return {
        "observation": observation.model_dump(),
        "reward": {
            "score": 0.1,
            "done": False,
        },
    }


@app.get("/state")
def state_env():
    current = env.state()
    if "error" in current:
        return JSONResponse(status_code=400, content=current)

    done = False
    if env.current_state is not None:
        done = env.current_state.done

    return {
        "observation": current,
        "reward": {
            "score": 0.1,
            "done": done,
        },
    }


@app.post("/step")
def step_env(action: StepRequest):
    if env.current_state is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Environment not initialized. Call /reset first."},
        )

    action_model = action_from_request(action)
    observation, reward, done, info = env.step(action_model)

    return {
        "observation": observation.model_dump(),
        "reward": {
            "score": reward.value,
            "done": done,
            "reason": reward.reason,
            "progress": reward.progress,
        },
        "info": info,
    }


@app.get("/grader")
def grader():
    if env.current_state is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Environment not initialized. Call /reset first."},
        )

    result = grade_episode(env.current_state)

    return {
        "task_id": result.task_id,
        "passed": result.score >= 0.5,
        "final_score": result.score,
        "details": result.details,
    }


@app.get("/baseline")
def baseline():
    return {
        "baseline_policy": [
            {
                "task_id": "easy_password_reset",
                "recommended_actions": [
                    {"action_type": "classify", "content": "account_access"},
                    {"action_type": "set_priority", "content": "low"},
                    {"action_type": "resolve", "content": "send_password_reset_steps"},
                    {"action_type": "close", "content": ""},
                ],
            },
            {
                "task_id": "medium_payment_failure",
                "recommended_actions": [
                    {"action_type": "classify", "content": "billing"},
                    {"action_type": "set_priority", "content": "high"},
                    {"action_type": "ask_info", "content": "Please share your transaction id."},
                    {"action_type": "resolve", "content": "request_transaction_id_and_open_billing_review"},
                    {"action_type": "close", "content": ""},
                ],
            },
            {
                "task_id": "hard_account_takeover",
                "recommended_actions": [
                    {"action_type": "classify", "content": "security"},
                    {"action_type": "set_priority", "content": "urgent"},
                    {"action_type": "ask_info", "content": "Please complete identity verification."},
                    {"action_type": "escalate", "content": "security_ops"},
                    {"action_type": "close", "content": ""},
                ],
            },
        ]
    }