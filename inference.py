def reset():
    return {"message": "Environment reset successful"}

def step(action):
    return {
        "observation": "Action received",
        "reward": 1,
        "done": True,
        "info": {}
    }

def state():
    return {"state": "running"}