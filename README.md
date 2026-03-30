cat > ~/Desktop/skynet_ops/README.md << 'EOF'
# skynet-ops-audit-service

A minimal operational audit event service for the AIRMAN Skynet ecosystem.
Stores and retrieves audit events for flight training academy tenants.

---

## Local Setup

### Prerequisites
- Docker
- Python 3.10+

### Run with Docker
```bash
cp .env.example .env
docker build -t skynet-ops .
docker run -d \
  --name skynet-ops \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  skynet-ops
```

### Run without Docker
```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Test Endpoints
```bash
# Health
curl http://localhost:8000/health

# POST event
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{"type":"roster_update","tenantId":"academy_001","severity":"info","message":"Test event","source":"skynet-api"}'

# GET events
curl "http://localhost:8000/events?tenantId=academy_001&severity=info"

# Validation rejection (returns 400)
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{"type":"x","tenantId":"","severity":"invalid","message":"","source":"x"}'

# metrics-demo
curl "http://localhost:8000/metrics-demo"
curl "http://localhost:8000/metrics-demo?mode=slow"
curl "http://localhost:8000/metrics-demo?mode=error"
curl "http://localhost:8000/metrics-demo?mode=burst"

# Prometheus metrics
curl http://localhost:8000/metrics
```

---

## Cloud Deployment (AWS EC2 — Manual)

Service is deployed on AWS EC2 t3.micro (us-east-1, Free Tier).
Live URL: http://3.210.77.230/health

### Deployment steps used
1. Launched EC2 t3.micro instance (Amazon Linux 2, us-east-1)
2. Configured security group: ports 22 (SSH) and 80 (HTTP)
3. Allocated Elastic IP 3.210.77.230 and associated to instance
4. SSH into instance, installed Docker
5. Pulled image from Docker Hub: pushpizzaaa/skynet-ops:latest
6. Ran container with restart policy
```bash
# On EC2 instance
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo docker pull pushpizzaaa/skynet-ops:latest
sudo docker run -d \
  --name skynet-ops \
  --restart unless-stopped \
  -p 80:8000 \
  -e APP_ENV=dev \
  -e LOG_LEVEL=INFO \
  -e SERVICE_NAME=skynet-ops-audit-service \
  pushpizzaaa/skynet-ops:latest
```

### Teardown
```bash
# Stop container
ssh -i ~/.ssh/id_rsa ec2-user@3.210.77.230
sudo docker stop skynet-ops

# Stop instance (AWS CLI)
aws ec2 stop-instances --instance-ids i-05ebe0f279e4d427a

# Release Elastic IP (to avoid charges)
aws ec2 disassociate-address --association-id eipassoc-089b6603f18279e2b
aws ec2 release-address --allocation-id eipalloc-08557e17a26c1537d

# Terminate instance
aws ec2 terminate-instances --instance-ids i-05ebe0f279e4d427a
```

---

## CI/CD (Level 2 — Option B)

GitHub Actions pipeline: `.github/workflows/ci-cd.yml`

| Job | Trigger | What it does |
|---|---|---|
| `test` | Every push/PR | Smoke tests all endpoints |
| `build-and-push` | Push to main | Builds and pushes Docker image to Docker Hub |
| `deploy` | After build | SSHes into EC2, pulls new image, restarts container |

### Required GitHub Secrets
| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | pushpizzaaa |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `EC2_HOST` | 3.210.77.230 |
| `EC2_SSH_KEY` | Contents of ~/.ssh/id_rsa |

---

## Project Structure
```
skynet_ops/
├── app/
│   ├── main.py        # FastAPI app, all endpoints
│   ├── models.py      # SQLAlchemy Event model
│   └── database.py    # SQLite engine and session
├── .github/
│   └── workflows/
│       └── ci-cd.yml  # CI/CD pipeline
├── docs/
│   ├── cost_report.md
│   └── runbook.md
├── Dockerfile
├── .dockerignore
├── .env.example
├── requirements.txt
├── submission_checklist.md
└── README.md
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `dev` | Environment name |
| `SERVICE_NAME` | `skynet-ops-audit-service` | Shown in /health |
| `LOG_LEVEL` | `INFO` | Log verbosity |
EOF