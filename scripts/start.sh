#!/bin/bash

# CareFlow AI - Quick Start Script
# This script helps you get CareFlow AI running locally

set -e

echo "🏥 CareFlow AI - Quick Start"
echo "============================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env

    # Generate secure keys
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    SECRET_KEY_REFRESH=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

    # Update .env with generated keys
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/change-this-secret-key-in-production-use-openssl-rand-base64-32/$SECRET_KEY/" .env
        sed -i '' "s/change-this-refresh-secret-key-in-production/$SECRET_KEY_REFRESH/" .env
        sed -i '' "s/change-this-encryption-key-32-bytes-hex-exactly/$ENCRYPTION_KEY/" .env
    else
        sed -i "s/change-this-secret-key-in-production-use-openssl-rand-base64-32/$SECRET_KEY/" .env
        sed -i "s/change-this-refresh-secret-key-in-production/$SECRET_KEY_REFRESH/" .env
        sed -i "s/change-this-encryption-key-32-bytes-hex-exactly/$ENCRYPTION_KEY/" .env
    fi

    echo "✅ Generated secure keys and updated .env"
else
    echo "✅ .env file exists"
fi

# Add OPENAI_API_KEY placeholder if not set
if ! grep -q "OPENAI_API_KEY=" .env || grep -q "OPENAI_API_KEY=sk-your" .env; then
    echo ""
    echo "⚠️  OPENAI_API_KEY is not configured."
    echo "   AI features will use mock responses."
    echo "   To enable real AI, add your OpenAI API key to .env"
    echo ""
fi

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo ""
echo "📊 Running database migrations..."
docker-compose exec -T backend alembic upgrade head || echo "⚠️  Migration failed - services may still be starting..."

# Seed database
echo ""
echo "🌱 Seeding database with demo data..."
docker-compose exec -T backend python scripts/seed_db.py || echo "⚠️  Seed failed - services may still be starting..."

echo ""
echo "✅ CareFlow AI is now running!"
echo ""
echo "════════════════════════════════════════"
echo "📍 Access Points:"
echo "────────────────────────────────────────"
echo "  Frontend:      http://localhost:3000"
echo "  Backend API:   http://localhost:8000"
echo "  API Docs:      http://localhost:8000/docs"
echo "  PgAdmin:       http://localhost:5050"
echo "    (admin@careflow.ai / admin)"
echo ""
echo "════════════════════════════════════════"
echo "👤 Demo Accounts:"
echo "────────────────────────────────────────"
echo "  Admin:    admin@careflow.ai / Admin123!"
echo "  Provider: doctor@careflow.ai / Doctor123!"
echo "  Patient:  patient@example.com / Patient123!"
echo "════════════════════════════════════════"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs -f [service]"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
echo ""
