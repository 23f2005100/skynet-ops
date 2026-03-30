cat > ~/Desktop/skynet_ops/submission_checklist.md << 'EOF'
# AIRMAN Skynet Cloud Ops Intern Assessment — Submission Checklist

## 1) Candidate & Submission Info
- **Name:** [YOUR NAME]
- **Email:** [YOUR EMAIL]
- **Chosen Cloud Platform:** AWS
- **Assessment Level Submitted:** Level 1 + Level 2
- **Level 2 Option Chosen:** Option B — CI/CD for Safe Cloud Deployments
- **GitHub Repo Link:** [YOUR REPO URL]
- **Demo Video Link:** [OPTIONAL]
- **Submission Date (UTC):** 2026-03-30

## 2) What I Implemented

### Level 1
- [x] Mini service (/health, POST /events, GET /events, GET /metrics-demo)
- [x] Dockerized service
- [x] Cloud deployment — EC2 t3.micro, us-east-1, Docker, Elastic IP
- [x] Infrastructure — manual EC2 provisioning with security groups
- [x] Cost optimization report (docs/cost_report.md)
- [x] Observability — Prometheus /metrics, structured logs, configurable LOG_LEVEL
- [x] Security/secrets — .env gitignored, .env.example provided
- [x] Ops runbook (docs/runbook.md) — 6 scenarios covered
- [x] README with setup + teardown

### Level 2
- [x] Option B — CI/CD for Safe Cloud Deployments (.github/workflows/ci-cd.yml)

## 3) Repository Structure

- Service path: app/
- Main entry file: app/main.py
- Local run command: uvicorn app.main:app --host 0.0.0.0 --port 8000
- Dockerfile path: Dockerfile
- .dockerignore path: .dockerignore
- README path: README.md
- Cost report path: docs/cost_report.md
- Runbook path: docs/runbook.md
- Level 2 path: .github/workflows/ci-cd.yml

## 4) Local Run Instructions

### Prerequisites
- Docker installed
- Python 3.10+

### Local Setup
```bash
git clone <repo-url>
cd skynet_ops
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Test Endpoints
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{"type":"roster_update","tenantId":"academy_001","severity":"info","message":"Test","source":"skynet-api"}'
curl "http://localhost:8000/events?tenantId=academy_001"
```

## 5) API Endpoint Checklist
- [x] GET /health works
- [x] POST /events stores an event
- [x] GET /events returns events
- [x] Validation rejects bad payloads (400)
- [x] GET /metrics-demo implemented (modes: success, slow, error, burst)

## 6) Cloud Deployment Summary

### Deployment Type
- [x] Real cloud deployment (AWS EC2 t3.micro, us-east-1)
- Live URL: http://3.210.77.230/health

### Cloud Services Used
- Compute: EC2 t3.micro (Free Tier)
- Storage/DB: SQLite on EBS root volume
- Networking: Default VPC, Elastic IP 3.210.77.230, Security Group (ports 22, 80)
- Logging: Structured application logs, Prometheus /metrics endpoint
- Secrets: .env gitignored, passed as Docker -e flags
- Budgeting: Manual cost monitoring via AWS Cost Explorer
- Container Registry: Docker Hub (pushpizzaaa/skynet-ops)
- IAM: IAM user with programmatic access for AWS CLI

### Why I chose this architecture
- t3.micro is Free Tier eligible — zero compute cost for 12 months
- SQLite eliminates RDS cost (~$20/month saved) — fine for pilot scale
- No ALB or NAT Gateway — saves ~$48/month, direct port 80 works for pilot
- Elastic IP ensures stable endpoint that survives reboots
- Docker Hub free tier avoids ECR costs

### Pilot Cost-Awareness Notes
- Estimated cost: ~$0.02/month on Free Tier
- Instance stopped outside working hours to stay within free tier
- Elastic IP released after submission to avoid idle charges
- All teardown steps documented in README

## 7) Cost Optimization Report
See docs/cost_report.md
- [x] Monthly estimate included
- [x] Assumptions documented  
- [x] Component-wise breakdown included
- [x] 10 cost traps identified and addressed

## 8) Observability & Monitoring

### Logging
- [x] Structured logs via Python logging module
- [x] LOG_LEVEL configurable via environment variable
- [x] Sample log: INFO: Event created: evt_abc | tenant: academy_001 | severity: info

### Metrics
- [x] request_latency_seconds (Prometheus Histogram)
- [x] error_count (Prometheus Counter, per endpoint)
- [x] request_count (Prometheus Counter, per endpoint)
- [x] GET /health as health signal

### Alerts
- Alert #1: Container restart count > 3 in 10 min — crash loop indicator
- Alert #2: Monthly AWS spend > $25 — early cost warning

### Evidence
- [x] Live /metrics endpoint: http://3.210.77.230/metrics
- [x] Live /health endpoint: http://3.210.77.230/health

## 9) Security / Secrets / IAM
- [x] .env gitignored — no secrets in repo
- [x] .env.example included
- [x] Secrets passed as Docker -e flags at runtime
- [x] Security group restricts inbound to ports 22 and 80 only
- [x] IAM user used for AWS CLI (not root account)
- [x] Known limitation: no HTTPS in pilot — production would add TLS

## 10) Ops Runbook
- Runbook path: docs/runbook.md
- [x] Service down / health checks failing
- [x] Latency spike
- [x] Sudden cost spike
- [x] DB/storage issue
- [x] Bad deployment / rollback
- [x] Accidental public exposure

## 11) IaC Validation
- IaC tool: None used — manual EC2 provisioning via AWS Console and CLI
- Teardown steps fully documented in README.md

## 12) Known Limitations / Trade-offs
1. SQLite is ephemeral — docker rm loses all data. Production needs EBS volume mount or RDS.
2. No HTTPS — plain HTTP. Production needs TLS via ALB + ACM.
3. No authentication — endpoints are open. Production needs API key or gateway.
4. Single instance, no HA — one t3.micro. Acceptable for 99.0% pilot SLA.
5. Manual deployment — no Terraform used. Infrastructure provisioned via AWS CLI and Console.

## 13) AI Tool Usage Disclosure
- [x] Claude (claude.ai)

### What I used AI for
- Generating README, cost report, runbook, submission checklist drafts
- Generating GitHub Actions CI/CD pipeline
- Code review of main.py against the spec

### What I manually verified / tested
- All endpoints tested live against http://3.210.77.230
- Docker build and push to Docker Hub
- EC2 instance setup, Docker installation, container deployment
- Elastic IP allocation and association

## 14) Final Notes
- SQLite chosen deliberately for pilot scale — eliminates ~$20/month DB cost
- Service running live on AWS EC2 at http://3.210.77.230/health
- Elastic IP ensures stable URL that survives reboots
- CI/CD pipeline automates test → build → deploy on every push to main
EOF