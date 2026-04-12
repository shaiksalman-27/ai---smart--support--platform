import os
import requests
from openai import OpenAI

LOCAL_BASE_URL = "http://localhost:8000"

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")


def llm_ping():
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=HF_TOKEN,
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": "Reply in one short sentence about support automation."}
        ],
        max_tokens=20,
    )

    return response.choices[0].message.content


def post_json(path, payload):
    return requests.post(f"{LOCAL_BASE_URL}{path}", json=payload, timeout=30).json()


def get_json(path):
    return requests.get(f"{LOCAL_BASE_URL}{path}", timeout=30).json()


def run_task(task_id, actions):
    reset_data = post_json("/reset", {"task_id": task_id})
    print("[STEP]", {"task_id": task_id, "reset": reset_data})

    final_step = None
    for action_type, content in actions:
        final_step = post_json(
            "/step",
            {
                "action_type": action_type,
                "content": content,
            },
        )
        print("[STEP]", {"task_id": task_id, "action": action_type, "result": final_step})

    grader_data = get_json("/grader")
    print("[STEP]", {"task_id": task_id, "grader": grader_data})

    state_data = get_json("/state")
    print("[STEP]", {"task_id": task_id, "state": state_data})

    return {
        "task_id": task_id,
        "final_reward": (final_step or {}).get("reward", {}),
        "grader": grader_data,
        "state": state_data,
    }


def run():
    print("[START]")

    try:
        llm_text = llm_ping()
        print("[STEP]", {"llm_proxy_call": llm_text})

        results = []

        results.append(
            run_task(
                "easy_password_reset",
                [
                    ("classify", "account_access"),
                    ("set_priority", "low"),
                    ("resolve", "send_password_reset_steps"),
                    ("close", ""),
                ],
            )
        )

        results.append(
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
        )

        results.append(
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
        )

        print("[STEP]", {"summary": results})

    except Exception as e:
        print("[STEP]", {"error": str(e)})

    print("[END]")


if __name__ == "__main__":
    run()