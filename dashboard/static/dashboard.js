/*
 * AWS AI Resource Cleanup - Dashboard JavaScript
 * Author: Mithin Sagar S
 */

document.addEventListener("DOMContentLoaded", function () {
    loadResources();
    loadIdleResources();
});

function loadResources() {
    fetch("/api/resources")
        .then(function (res) { return res.json(); })
        .then(function (json) {
            if (json.status !== "ok") return;
            var data = json.data;

            var ec2Count = document.getElementById("ec2-count");
            if (ec2Count) ec2Count.textContent = data.ec2_instances.length;

            var s3Count = document.getElementById("s3-count");
            if (s3Count) s3Count.textContent = data.s3_buckets.length;

            var ebsCount = document.getElementById("ebs-count");
            if (ebsCount) ebsCount.textContent = data.ebs_snapshots.length;
        })
        .catch(function (err) {
            console.error("Failed to load resources:", err);
        });
}

function loadIdleResources() {
    fetch("/api/idle")
        .then(function (res) { return res.json(); })
        .then(function (json) {
            if (json.status !== "ok") return;
            var data = json.data;
            var total = 0;
            for (var key in data) {
                total += data[key].length;
            }

            var idleCount = document.getElementById("idle-count");
            if (idleCount) idleCount.textContent = total;

            var details = document.getElementById("idle-details");
            if (details) {
                var html = "<ul>";
                for (var category in data) {
                    html += "<li><strong>" + category + ":</strong> " + data[category].length + " flagged</li>";
                }
                html += "</ul>";
                details.innerHTML = html;
            }
        })
        .catch(function (err) {
            console.error("Failed to load idle resources:", err);
        });
}

function generateReport(format) {
    alert("Report generation in " + format.toUpperCase() + " format will be available in the next release.");
}
