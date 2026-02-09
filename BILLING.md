# Billing and Subscription System

This document describes the billing and subscription system implementation for the Masidy platform.

## Overview

The billing system provides:
- **Usage Tracking**: Track OpenAI API calls, Docker executions, GitHub repos, and project creations
- **Stripe Integration**: Secure payment processing and subscription management
- **Quota Enforcement**: Enforce usage limits based on subscription tiers
- **Cost Calculation**: Real-time cost tracking with platform markup
- **Invoice Generation**: Automated invoice creation and history
- **Free Trial**: 7-day free trial for new users

## Subscription Tiers

### Free Tier (Trial)
- **Price**: $0/month
- **Trial**: 7 days
- **Limits**:
  - 5 projects/month
  - 10 OpenAI API calls
  - 5 Docker executions
  - 1 GitHub repo
- **Features**: Basic platform access, community support

### Pro Tier
- **Price**: $29/month
- **Limits**:
  - 50 projects/month
  - 100 OpenAI API calls
  - 50 Docker executions
  - 50 GitHub repos
- **Features**: Advanced analytics, priority support

### Team Tier
- **Price**: $99/month
- **Limits**:
  - 100 projects/month
  - 500 OpenAI API calls
  - 500 Docker executions
  - 100 GitHub repos
  - 10 team members
- **Features**: Team collaboration, admin controls, priority support

### Enterprise Tier
- **Price**: Custom pricing
- **Limits**: Unlimited
- **Features**: SSO/SAML, dedicated support, custom workflows, SLA guarantees

## Setup

### Environment Variables

Add the following to your `.env` file:

```bash
# Stripe Configuration
STRIPE_API_KEY=sk_test_...  # Your Stripe secret key
STRIPE_WEBHOOK_SECRET=whsec_...  # Webhook signing secret
STRIPE_PRICE_ID_PRO=price_...  # Stripe price ID for Pro tier
STRIPE_PRICE_ID_TEAM=price_...  # Stripe price ID for Team tier

# Usage Tracking & Pricing
OPENAI_COST_PER_1K_TOKENS=0.0015
DOCKER_COST_PER_MINUTE=0.001
GITHUB_STORAGE_PER_REPO=0.10
PLATFORM_MARKUP_PERCENT=10.0
```

### Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Create products and prices in Stripe Dashboard:
   - Pro tier: $29/month recurring
   - Team tier: $99/month recurring
3. Get your API keys from the Stripe Dashboard
4. Set up webhook endpoint: `https://your-domain.com/api/billing/webhook`
5. Configure webhook to listen for:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.updated`

### Database Migration

The system will automatically create the necessary tables on startup:
- `billing` - User billing and subscription information
- `subscription_tiers` - Tier configuration (optional, uses hardcoded tiers)
- `usage_logs` - Detailed usage tracking logs
- `invoices` - Invoice history

## API Endpoints

### Billing Information

#### Get Current Billing
```http
GET /api/billing/
Authorization: Bearer <token>
```

Returns user's billing information including usage, limits, and costs.

#### Get Current Tier
```http
GET /api/billing/tier
Authorization: Bearer <token>
```

Returns current subscription tier details.

### Usage

#### Get Usage Statistics
```http
GET /api/billing/usage
Authorization: Bearer <token>
```

Returns current usage for projects, API calls, executions, and costs.

#### Get Usage Logs
```http
GET /api/billing/usage/logs?limit=100
Authorization: Bearer <token>
```

Returns detailed usage logs with metadata.

### Subscription Management

#### Get Available Plans
```http
GET /api/billing/plans
```

Returns all available subscription plans (no auth required).

#### Create Checkout Session
```http
POST /api/billing/checkout
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan": "pro",
  "success_url": "https://your-app.com/success",
  "cancel_url": "https://your-app.com/cancel"
}
```

Creates a Stripe checkout session and returns the checkout URL.

#### Cancel Subscription
```http
POST /api/billing/cancel
Authorization: Bearer <token>
```

Cancels the subscription at the end of the billing period.

#### Downgrade Plan
```http
POST /api/billing/downgrade
Authorization: Bearer <token>
```

Downgrades to the free plan at the end of the billing period.

### Invoices

#### Get Invoice History
```http
GET /api/billing/invoices?limit=50
Authorization: Bearer <token>
```

Returns list of past invoices.

### Webhooks

#### Stripe Webhook Handler
```http
POST /api/billing/webhook
Stripe-Signature: <signature>
```

Handles Stripe webhook events. **Must** be called from Stripe servers.

## Usage Tracking

### Automatic Tracking

The system automatically tracks usage when:
- **Projects**: Created via `POST /api/projects/`
- **Executions**: Run via `POST /api/sandbox/execute` or `/execute-code`
- **Deployments**: Created via `POST /api/deployments/project/{id}`

### Manual Tracking

To manually log usage in your code:

```python
from app.services.usage_tracking import usage_tracking
from app.models.billing import UsageType

# Log OpenAI usage
await usage_tracking.log_openai_usage(
    db,
    user_id=user.id,
    tokens=1500,
    model="gpt-4",
    metadata={"request_id": "abc123"}
)

# Log Docker execution
await usage_tracking.log_docker_usage(
    db,
    user_id=user.id,
    minutes=2.5,
    metadata={"container_id": "xyz789"}
)

# Log GitHub repo creation
await usage_tracking.log_github_repo_creation(
    db,
    user_id=user.id,
    repo_name="my-repo",
    metadata={"org": "my-org"}
)

# Log project creation
await usage_tracking.log_project_creation(
    db,
    user_id=user.id,
    project_id=project.id,
    metadata={"name": "My Project"}
)
```

## Quota Enforcement

### Automatic Enforcement

Quotas are automatically enforced on:
- Project creation
- Docker/sandbox executions
- Deployments

When a user exceeds their quota, they receive a `429 Too Many Requests` response with a message suggesting an upgrade.

### Manual Quota Check

```python
from app.services.usage_tracking import usage_tracking

# Check quota
has_quota, message = await usage_tracking.check_quota(
    db,
    user_id=user.id,
    quota_type="projects"  # or "executions", "api_calls", etc.
)

if not has_quota:
    raise HTTPException(
        status_code=429,
        detail=message
    )
```

## Cost Calculation

Costs are calculated with a 10% platform markup:

- **OpenAI**: $0.0015 per 1K tokens × 1.10 = $0.00165
- **Docker**: $0.001 per minute × 1.10 = $0.0011
- **GitHub**: $0.10 per repo/month × 1.10 = $0.11

Costs are tracked in real-time and displayed in the billing dashboard.

## Trial Logic

New users automatically receive a 7-day free trial:
1. Trial starts when user account is created
2. User has access to Free tier limits during trial
3. Trial expiration is tracked in `billing.trial_end`
4. After trial expiration, user must upgrade to continue
5. No payment method required during trial

## Security

### Best Practices

1. **Never store credit card data** - All payment processing is handled by Stripe
2. **Verify webhook signatures** - Always validate Stripe webhook signatures
3. **Use HTTPS** - Ensure all API endpoints use HTTPS in production
4. **Secure API keys** - Store Stripe keys in environment variables
5. **Rate limiting** - Implement rate limiting on billing endpoints
6. **Audit logs** - All billing operations are logged in `usage_logs`

### PCI Compliance

Since Stripe handles all payment processing, you do not need to be PCI compliant. However:
- Never store credit card numbers
- Never log full card details
- Always use Stripe's secure checkout

## Email Notifications

The following email notifications should be implemented (requires email provider integration):

1. **Subscription Confirmation** - When user subscribes to paid plan
2. **Upgrade/Downgrade Confirmation** - When plan changes
3. **Invoice Received** - When new invoice is generated
4. **Payment Failed** - When payment fails (with retry information)
5. **Usage Quota Warning** - When usage reaches 80% of limit
6. **Quota Exceeded** - When user hits their quota
7. **Trial Expiring Soon** - 2 days before trial ends
8. **Subscription Expiring** - When subscription is about to end

To implement, create an email service using SendGrid, Mailgun, or similar.

## Troubleshooting

### Common Issues

**"Stripe is not configured"**
- Ensure `STRIPE_API_KEY` is set in environment variables
- Verify the key starts with `sk_test_` (test) or `sk_live_` (production)

**"Invalid signature" on webhook**
- Verify `STRIPE_WEBHOOK_SECRET` is set correctly
- Ensure webhook endpoint URL matches Stripe dashboard
- Check that request is coming from Stripe

**Quota not updating**
- Verify usage tracking is called after operations
- Check database connection
- Ensure `billing` record exists for user

**Trial not working**
- Check `trial_end` date in billing record
- Verify `create_for_user` is called on user registration
- Check billing status is set to `TRIALING`

## Testing

### Test Mode

Use Stripe test mode for development:
1. Use test API keys (start with `sk_test_`)
2. Use test card numbers: `4242 4242 4242 4242`
3. Any future expiry date
4. Any 3-digit CVC

### Testing Webhooks

Use Stripe CLI for local webhook testing:
```bash
stripe listen --forward-to localhost:8000/api/billing/webhook
```

## Admin Features (Future)

The following admin features can be added:
- Revenue metrics dashboard
- Subscription analytics
- User spend tracking
- Manual quota adjustments
- Refund processing
- Custom pricing for enterprise

## Support

For issues:
1. Check logs in `usage_logs` table
2. Verify Stripe dashboard for subscription status
3. Check webhook event history in Stripe
4. Review billing status in database
