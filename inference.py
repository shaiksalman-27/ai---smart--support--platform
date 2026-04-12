import os
import requests

LOCAL_BASE_URL = "http://localhost:8000"

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")


def call_llm_proxy():
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": "Reply with one short sentence about customer support."}
        ],
        "max_tokens": 30,
    }

    res = requests.post(
        f"{API_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    return {
        "status_code": res.status_code,
        "body": res.json(),
    }


def post_step(action_type, content):
    return requests.post(
        f"{LOCAL_BASE_URL}/step",
        json={
            "action_type": action_type,
            "content": content,
        },
        timeout=30,
    ).json()


def run_task(task_id, actions):
    print("[START]")
    reset_res = requests.post(
        f"{LOCAL_BASE_URL}/reset",
        json={"task_id": task_id},
        timeout=30,
    )
    print("[STEP]", {"task": task_id, "reset": reset_res.json()})

    for action_type, content in actions:
        step_res = post_step(action_type, content)
        print("[STEP]", {"task": task_id, "action": action_type, "result": step_res})

    state_res = requests.get(f"{LOCAL_BASE_URL}/state", timeout=30).json()
    print("[STEP]", {"task": task_id, "state": state_res})
    print("[END]")


def run():
    print("[START]")

    try:
        llm_result = call_llm_proxy()
        print("[STEP]", {"llm_proxy": llm_result})

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

    except Exception as e:
        print("[STEP]", {"error": str(e)})

    print("[END]")


if __name__ == "__main__":
    run()