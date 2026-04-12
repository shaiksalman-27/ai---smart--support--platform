import os
import requests
from openai import OpenAI

LOCAL_BASE_URL = "http://localhost:8000"

API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")


def llm_ping():
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": "Reply in exactly five words."}
        ],
        max_tokens=10,
    )

    return response.choices[0].message.content


def post_json(path, payload):
    response = requests.post(f"{LOCAL_BASE_URL}{path}", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def get_json(path):
    response = requests.get(f"{LOCAL_BASE_URL}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def run_task(task_id, actions):
    reset_data = post_json("/reset", {"task_id": task_id})
    print("[STEP]", {"task_id": task_id, "reset": reset_data})

    for action_type, content in actions:
        step_data = post_json(
            "/step",
            {
                "action_type": action_type,
                "content": content,
            },
        )
        print("[STEP]", {"task_id": task_id, "action": action_type, "result": step_data})

    grader_data = get_json("/grader")
    print("[STEP]", {"task_id": task_id, "grader": grader_data})


def run():
    print("[START]")

    llm_text = llm_ping()
    print("[STEP]", {"llm_proxy_call": llm_text})

    run_task(
        "easy_password_reset",
        [
            ("classify", "account_access"),
            ("set_priority", "low"),
            ("resolve", "send_password_reset_steps"),
            ("close", ""),
        ],
    )

    run_task(
        "medium_payment_failure",
        [
            ("classify", "billing"),
            ("set_priority", "high"),
            ("ask_info", "Please share your transaction id."),
            ("resolve", "request_transaction_id_and_open_billing_review"),
            ("close", ""),
        ],
    )

    run_task(
        "hard_account_takeover",
        [
            ("classify", "security"),
            ("set_priority", "urgent"),
            ("ask_info", "Please complete identity verification."),
            ("escalate", "security_ops"),
            ("close", ""),
        ],
    )

    print("[END]")


if __name__ == "__main__":
    run()