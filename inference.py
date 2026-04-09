import requests

BASE_URL = "http://localhost:8000"

def run():
    print("[START]")

    try:
        r = requests.post(f"{BASE_URL}/reset")
        print("[STEP]", r.json())

        for i in range(3):
            response = requests.post(
                f"{BASE_URL}/step",
                json={
                    "action_type": "respond",
                    "content": f"Test response {i+1}"
                }
            )
            print("[STEP]", response.json())

    except Exception as e:
        print("[STEP]", {"error": str(e)})

    print("[END]")

if __name__ == "__main__":
    run()