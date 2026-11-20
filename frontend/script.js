let monitoring = false;
let totalEvents = 0;

const sessionId = crypto.randomUUID();

const testArea = document.getElementById("testArea");
const logs = document.getElementById("logs");


async function checkBackend() {

    try {

        const response = await fetch("/api/status");
        const data = await response.json();

        document.getElementById("backend").textContent =
            data.status === "Online" ? "ONLINE" : "OFFLINE";

    } catch {

        document.getElementById("backend").textContent = "OFFLINE";

    }
}


function startMonitoring() {

    monitoring = true;

    logs.textContent = "Simulation started.";

    testArea.focus();

}


function stopMonitoring() {

    monitoring = false;

    logs.textContent += "\nSimulation stopped.";
    loadAnalytics();

}



function clearLogs() {

    totalEvents = 0;

    logs.textContent = "No activity recorded yet.";

    document.getElementById("events").textContent = "0";

    document.getElementById("risk").textContent = "0%";

    document.getElementById("risk-level").textContent = "LOW RISK";

    testArea.value = "";

}


testArea.addEventListener("keydown", async function(event) {

    if (!monitoring) return;

    totalEvents++;

    document.getElementById("events").textContent = totalEvents;

    let category = "other";

    if (/^[a-z]$/i.test(event.key)) {
        category = "letter";
    }
    else if (/^[0-9]$/.test(event.key)) {
        category = "number";
    }
    else if (event.key === " ") {
        category = "space";
    }
    else if (["Shift", "Control", "Alt"].includes(event.key)) {
        category = "modifier";
    }
    else if (event.key.startsWith("Arrow") ||
             ["Enter", "Backspace", "Tab"].includes(event.key)) {
        category = "navigation";
    }

    const entry = document.createElement("div");

    entry.textContent =
        `Event ${totalEvents}: ${category}`;

    logs.appendChild(entry);

    logs.scrollTop = logs.scrollHeight;

    try {

        await fetch("/api/events", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                category: category,
                session_id: sessionId
            })

        });

    } catch (error) {

        console.error("Database error:", error);

    }

});


checkBackend();
let pieChart = null;
let barChart = null;

async function loadAnalytics() {

    try {

        const response = await fetch(`/api/analytics?session_id=${encodeURIComponent(sessionId)}`)
        const data = await response.json();

        const categories = data.categories;

        const labels = Object.keys(categories);
        const values = Object.values(categories);

        // PIE CHART

        const pieContext = document
            .getElementById("pieChart")
            .getContext("2d");

        if (pieChart) pieChart.destroy();

        pieChart = new Chart(pieContext, {

            type: "pie",

            data: {
                labels: labels,

                datasets: [{
                    data: values,
                    backgroundColor: [
                        "#38bdf8",
                        "#4ade80",
                        "#facc15",
                        "#f87171",
                        "#a78bfa"
                    ],
                    borderWidth: 2,
                    borderColor: "#162238"
                }]
            },

            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: "white"
                        }
                    }
                }
            }

        });


        // BAR CHART

        const barContext = document
            .getElementById("barChart")
            .getContext("2d");

        if (barChart) barChart.destroy();

        barChart = new Chart(barContext, {

            type: "bar",

            data: {
                labels: labels,

                datasets: [{
                    label: "Total Events",
                    data: values,
                    backgroundColor: "#38bdf8",
                    borderRadius: 6
                }]
            },

            options: {
                responsive: true,

                scales: {

                    x: {
                        ticks: {
                            color: "white"
                        },
                        grid: {
                            color: "#263650"
                        }
                    },

                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: "white",
                            precision: 0
                        },
                        grid: {
                            color: "#263650"
                        }
                    }

                },

                plugins: {
                    legend: {
                        labels: {
                            color: "white"
                        }
                    }
                }

            }

        });

    }

    catch (error) {
        console.error("Analytics loading failed:", error);
    }

}

loadAnalytics();
async function runThreatAssessment() {

    const background =
        document.getElementById("background").checked;

    const permission =
        document.getElementById("permission").checked;

    const startup =
        document.getElementById("startup").checked;

    const eventCount = totalEvents;

    const assessmentData = {

        event_count: eventCount,

        background_attempt: background,

        permission_warning: permission,

        startup_warning: startup

    };

    try {

        const response = await fetch("/api/analyze", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(assessmentData)

        });

        if (!response.ok) {
            throw new Error("Assessment request failed");
        }

        const result = await response.json();

        document.getElementById("risk-result").textContent =
            `Risk Score: ${result.risk_score}/100 — ${result.risk_level} RISK`;

        const indicatorElement =
            document.getElementById("indicator-result");

        if (result.indicators.length === 0) {

            indicatorElement.textContent =
                "No simulated suspicious indicators detected.";

        } else {

            indicatorElement.innerHTML =
                result.indicators.map(item =>

                    `<div style="margin-bottom:12px">
                        <strong>${item.name}</strong>
                        (${item.severity})
                        <br>
                        ${item.description}
                    </div>`

                ).join("");

        }

    }

    catch (error) {

        console.error(error);

        document.getElementById("risk-result").textContent =
            "Assessment failed. Check backend connection.";

    }

}
async function loadAssessmentHistory() {

    const table = document.getElementById("assessmentHistory");

    try {

        const response = await fetch("/api/assessment-history");

        const history = await response.json();

        table.innerHTML = "";

        if (history.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="4">No assessments recorded yet.</td>
                </tr>
            `;

            return;
        }

        history.forEach(item => {

            const row = document.createElement("tr");

            const riskClass = "risk-" + item.risk_level.toLowerCase();

            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.timestamp}</td>
                <td>${item.risk_score}%</td>
                <td class="${riskClass}">${item.risk_level}</td>
            `;

            table.appendChild(row);

        });

    } catch (error) {

        table.innerHTML = `
            <tr>
                <td colspan="4">Unable to load assessment history.</td>
            </tr>
        `;

        console.error(error);
    }
}
loadAssessmentHistory();