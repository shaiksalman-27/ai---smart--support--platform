# app/security_logic.py

def analyze_security_risk(issue: str) -> dict:
    text = issue.lower()

    score = 0
    reasons = []

    signals = {
        "popup": ("Frequent popups detected from your description.", 20),
        "popups": ("Frequent popups detected from your description.", 20),
        "battery drain": ("Unusual battery drain may indicate suspicious background activity.", 15),
        "draining fast": ("Rapid battery drain can be a warning sign.", 15),
        "overheating": ("Overheating may indicate heavy background processes.", 10),
        "unknown app": ("Unknown apps can be risky.", 25),
        "unknown apps": ("Unknown apps can be risky.", 25),
        "unusual network": ("Unusual network activity can indicate compromise.", 20),
        "network usage": ("Suspicious network usage may indicate hidden activity.", 20),
        "slow": ("Sudden slowness can be a compromise signal.", 10),
        "lag": ("System lag can be a warning sign.", 10),
        "camera on": ("Unexpected camera behavior is suspicious.", 25),
        "mic on": ("Unexpected microphone behavior is suspicious.", 25),
        "microphone": ("Microphone misuse may be risky.", 15),
        "hacked": ("The report directly indicates suspected compromise.", 30),
        "hack": ("The report directly indicates suspected compromise.", 30),
        "virus": ("Possible malware indicator detected.", 30),
        "malware": ("Possible malware indicator detected.", 30),
        "suspicious": ("Suspicious behavior is mentioned in the report.", 10),
        "unauthorized": ("Unauthorized behavior may indicate account or device compromise.", 20),
        "ads": ("Unexpected ads may indicate adware or malware.", 15)
    }

    for keyword, (reason, points) in signals.items():
        if keyword in text:
            score += points
            reasons.append(reason)

    if score == 0:
        return {
            "risk_level": "Low",
            "risk_score": 10,
            "confidence": 55,
            "security_summary": "No strong hacking signals were found in the current description.",
            "detected_signals": ["No major suspicious signs detected from the text."],
        }

    if score >= 60:
        risk_level = "High"
        confidence = 88
    elif score >= 30:
        risk_level = "Medium"
        confidence = 76
    else:
        risk_level = "Low"
        confidence = 68

    return {
        "risk_level": risk_level,
        "risk_score": min(score, 100),
        "confidence": confidence,
        "security_summary": f"The system found {risk_level.lower()}-risk security indicators from the issue description.",
        "detected_signals": reasons[:5]
    }