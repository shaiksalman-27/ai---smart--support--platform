from typing import Dict, Optional
import random

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.support_logic import analyze_support_issue
from app.security_logic import analyze_security_risk
from app.recovery_logic import get_recovery_steps

app = FastAPI(title="AI Smart Support & Cybersecurity Assistant")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class IssueRequest(BaseModel):
    issue: str


class ResetRequest(BaseModel):
    task_id: Optional[str] = None


class StepRequest(BaseModel):
    action_type: str
    content: Optional[str] = ""


TASKS: Dict[str, Dict] = {
    "easy_password_reset": {
        "task_id": "easy_password_reset",
        "ticket": "I cannot log in to my account and need a password reset.",
        "expected_category": "account access",
        "expected_priority": "low",
        "goal": "Agent should identify password reset issue, provide reset guidance, and close safely.",
        "success_keywords": ["forgot password", "reset password", "password reset", "forgot my password"],
        "safe_close_keywords": ["forgot password", "reset password", "password reset"],
        "max_steps": 4,
    },
    "medium_payment_failure": {
        "task_id": "medium_payment_failure",
        "ticket": "My payment failed but money was deducted from my bank account.",
        "expected_category": "billing",
        "expected_priority": "high",
        "goal": "Agent should identify billing issue, ask for relevant transaction details or escalate carefully.",
        "success_keywords": ["transaction id", "payment reference", "bank statement", "billing team", "escalate"],
        "safe_close_keywords": [],
        "max_steps": 4,
    },
    "hard_account_takeover": {
        "task_id": "hard_account_takeover",
        "ticket": "I think someone hacked my account and changed my password.",
        "expected_category": "security",
        "expected_priority": "critical",
        "goal": "Agent should identify account takeover risk, avoid unsafe closure, recommend urgent security steps, and escalate.",
        "success_keywords": ["secure account", "escalate", "security team", "compromised", "change password", "safe device"],
        "safe_close_keywords": [],
        "max_steps": 4,
    },
}

CURRENT_EPISODE: Dict = {}


def normalize_score(score: float) -> float:
    if score <= 0.0:
        return 0.1
    if score >= 1.0:
        return 0.9
    return round(score, 3)


def build_observation() -> Dict:
    return {
        "task_id": CURRENT_EPISODE.get("task_id"),
        "ticket": CURRENT_EPISODE.get("ticket"),
        "received_action": CURRENT_EPISODE.get("last_action"),
        "message": CURRENT_EPISODE.get("last_message", ""),
        "step_count": CURRENT_EPISODE.get("step_count", 0),
        "status": CURRENT_EPISODE.get("status", "not_started"),
    }


def build_reward(score: float, done: bool) -> Dict:
    return {
        "score": normalize_score(score),
        "done": done,
    }


def choose_task(task_id: Optional[str] = None) -> Dict:
    if task_id and task_id in TASKS:
        return TASKS[task_id]
    return TASKS[random.choice(list(TASKS.keys()))]


def start_episode(task: Dict) -> None:
    CURRENT_EPISODE.clear()
    CURRENT_EPISODE.update({
        "task_id": task["task_id"],
        "ticket": task["ticket"],
        "expected_category": task["expected_category"],
        "expected_priority": task["expected_priority"],
        "goal": task["goal"],
        "success_keywords": task["success_keywords"],
        "safe_close_keywords": task["safe_close_keywords"],
        "max_steps": task["max_steps"],
        "step_count": 0,
        "status": "in_progress",
        "last_action": None,
        "last_message": "",
        "history": [],
    })


def evaluate_action(action_type: str, content: str) -> tuple[float, bool, str]:
    action_type = action_type.lower().strip()
    content_lower = content.lower().strip()
    task_id = CURRENT_EPISODE["task_id"]

    score = 0.1
    done = False
    note = "Action recorded."

    CURRENT_EPISODE["step_count"] += 1
    CURRENT_EPISODE["last_action"] = action_type
    CURRENT_EPISODE["last_message"] = content
    CURRENT_EPISODE["history"].append({
        "action_type": action_type,
        "content": content,
    })

    if action_type == "classify":
        expected = CURRENT_EPISODE["expected_category"]
        if expected in content_lower:
            score = 0.2
            note = "Correct classification direction."
        else:
            score = 0.1
            note = "Classification seems incorrect."

    elif action_type == "prioritize":
        expected = CURRENT_EPISODE["expected_priority"]
        if expected in content_lower:
            score = 0.2
            note = "Priority matches task."
        else:
            score = 0.1
            note = "Priority does not match expected level."

    elif action_type == "respond":
        matched = any(keyword in content_lower for keyword in CURRENT_EPISODE["success_keywords"])
        if matched:
            score = 0.2
            note = "Helpful response."
        else:
            score = 0.1
            note = "Response recorded, but could be stronger."

    elif action_type == "ask_info":
        if task_id == "medium_payment_failure":
            if any(word in content_lower for word in ["transaction", "reference", "payment", "bank", "screenshot"]):
                score = 0.2
                note = "Good request for relevant payment details."
            else:
                score = 0.1
                note = "Question asked, but not very targeted."
        elif task_id == "hard_account_takeover":
            if any(word in content_lower for word in ["identity", "verification", "email", "phone", "confirm"]):
                score = 0.2
                note = "Good request for security verification details."
            else:
                score = 0.1
                note = "Additional info requested, but not targeted."
        else:
            score = 0.1
            note = "Additional info requested."

    elif action_type == "escalate":
        if task_id in ["medium_payment_failure", "hard_account_takeover"]:
            score = 0.2
            done = True
            CURRENT_EPISODE["status"] = "resolved"
            note = "Correct escalation."
        else:
            score = 0.1
            note = "Escalation not necessary for this simple task."

    elif action_type == "close":
        if task_id == "easy_password_reset":
            if any(keyword in content_lower for keyword in CURRENT_EPISODE["safe_close_keywords"]):
                score = 0.2
                done = True
                CURRENT_EPISODE["status"] = "resolved"
                note = "Safe resolution and closure."
            else:
                score = 0.1
                note = "Closure happened without enough guidance."
        elif task_id == "medium_payment_failure":
            score = 0.1
            note = "Unsafe to close this before validation or escalation."
        elif task_id == "hard_account_takeover":
            score = 0.1
            note = "Unsafe closure for account takeover case."

    else:
        score = 0.1
        note = "Unknown action type."

    if CURRENT_EPISODE["step_count"] >= CURRENT_EPISODE["max_steps"] and not done:
        done = True
        CURRENT_EPISODE["status"] = "max_steps_reached"
        note = f"{note} Maximum steps reached."

    return normalize_score(score), done, note


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
        return JSONResponse(
            status_code=400,
            content={"error": "Issue text is required."},
        )

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
        return JSONResponse(
            status_code=400,
            content={"error": "Issue text is required."},
        )

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
                "task_id": task["task_id"],
                "goal": task["goal"],
                "ticket": task["ticket"],
            }
            for task in TASKS.values()
        ]
    }


@app.post("/reset")
def reset_env(data: Optional[ResetRequest] = None):
    task_id = None
    if data is not None:
        task_id = data.task_id

    task = choose_task(task_id)
    start_episode(task)

    return {
        "observation": build_observation(),
        "reward": build_reward(0.1, False),
    }


@app.get("/state")
def state_env():
    if not CURRENT_EPISODE:
        return JSONResponse(
            status_code=400,
            content={"error": "Environment not initialized. Call /reset first."},
        )

    return {
        "observation": build_observation(),
        "reward": build_reward(0.1, False),
    }


@app.post("/step")
def step_env(action: StepRequest):
    if not CURRENT_EPISODE:
        return JSONResponse(
            status_code=400,
            content={"error": "Environment not initialized. Call /reset first."},
        )

    score, done, note = evaluate_action(action.action_type, action.content or "")

    return {
        "observation": build_observation(),
        "reward": build_reward(score, done),
        "info": {
            "note": note,
            "history": CURRENT_EPISODE.get("history", []),
        },
    }


@app.get("/grader")
def grader():
    if not CURRENT_EPISODE:
        return JSONResponse(
            status_code=400,
            content={"error": "Environment not initialized. Call /reset first."},
        )

    history = CURRENT_EPISODE.get("history", [])
    total_score = 0.1

    for item in history:
        text = f"{item.get('action_type', '')} {item.get('content', '')}".lower()

        if CURRENT_EPISODE["task_id"] == "easy_password_reset":
            if "password" in text or "reset" in text:
                total_score += 0.2
            if "close" in text:
                total_score += 0.2

        elif CURRENT_EPISODE["task_id"] == "medium_payment_failure":
            if "transaction" in text or "reference" in text or "billing" in text:
                total_score += 0.2
            if "escalate" in text:
                total_score += 0.2

        elif CURRENT_EPISODE["task_id"] == "hard_account_takeover":
            if "security" in text or "compromised" in text or "safe device" in text:
                total_score += 0.2
            if "escalate" in text:
                total_score += 0.2
            if "close" in text:
                total_score -= 0.1

    total_score = normalize_score(total_score)
    passed = total_score >= 0.5

    return {
        "task_id": CURRENT_EPISODE["task_id"],
        "passed": passed,
        "final_score": total_score,
        "history": history,
    }


@app.get("/baseline")
def baseline():
    return {
        "baseline_policy": [
            {
                "task_id": "easy_password_reset",
                "recommended_actions": [
                    {"action_type": "classify", "content": "account access"},
                    {"action_type": "prioritize", "content": "low"},
                    {"action_type": "respond", "content": "Please use the forgot password option to reset your password."},
                    {"action_type": "close", "content": "Password reset guidance provided."},
                ],
            },
            {
                "task_id": "medium_payment_failure",
                "recommended_actions": [
                    {"action_type": "classify", "content": "billing"},
                    {"action_type": "prioritize", "content": "high"},
                    {"action_type": "ask_info", "content": "Please share transaction ID or payment reference number."},
                    {"action_type": "escalate", "content": "Escalating to billing support team."},
                ],
            },
            {
                "task_id": "hard_account_takeover",
                "recommended_actions": [
                    {"action_type": "classify", "content": "security"},
                    {"action_type": "prioritize", "content": "critical"},
                    {"action_type": "respond", "content": "Use a safe device and change your password immediately if possible."},
                    {"action_type": "escalate", "content": "Escalating to security team for account takeover handling."},
                ],
            },
        ]
    }