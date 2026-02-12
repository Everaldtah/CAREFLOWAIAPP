# CareFlow AI - Deployment Guide

This guide covers deploying CareFlow AI to production.

## Prerequisites

- Docker and Docker Compose installed
- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured
- Domain name configured with DNS
- SSL certificates (or use cert-manager)

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Application
APP_NAME=CareFlow AI
APP_ENV=production
APP_URL=https://app.careflow.ai
API_URL=https://api.careflow.ai

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/careflow

# Redis
REDIS_URL=redis://:password@host:6379/0

# Security (Generate these!)
SECRET_KEY=<32+ character random string>
SECRET_KEY_REFRESH=<32+ character random string>
ENCRYPTION_KEY=<64 character hex string>

# AI Provider
OPENAI_API_KEY=sk-your-openai-api-key
LLM_MODEL=gpt-4-turbo-preview

# Email (Resend)
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=your-resend-api-key
SMTP_FROM=noreply@careflow.ai
```

### Generating Secure Keys

```bash
# Generate secret keys
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate encryption key (64 hex characters)
python -c "import secrets; print(secrets.token_hex(32))"
```

## Local Development

### Using Docker Compose

1. Copy environment file:
```bash
cp .env.example .env
# Edit .env with your values
```

2. Start all services:
```bash
docker-compose up -d
```

3. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

4. Seed database:
```bash
docker-compose exec backend python scripts/seed_db.py
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stopping Services

```bash
docker-compose down
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Production Deployment (Kubernetes)

### 1. Build and Push Images

```bash
# Backend
cd backend
docker build -t your-registry/careflow-backend:latest .
docker push your-registry/careflow-backend:latest

# Frontend
cd ../frontend
docker build -t your-registry/careflow-frontend:latest .
docker push your-registry/careflow-frontend:latest
```

### 2. Update Kubernetes Secrets

Edit `docker/kubernetes/secret.yaml` and update all values:

```bash
nano docker/kubernetes/secret.yaml
```

### 3. Deploy to Kubernetes

```bash
cd docker/kubernetes

# Apply all manifests
kubectl apply -k .

# Or apply individually
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml
kubectl apply -f backend.yaml
kubectl apply -f frontend.yaml
kubectl apply -f ingress.yaml
```

### 4. Run Database Migrations

```bash
# Port-forward to backend pod
kubectl port-forward -n careflow-ai deployment/backend 8000:8000

# In another terminal, run migrations
alembic upgrade head
```

### 5. Seed Database

```bash
# From backend directory
python scripts/seed_db.py
```

### 6. Verify Deployment

```bash
# Check pod status
kubectl get pods -n careflow-ai

# Check services
kubectl get svc -n careflow-ai

# Check ingress
kubectl get ingress -n careflow-ai

# View logs
kubectl logs -n careflow-ai deployment/backend
kubectl logs -n careflow-ai deployment/frontend
```

## Scaling

### Horizontal Pod Autoscaling

The backend and frontend deployments include HPA:

```bash
# View HPA status
kubectl get hpa -n careflow-ai

# Manually scale
kubectl scale deployment/backend -n careflow-ai --replicas=5
```

### Database Scaling

For production, consider managed PostgreSQL:
- AWS RDS
- Google Cloud SQL
- Azure Database for PostgreSQL

## Monitoring

### Health Checks

- Backend: `/health`
- Frontend: `/api/health`

### Metrics

Prometheus metrics are exposed on `/metrics` endpoint.

### Logging

Logs are output to stdout/stderr and can be viewed with:

```bash
kubectl logs -n careflow-ai deployment/backend -f
```

For production, integrate with:
- AWS CloudWatch
- Google Cloud Logging
- Datadog
- ELK Stack

## Backup & Recovery

### Database Backup

```bash
# From within the pod
kubectl exec -n careflow-ai statefulset/postgres -- pg_dump -U postgres careflow > backup.sql

# Or use pgBackRest for automated backups
```

### Database Restore

```bash
kubectl exec -i -n careflow-ai statefulset/postgres -- psql -U postgres careflow < backup.sql
```

## SSL/TLS Certificates

### Using cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod
kubectl describe pod -n careflow-ai <pod-name>

# View logs
kubectl logs -n careflow-ai <pod-name>

# Check events
kubectl get events -n careflow-ai
```

### Database Connection Issues

```bash
# Check PostgreSQL pod
kubectl get pods -n careflow-ai -l app=postgres

# Port-forward for direct access
kubectl port-forward -n careflow-ai statefulset/postgres 5432:5432

# Test connection
psql -h localhost -U postgres -d careflow
```

### Backend API Issues

```bash
# Port-forward backend
kubectl port-forward -n careflow-ai deployment/backend 8000:8000

# Test endpoint
curl http://localhost:8000/health
```

## Security Checklist

- [ ] All secrets stored in Kubernetes secrets (not in configmaps)
- [ ] TLS enabled for all external endpoints
- [ ] Database access restricted to backend pods only
- [ ] Redis password configured
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers enabled
- [ ] Pod security policies enforced
- [ ] Network policies configured
- [ ] Regular security scans scheduled

## Support

For issues or questions:
- GitHub: https://github.com/your-org/careflow-ai/issues
- Email: support@careflow.ai
