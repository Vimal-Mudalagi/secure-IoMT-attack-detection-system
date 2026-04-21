let chart;
let lastAlertTimestamp = null;  // 🔐 prevents repeated alerts

async function fetchData() {
    const res = await fetch("/data");
    const data = await res.json();

    const tbody = document.getElementById("table-body");
    tbody.innerHTML = "";

    let labels = [];
    let values = [];

    let tamperedDetected = false;

    data.reverse().forEach(row => {

        // 🔐 Detect tampered (but don't spam)
        if (row.status === "TAMPERED") {
            tamperedDetected = true;

            // only alert once per new event
            if (row.timestamp !== lastAlertTimestamp) {
                lastAlertTimestamp = row.timestamp;
                showAlert("⚠️ Tampered Data Detected!");
            }
        }

        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${row.device}</td>
            <td>${row.heart_rate || "-"}</td>
            <td class="${getStatusClass(row.status)}">${row.status}</td>
            <td>${row.timestamp}</td>
        `;

        tbody.appendChild(tr);

        if (row.heart_rate) {
            labels.push(row.timestamp);
            values.push(row.heart_rate);
        }
    });

    updateChart(labels, values);
}

// 🔥 Better status colors
function getStatusClass(status) {
    if (status === "VALID") return "valid";
    if (status === "TAMPERED") return "tampered";
    if (status === "REPLAY") return "replay";
    return "error";
}

// 🔥 Clean UI alert (no popup spam)
function showAlert(message) {
    let alertBox = document.getElementById("alert-box");

    if (!alertBox) {
        alertBox = document.createElement("div");
        alertBox.id = "alert-box";
        alertBox.style.background = "red";
        alertBox.style.color = "white";
        alertBox.style.padding = "10px";
        alertBox.style.margin = "10px";
        alertBox.style.fontWeight = "bold";
        document.body.prepend(alertBox);
    }

    alertBox.innerText = message;
}

// 📈 Chart
function updateChart(labels, values) {
    if (!chart) {
        const ctx = document.getElementById("chart").getContext("2d");

        chart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Heart Rate",
                    data: values,
                    borderWidth: 2,
                    tension: 0.3
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
                },
                scales: {
                    x: {
                        ticks: { color: "white" }
                    },
                    y: {
                        ticks: { color: "white" }
                    }
                }
            }
        });
    } else {
        chart.data.labels = labels;
        chart.data.datasets[0].data = values;
        chart.update();
    }
}

// 📄 Export
function exportPDF() {
    window.open("/export");
}

// ⚠️ Attack button
function simulateAttack() {
    fetch("/attack");
}

// 🔁 Auto refresh
setInterval(fetchData, 2000);
fetchData();