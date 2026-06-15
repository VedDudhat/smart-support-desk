# CRM Integration Service

## Overview

CRM Integration Service is a FastAPI-based backend application that synchronizes customer and ticket data with HubSpot CRM. It acts as a middleware layer between internal support systems and HubSpot, enabling seamless customer management, ticket creation, ticket association, and AI-powered support workflows.

The project provides APIs for:

- Customer Management
- Ticket Management
- HubSpot CRM Synchronization
- AI Assistant Integration
- Redis-Based Caching
- Rate Limiting and API Protection

---

## Features

### Customer Operations
- Create HubSpot contacts
- Update existing contacts
- Search contacts by email
- Store HubSpot contact mappings in Redis cache

### Ticket Operations
- Create support tickets in HubSpot
- Associate tickets with existing contacts
- Manage ticket priorities
- Track ticket status

### AI Assistant
- Natural language ticket management
- Customer lookup assistance
- Conversation memory support
- LangChain & LangGraph integration
- Google Gemini LLM support

### Performance & Security
- Redis caching
- API rate limiting
- Environment variable configuration
- CORS protection
- Error handling and validation

---

## Technology Stack

### Backend
- FastAPI
- Python 3.10+
- Uvicorn

### AI & LLM
- LangChain
- LangGraph
- Google Gemini

### CRM
- HubSpot CRM API

### Database & Cache
- Redis

### HTTP Client
- HTTPX

### Validation
- Pydantic

---

## Project Structure

```text
CRM-Integration/
│
├── app.py
├── requirement.txt
├── .env
│
├── backend/
│   ├── assistant/
│   │   ├── ai_agent.py
│   │   ├── ai_tools_customer_ops.py
│   │   ├── ai_tools_ticket_ops.py
│   │   ├── conversation_memory.py
│   │   └── logic.py
│   │
│   ├── models/
│   ├── routes/
│   │   ├── customer.py
│   │   ├── ticket.py
│   │   └── chat.py
│   │
│   ├── schemas/
│   └── redis.py
│
└── ui/
    └── streamlit_ui.py
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
# HubSpot
HUBSPOT_API_KEY=your_hubspot_api_key
HUBSPOT_BASE_URL=https://api.hubapi.com
HUBSPOT_PORTAL_ID=your_portal_id

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Gemini
GOOGLE_API_KEY=your_google_api_key
```

---

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd CRM-Integration
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirement.txt
```

---

## Running the Application

Start the FastAPI server:

```bash
python app.py
```

or

```bash
uvicorn app:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

---

## API Endpoints

### Health Check

```http
GET /
```

Response:

```json
{
  "service": "CRM Integration Service",
  "status": "running",
  "version": "2.0.0"
}
```

---

### Customer APIs

#### Create Customer

```http
POST /customers
```

Creates or updates a contact in HubSpot.

---

### Ticket APIs

#### Create Ticket

```http
POST /tickets
```

Creates a support ticket and associates it with a HubSpot contact if available.

---

### Chat APIs

#### Create Chat Session

```http
POST /chat/session
```

Creates a new AI assistant session.

---

## HubSpot Integration Flow

```text
User Request
      │
      ▼
CRM Integration Service
      │
      ▼
HubSpot CRM
      │
      ├── Contacts
      └── Tickets
```

### Customer Creation Flow

1. Receive customer details.
2. Check if contact already exists.
3. Update existing contact or create a new one.
4. Store HubSpot ID mapping in Redis.

### Ticket Creation Flow

1. Receive ticket details.
2. Create ticket in HubSpot.
3. Find associated customer.
4. Link ticket to contact.
5. Return HubSpot ticket information.

---

## AI Assistant Capabilities

The AI Assistant can:

- Create tickets from natural language
- Retrieve ticket information
- Update ticket details
- Search customer records
- Maintain conversation history
- Automate support workflows

### Example Queries

```text
Create a high-priority ticket for login issues.

Show all tickets for john@example.com.

Update ticket 123 to Closed.

Find customer by email.
```

---

## Error Handling

The service handles:

- Invalid requests
- Missing HubSpot credentials
- Rate limit violations
- API failures
- Timeout exceptions
- Validation errors

---

## Security

- Environment variable based secrets
- Redis-backed rate limiting
- API validation using Pydantic
- CORS configuration
- HubSpot token protection

---

## Future Enhancements

- OAuth-based HubSpot authentication
- Dashboard analytics
- Multi-CRM support
- Ticket status synchronization
- Automated ticket categorization
- Vector database integration for AI memory

---

## Author

Developed as a CRM integration and AI-powered support automation platform using FastAPI, HubSpot CRM, Redis, LangChain, and Google Gemini.
