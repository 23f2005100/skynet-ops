cat > ~/Desktop/skynet_ops/docs/cost_report.md << 'EOF'
# Cost Optimization Report — skynet-ops-audit-service

## Deployment
- Cloud: AWS us-east-1
- Compute: EC2 t3.micro (Free Tier eligible)
- Storage: SQLite on EBS root volume
- Registry: Docker Hub (free)

## Monthly Cost Estimate

| Component | Cost |
|---|---|
| EC2 t3.micro (Free Tier yr 1) | $0 |
| EBS 8GB gp2 (Free Tier: 30GB) | $0 |
| SQLite (no managed DB) | $0 |
| Elastic IP (attached to running instance) | $0 |
| CloudWatch basic metrics | $0 |
| Data transfer ~200MB/month | ~$0.02 |
| **Total (Free Tier)** | **~$0.02/month** |
| **Total (after Free Tier)** | **~$8.60/month** |

Well within the $25–$75 pilot target.

## Key Cost Decisions

1. **SQLite over RDS** — saves $15–25/month. Acceptable for <2000 events/day pilot scale.
2. **No ALB** — saves $16/month. Direct port 80 access sufficient for pilot.
3. **No NAT Gateway** — saves $32/month. Instance has public IP in default VPC.
4. **Docker Hub over ECR** — saves $1–2/month.
5. **Elastic IP** — free while attached to running instance. Released on teardown.
6. **t3.micro** — correctly sized for 5k–20k req/day. No over-provisioning.

## Cost Controls

- Instance stopped outside working hours (no compute charges when stopped)
- Elastic IP released after submission (avoid $0.005/hr idle charge)
- No automated snapshots
- Single region only (no cross-region egress)
- Dev log retention: 7 days

## Common Cost Traps Accounted For

1. Idle compute — instance stopped when not in use
2. Overprovisioned DB — avoided, SQLite used
3. NAT Gateway — not used
4. Load Balancer — not used
5. Elastic IP left unattached — released on teardown
6. Cross-region traffic — single region
7. Container registry accumulation — Docker Hub free tier
8. Overprovisioned instance — t3.micro is correct size
9. Snapshots and unattached disks — none created
10. Excessive log volume — structured logs, INFO level only

## Teardown Steps
See README.md teardown section.
After submission:
- Stop instance
- Release Elastic IP
- Terminate instance
- Delete security group
EOF