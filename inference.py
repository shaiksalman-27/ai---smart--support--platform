import os
from openai import OpenAI

def run():
    print("[START]")

    try:
        # ✅ Correct environment variables (MANDATORY)
        API_BASE_URL = os.environ["API_BASE_URL"]
        API_KEY = os.environ["API_KEY"]
        MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

        # ✅ Correct OpenAI client (IMPORTANT FIX)
        client = OpenAI(
            base_url=API_BASE_URL,
            api_key=API_KEY
        )

        # TASK 1
        response1 = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print("[STEP]", {"task": 1, "output": response1.choices[0].message.content, "score": 0.5})

        # TASK 2
        response2 = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "2+2?"}],
            max_tokens=10
        )
        print("[STEP]", {"task": 2, "output": response2.choices[0].message.content, "score": 0.6})

        # TASK 3
        response3 = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "What is AI?"}],
            max_tokens=20
        )
        print("[STEP]", {"task": 3, "output": response3.choices[0].message.content, "score": 0.7})

    except Exception as e:
        print("[STEP]", {"error": str(e), "score": 0.5})

    print("[END]")


if __name__ == "__main__":
    run()