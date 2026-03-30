cat > ~/Desktop/skynet_ops/docs/runbook.md << 'EOF'
# Ops Runbook — skynet-ops-audit-service

**Live URL:** http://3.210.77.230/health
**Instance:** i-05ebe0f279e4d427a (us-east-1)
**Image:** pushpizzaaa/skynet-ops:latest

## Quick Reference
```bash
# SSH in
ssh -i skynet-key-final.pem ec2-user@3.210.77.230

# Check container
sudo docker ps
sudo docker logs skynet-ops --tail 50

# Restart container
sudo docker restart skynet-ops

# Health check
curl http://3.210.77.230/health
```

## Scenario 1 — Service Down / Health Check Failing
```bash
# SSH in and check container
ssh -i skynet-key-final.pem ec2-user@3.210.77.230
sudo docker ps

# If not running, start it
sudo docker start skynet-ops

# If start fails, check logs
sudo docker logs skynet-ops --tail 100

# Full restart
sudo docker restart skynet-ops
```
If instance itself is down: start via AWS CLI
```bash
aws ec2 start-instances --instance-ids i-05ebe0f279e4d427a
```

## Scenario 2 — Latency Spike
```bash
# Check metrics
curl http://3.210.77.230/metrics | grep request_latency

# Check container logs for slow queries
sudo docker logs skynet-ops --tail 100 | grep -i slow

# Check CPU on instance
top

# Restart if needed
sudo docker restart skynet-ops
```
Alert threshold: avg latency > 1s on /events for 5+ minutes.

## Scenario 3 — Sudden Cost Spike
- Check AWS Console → Cost Explorer → filter by service
- Common causes: instance left running 24/7, Elastic IP unattached
- Immediate action: stop instance if not needed
```bash
aws ec2 stop-instances --instance-ids i-05ebe0f279e4d427a
```

## Scenario 4 — DB / Storage Issue
```bash
# Check disk space
ssh -i skynet-key-final.pem ec2-user@3.210.77.230
df -h

# Check SQLite file size
sudo docker exec skynet-ops ls -lh /app/events.db

# If locked, restart container
sudo docker restart skynet-ops
```
Note: SQLite is ephemeral — docker rm loses all data. Known limitation.

## Scenario 5 — Bad Deployment / Rollback
```bash
# Pull previous image using git SHA tag
sudo docker pull pushpizzaaa/skynet-ops:<PREVIOUS_SHA>
sudo docker stop skynet-ops
sudo docker rm skynet-ops
sudo docker run -d \
  --name skynet-ops \
  --restart unless-stopped \
  -p 80:8000 \
  pushpizzaaa/skynet-ops:<PREVIOUS_SHA>
curl http://localhost/health
```

## Scenario 6 — Accidental Public Exposure
```bash
# Immediately restrict security group via AWS Console
# EC2 → Security Groups → edit inbound rules
# Remove any unintended open ports

# Or via CLI — revoke a rule
aws ec2 revoke-security-group-ingress \
  --group-id <SG_ID> \
  --protocol tcp \
  --port <PORT> \
  --cidr 0.0.0.0/0
```

## Alert Thresholds
| Alert | Threshold | Rationale |
|---|---|---|
| High CPU | >80% for 10min | Runaway process or traffic spike |
| Budget warning | >$25/month | Early warning before $75 cap |
| Container restarts | >3 in 10min | Crash loop — needs investigation |
EOF