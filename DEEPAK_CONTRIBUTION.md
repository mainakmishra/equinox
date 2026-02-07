# Deepak's Contribution to Equinox

## Session: January 26, 2026 (Late Night Session 🌙)

---

## What I Built

### 1. Complete Wellness Agent Backend

**The Coach is now alive!** Built the entire B. The Wellness Agent from the project proposal.

#### Database Layer (`backend/database/`)
- `connection.py` - PostgreSQL connection via Neon (cloud database)
- `models.py` - 9 SQLAlchemy models:
  - User, UserProfile
  - HealthLog (daily health data)
  - MoodEntry (mood tracking)
  - Workout (fitness recommendations)
  - Streak, Achievement (gamification)
  - AgentSignal (inter-agent communication)
  - WellnessForecast (predictions)
- `pinecone_db.py` - Vector database for long-term memory
- `init.sql` - Database schema

#### REST APIs (`backend/api/`)
- `health.py`:
  - POST /api/health/log - Log daily health data
  - GET /api/health/today - Get today's log
  - GET /api/health/history - Get history (last N days)
  - GET /api/health/readiness - Get readiness score with breakdown
- `profile.py`:
  - GET /api/profile/ - Get user profile
  - PUT /api/profile/ - Update profile
- `chat.py`:
  - POST /api/chat/wellness - Chat with wellness agent

#### Algorithms (`backend/agents/wellness/algorithms/`)
- `readiness.py` - Readiness score calculation (0-100)
  - Weights: Sleep 35%, Energy 25%, Stress 20%, Activity 10%, Consistency 10%
  - Zones: peak, good, moderate, low, critical
- `sleep_debt.py` - Tracks accumulated sleep debt over 14 days
- `trends.py` - Analyzes weekly wellness trends

#### LangGraph Agent (`backend/agents/wellness/`)
- `agent.py` - LangGraph ReAct agent with Groq LLM (llama-3.3-70b-versatile)
- `state.py` - Agent state definition
- `tools/health_tools.py` - 5 LangGraph tools:
  1. get_health_today() - Fetch today's health data
  2. get_readiness_score() - Calculate readiness with breakdown
  3. get_sleep_debt_info() - Get sleep debt and recovery needs
  4. get_wellness_trends() - Analyze 7-day trends
  5. suggest_activity() - Recommend workouts based on readiness zone

---

### 2. Frontend Updates

- Updated `chatApi.ts` to support agent selection (wellness, productivity, supervisor)
- Updated `ChatPage.tsx` to handle multiple response formats

---

### 3. Google OAuth Setup

- Fixed `google_auth.py` to use local `client_secret.json` path
- Set up Google Cloud project with OAuth credentials
- Added test users for development

---

## Files I Created/Modified

### New Files (23)
```
backend/database/__init__.py
backend/database/connection.py
backend/database/models.py
backend/database/init.sql
backend/database/pinecone_db.py
backend/schemas/__init__.py
backend/schemas/health.py
backend/schemas/profile.py
backend/api/__init__.py
backend/api/health.py
backend/api/profile.py
backend/api/chat.py
backend/agents/wellness/__init__.py
backend/agents/wellness/agent.py
backend/agents/wellness/state.py
backend/agents/wellness/algorithms/__init__.py
backend/agents/wellness/algorithms/readiness.py
backend/agents/wellness/algorithms/sleep_debt.py
backend/agents/wellness/algorithms/trends.py
backend/agents/wellness/tools/__init__.py
backend/agents/wellness/tools/health_tools.py
```

### Modified Files
```
backend/main.py - Merged with Abhyajit's code, added wellness routes, fixed CORS
backend/requirements.txt - Added dependencies
backend/tools/google_auth.py - Fixed path to use local client_secret.json
frontend/src/api/chatApi.ts - Added agent selection support
frontend/src/pages/Chat/ChatPage.tsx - Handle multiple response formats
```

---

## Git Activity

- Created branch: `feature/wellness-agent`
- Commit: `add wellness agent with health tracking apis`
- Lines added: +2255

---

## What's Implemented from Project Proposal

| Feature from Proposal | Status |
|-----------------------|--------|
| B. The Wellness Agent (The Coach) | ✅ Built |
| Recovery Tracking - readiness score | ✅ Working |
| Adaptive Fitness Plans | ✅ suggest_activity() tool |
| Inter-Agent Communication | ⏳ AgentSignal model ready |
| Wearable Integrations | ⏳ Source field ready, API TBD |

---

## What's Abhyajit's "Google LLM" Comment About?

Abhyajit mentioned wanting to **switch from Groq API to Google LLM (Gemini)**.

Currently we use:
- **Groq** (llama-3.3-70b-versatile) - Fast, free tier available

He wants to switch to:
- **Google Gemini** - Better for hackathon since Google is a sponsor

**Impact on my code:**
- Would need to change `langchain-groq` → `langchain-google-genai`
- Update agent.py to use `ChatGoogleGenerativeAI` instead of `ChatGroq`
- Easy migration, ~10 lines of code

---

## Still TODO

- [ ] Opik integration (sponsor requirement from Section 5)
- [ ] Morning Briefing Protocol (Section 4C)
- [ ] Actual wearable APIs (Apple Health, Fitbit)
- [ ] Gemini migration if team decides
- [ ] Production deployment

---

## Session: February 2, 2026 (Wellness Frontend 🎨)

---

## What I Built

### 1. Complete Wellness Page Frontend

**Full health logging form with professional enterprise UI**

#### Files Created
- `frontend/src/pages/Wellness/WellnessPage.tsx` - Full health logging form
- `frontend/src/pages/Wellness/WellnessPage.css` - Professional earthy theme styling
- `frontend/src/components/HealthLogPopup/HealthLogPopup.tsx` - Morning check-in popup
- `frontend/src/components/HealthLogPopup/HealthLogPopup.css` - Popup styling
- `frontend/src/api/healthApi.ts` - API client for health endpoints

#### Files Modified
- `frontend/src/App.tsx` - Added /wellness route, popup logic for daily health check
- `frontend/src/components/Navbar/SignedInNavbar.tsx` - Added "Wellness" link
- `frontend/src/index.css` - Updated global colors from blue to earthy green

---

### 2. Features Implemented

| Feature | Description |
|---------|-------------|
| Daily Health Form | Sleep, Energy, Mood, Stress, Activity, Nutrition, Notes |
| Morning Popup | Shows when user hasn't logged health today |
| Readiness Score Card | Displays score with zone (peak/good/moderate/low/critical) |
| Professional Theme | Earthy green palette, no emojis, enterprise-grade UI |
| Smart Defaults | Activity/Steps/Water/Caffeine default to 0 (can't know in morning) |
| Clean Number Input | Fields show empty when 0, no leading zeros when typing |

---

### 3. Design Decisions

#### Color Palette (Earthy Theme)
- Background: `#1a1a1a` (charcoal)
- Cards: `#252525` (dark gray)
- Primary accent: `#4a7c59` (forest green)
- Secondary: `#5d8a66` (sage)
- Text: `#e8ddd4` (warm white)
- Muted text: `#9a8f85` (taupe)

#### UX Improvements
- Section hints: "How did you sleep last night?", "Update these throughout the day"
- Daily tracking section visually separated from morning check-in
- Update mode: Button says "Update Log" after first submission

---

### 4. TypeScript Fixes

Fixed 10+ TypeScript errors across the codebase:
- Removed unused imports (React, useState, useEffect, useNavigate)
- Added `type` keyword for type-only imports (verbatimModuleSyntax)
- Fixed FormEvent typing

---

## Git Activity (This Session)

- Branch: `feature/wellness-agent`
- New files: 5
- Modified files: 4
- Focus: Frontend health logging UI

---

*Built with love and lots of coffee ☕*

---

## Session: February 2, 2026 (Productivity Agent 📧)

---

## What I Built

### 1. Complete Productivity Agent LangGraph

**Full productivity agent with email summarization and Google Tasks integration!**

#### Files Created
- `backend/agents/productivity/state.py` - State definition for LangGraph
- `backend/agents/productivity/tools.py` - 4 LangGraph tools:
  1. `get_emails()` - Fetch recent emails with subject/sender
  2. `get_email_summary()` - LLM-summarized email priorities
  3. `get_tasks()` - Get Google Tasks
  4. `create_task()` - Create new task
- `backend/agents/productivity/agent.py` - LangGraph ReAct workflow
- `backend/agents/productivity/__init__.py` - Package exports

#### Files Modified
- `backend/tools/google_auth.py`:
  - Added Google Tasks API scope
  - Added `get_email_details()` - Fetch full email body
  - Added `get_tasks_service()` - Tasks API client
  - Added `fetch_task_lists()`, `fetch_tasks()` - Get tasks
  - Added `create_task()`, `complete_task()` - Task CRUD
- `backend/api/chat.py` - Added `/api/chat/productivity` endpoint
- `backend/agents/productivity/productivity_tools.py` - Email summarization with Groq LLM

---

### 2. Bug Fixes

| Fix | Description |
|-----|-------------|
| Wellness Agent Hallucination | Fixed `suggest_activity` tool to require real readiness data |
| Token Lookup | Fixed productivity tools to fallback to any available token |
| Import Errors | Fixed broken imports in productivity_tools.py |

---

### 3. Tested Features

All tested and working with real Gmail and Google Tasks data:

| Feature | Status | Test Result |
|---------|--------|-------------|
| Get Emails | ✅ Working | Fetched 5 real emails |
| Get Tasks | ✅ Working | Found: "JP Morgan apply", "Kanishk Birthday", etc. |
| Email Summary (LLM) | ✅ Working | Identified: LinkedIn alerts, Republic Day offers |
| Create Task | ✅ Working | Creates tasks in Google Tasks |

---

## Git Activity (This Session)

- Branch: `feature/wellness-frontend`
- New files: 4
- Modified files: 4
- Focus: Productivity Agent completion

