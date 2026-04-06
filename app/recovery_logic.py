# app/recovery_logic.py

def get_recovery_steps(risk_level: str) -> list:
    if risk_level == "High":
        return [
            "Disconnect the device from Wi-Fi or mobile data immediately.",
            "Do not enter passwords or banking details on this device.",
            "Uninstall any suspicious or unknown apps.",
            "Run a trusted antivirus or security scan.",
            "Change important passwords from another safe device.",
            "Enable two-factor authentication on critical accounts.",
            "Check installed apps and permissions carefully.",
            "Update the operating system and security patches.",
            "If the issue continues, back up important files and consider a factory reset."
        ]

    if risk_level == "Medium":
        return [
            "Check for unknown apps and remove anything suspicious.",
            "Review app permissions such as camera, mic, storage, and SMS.",
            "Run a trusted security scan.",
            "Update the device OS and applications.",
            "Change sensitive passwords if you notice account issues.",
            "Monitor battery, network usage, and popup behavior."
        ]

    return [
        "Keep your device updated.",
        "Install apps only from trusted sources.",
        "Use strong passwords and two-factor authentication.",
        "Monitor the device for any new suspicious behavior."
    ]