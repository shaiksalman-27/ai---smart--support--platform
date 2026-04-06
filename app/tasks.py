from typing import Dict, List

from app.models import TaskMetadata, TicketState


TASKS: Dict[str, TicketState] = {
    "easy_password_reset": TicketState(
        task_id="easy_password_reset",
        difficulty="easy",
        title="Password Reset",
        objective="Classify the issue, set low priority, resolve with password reset steps, then close safely.",
        customer_message=(
            "Hi support, I forgot my password and now I cannot log into my account. "
            "Please help me reset it."
        ),
        true_category="account_access",
        true_priority="low",
        expected_resolution="send_password_reset_steps",
        unsafe_to_close_early=False,
        max_steps=6,
    ),
    "medium_payment_failure": TicketState(
        task_id="medium_payment_failure",
        difficulty="medium",
        title="Payment Failure",
        objective="Classify as billing, set high priority, request transaction ID, open billing review, then close safely.",
        customer_message=(
            "Hello, my payment failed yesterday but the amount seems deducted from my bank account. "
            "My subscription is still not active."
        ),
        true_category="billing",
        true_priority="high",
        required_info_request=True,
        required_missing_fields=["transaction_id"],
        expected_resolution="request_transaction_id_and_open_billing_review",
        unsafe_to_close_early=True,
        max_steps=6,
    ),
    "hard_account_takeover": TicketState(
        task_id="hard_account_takeover",
        difficulty="hard",
        title="Account Takeover",
        objective="Classify as security, set urgent priority, request identity verification, escalate to security ops, then close safely.",
        customer_message=(
            "I received login alerts from another city and my recovery email seems changed. "
            "I think someone hacked my account. Fix this now!"
        ),
        true_category="security",
        true_priority="urgent",
        required_info_request=True,
        required_missing_fields=["identity_verification"],
        expected_escalation_team="security_ops",
        unsafe_to_close_early=True,
        max_steps=6,
    ),
}


TASK_METADATA: List[TaskMetadata] = [
    TaskMetadata(
        task_id="easy_password_reset",
        difficulty="easy",
        title="Password Reset",
        objective="Classify the issue, set low priority, resolve with password reset steps, then close safely.",
    ),
    TaskMetadata(
        task_id="medium_payment_failure",
        difficulty="medium",
        title="Payment Failure",
        objective="Classify as billing, set high priority, request transaction ID, open billing review, then close safely.",
    ),
    TaskMetadata(
        task_id="hard_account_takeover",
        difficulty="hard",
        title="Account Takeover",
        objective="Classify as security, set urgent priority, request identity verification, escalate to security ops, then close safely.",
    ),
]