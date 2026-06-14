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

RingCentral API · Python · Node.js · OAuth/JWT · Claude/GPT API · Google Sheets API

## 3. Architecture

- Backend: Python (FastAPI) REST API
- AI/ML: Model integration (OpenAI/Anthropic API)
- Serverless: AWS Lambda / Vercel / Cloudflare Functions ready
- Data: ETL pipeline with task orchestration (Celery)
- Database: PostgreSQL with SQLAlchemy ORM
- Authentication: JWT (HS256)

### API Design
- RESTful endpoints with JSON request/response
- Authentication via JWT (HS256)
- Middleware for logging, error handling, CORS
- Versioned routes (/api/v1/...)

### Data Layer
- PostgreSQL as primary datastore
- Connection pooling via SQLAlchemy
- Migration management via Alembic
- Indexes on foreign keys and high-cardinality columns

## 4. Data Model

### Core Entities

#### User
- id: UUID (PK)
- email: String (unique, indexed)
- password_hash: String
- ringcentral_token: JSON (encrypted)
- created_at: Timestamp
- updated_at: Timestamp

#### CallRecord
- id: UUID (PK)
- user_id: UUID (FK -> User, indexed)
- ringcentral_call_id: String (indexed)
- direction: Enum (inbound/outbound)
- from_number: String
- to_number: String
- duration_seconds: Integer
- recording_url: String (nullable)
- call_status: Enum (completed, missed, voicemail)
- raw_data: JSON
- created_at: Timestamp (indexed)
- updated_at: Timestamp

#### CallSummary
- id: UUID (PK)
- call_record_id: UUID (FK -> CallRecord, indexed)
- user_id: UUID (FK -> User, indexed)
- summary_text: Text
- key_points: JSON (array of strings)
- action_items: JSON (array of objects)
- sentiment: Enum (positive, neutral, negative)
- ai_model: String
- processing_status: Enum (pending, processing, completed, failed)
- error_message: String (nullable)
- created_at: Timestamp (indexed)
- updated_at: Timestamp

#### GoogleSheetIntegration
- id: UUID (PK)
- user_id: UUID (FK -> User, indexed)
- spreadsheet_id: String
- sheet_name: String
- last_sync_at: Timestamp (nullable)
- sync_status: Enum (active, paused, error)
- created_at: Timestamp
- updated_at: Timestamp

#### JobStatus
- id: UUID (PK)
- job_type: String (indexed)
- status: Enum (pending, processing, completed, failed)
- input_data: JSON
- output_data: JSON (nullable)
- error_message: String (nullable)
- started_at: Timestamp (nullable)
- completed_at: Timestamp (nullable)
- created_at: Timestamp (indexed)

### Relationships
- User has many CallRecords
- User has many CallSummaries
- User has many GoogleSheetIntegrations
- CallRecord has one CallSummary
- All entities have created_at/updated_at timestamps

## 5. API Endpoints

### Authentication
- POST /api/v1/auth/register - Register new user
- POST /api/v1/auth/login - Login and get JWT
- POST /api/v1/auth/refresh - Refresh JWT token
- POST /api/v1/auth/logout - Logout user

### RingCentral Integration
- GET /api/v1/ringcentral/auth - Get OAuth URL
- POST /api/v1/ringcentral/callback - OAuth callback
- GET /api/v1/ringcentral/calls - List call records
- POST /api/v1/ringcentral/webhook - Webhook for call events

### Call Summaries
- GET /api/v1/summaries - List summaries
- GET /api/v1/summaries/{id} - Get summary details
- POST /api/v1/summaries/generate - Generate new summary
- GET /api/v1/summaries/{id}/status - Get generation status

### Google Sheets
- GET /api/v1/sheets/integrations - List integrations
- POST /api/v1/sheets/integrations - Create integration
- PUT /api/v1/sheets/integrations/{id} - Update integration
- DELETE /api/v1/sheets/integrations/{id} - Delete integration
- POST /api/v1/sheets/integrations/{id}/sync - Sync to sheet

### Jobs
- GET /api/v1/jobs - List jobs
- GET /api/v1/jobs/{id} - Get job status

### Health
- GET /api/v1/health - Health check
- GET /api/v1/health/ready - Readiness check

## 6. Business Logic

### Call Summary Generation
1. Receive call record from RingCentral webhook
2. Store call record in database
3. Queue summary generation job
4. Worker picks up job
5. Worker calls OpenAI API for summarization
6. Worker stores summary
7. Worker triggers Google Sheets sync if enabled

### Google Sheets Sync
1. Query all completed summaries for user
2. Format data for Google Sheets
3. Batch update/append to spreadsheet
4. Update last_sync_at timestamp

## 7. Security Requirements

- All passwords hashed with bcrypt
- JWT tokens with 15-minute expiry
- Refresh tokens with 7-day expiry
- Rate limiting on API endpoints
- Input validation on all endpoints
- SQL injection prevention via ORM
- CORS configuration for frontend

## 8. Acceptance Criteria

- User can register and login
- User can connect RingCentral account via OAuth
- Call records are captured via webhook
- Summaries are generated automatically for completed calls
- Summaries can be synced to Google Sheets
- All endpoints return proper HTTP status codes
- All errors are logged and returned in JSON format
- Unit tests cover core business logic
- API documentation available via OpenAPI/Swagger
