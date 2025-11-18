# FF Domination 2.0 - Modern SaaS Platform

**Your AI-Powered Fantasy Football Coach** - Win your league with AI-powered insights, trade analysis, and expert strategy.

---

## 🚀 What's New in 2.0

Complete rebuild with modern 2026 best practices:

- **Next.js 15** with App Router and Server Components
- **TypeScript** throughout for type safety
- **Tailwind CSS 4** + shadcn/ui for beautiful, accessible UI
- **FastAPI** backend with async Python 3.12
- **PostgreSQL** with async SQLAlchemy
- **Stripe** subscription billing (Free/Pro/Champion tiers)
- **Redis** caching and background jobs
- **Docker** for easy deployment

---

## 💰 Monetization

### Subscription Tiers

- **Rookie (Free)**: 1 league, basic features, 5 AI queries/month
- **Pro ($14.99/mo)**: Unlimited leagues, AI Trade Analyzer, 100 queries/month
- **Champion ($29.99/mo)**: Everything + unlimited AI, multi-team trades, BYOK

---

## 🏗️ Architecture

```
FF-Domination/
├── app/                    # Next.js 15 Frontend
│   ├── app/               # App Router pages
│   ├── components/        # React components (shadcn/ui)
│   ├── lib/               # Utilities and helpers
│   └── hooks/             # Custom React hooks
│
├── api/                   # FastAPI Backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic (Stripe, AI)
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
│
├── docker-compose.new.yml # Docker orchestration
└── REBUILD_2026_PLAN.md  # Detailed rebuild plan
```

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5.7
- **Styling**: Tailwind CSS 4
- **Components**: shadcn/ui (Radix UI primitives)
- **State**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts

### Backend
- **Framework**: FastAPI 0.115+
- **Language**: Python 3.12 (async/await)
- **Database**: PostgreSQL 16 + AsyncPG
- **ORM**: SQLAlchemy 2.0 (async)
- **Cache**: Redis 7
- **Tasks**: Celery
- **AI**: OpenAI GPT-4.5

### Infrastructure
- **Hosting**: Vercel (frontend) + Railway (backend)
- **Database**: Supabase or Neon (PostgreSQL)
- **Cache**: Upstash (Redis)
- **Payments**: Stripe
- **Monitoring**: Sentry + Axiom

---

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- Docker & Docker Compose (recommended)
- PostgreSQL 16+ (or use Docker)
- Redis (or use Docker)

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/FF-Domination.git
cd FF-Domination
```

### 2. Environment Variables

Create `.env` files:

```bash
# Frontend (app/.env.local)
cp app/.env.example app/.env.local

# Backend (api/.env)
cp api/.env.example api/.env
```

Update with your keys:
- Stripe API keys
- OpenAI API key
- Database URL
- NextAuth secret

### 3. Run with Docker (Recommended)

```bash
docker-compose -f docker-compose.new.yml up
```

This starts:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 4. Run Locally (Development)

**Backend:**
```bash
cd api
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd app
npm install
npm run dev
```

---

## 📊 Database Setup

The app automatically creates tables on startup. To run migrations manually:

```bash
cd api
alembic upgrade head
```

---

## 🎯 Core Features

### Implemented in 2.0

✅ **Authentication**
- Email/password signup and login
- OAuth with Google
- JWT-based sessions
- Role-based access control

✅ **Subscription Billing**
- Stripe Checkout for upgrades
- Customer Portal for self-service
- Usage-based billing for AI queries
- Webhook handling for subscription events

✅ **League Management**
- Connect ESPN and Sleeper leagues
- Real-time sync
- Multi-league support

✅ **AI Trade Analyzer**
- GPT-4 powered trade evaluation
- Value scoring (0-100)
- Risk assessment
- Multi-team trade discovery (Champion tier)

✅ **API Infrastructure**
- RESTful API with OpenAPI docs
- Async throughout for performance
- Redis caching
- Rate limiting by tier

### Coming Soon

🔜 Expert Draft Tool
🔜 Waiver Wire Optimizer
🔜 Real-time News Monitoring
🔜 Push Notifications
🔜 Mobile Apps (React Native)

---

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Leagues
- `GET /api/v1/leagues` - List user's leagues
- `POST /api/v1/leagues` - Connect new league
- `DELETE /api/v1/leagues/{id}` - Disconnect league

### AI
- `POST /api/v1/ai/analyze-trade` - Analyze trade (Pro+)
- `POST /api/v1/ai/draft-strategy` - Get draft strategy (Pro+)

### Billing
- `POST /api/v1/billing/create-checkout-session` - Start subscription
- `POST /api/v1/billing/create-portal-session` - Manage subscription
- `POST /api/v1/billing/webhook` - Stripe webhooks

Full API documentation: http://localhost:8000/api/docs

---

## 🧪 Testing

```bash
# Backend tests
cd api
pytest

# Frontend tests
cd app
npm test

# E2E tests
npm run test:e2e
```

---

## 📦 Deployment

### Vercel (Frontend)

```bash
cd app
vercel deploy --prod
```

### Railway (Backend)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
cd api
railway up
```

### Environment Variables

Set these in your deployment platforms:

**Frontend (Vercel):**
- `NEXT_PUBLIC_API_URL`
- `NEXTAUTH_URL`
- `NEXTAUTH_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

**Backend (Railway):**
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `OPENAI_API_KEY`

---

## 🔒 Security

- HTTPS everywhere (TLS 1.3)
- JWT tokens in httpOnly cookies
- CSRF protection
- Rate limiting
- SQL injection prevention (parameterized queries)
- XSS protection
- Encrypted credentials at rest
- Stripe handles all payment data (PCI DSS compliant)

---

## 📈 Monitoring

- **Error Tracking**: Sentry
- **Performance**: Vercel Analytics
- **Logs**: Axiom or Better Stack
- **Uptime**: Custom health checks

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

Proprietary - All rights reserved

---

## 🎉 Credits

Built with modern tools:
- [Next.js](https://nextjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Stripe](https://stripe.com/)
- [OpenAI](https://openai.com/)

---

## 📧 Support

- Email: support@ffdomination.com
- Documentation: https://docs.ffdomination.com
- Discord: https://discord.gg/ffdomination

---

**Ready to dominate your fantasy league? Let's go!** 🏆
