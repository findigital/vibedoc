# 🚀 VibeDoc SaaS Guide

Complete guide for deploying and using VibeDoc as a full-featured SaaS application.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Features](#features)
4. [Architecture](#architecture)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [API Documentation](#api-documentation)
8. [Payment Integration](#payment-integration)
9. [Admin Guide](#admin-guide)

---

## Overview

VibeDoc SaaS is a full-featured Software-as-a-Service platform for AI-powered product planning and development documentation. It includes:

- **User Authentication** - Secure signup, login, and session management
- **Subscription Tiers** - Free, Pro, and Enterprise plans with usage limits
- **Project Management** - Save, organize, and manage generated plans
- **Usage Tracking** - Monitor and limit resource consumption per tier
- **RESTful API** - Full programmatic access with authentication
- **Payment Processing** - Stripe integration for subscriptions
- **Admin Dashboard** - System monitoring and user management

---

## Quick Start

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YourUsername/VibeDoc.git
cd VibeDoc

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env and add your API keys

# 4. Initialize the database
python init_saas.py

# 5. Run the SaaS application
python saas_app.py
```

### First Time Setup

The `init_saas.py` script will:

1. Create database tables
2. Set up an admin user
3. Optionally create sample users for testing

Follow the prompts to create your admin account.

### Access the Application

- **Web Interface**: http://localhost:7860
- **API Docs**: http://localhost:8000/docs (if running API server)

---

## Features

### 1. User Authentication

**Signup**
- Email-based registration
- Password validation (min 8 characters)
- Unique username and email
- Email verification (optional)
- Automatic Free tier subscription

**Login**
- Login with email or username
- JWT token-based authentication
- Secure password hashing with bcrypt
- Session management

**API Keys**
- Auto-generated for each user
- Use for programmatic API access
- Regenerate from user settings

### 2. Subscription Tiers

#### Free Tier ($0/month)
- 5 AI-generated plans per month
- 3 saved projects
- 10 exports per month
- Basic support
- All export formats

#### Pro Tier ($19.99/month)
- 50 AI-generated plans per month
- 20 saved projects
- 200 exports per month
- Priority support
- Advanced editing features
- Custom templates
- API access

#### Enterprise Tier ($99.99/month)
- Unlimited AI-generated plans
- Unlimited projects
- Unlimited exports
- 24/7 priority support
- Team collaboration (coming soon)
- Custom AI model fine-tuning
- Full API access
- SSO integration
- Dedicated account manager

### 3. Project Management

**Save Plans**
- Save generated development plans
- Organize by tags
- Mark favorites
- Version tracking

**Load & Edit**
- Access saved projects
- Edit and update plans
- Track modification history

**Export**
- Multiple formats: Markdown, Word, PDF, HTML
- Export count tracking per subscription tier

### 4. Usage Tracking

**Per-User Tracking**
- Plan generation count
- Project creation count
- Export count
- Processing time metrics
- Token consumption

**Analytics**
- User usage statistics
- Success/failure tracking
- Performance monitoring

### 5. RESTful API

**Authentication**
- JWT token-based
- API key authentication
- Secure endpoints

**Endpoints**
- `/auth/signup` - Register new user
- `/auth/login` - User login
- `/plans/generate` - Generate development plan
- `/projects` - CRUD operations for projects
- `/subscription` - View subscription details

See [API Documentation](#api-documentation) for details.

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────┐
│         Web Interface (Gradio)              │
│  • User Authentication                      │
│  • Plan Generation                          │
│  • Project Management                       │
│  • Subscription Dashboard                   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          RESTful API (FastAPI)              │
│  • JWT Authentication                       │
│  • Rate Limiting                            │
│  • CRUD Operations                          │
│  • Webhook Handlers                         │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Business Logic Layer                │
│  • AuthService                              │
│  • SubscriptionService                      │
│  • ProjectService                           │
│  • PaymentService                           │
│  • UsageTrackingService                     │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│       Database Layer (SQLAlchemy)           │
│  • User                                     │
│  • Subscription                             │
│  • Project                                  │
│  • UsageLog                                 │
│  • Export                                   │
└─────────────────────────────────────────────┘
```

### Database Schema

**Users Table**
- id, email, username, password_hash
- api_key, is_admin, email_verified
- created_at, updated_at, last_login

**Subscriptions Table**
- id, user_id, tier, status
- plan_generation_limit, project_limit, export_limit
- plans_generated, projects_created, exports_made
- stripe_customer_id, stripe_subscription_id
- current_period_start, current_period_end

**Projects Table**
- id, user_id, title, description
- generated_plan, reference_urls
- is_favorite, tags, version
- created_at, updated_at

**UsageLogs Table**
- id, user_id, action_type
- processing_time, tokens_consumed
- success, error_message, created_at

---

## Configuration

### Environment Variables

Required:
```env
SILICONFLOW_API_KEY=your_key           # AI model access
JWT_SECRET_KEY=your_secret             # Session security
```

Database:
```env
DATABASE_URL=sqlite:///vibedoc.db      # SQLite (default)
# DATABASE_URL=postgresql://...        # PostgreSQL (production)
```

Stripe (optional):
```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_ENTERPRISE=price_...
```

Application:
```env
PORT=7860
ENVIRONMENT=production
LOG_LEVEL=INFO
SESSION_TIMEOUT_HOURS=24
```

### Database Configuration

**SQLite (Development)**
```python
DATABASE_URL=sqlite:///vibedoc.db
```

**PostgreSQL (Production)**
```python
DATABASE_URL=postgresql://user:password@localhost:5432/vibedoc
```

---

## Deployment

### Local Development

```bash
# Initialize database
python init_saas.py

# Run web interface
python saas_app.py

# Run API server (separate terminal)
python api.py
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize database on first run
RUN python init_saas.py --auto

EXPOSE 7860 8000

# Run both web and API
CMD ["sh", "-c", "python saas_app.py & python api.py"]
```

Build and run:
```bash
docker build -t vibedoc-saas .
docker run -p 7860:7860 -p 8000:8000 \
  -e SILICONFLOW_API_KEY=your_key \
  -e JWT_SECRET_KEY=your_secret \
  vibedoc-saas
```

### Production Deployment

1. **Use PostgreSQL**
   - More robust than SQLite
   - Better concurrent access
   - Proper backup support

2. **Configure HTTPS**
   - Use nginx or Caddy as reverse proxy
   - Obtain SSL certificates (Let's Encrypt)

3. **Set Environment Variables**
   - Never hardcode secrets
   - Use secret management service

4. **Enable Monitoring**
   - Application logs
   - Error tracking (Sentry)
   - Performance monitoring

5. **Set Up Backups**
   - Database backups
   - User data backups
   - Regular testing

---

## API Documentation

### Authentication

**Signup**
```http
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Login**
```http
POST /auth/login
Content-Type: application/json

{
  "email_or_username": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {...}
}
```

**Using JWT Token**
```http
GET /auth/me
Authorization: Bearer eyJhbGciOi...
```

**Using API Key**
```http
GET /projects
X-API-Key: vbd_your_api_key_here
```

### Plan Generation

```http
POST /plans/generate
Authorization: Bearer eyJhbGciOi...
Content-Type: application/json

{
  "idea": "Build a fitness tracking app",
  "reference_url": "https://example.com/reference"
}

Response:
{
  "plan": "# Development Plan\n...",
  "message": "Plan generated successfully"
}
```

### Project Management

**List Projects**
```http
GET /projects?skip=0&limit=50
Authorization: Bearer eyJhbGciOi...
```

**Create Project**
```http
POST /projects
Authorization: Bearer eyJhbGciOi...
Content-Type: application/json

{
  "title": "My Awesome App",
  "description": "A fitness tracking application",
  "plan": "# Development Plan\n...",
  "reference_urls": ["https://example.com"]
}
```

**Get Project**
```http
GET /projects/{project_id}
Authorization: Bearer eyJhbGciOi...
```

**Update Project**
```http
PUT /projects/{project_id}
Authorization: Bearer eyJhbGciOi...
Content-Type: application/json

{
  "title": "Updated Title",
  "is_favorite": true,
  "tags": ["fitness", "mobile"]
}
```

**Delete Project**
```http
DELETE /projects/{project_id}
Authorization: Bearer eyJhbGciOi...
```

### Subscription

**Get Subscription**
```http
GET /subscription
Authorization: Bearer eyJhbGciOi...

Response:
{
  "tier": "pro",
  "status": "active",
  "limits": {
    "plan_generation": 50,
    "projects": 20,
    "exports": 200
  },
  "usage": {
    "plans_generated": 12,
    "projects_created": 5,
    "exports_made": 23
  }
}
```

**Usage Statistics**
```http
GET /subscription/usage?days=30
Authorization: Bearer eyJhbGciOi...
```

---

## Payment Integration

### Stripe Setup

1. **Create Stripe Account**
   - Go to https://stripe.com
   - Complete registration

2. **Get API Keys**
   - Dashboard → Developers → API Keys
   - Copy Secret Key and Publishable Key

3. **Create Products**
   - Products → Create Product
   - "VibeDoc Pro" - $19.99/month
   - "VibeDoc Enterprise" - $99.99/month

4. **Get Price IDs**
   - Copy price IDs for each product
   - Add to `.env` file

5. **Set Up Webhooks**
   - Developers → Webhooks → Add Endpoint
   - URL: `https://yourdomain.com/webhooks/stripe`
   - Events:
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`

### Webhook Handler

The payment system automatically handles:
- Subscription creation
- Subscription updates
- Subscription cancellation
- Payment success/failure
- Tier upgrades/downgrades

---

## Admin Guide

### Admin Dashboard

Access the admin dashboard from the web interface (admin users only):

- **System Statistics**
  - Total users
  - Active users
  - Total projects
  - Subscription breakdown

- **User Management**
  - View all users
  - Activate/deactivate accounts
  - View user subscriptions
  - Check usage statistics

### Admin API Endpoints

```http
GET /admin/stats
Authorization: Bearer eyJhbGciOi... (admin token)

Response:
{
  "total_users": 150,
  "active_users": 142,
  "total_projects": 523,
  "subscription_breakdown": {
    "free": 100,
    "pro": 45,
    "enterprise": 5
  }
}
```

### Maintenance Tasks

**Reset Monthly Usage**
```python
from database import SubscriptionService

# Run as monthly cron job
SubscriptionService.reset_monthly_usage_for_all()
```

**Cleanup Expired Sessions**
```python
from auth import session_manager

# Run daily
session_manager.cleanup_expired_sessions(max_age_hours=24)
```

---

## Best Practices

### Security

1. **Always use HTTPS in production**
2. **Generate strong JWT secrets**
3. **Rotate API keys regularly**
4. **Enable rate limiting**
5. **Validate all user inputs**
6. **Use prepared statements** (SQLAlchemy handles this)
7. **Enable CORS properly**
8. **Monitor for suspicious activity**

### Performance

1. **Use PostgreSQL for production**
2. **Enable database indexing**
3. **Implement caching** (Redis)
4. **Monitor API response times**
5. **Optimize database queries**
6. **Use connection pooling**

### Monitoring

1. **Application logs**
2. **Error tracking** (Sentry, Rollbar)
3. **Performance monitoring** (New Relic, DataDog)
4. **Uptime monitoring**
5. **Database monitoring**
6. **User analytics**

---

## Troubleshooting

### Common Issues

**Issue: Database not found**
```bash
# Solution: Initialize database
python init_saas.py
```

**Issue: Authentication failed**
```
# Check JWT secret is set
echo $JWT_SECRET_KEY

# Regenerate if needed
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Issue: Stripe webhook fails**
```
# Verify webhook secret
# Check endpoint URL is correct
# Ensure HTTPS is enabled
# Check webhook event types
```

**Issue: Usage limits not working**
```
# Check subscription is active
# Verify current period dates
# Check limit values in database
```

---

## Support

- **Documentation**: https://github.com/YourUsername/VibeDoc
- **Issues**: https://github.com/YourUsername/VibeDoc/issues
- **Email**: support@vibedoc.com

---

## License

MIT License - See LICENSE file for details.

---

Made with ❤️ by the VibeDoc Team
