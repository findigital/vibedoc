# 🚀 VibeDoc SaaS - Quick Start Guide

Welcome to VibeDoc SaaS! This guide will help you get your SaaS application up and running in minutes.

## What's New in SaaS Edition?

✅ **User Authentication** - Secure signup, login, and session management
✅ **Subscription Tiers** - Free, Pro, and Enterprise plans
✅ **Project Management** - Save and manage your generated plans
✅ **Usage Tracking** - Monitor resource consumption
✅ **RESTful API** - Full programmatic access
✅ **Payment Integration** - Stripe for subscriptions
✅ **Admin Dashboard** - System monitoring and management

---

## Installation (Local Development)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your keys
nano .env
```

**Required Configuration:**
```env
SILICONFLOW_API_KEY=your_siliconflow_key_here
JWT_SECRET_KEY=your_jwt_secret_here
```

**Generate JWT Secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Initialize Database

```bash
python init_saas.py
```

This will:
- Create database tables
- Set up an admin user
- Optionally create sample users

### 4. Run the Application

**Option A: Web Interface Only**
```bash
python saas_app.py
```
Access at: http://localhost:7860

**Option B: Web + API Server**
```bash
# Terminal 1: Web Interface
python saas_app.py

# Terminal 2: API Server
python api.py
```
- Web: http://localhost:7860
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Installation (Docker)

### Prerequisites
- Docker
- Docker Compose

### Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your keys

# 2. Start all services
docker-compose up -d

# 3. Initialize database (first time only)
docker-compose exec web python init_saas.py
```

**Services Running:**
- Web Interface: http://localhost:7860
- API Server: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f web
docker-compose logs -f api
```

---

## First Steps

### 1. Create Your Admin Account

When running `init_saas.py`, you'll be prompted to create an admin account:

```
Email: admin@example.com
Username: admin
Full Name: Admin User
Password: ******** (min 8 characters)
```

### 2. Login to Web Interface

1. Go to http://localhost:7860
2. Click "Login" tab
3. Enter your credentials
4. Start generating development plans!

### 3. Try the API

**Get Access Token:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_username": "admin@example.com",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {...}
}
```

**Generate a Plan:**
```bash
curl -X POST http://localhost:8000/plans/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Build a fitness tracking app with AI coaching"
  }'
```

---

## Subscription Tiers

### Free Tier ($0/month)
- 5 AI-generated plans/month
- 3 saved projects
- 10 exports/month
- All export formats

### Pro Tier ($19.99/month)
- 50 AI-generated plans/month
- 20 saved projects
- 200 exports/month
- Priority support
- API access
- Custom templates

### Enterprise Tier ($99.99/month)
- **Unlimited** everything
- 24/7 support
- Team collaboration
- Custom AI tuning
- SSO integration
- Dedicated account manager

---

## Key Features

### 1. Plan Generation
- Enter your product idea
- Add reference URLs (optional)
- Get complete development plan in 60-180 seconds
- Includes architecture, tech stack, timeline, and AI prompts

### 2. Project Management
- Save generated plans as projects
- Organize with tags
- Mark favorites
- Track versions
- Quick search

### 3. Export Options
- **Markdown** (.md) - GitHub-friendly
- **Word** (.docx) - Business docs
- **PDF** (.pdf) - Professional proposals
- **HTML** (.html) - Web sharing

### 4. Admin Dashboard
- System statistics
- User management
- Subscription breakdown
- Usage analytics

---

## Configuration Options

### Database

**SQLite (Default - Development):**
```env
DATABASE_URL=sqlite:///vibedoc.db
```

**PostgreSQL (Production):**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/vibedoc
```

### Payment Integration (Optional)

To enable Stripe payments:

```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_ENTERPRISE=price_...
```

See [SAAS_GUIDE.md](SAAS_GUIDE.md#payment-integration) for detailed Stripe setup.

---

## File Structure

```
vibedoc/
├── saas_app.py              # Main SaaS web application
├── api.py                   # RESTful API server
├── models.py                # Database models
├── auth.py                  # Authentication & sessions
├── database.py              # Database utilities
├── payment.py               # Stripe integration
├── init_saas.py             # Database initialization
├── requirements.txt         # Dependencies (updated for SaaS)
├── .env.example             # Environment template
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Multi-service deployment
├── SAAS_GUIDE.md           # Comprehensive SaaS guide
└── SAAS_QUICKSTART.md      # This file
```

---

## Troubleshooting

### "Database not found"
```bash
python init_saas.py
```

### "Authentication failed"
Check your JWT secret is set:
```bash
echo $JWT_SECRET_KEY
```

### "Usage limit reached"
- Check your subscription tier
- View usage in Subscription tab
- Upgrade for higher limits

### "API connection refused"
Make sure API server is running:
```bash
python api.py
```

---

## Next Steps

1. **Read Full Documentation**: [SAAS_GUIDE.md](SAAS_GUIDE.md)
2. **Explore API**: http://localhost:8000/docs
3. **Set Up Payments**: Configure Stripe (optional)
4. **Deploy to Production**: See deployment guide
5. **Customize**: Modify templates and pricing

---

## Support

- **Documentation**: [SAAS_GUIDE.md](SAAS_GUIDE.md)
- **API Reference**: http://localhost:8000/docs
- **Issues**: https://github.com/YourUsername/VibeDoc/issues
- **Discussions**: https://github.com/YourUsername/VibeDoc/discussions

---

## License

MIT License - See [LICENSE](LICENSE) file

---

**🎉 Welcome to VibeDoc SaaS! Start building amazing products with AI assistance.**

Made with ❤️ by the VibeDoc Team
