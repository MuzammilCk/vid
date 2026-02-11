# 🧠 VidBrain AI

**Extract structured insights from any YouTube video using AI**

## 🚀 Tech Stack

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI
- **AI Model**: Google Gemini 1.5 Pro
- **Database**: Supabase (PostgreSQL + Auth + Storage)
- **Cache**: Redis (via Upstash)

## 📦 Project Structure

```
vidbrain/
├── frontend/          # Next.js 14 application
├── backend/           # Python FastAPI server
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Git

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Copy `.env` and fill in your API keys
   - Get API keys from:
     - Google AI Studio: https://aistudio.google.com/apikey
     - YouTube Data API: https://console.cloud.google.com
     - Spotify Developer: https://developer.spotify.com
     - TMDB: https://www.themoviedb.org/settings/api
     - Supabase: https://supabase.com

5. Start the server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

4. Open http://localhost:3000

## ✅ Phase 0 Checkpoint

- [x] Project structure created
- [x] Backend FastAPI server with health check
- [x] Frontend Next.js 14 with Tailwind CSS
- [x] All configuration files in place
- [x] Environment variables template ready

## 📋 Next Steps

**Phase 1**: YouTube Video Data Extraction
- Implement YouTube URL validation
- Create video metadata extractor
- Implement audio extraction service
- Implement frame extraction service

## 🎯 Project Phases

1. ✅ **Phase 0**: Project Setup & Architecture
2. 🔄 **Phase 1**: YouTube Video Data Extraction
3. **Phase 2**: AI Classification Engine
4. **Phase 3**: Category-Specific Processors
5. **Phase 4**: Frontend - Core UI
6. **Phase 5**: Third-Party Integrations
7. **Phase 6**: Database & User System
8. **Phase 7**: Polish & Error Handling
9. **Phase 8**: Deployment & Launch
10. **Phase 9**: Advanced Features & Scale

## 📝 License

MIT
# vid
