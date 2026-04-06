let latestResult = null;
let latestRecovery = null;
let issueHistory = JSON.parse(localStorage.getItem("issueHistory") || "[]");

function setDemo(type) {
    const issueInput = document.getElementById("issueInput");

    if (type === "login") {
        issueInput.value = "I cannot log in to my account and need to reset my password.";
    } else if (type === "payment") {
        issueInput.value = "My payment failed and money was deducted from my account.";
    } else if (type === "hack") {
        issueInput.value = "My phone is slow, random popups are coming, battery is draining fast, and I think it is hacked.";
    } else if (type === "crash") {
        issueInput.value = "My app is crashing and freezing again and again.";
    }
}

function startMic() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Mic input is not supported in this browser. Please use Google Chrome.");
        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
        alert("Listening... Speak your issue now.");
    };

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        document.getElementById("issueInput").value = text;
    };

    recognition.onerror = () => {
        alert("Mic permission denied or speech recognition failed.");
    };

    recognition.start();
}

function typeEffect(element, text, speed = 12) {
    element.textContent = "";
    let i = 0;

    function typing() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(typing, speed);
        }
    }

    typing();
}

function setBadge(el, value) {
    el.textContent = value;
    el.className = "badge neutral-badge";

    const text = value.toLowerCase();

    if (text.includes("high")) {
        el.classList.add("danger-badge");
    } else if (text.includes("medium") || text.includes("partially")) {
        el.classList.add("warning-badge");
    } else if (text.includes("low") || text.includes("recovered") || text.includes("optimized") || text.includes("reviewed")) {
        el.classList.add("success-badge");
    } else if (text.includes("stabilized")) {
        el.classList.add("info-badge");
    } else {
        el.classList.add("info-badge");
    }
}

function setMeter(score, riskLevel) {
    const meterBar = document.getElementById("meterBar");
    meterBar.style.width = `${score}%`;
    meterBar.className = "meter-bar";

    const text = riskLevel.toLowerCase();
    if (text.includes("high")) {
        meterBar.classList.add("meter-danger");
    } else if (text.includes("medium")) {
        meterBar.classList.add("meter-warning");
    } else {
        meterBar.classList.add("meter-success");
    }
}

function showLoading(show) {
    const loadingBar = document.getElementById("loadingBar");
    if (show) {
        loadingBar.classList.remove("hidden");
    } else {
        loadingBar.classList.add("hidden");
    }
}

function fillList(id, items) {
    const el = document.getElementById(id);
    el.innerHTML = "";

    if (!items || items.length === 0) {
        el.innerHTML = "<li>No data available.</li>";
        return;
    }

    items.forEach(item => {
        const li = document.createElement("li");
        li.textContent = item;
        el.appendChild(li);
    });
}

function saveHistoryEntry(entry) {
    issueHistory.unshift(entry);
    issueHistory = issueHistory.slice(0, 8);
    localStorage.setItem("issueHistory", JSON.stringify(issueHistory));
    renderHistory();
}

function renderHistory() {
    const historyList = document.getElementById("historyList");

    if (!historyList) return;

    if (issueHistory.length === 0) {
        historyList.innerHTML = `<p class="empty-text">No history yet.</p>`;
        return;
    }

    historyList.innerHTML = "";

    issueHistory.forEach((item, index) => {
        const card = document.createElement("div");
        card.className = "history-card";
        card.innerHTML = `
            <div class="history-top">
                <strong>Case ${index + 1}</strong>
                <span>${item.category} • ${item.risk_level}</span>
            </div>
            <div class="history-issue">${item.issue}</div>
            <div class="history-meta">
                <span>Priority: ${item.priority}</span>
                <span>Risk Score: ${item.risk_score}%</span>
            </div>
        `;
        historyList.appendChild(card);
    });
}

function clearHistory() {
    issueHistory = [];
    localStorage.removeItem("issueHistory");
    renderHistory();
}

async function analyze() {
    const issue = document.getElementById("issueInput").value.trim();

    if (!issue) {
        alert("Please enter an issue first.");
        return;
    }

    showLoading(true);

    try {
        const res = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ issue })
        });

        const data = await res.json();
        showLoading(false);

        if (!res.ok) {
            alert(data.error || "Something went wrong.");
            return;
        }

        latestResult = data;

        document.getElementById("category").textContent = data.category;
        document.getElementById("supportConfidence").textContent = `${data.support_confidence}%`;
        document.getElementById("riskScore").textContent = `${data.risk_score}%`;
        document.getElementById("securityConfidence").textContent = `${data.security_confidence}%`;

        document.getElementById("miniCategory").textContent = data.category;
        document.getElementById("miniRisk").textContent = data.risk_level;
        document.getElementById("miniScore").textContent = `${data.risk_score}%`;

        setBadge(document.getElementById("priorityBadge"), data.priority);
        setBadge(document.getElementById("riskBadge"), data.risk_level);
        setMeter(data.risk_score, data.risk_level);

        typeEffect(document.getElementById("supportText"), data.support_response);
        typeEffect(document.getElementById("securitySummary"), data.security_summary);

        fillList("supportReasons", data.support_reasons);
        fillList("detectedSignals", data.detected_signals);
        fillList("recoverySteps", data.recovery_steps);

        saveHistoryEntry({
            issue: data.issue,
            category: data.category,
            priority: data.priority,
            risk_level: data.risk_level,
            risk_score: data.risk_score
        });

    } catch (error) {
        showLoading(false);
        alert("Server error. Please check whether the backend is running.");
        console.error(error);
    }
}

async function autoRecover() {
    const issue = document.getElementById("issueInput").value.trim();

    if (!issue) {
        alert("Please enter an issue first.");
        return;
    }

    try {
        const res = await fetch("/auto-recover", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ issue })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error || "Something went wrong.");
            return;
        }

        latestRecovery = data;

        setBadge(document.getElementById("recoveryStatusBadge"), data.status);
        document.getElementById("miniRecovery").textContent = data.status;

        const fullText =
            `Status: ${data.status}\n\n` +
            `${data.actions.map((a, i) => `${i + 1}. ${a}`).join("\n")}\n\n` +
            `${data.note}`;

        typeEffect(document.getElementById("autoRecoveryBox"), fullText, 10);

    } catch (error) {
        alert("Auto recovery failed.");
        console.error(error);
    }
}

function downloadReport() {
    if (!latestResult) {
        alert("Please analyze an issue first.");
        return;
    }

    const recoveryText = latestRecovery
        ? `Auto Recovery Status: ${latestRecovery.status}
Actions:
${latestRecovery.actions.map((a, i) => `${i + 1}. ${a}`).join("\n")}
Note: ${latestRecovery.note}`
        : "Auto Recovery: Not run yet.";

    const content = `
AI SMART SUPPORT & CYBERSECURITY ASSISTANT REPORT
------------------------------------------------

Issue:
${latestResult.issue}

Support Analysis
----------------
Category: ${latestResult.category}
Priority: ${latestResult.priority}
Support Confidence: ${latestResult.support_confidence}%
Response: ${latestResult.support_response}

Why this result:
${latestResult.support_reasons.map((r, i) => `${i + 1}. ${r}`).join("\n")}

Security Analysis
-----------------
Risk Level: ${latestResult.risk_level}
Risk Score: ${latestResult.risk_score}%
Security Confidence: ${latestResult.security_confidence}%
Summary: ${latestResult.security_summary}

Detected Signals:
${latestResult.detected_signals.map((s, i) => `${i + 1}. ${s}`).join("\n")}

Recovery Steps
--------------
${latestResult.recovery_steps.map((s, i) => `${i + 1}. ${s}`).join("\n")}

${recoveryText}
`;

    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "ai_support_security_report.txt";
    a.click();

    URL.revokeObjectURL(url);
}

window.onload = () => {
    renderHistory();
};