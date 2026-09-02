<p align="center">
  <h1 align="center">AWS AI Resource Cleanup</h1>
  <p align="center">
    Automated detection and cleanup of unused AWS resources using Python, Boto3, and Machine Learning.
    <br />
    <strong>Author: Mithin Sagar S</strong>
    <br />
    <em>Department of Computer Science and Engineering (AI&ML), Vellore Institute of Technology, Chennai</em>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/AWS-Boto3-orange?style=flat-square&logo=amazonaws" />
  <img src="https://img.shields.io/badge/ML-scikit--learn-green?style=flat-square&logo=scikitlearn" />
  <img src="https://img.shields.io/badge/dashboard-Flask-lightgrey?style=flat-square&logo=flask" />
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square" />
</p>

---

## Overview

Cloud Infrastructure sprawl is a real problem. Developers spin up EC2 instances, create EBS snapshots, add IAM users for temporary access, and then forget about them. These orphaned resources silently inflate AWS bills and expose unused access points as security risks.

**AWS AI Resource Cleanup** solves this by automatically scanning your AWS account, identifying idle and unused resources based on configurable thresholds, and cleaning them up safely with dry-run previews, AI-powered recommendations, and detailed reporting.

This project was developed as part of a research paper presented at the **2nd International Conference on Advanced Nexus of Data and Information Technology (ICANDIT 2026)**.

---

## Features

- **Multi-Service Scanning** - EC2 instances, EBS snapshots, S3 buckets, IAM users, CloudWatch log groups, RDS instances, security groups, and key pairs
- **Configurable Thresholds** - YAML-based rules for age limits, inactivity periods, and exclusion tags
- **Dry Run Mode** - Preview all deletions before executing anything
- **AI-Powered Recommendations** - A trained Random Forest model predicts whether to keep, review, or delete each resource based on utilization metrics
- **Anomaly Detection** - Statistical outlier detection for cost spikes
- **Web Dashboard** - Flask-based UI for visualizing resources, recommendations, and reports
- **PDF and CSV Reports** - Automated report generation for audit trails
- **Scheduled Execution** - Run locally via cron or deploy as an AWS Lambda triggered by EventBridge
- **SNS Notifications** - Get alerts when cleanup runs complete
- **Protected Resources** - Tag-based exclusion prevents accidental deletion of critical infrastructure

---

## Architecture

```
                  +------------------+
                  |   main.py (CLI)  |
                  +--------+---------+
                           |
          +----------------+----------------+
          |                |                |
   +------v------+  +-----v------+  +------v------+
   | AWS Managers |  |  Analyzer  |  |  Dashboard  |
   | (ec2, s3,   |  | (idle det, |  |  (Flask UI) |
   |  ebs, iam,  |  |  rule eng, |  +-------------+
   |  cw, rds)   |  |  AI model) |
   +------+------+  +-----+------+
          |                |
   +------v----------------v------+
   |       Cleanup Engine         |
   | (dry run / live execution)   |
   +------+-----------------------+
          |
   +------v------+    +-----------+
   |  Reports    |    | Scheduler |
   | (PDF, CSV)  |    | (Lambda / |
   +-------------+    |  cron)    |
                      +-----------+
```

---

## Project Structure

```
aws-ai-resource-cleanup/
├── main.py                          # CLI entry point
├── config.py                        # Configuration loader
├── requirements.txt                 # Python dependencies
├── .gitignore
├── LICENSE
├── README.md
│
├── config/
│   ├── settings.yaml                # Thresholds, AWS profile, scheduling
│   └── cleanup_rules.json           # Rule definitions and exclusions
│
├── aws/                             # AWS service interaction layer
│   ├── aws_session.py               # Session and client factory
│   ├── ec2_manager.py               # EC2 instance operations
│   ├── ebs_manager.py               # EBS snapshot operations
│   ├── s3_manager.py                # S3 bucket operations
│   ├── iam_manager.py               # IAM user operations
│   ├── cloudwatch_manager.py        # CloudWatch log group operations
│   ├── rds_manager.py               # RDS instance operations
│   └── cost_explorer.py             # Cost analysis via AWS Cost Explorer
│
├── analyzer/                        # Resource analysis and AI
│   ├── idle_detector.py             # Cross-service idle resource detection
│   ├── rule_engine.py               # Configurable rule evaluation
│   ├── ai_recommender.py            # ML-based cleanup recommendations
│   ├── anomaly_detector.py          # Statistical anomaly detection
│   └── utilization_calculator.py    # CloudWatch metrics aggregation
│
├── cleanup/                         # Cleanup execution
│   ├── cleanup_engine.py            # Central orchestrator
│   ├── ec2_cleanup.py               # EC2 cleanup logic
│   ├── ebs_cleanup.py               # EBS cleanup logic
│   ├── s3_cleanup.py                # S3 cleanup logic
│   ├── rds_cleanup.py               # RDS cleanup logic
│   └── notification.py              # SNS notification service
│
├── dashboard/                       # Web UI
│   ├── app.py                       # Flask application
│   ├── templates/                   # HTML templates
│   └── static/                      # CSS, JS, assets
│
├── reports/                         # Report generation
│   ├── generate_report.py           # Report orchestrator
│   ├── pdf_report.py                # PDF output via ReportLab
│   └── csv_export.py                # CSV export
│
├── scheduler/                       # Automated scheduling
│   ├── lambda_handler.py            # AWS Lambda function
│   ├── eventbridge_config.json      # EventBridge rule definition
│   └── cron_scheduler.py            # Local cron-style scheduler
│
├── ml/                              # Machine learning pipeline
│   ├── dataset.csv                  # Training data
│   ├── preprocess.py                # Data cleaning and encoding
│   ├── feature_engineering.py       # Derived feature construction
│   ├── train_model.py               # Model training (Random Forest)
│   └── predict.py                   # Inference module
│
├── tests/                           # Unit tests
│   ├── test_ec2.py
│   ├── test_s3.py
│   ├── test_cleanup.py
│   └── test_ai.py
│
├── utils/                           # Shared utilities
│   ├── constants.py                 # Project-wide constants
│   ├── logger.py                    # Centralized logging
│   ├── helper.py                    # Helper functions
│   └── validators.py               # Input validation
│
├── docs/                            # Documentation and diagrams
├── screenshots/                     # UI and console screenshots
└── logs/                            # Runtime logs
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- AWS CLI configured with valid credentials (`aws configure`)
- An AWS account (Free Tier works fine for testing)

### Installation

```bash
git clone https://github.com/mithinsagar/aws-ai-resource-cleanup.git
cd aws-ai-resource-cleanup
pip install -r requirements.txt
```

### Configuration

Edit `config/settings.yaml` to set your AWS profile, region, and thresholds:

```yaml
aws:
  profile: "default"
  region: "us-east-1"

thresholds:
  ec2_stopped_days: 90
  ebs_snapshot_days: 90
  iam_inactive_days: 180
```

---

## Usage

### Scan for idle resources

```bash
python main.py --mode scan
```

### Run cleanup (dry run)

```bash
python main.py --mode cleanup
```

### Run cleanup (live execution)

```bash
python main.py --mode cleanup --live
```

### Launch the dashboard

```bash
python main.py --mode dashboard
```

Then open `http://localhost:5000` in your browser.

### Generate reports

```bash
python main.py --mode report
```

### Train the AI model

```bash
cd ml
python train_model.py
```

### Run tests

```bash
python -m pytest tests/ -v
```

---

## AI / ML Component

The project includes a machine learning pipeline that goes beyond simple threshold-based rules. A Random Forest classifier is trained on resource utilization features (CPU usage, network I/O, disk activity, age, and state) to predict one of three actions for each resource:

| Prediction | Meaning |
|---|---|
| **Keep** | Resource is actively used, leave it alone |
| **Review** | Resource shows low activity, flag for manual review |
| **Delete** | Resource is idle and safe to remove |

When no trained model is available, the system falls back to a rule-based heuristic that still provides reasonable recommendations.

---

## Scheduling

### Option A: AWS Lambda + EventBridge (Recommended for production)

Deploy `scheduler/lambda_handler.py` as a Lambda function and configure the EventBridge rule using `scheduler/eventbridge_config.json`. The default schedule runs cleanup every Sunday at 2:00 AM UTC.

### Option B: Local cron scheduler

```bash
python scheduler/cron_scheduler.py
```

This runs the cleanup at intervals defined in `settings.yaml` and keeps running in the foreground.

---

## Research Paper

This project accompanies the paper:

> **Automated AWS Resource Cleanup for Optimization of Cost and Security**
> S. Mithin Sagar, Vellore Institute of Technology, Chennai Campus
> Presented at ICANDIT 2026 (2nd International Conference on Advanced Nexus of Data and Information Technology)

---

## License

This project is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

## Author

**Mithin Sagar S**
B.Tech, AI & ML, School of Computer Science and Engineering
Vellore Institute of Technology, Chennai, India

---
