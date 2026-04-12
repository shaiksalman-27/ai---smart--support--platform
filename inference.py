import os
import requests
from openai import OpenAI

LOCAL_BASE_URL = "http://localhost:8000"

API_BASE_URL = os.environ["API_BASE_URL"].rstrip("/")
MODEL_NAME = os.environ["MODEL_NAME"]
HF_TOKEN = os.environ["HF_TOKEN"]

if not API_BASE_URL.endswith("/v1"):
    API_BASE_URL = f"{API_BASE_URL}/v1"


def llm_ping():
    client = OpenAI(
        api_key=HF_TOKEN,
        base_url=API_BASE_URL,
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": "Reply in exactly five words."
            }
        ],
        max_tokens=10,
    )

    text = response.choices[0].message.content
    if not text:
        raise RuntimeError("Empty LLM response")
    return text


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
    print("[STEP]", {"llm_proxy_call": llm_text, "api_base_url": API_BASE_URL})

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