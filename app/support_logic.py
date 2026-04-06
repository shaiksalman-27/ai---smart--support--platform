# app/support_logic.py

def analyze_support_issue(issue: str) -> dict:
    text = issue.lower()

    if any(word in text for word in ["password", "login", "log in", "sign in", "reset password", "account access"]):
        return {
            "category": "Account Access",
            "priority": "Low",
            "response": "Please use the Forgot Password option to reset your password. If the issue continues, contact support.",
            "confidence": 90,
            "reasons": [
                "The issue mentions login or password-related words.",
                "This usually matches account access problems."
            ]
        }

    elif any(word in text for word in ["payment", "transaction", "charged", "billing", "refund", "upi", "debit", "credit"]):
        return {
            "category": "Billing / Payment",
            "priority": "High",
            "response": "Please verify your payment details and transaction status. If money was debited but the service failed, escalate to billing support immediately.",
            "confidence": 88,
            "reasons": [
                "The issue contains payment or billing keywords.",
                "Payment failures are usually high-priority customer issues."
            ]
        }

    elif any(word in text for word in ["crash", "not opening", "freeze", "stuck", "bug", "error", "app issue"]):
        return {
            "category": "Application Problem",
            "priority": "Medium",
            "response": "Try restarting the app, clearing cache, and updating to the latest version. If the issue continues, collect logs and report the error.",
            "confidence": 84,
            "reasons": [
                "The issue points to app behavior problems.",
                "These issues are often caused by crashes or software bugs."
            ]
        }

    elif any(word in text for word in ["slow", "lag", "hanging", "performance", "heating", "overheating"]):
        return {
            "category": "Performance Issue",
            "priority": "Medium",
            "response": "Please close unused apps, restart the device, free storage space, and check for pending updates.",
            "confidence": 80,
            "reasons": [
                "The issue suggests device or application performance degradation."
            ]
        }

    elif any(word in text for word in ["hack", "hacked", "virus", "malware", "popup", "suspicious", "spy", "unauthorized"]):
        return {
            "category": "Security Threat",
            "priority": "High",
            "response": "This may be a security-related issue. Run a device security scan and follow the recovery steps immediately.",
            "confidence": 92,
            "reasons": [
                "The issue contains threat-related terms such as hacked or malware.",
                "Possible security compromise needs urgent attention."
            ]
        }

    else:
        return {
            "category": "General Support",
            "priority": "Medium",
            "response": "We could not map the issue to a specific category. Please provide more details for better support.",
            "confidence": 60,
            "reasons": [
                "The issue is too general or does not strongly match a known category."
            ]
        }