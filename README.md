# RingCentral Call Summary Pipeline

**Built by: KMan | AI-Augmented Engineering Factory**

## Business Problem Solved

Enterprise sales and support teams waste countless hours manually reviewing call recordings and notes to extract key insights. RingCentral Call Summary Pipeline automates the entire process - from receiving call events via webhook, to AI-powered summarization using OpenAI or Anthropic, and finally syncing results to Google Sheets for team visibility.

**Key Pain Points Addressed:**
- Manual call review is time-consuming and inconsistent
- Key points and action items get lost in lengthy recordings
- No standardized way to share call insights across teams
- Integration gaps between RingCentral, AI services, and collaboration tools

**Solution:**
- Automatic call capture via RingCentral webhooks
- AI-powered summarization with sentiment analysis and action item extraction
- Google Sheets integration for seamless workflow automation
- RESTful API for easy integration into existing systems

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- RingCentral Developer Account
- OpenAI API Key (or Anthropic API Key)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/9KMan/JOB-20260614011259-000092.git
cd JOB-20260614011259-000092
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the API server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

7. (Optional) Start the Celery worker:
```bash
celery -A app.worker.tasks.celery_app worker --loglevel=info
```

### Using Docker Compose

```bash
docker-compose up --build
```

## Project Structure

```
JOB-20260614011259-000092/
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── health.py
│   │       ├── jobs.py
│   │       ├── ringcentral.py
│   │       ├── sheets.py
│   │       ├── summaries.py
│   │       └── __init__.py
│   ├── models/
│   │   ├── call_record.py
│   │   ├── call_summary.py
│   │   ├── google_sheet.py
│   │   ├── job_status.py
│   │   ├── user.py
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── call_record.py
│   │   ├── call_summary.py
│   │   ├── google_sheet.py
│   │   ├── job_status.py
│   │   ├── user.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── openai_service.py
│   │   ├── ringcentral_service.py
│   │   ├── sheets_service.py
│   │   └── __init__.py
│   ├── worker/
│   │   ├── summarizer.py
│   │   ├── tasks.py
│   │   └── __init__.py
│   ├── config.py
│   ├── database.py
│   └── main.py
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| **Authentication** | | |
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login and get JWT tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout user |
| **RingCentral** | | |
| GET | `/api/v1/ringcentral/auth` | Get RingCentral OAuth URL |
| POST | `/api/v1/ringcentral/callback` | OAuth callback handler |
| GET | `/api/v1/ringcentral/calls` | List call records |
| POST | `/api/v1/ringcentral/webhook` | Webhook for call events |
| **Summaries** | | |
| GET | `/api/v1/summaries` | List all summaries |
| GET | `/api/v1/summaries/{id}` | Get summary details |
| POST | `/api/v1/summaries/generate` | Generate new summary |
| GET | `/api/v1/summaries/{id}/status` | Get generation status |
| **Google Sheets** | | |
| GET | `/api/v1/sheets/integrations` | List integrations |
| POST | `/api/v1/sheets/integrations` | Create integration |
| PUT | `/api/v1/sheets/integrations/{id}` | Update integration |
| DELETE | `/api/v1/sheets/integrations/{id}` | Delete integration |
| POST | `/api/v1/sheets/integrations/{id}/sync` | Sync to sheet |
| **Jobs** | | |
| GET | `/api/v1/jobs` | List all jobs |
| GET | `/api/v1/jobs/{id}` | Get job status |
| **Health** | | |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/health/ready` | Readiness check |

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ RingCentral │────▶│  FastAPI    │────▶│ PostgreSQL  │
│   Webhook   │     │    API      │     │  Database   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
                          ▼
                   ┌─────────────┐     ┌─────────────┐
                   │   Celery    │────▶│    Redis    │
                   │   Worker    │     │   Broker    │
                   └──────┬──────┘     └─────────────┘
                          │
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   OpenAI    │ │  Anthropic  │ │   Google    │
    │   Service   │ │   Service   │ │   Sheets    │
    └─────────────┘ └─────────────┘ └─────────────┘
```

## Key Technical Decisions

1. **Python + FastAPI (not Node.js)** — Better async support for parallel API calls, richer ecosystem for data pipeline work (pandas, pydantic)

2. **PostgreSQL over Sheets-as-DB** — Sheets is for *output*; raw RingSense data needs durable storage because RingCentral truncates at 90 days

3. **Claude over GPT** — Per your preference; better at structured extraction tasks

4. **JWT server-only auth** — No OAuth redirect flow needed; simpler, more secure for backend-only pipeline

## Configuration

Environment variables can be set in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:***@localhost:5432/ringcentral_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | Secret key for JWT signing | (required) |
| `RINGCENTRAL_CLIENT_ID` | RingCentral OAuth client ID | (required) |
| `RINGCENTRAL_CLIENT_SECRET` | RingCentral OAuth client secret | (required) |
| `OPENAI_API_KEY` | OpenAI API key | (required for OpenAI) |
| `ANTHROPIC_API_KEY` | Anthropic API key | (required for Anthropic) |
| `GOOGLE_SHEETS_CLIENT_ID` | Google Sheets OAuth client ID | (required) |
| `GOOGLE_SHEETS_CLIENT_SECRET` | Google Sheets OAuth client secret | (required) |

## API Documentation

Once the server is running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
