"""
Flask web dashboard for AWS AI Resource Cleanup.
Author: Mithin Sagar S
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, jsonify, request
from config import SETTINGS, CLEANUP_RULES
from aws.aws_session import AWSSession
from aws.ec2_manager import EC2Manager
from aws.ebs_manager import EBSManager
from aws.s3_manager import S3Manager
from aws.iam_manager import IAMManager
from aws.cloudwatch_manager import CloudWatchManager
from analyzer.idle_detector import IdleDetector
from utils.logger import log

app = Flask(__name__)

session = AWSSession(
    profile_name=SETTINGS["aws"]["profile"],
    region_name=SETTINGS["aws"]["region"],
)

ec2_mgr = EC2Manager(session)
ebs_mgr = EBSManager(session)
s3_mgr = S3Manager(session)
iam_mgr = IAMManager(session)
cw_mgr = CloudWatchManager(session)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/resources")
def resources():
    return render_template("resources.html")


@app.route("/recommendations")
def recommendations():
    return render_template("recommendations.html")


@app.route("/reports")
def reports():
    return render_template("reports.html")


@app.route("/api/resources")
def api_resources():
    try:
        data = {
            "ec2_instances": ec2_mgr.list_all_instances(),
            "s3_buckets": s3_mgr.list_buckets(),
            "ebs_snapshots": ebs_mgr.list_snapshots(),
        }
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        log.error("API error: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/idle")
def api_idle():
    try:
        detector = IdleDetector(
            ec2_mgr, ebs_mgr, iam_mgr, cw_mgr, CLEANUP_RULES["rules"]
        )
        results = detector.detect_all()
        return jsonify({"status": "ok", "data": results})
    except Exception as e:
        log.error("API error: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/health")
def api_health():
    return jsonify({"status": "healthy", "version": "1.0.0"})


if __name__ == "__main__":
    port = SETTINGS.get("dashboard", {}).get("port", 5000)
    debug = SETTINGS.get("dashboard", {}).get("debug", False)
    app.run(host="0.0.0.0", port=port, debug=debug)
