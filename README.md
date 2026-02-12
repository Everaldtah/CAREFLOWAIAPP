# CareFlow AI — Autonomous Clinic Operations Platform

A production-ready, multi-tenant healthcare AI SaaS that automates patient triage, scheduling, clinical documentation, and billing operations.

## 🏥 Features

- **AI-Powered Triage**: Symptom intake with urgency classification
- **Smart Scheduling**: Calendar optimization with no-show prediction
- **Clinical Scribe**: Automatic SOAP note generation from transcripts
- **Follow-Up Management**: Automated reminders and escalation detection
- **Billing Automation**: ICD-10/CPT code suggestions and claim validation
- **EHR Integration**: Ready for healthcare system integration
- **HIPAA/GDPR Ready**: Built-in compliance architecture

## 🏗️ Architecture

```
careflow-ai/
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── api/      # REST API endpoints
│   │   ├── core/     # Security, config, dependencies
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   ├── agents/   # AI agent orchestration
│   │   └── utils/    # Utilities
│   ├── alembic/      # Database migrations
│   └── tests/        # Backend tests
├── frontend/         # Next.js TypeScript frontend
│   ├── src/
│   │   ├── app/      # App Router pages
│   │   ├── components/  # React components
│   │   ├── lib/      # Utilities and API client
│   │   └── types/    # TypeScript types
├── docker/           # Kubernetes manifests
└── scripts/          # Deployment and utility scripts
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Local Development

1. **Clone and setup:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Run database migrations:**
```bash
docker-compose exec backend alembic upgrade head
```

4. **Seed database:**
```bash
docker-compose exec backend python scripts/seed_db.py
```

5. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔐 Security Features

- AES-256 encryption at rest
- TLS 1.3 in transit
- JWT-based authentication with refresh tokens
- Role-Based Access Control (RBAC)
- Multi-factor authentication ready
- Complete audit logging of PHI access
- Tenant isolation at database level

## 🧪 Running Tests

```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test

# End-to-end tests
docker-compose exec e2e npm test
```

## 📦 Production Deployment

### Docker Compose (Simple)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes (Recommended)

```bash
kubectl apply -f docker/kubernetes/
# Or use Helm
helm install careflow-ai docker/helm/
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete production deployment guide.

## 📊 Environment Variables

Key variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | Required |
| `REDIS_URL` | Redis connection | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `LLM_PROVIDER` | AI provider (openai/anthropic) | openai |
| `ENCRYPTION_KEY` | AES-256 encryption key | Required |

## 🏥 HIPAA/GDPR Compliance

This application is designed to support healthcare compliance:

- **Data Minimization**: Only collect necessary PHI
- **Right to Access**: Patient data export functionality
- **Right to Delete**: Patient data deletion capability
- **Audit Trail**: Complete logging of all PHI access
- **Breach Detection**: Automated security monitoring

## 🤝 Contributing

Contributions are welcome. Please ensure all tests pass and follow the coding standards defined in the project.

## 📄 License

Proprietary - All rights reserved

## 🆘 Support

For support, contact support@careflow.ai

---

**Built with ❤️ for Healthcare Innovation**
