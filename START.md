# 🚀 Getting Started with FF Domination 2.0

## Quick Start (5 minutes)

### Option 1: Docker (Recommended)

1. **Start everything:**
   ```bash
   docker-compose -f docker-compose.new.yml up
   ```

2. **Access the app:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

3. **Create an account:**
   - Go to http://localhost:3000/register
   - Sign up with email
   - Start connecting leagues!

### Option 2: Local Development

**Terminal 1 - Backend:**
```bash
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd app
npm install
npm run dev
```

**Terminal 3 - PostgreSQL:**
```bash
docker run -d \
  --name ff-postgres \
  -e POSTGRES_USER=ffuser \
  -e POSTGRES_PASSWORD=ffpass \
  -e POSTGRES_DB=ff_domination \
  -p 5432:5432 \
  postgres:16
```

**Terminal 4 - Redis:**
```bash
docker run -d \
  --name ff-redis \
  -p 6379:6379 \
  redis:7-alpine
```

---

## Environment Setup

### Backend `.env`

Create `api/.env`:

```env
DATABASE_URL=postgresql+asyncpg://ffuser:ffpass@localhost:5432/ff_domination
REDIS_URL=redis://localhost:6379
SECRET_KEY=generate-a-secure-key-here
CORS_ORIGINS=["http://localhost:3000"]

# Optional - add when ready
STRIPE_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-...
```

### Frontend `.env.local`

Create `app/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=generate-another-secure-key-here
```

---

## Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "securepassword123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=securepassword123"
```

---

## Next Steps

1. **Configure Stripe** (for billing):
   - Create account at https://stripe.com
   - Get API keys from dashboard
   - Add to `.env` files
   - Set up products in Stripe dashboard

2. **Configure OpenAI** (for AI features):
   - Get API key from https://platform.openai.com
   - Add `OPENAI_API_KEY` to `api/.env`

3. **Connect a League**:
   - Sign in to the app
   - Go to Dashboard
   - Click "Connect League"
   - Enter your ESPN or Sleeper league info

4. **Try AI Features**:
   - Upgrade to Pro tier (or add OpenAI key)
   - Go to Trades section
   - Click "Analyze Trade"
   - See AI-powered insights!

---

## Troubleshooting

### Database connection failed
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Try: `docker ps` to see if container is up

### Frontend can't reach API
- Check `NEXT_PUBLIC_API_URL` matches backend port
- Verify CORS settings in `api/app/core/config.py`

### Stripe webhooks not working locally
- Use Stripe CLI for local testing:
  ```bash
  stripe listen --forward-to localhost:8000/api/v1/billing/webhook
  ```

---

## Development Workflow

1. **Make changes** to code
2. **Hot reload** handles frontend/backend updates
3. **Test** locally at http://localhost:3000
4. **Commit** when ready
5. **Deploy** to production

---

## Production Checklist

Before deploying:

- [ ] Change `SECRET_KEY` to secure random values
- [ ] Set up production database (Supabase/Neon)
- [ ] Configure Stripe production keys
- [ ] Set up error monitoring (Sentry)
- [ ] Enable HTTPS
- [ ] Set up CI/CD pipeline
- [ ] Configure domain and DNS
- [ ] Test Stripe webhooks with live endpoint

---

**Need help?** Check the main README.new.md or open an issue!
