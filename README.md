# Equinox - AI-Powered Wellness & Productivity Assistant

A full-stack multi-agent AI application that helps manage your wellness and productivity through intelligent chat-based interactions.

## Features

### Multi-Agent Architecture
- **Supervisor Agent**: Routes queries to the appropriate specialist
- **Wellness Agent**: Handles health, sleep, readiness, and workout queries
- **Productivity Agent**: Manages emails, notes, todos, and task management

### Integrations
- **Google OAuth**: Sign in with Google to access email summaries
- **Opik Tracing**: LLM observability and conversation threading
- **PostgreSQL**: Persistent storage for notes, todos, and chat history

### Frontend
- Modern React + TypeScript UI with Vite
- Markdown-rendered chat responses
- Note-taking with auto-save
- Todo management
- Chat history persistence

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL database
- API Keys:
  - Groq API key (https://console.groq.com/keys)
  - Opik API key (https://www.comet.com/opik)
  - Google OAuth credentials (for email integration)

### One-Command Startup

```bash
# Clone and setup
git clone <repo-url>
cd equinox

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Run everything
chmod +x startup.sh
./startup.sh
```

### Environment Variables

Create `backend/.env`:

```env
# Required
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:pass@localhost:5432/equinox

# Observability (Optional but recommended)
OPIK_API_KEY=your_opik_api_key
OPIK_WORKSPACE=your_workspace

# Google OAuth (for email features)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

## Project Structure

```
equinox/
├── backend/
│   ├── agents/
│   │   ├── productivity/    # Email, notes, todos agent
│   │   └── wellness/        # Health and fitness agent
│   ├── supervisor/          # Query router
│   ├── api/                 # REST endpoints
│   ├── database/            # Models and connection
│   ├── tools/               # Google auth utilities
│   └── main.py              # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Chat/        # Chat interface
│   │   │   ├── Productivity/# Notes, Todos
│   │   │   └── Wellness/    # Health dashboard
│   │   ├── components/      # Shared components
│   │   └── api/             # API utilities
│   └── package.json
└── startup.sh               # Dev startup script
```

## API Endpoints

### Core
- `GET /ping` - Health check
- `POST /supervisor` - Send message to AI

### Notes
- `GET /notes/{email}` - Get user notes
- `POST /notes/` - Create note
- `PATCH /notes/{id}` - Update note
- `DELETE /notes/{id}` - Delete note

### Todos
- `GET /todos/{email}` - Get user todos
- `POST /todos/` - Create todo
- `PATCH /todos/{id}` - Toggle/update todo
- `DELETE /todos/{id}` - Delete todo

### Chat History
- `GET /api/history/{email}` - Get all threads
- `GET /api/history/{email}/{thread_id}` - Get specific thread
- `POST /api/history/{email}/{thread_id}` - Save thread

## Tech Stack

### Backend
- FastAPI + Uvicorn
- LangGraph + LangChain
- Groq (Llama 3.3 70B)
- SQLAlchemy + PostgreSQL
- Opik (LLM observability)

### Frontend
- React 19 + TypeScript
- Vite
- React Router
- React Markdown (GFM)
- Lucide Icons

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Observability

Traces are sent to Opik under the `equinox` project. Each conversation is grouped by `thread_id` for easy debugging.

View traces at: https://www.comet.com/opik

## Troubleshooting

### "OPIK_API_KEY not found"
Set the environment variable in `backend/.env`

### Google OAuth errors
Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set

### Rate limiting (429)
Groq free tier: 30 req/min. Wait or upgrade plan.

### Database connection errors
Verify `DATABASE_URL` and that PostgreSQL is running

## License

MIT
