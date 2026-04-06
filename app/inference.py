import requests

BASE_URL = "http://localhost:8000"

def run():
    r = requests.post(f"{BASE_URL}/reset")
    print("RESET:", r.json())

if __name__ == "__main__":
    run()