# Specification: RingCentral Call Summary Pipeline

## 1. Project Overview

**Project:** RingCentral Call Summary Pipeline
**GitHub Repo:** https://github.com/9KMan/JOB-20260614011259-000092
**Lead:** https://www.upwork.com/jobs/~022065963408978544115
**Client:** RingCentral Client (Upwork)
**Tier:** EXPERT
**Budget:** $20-$60/hr hourly, 1-3 months, <30 hrs/week
**Rate:** $20-60/hr
**Timeline:** 1-3 months

## 2. Technical Stack

- **Backend:** Python (FastAPI)
- **Frontend:** Node.js with modern framework (optional)
- **Database:** PostgreSQL with connection pooling
- **AI/ML:** OpenAI GPT-4 / Anthropic Claude API
- **Task Queue:** Celery with Redis broker
- **Serverless:** AWS Lambda / Cloudflare Workers ready
- **Orchestration:** ETL pipeline with Apache Airflow (optional)
- **Infrastructure:** Docker, Docker Compose, AWS

## 3. Core Features

### 3.1 RingCentral Integration
- OAuth 2.0 authentication flow
- Webhook subscriptions for call events
- Call recording download and storage
- Call metadata extraction (duration, participants, timestamps)

### 3.2 AI-Powered Summarization
- Automatic call transcription (via external service or RingCentral native)
- AI-generated summaries using GPT-4 or Claude
- Sentiment analysis
- Action item extraction
- Key topic identification

### 3.3 Data Pipeline
- ETL pipeline for processing call data
- Background job processing with Celery
- Retry logic with exponential backoff
- Dead letter queue for failed jobs

### 3.4 API Endpoints
- RESTful API with JSON request/response
- JWT authentication (HS256)
- Rate limiting and throttling
- Comprehensive error handling
- Request validation with Pydantic

## 4. Data Model

### 4.1 Core Entities

**User**
- id (UUID, PK)
- email (unique)
- password_hash
- ringcentral_refresh_token
- ringcentral_access_token
- created_at, updated_at

**Call**
- id (UUID, PK)
- ringcentral_call_id
- user_id (FK -> User)
- direction (inbound/outbound)
- status (completed/missed/voicemail)
- duration_seconds
- started_at
- ended_at
- recording_url
- created_at, updated_at

**CallSummary**
- id (UUID, PK)
- call_id (FK -> Call, unique)
- transcript_text
- summary_text
- sentiment_score
- action_items (JSON array)
- key_topics (JSON array)
- ai_provider (openai/anthropic)
- processing_status
- created_at, updated_at

**WebhookEvent**
- id (UUID, PK)
- event_type
- event_id (unique)
- payload (JSON)
- processed (boolean)
- processed_at
- created_at

### 4.2 Indexes
- Index on Call.user_id
- Index on Call.started_at
- Index on CallSummary.call_id
- Index on WebhookEvent.event_id
- Index on WebhookEvent.event_type
- Composite index on WebhookEvent(processed, created_at)

## 5. API Design

### 5.1 Authentication
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/login - User login (returns JWT)
- POST /api/v1/auth/refresh - Refresh access token
- POST /api/v1/auth/ringcentral/connect - Initiate RingCentral OAuth
- GET /api/v1/auth/ringcentral/callback - OAuth callback

### 5.2 Calls
- GET /api/v1/calls - List calls (paginated, filterable)
- GET /api/v1/calls/{id} - Get call details
- GET /api/v1/calls/{id}/summary - Get AI summary
- POST /api/v1/calls/{id}/summarize - Trigger re-summarization

### 5.3 Webhooks
- POST /api/v1/webhooks/ringcentral - RingCentral webhook endpoint

### 5.4 Health
- GET /api/v1/health - Health check

## 6. Configuration

Environment variables:
- DATABASE_URL
- REDIS_URL
- JWT_SECRET_KEY
- JWT_ALGORITHM
- RINGCENTRAL_CLIENT_ID
- RINGCENTRAL_CLIENT_SECRET
- RINGCENTRAL_SERVER_URL
- RINGCENTRAL_WEBHOOK_SECRET
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- LOG_LEVEL

## 7. Error Handling

- Structured error responses with error codes
- HTTP status codes: 400 (bad request), 401 (unauthorized), 404 (not found), 500 (server error)
- Error logging with correlation IDs
- Graceful degradation for AI service failures

## 8. Acceptance Criteria

- [ ] Users can authenticate via RingCentral OAuth
- [ ] Call events are received via webhooks
- [ ] Calls are stored with metadata
- [ ] AI summaries are generated automatically
- [ ] API returns paginated call lists
- [ ] Background jobs process summaries
- [ ] System handles failures gracefully
- [ ] Unit tests cover core functionality
