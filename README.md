<div align="center">

# 🚀 HireFlow AI

### AI-Powered Applicant Tracking System — Advanced Edition

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)](https://mysql.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-purple.svg)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

**HireFlow AI** is a production-ready, AI-powered Applicant Tracking System built with modern web technologies. It streamlines the entire recruitment lifecycle — from AI-powered job matching and resume parsing to candidate ranking and interactive career guidance.

🔗 **Live Demo**: [Coming Soon]  
📖 **API Docs**: [View API Documentation](#api-documentation)

</div>

---

## 📸 Screenshots

<div align="center">
  
| Login Page | Candidate Dashboard | Browse Jobs |
|:---:|:---:|:---:|
| ![Login Page](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) | ![Browse Jobs](screenshots/jobs.png) |
| **AI Chat Assistant** | **Light Theme** | **Profile Page** |
| ![AI Chat](screenshots/ai-chat.png) | ![Light Theme](screenshots/light-theme.png) | ![Profile](screenshots/profile.png) |

</div>

---

## ✨ Advanced Features

### 🤖 AI-Powered Career Assistant (NEW)
- **Interactive AI Chat** — Real-time career guidance chatbot with context-aware responses
- **Resume Optimization** — Get ATS-specific tips to improve your resume
- **Interview Preparation** — Practice with AI-generated interview questions
- **Career Counseling** — Personalized career path and skill development advice
- **Quick Actions** — One-click access to common AI tasks
- **Context Switching** — Toggle between General, Career, Resume, and Interview modes

### 📊 Advanced Visual Analytics (NEW)
- **Skills Radar Chart** — Visualize your skill proficiency distribution
- **ATS Profile Gauge** — Animated gauge showing your profile strength score
- **Application Progress Bar** — Visual pipeline of your application statuses
- **Real-time Chart Updates** — Interactive Chart.js visualizations

### 🎨 Theme System (NEW)
- **Dark/Light Mode Toggle** — One-click theme switching
- **Persistent Preferences** — Theme saved to localStorage
- **Optimized Contrast** — Both themes tested for readability
- **Smooth Transitions** — Animated theme switching

### 📥 Data Export (NEW)
- **CSV Export** — Download your applications as CSV files
- **JSON Export** — Export data in machine-readable format
- **One-click Download** — Browser-native file download

### ⌨️ Productivity Features (NEW)
- **Keyboard Shortcuts** — `Ctrl+K` to focus search, `Escape` to close popups
- **Scroll-to-Top** — Floating button for quick navigation
- **Global Error Handler** — Graceful error recovery with toast notifications
- **Smart Router** — Queue-based navigation for reliable page transitions

### 🤖 AI-Powered Features
- **Resume Parsing** — Extract structured data from resumes using Google Gemini AI
- **ATS Score Calculation** — Analyze resume compatibility with job descriptions
- **Smart Candidate Ranking** — Rank applicants based on job requirements
- **Interview Question Generation** — Generate role-specific interview questions
- **Cover Letter Generator** — Create professional cover letters with AI
- **Professional Summary Generator** — Craft compelling summaries
- **Skill Gap Analysis** — Identify missing skills and learning resources
- **Keyword Optimization** — Optimize resumes for ATS systems
- **Job Description Analysis** — Extract key requirements and skills
- **Sentiment Analysis** — Analyze tone of cover letters and messages

### 👥 For Candidates
- **Dashboard** — Interactive analytics with Chart.js visualizations
- **Job Search** — Advanced search with filters (location, salary, skills, remote, type)
- **Salary Filter (INR)** — Filter jobs by Indian salary ranges (₹5L, ₹10L, ₹20L+)
- **Application Tracking** — Real-time status updates with timeline
- **Resume Management** — Upload, preview, and manage multiple resumes
- **AI Resume Analysis** — Get instant ATS scores and improvement suggestions
- **Profile Management** — Skills, education, experience, and preferences
- **Saved Jobs** — Bookmark positions for later review
- **Notifications** — Real-time alerts for application updates

### 🏢 For Recruiters
- **Recruiter Dashboard** — Comprehensive recruitment analytics
- **Company Profile** — Manage company details and branding
- **Job Posting** — Create and manage job listings with rich details
- **Application Management** — Review, shortlist, reject with one click
- **Candidate Search** — Find candidates by skills and location
- **Interview Scheduling** — Send interview invitations seamlessly
- **Analytics** — Track job performance and recruitment KPIs

### 🔧 For Admins
- **System Dashboard** — Platform-wide analytics and KPIs
- **User Management** — Manage users, roles, and permissions
- **Job Oversight** — Moderate all platform job listings
- **Activity Logs** — Complete audit trail for compliance
- **Reporting** — Generate system reports and insights

### 🎨 Design
- **Dark/Light Theme** — Professional dual-theme UI with purple accents
- **Glassmorphism** — Modern frosted glass card design
- **Responsive** — Fully responsive across desktop, tablet, and mobile
- **Animations** — Smooth transitions and micro-interactions
- **Loading States** — Skeleton loading and spinners
- **Toast Notifications** — Non-intrusive feedback system
- **Interactive Charts** — Chart.js powered analytics visualizations
- **Indian Currency** — All salaries displayed in ₹ (Lakhs/Crores)

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (SPA)                            │
│  HTML5 │ CSS3 │ Vanilla JS │ Chart.js │ Font Awesome        │
│  AI Chat │ Radar Charts │ Theme System │ CSV Export         │
│  Keyboard Shortcuts │ Global Error Handler                   │
└──────────────────────┬───────────────────────────────────────┘
                       │ REST API (JWT Auth)
┌──────────────────────▼───────────────────────────────────────┐
│                    Backend (Flask)                           │
│  Blueprints │ Middleware │ Services │ Utils                 │
├──────────────────────┬───────────────────────────────────────┤
│  JWT Auth │ Rate Limiting │ Input Validation │ CORS        │
├──────────────────────┼───────────────────────────────────────┤
│  AI Service │ Email Service │ File Service │ Resume Parser  │
│  CSV Export │ Chat Endpoint │ Analytics Engine              │
└──────────────────────┬───────────────────────────────────────┘
                       │ SQLAlchemy ORM
┌──────────────────────▼───────────────────────────────────────┐
│                 Database (MySQL)                             │
│  17+ Tables │ Optimized Queries │ Full-Text Search          │
│  Users │ Jobs │ Applications │ Resumes │ Skills │ AI Analysis│
└──────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
hireflow-ai/
├── backend/
│   ├── __init__.py              # App factory & JWT setup
│   ├── config/
│   │   └── config.py            # Configuration management
│   ├── models/
│   │   ├── user.py              # User & authentication
│   │   ├── candidate.py         # Candidate profiles
│   │   ├── recruiter.py         # Recruiter profiles
│   │   ├── company.py           # Company profiles
│   │   ├── job.py               # Job postings
│   │   ├── application.py       # Job applications
│   │   ├── resume.py            # Resume management
│   │   ├── skill.py             # Skills taxonomy
│   │   ├── notification.py      # User notifications
│   │   ├── interview.py         # Interview invitations
│   │   ├── ai_analysis.py       # AI analysis results
│   │   ├── saved_job.py         # Saved/bookmarked jobs
│   │   └── activity_log.py      # Audit logs
│   ├── routes/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── jobs.py              # Job CRUD endpoints
│   │   ├── applications.py      # Application + CSV export
│   │   ├── candidates.py        # Candidate endpoints
│   │   ├── recruiters.py        # Recruiter endpoints
│   │   ├── admin.py             # Admin endpoints
│   │   ├── ai_routes.py         # AI features + Chat endpoint
│   │   ├── notifications.py     # Notification endpoints
│   │   ├── analytics.py         # Analytics endpoints
│   │   ├── search.py            # Search endpoints
│   │   ├── resumes.py           # Resume endpoints
│   │   ├── companies.py         # Company endpoints
│   │   ├── skills.py            # Skills endpoints
│   │   └── uploads.py           # File upload endpoints
│   ├── middleware/
│   │   ├── auth.py              # JWT middleware
│   │   └── validation.py        # Input validation
│   ├── services/
│   │   ├── ai_service.py        # Google Gemini integration
│   │   ├── email_service.py     # Email communications
│   │   ├── file_service.py      # File management
│   │   └── resume_parser.py     # Resume text extraction
│   └── utils/
│       ├── helpers.py           # Utility functions
│       └── decorators.py        # Custom decorators
├── static/
│   ├── css/
│   │   └── style.css            # Complete CSS framework w/ themes
│   └── js/
│       ├── app.js               # Core app, API, Router, UI utils
│       ├── auth.js              # Authentication pages
│       ├── pages.js             # Dynamic page routing engine
│       ├── dashboard.js         # Dashboard + Radar charts + Gauges
│       ├── jobs.js              # Job management + Data export
│       ├── recruiter.js         # Recruiter features
│       ├── admin.js             # Admin features
│       ├── profile.js           # Profile management
│       └── chat.js              # AI Chat Assistant (NEW)
├── templates/
│   └── index.html               # SPA entry point
├── screenshots/                 # Project screenshots
├── database/
│   └── seed_data.py             # Sample data generator
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

---

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- Google Gemini API key ([Get one free](https://ai.google.dev/))

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/hireflow-ai.git
cd hireflow-ai
```

### Step 2: Set Up Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/hireflow_ai
JWT_SECRET_KEY=your-jwt-secret
GEMINI_API_KEY=your-gemini-api-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Step 5: Set Up Database

```bash
# Create the MySQL database
mysql -u root -p -e "CREATE DATABASE hireflow_ai"

# Initialize tables
flask init-db

# Seed with sample data
flask seed-data
```

### Step 6: Run the Application

```bash
python run.py
```

The application will be available at **http://localhost:5000**

---

## 🚀 Deployment

### Deploy on Render (Backend)

1. Push your code to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Connect your GitHub repository
4. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
5. Add environment variables from your `.env` file
6. Deploy!

### Deploy Database on Railway

1. Create a [Railway](https://railway.app) account
2. Create a new **MySQL** database
3. Copy the connection string
4. Update `DATABASE_URL` in your environment variables

---

## 🔌 API Documentation

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT |
| POST | `/api/auth/logout` | Logout and invalidate token |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/profile` | Get current user profile |
| PUT | `/api/auth/update-profile` | Update user profile |
| POST | `/api/auth/change-password` | Change password |
| POST | `/api/auth/forgot-password` | Request password reset |
| POST | `/api/auth/reset-password` | Reset password |

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List jobs (with filters: salary_min, salary_max, employment_type, work_mode, experience_level, search) |
| GET | `/api/jobs/:id` | Get job details |
| POST | `/api/jobs` | Create job (Recruiter) |
| PUT | `/api/jobs/:id` | Update job |
| DELETE | `/api/jobs/:id` | Delete job |
| POST | `/api/jobs/:id/save` | Save/unsave job |
| GET | `/api/jobs/saved` | Get saved jobs |
| GET | `/api/jobs/categories` | Get job categories |

### Applications

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/applications` | Apply for a job |
| GET | `/api/applications` | Get applications |
| GET | `/api/applications/:id` | Get application details |
| PUT | `/api/applications/:id/status` | Update status (Recruiter) |
| PUT | `/api/applications/:id/notes` | Add recruiter notes |
| POST | `/api/applications/:id/withdraw` | Withdraw application |
| GET | `/api/applications/export` | **NEW** Export applications as CSV |
| GET | `/api/applications/stats` | Application statistics |

### AI Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chat` | **NEW** Interactive AI career chat assistant |
| POST | `/api/ai/parse-resume` | Parse resume with AI |
| POST | `/api/ai/ats-score` | Calculate ATS score |
| POST | `/api/ai/interview-questions` | Generate interview questions |
| POST | `/api/ai/cover-letter` | Generate cover letter |
| POST | `/api/ai/professional-summary` | Generate professional summary |
| POST | `/api/ai/skill-gap` | Analyze skill gaps |
| POST | `/api/ai/keyword-optimize` | Optimize resume keywords |
| POST | `/api/ai/rank-candidates` | Rank candidates (Recruiter) |
| POST | `/api/ai/analyze-job` | Analyze job description |

### Recruiters

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/recruiters/dashboard` | Get recruiter dashboard |
| GET/PUT | `/api/recruiters/company` | Manage company profile |
| GET | `/api/recruiters/jobs` | Get recruiter's jobs |
| GET | `/api/recruiters/applications` | Get applications |
| GET/POST | `/api/recruiters/interviews` | Manage interviews |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard` | System dashboard |
| GET | `/api/admin/users` | List all users |
| GET/PUT/DELETE | `/api/admin/users/:id` | Manage specific user |
| GET | `/api/admin/jobs` | List all jobs |
| GET | `/api/admin/logs` | Activity logs |
| GET | `/api/admin/reports` | System reports |

---

## 📊 Sample Data

After running `flask seed-data`, use these credentials:

| Role | Email | Password |
|------|-------|----------|
| 👑 Admin | admin@hireflow.ai | Admin@123 |
| 💼 Recruiter | sarah.johnson@techcorp.com | Recruiter@123 |
| 👤 Candidate | alex.martinez@gmail.com | Candidate@123 |

---

## 🧪 Testing

```bash
# Run tests
python -m pytest

# With coverage
python -m pytest --cov=backend tests/
```

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🌟 Future Roadmap

- [ ] **Real-time WebSocket notifications** for instant updates
- [ ] **Video interview integration** (Zoom/Google Meet API)
- [ ] **Advanced reporting & export** (PDF reports, Excel with charts)
- [ ] **SSO/OAuth authentication** (Google, LinkedIn, GitHub)
- [ ] **Mobile apps** (React Native / Flutter)
- [ ] **AI-powered job recommendations** using collaborative filtering
- [ ] **Automated interview scheduling** (Calendar API integration)
- [ ] **Multi-language support** (i18n)
- [ ] **Advanced analytics** with predictive hiring models
- [ ] **Integration with job boards** (LinkedIn, Indeed, Naukri)
- [ ] **Resume builder** — In-browser drag-and-drop resume editor
- [ ] **Email templates** — Customizable email notification templates

---

<div align="center">
  <sub>Built with ❤️ using Flask, MySQL, and Google Gemini AI</sub>
  <br>
  <sub>© 2024 HireFlow AI. All rights reserved.</sub>
  <br><br>
  <sub>
    <a href="#-hireflow-ai">Back to Top</a> •
    <a href="#-features">Features</a> •
    <a href="#-screenshots">Screenshots</a> •
    <a href="#-installation">Installation</a> •
    <a href="#-api-documentation">API Docs</a>
  </sub>
</div>
