# 📚 StudyShare - Student Notes Sharing Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**A collaborative, mobile-first platform for students to share notes and learn together.**

[Features](#-features) • [Quick Start](#-quick-start) • [Deployment](#-deployment) • [Tech Stack](#-tech-stack)

</div>

---

## ✨ Features

### 📁 Organized Note System
- **Department → Subject → Unit → Notes** hierarchy
- Browse and filter notes easily
- Search across all content
- View counts and popularity tracking

### 📤 Easy Upload
- Drag & drop file upload
- Supports **PDF, PNG, JPG, JPEG**
- Automatic thumbnail generation
- File validation (max 16MB)

### ⚡ Real-time Collaboration
- **Live Notes Editor** - Type together in real-time
- WebSocket-powered instant sync
- Auto-save functionality
- See active collaborators

### 📱 QR Code Sharing
- Instant QR code for every note
- Easy mobile sharing in class
- Copy link with one click

### 🌙 Modern UI/UX
- **Mobile-first** responsive design
- Dark mode toggle
- Smooth **anime.js** animations
- Clean teal color theme
- Beautiful typography with Outfit & DM Sans fonts

### 🔓 No Barriers
- **No login required**
- Instant access to all features
- Share and collaborate freely

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/student-notes-platform.git
cd student-notes-platform
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the development server**
```bash
python run.py
```

5. **Open your browser**
```
http://localhost:5000
```

That's it! The database will be created automatically with sample departments and subjects.

---

## 📁 Project Structure

```
student-notes-platform/
├── backend/
│   ├── __init__.py
│   ├── app.py          # Flask app factory & SocketIO
│   ├── api.py          # REST API routes
│   ├── config.py       # Configuration settings
│   ├── models.py       # SQLAlchemy models
│   └── utils.py        # Helper functions
├── templates/
│   ├── base.html       # Base template with nav/footer
│   ├── home.html       # Homepage
│   ├── department.html # Department page
│   ├── subject.html    # Subject page with units
│   ├── notes_list.html # Notes listing
│   ├── view_note.html  # Note viewer with PDF.js
│   ├── live_notes_list.html
│   ├── live_note.html  # Real-time editor
│   ├── search.html     # Search & filter
│   ├── upload.html     # Upload form
│   ├── about.html      # About page
│   ├── 404.html
│   └── 500.html
├── static/             # Static assets
├── uploads/            # Uploaded files
│   └── thumbnails/     # Generated thumbnails
├── database/           # SQLite database
├── .github/
│   └── workflows/
│       └── deploy.yml  # CI/CD pipeline
├── requirements.txt
├── run.py              # Development entry point
├── wsgi.py             # Production entry point
├── Procfile            # Heroku/Railway config
├── render.yaml         # Render.com config
├── railway.json        # Railway config
└── README.md
```

---

## 🛠 Tech Stack

### Backend
- **Flask 3.0** - Python web framework
- **Flask-SQLAlchemy** - ORM for database
- **Flask-SocketIO** - WebSocket support
- **SQLite** - Lightweight database
- **Pillow** - Image processing
- **PyMuPDF** - PDF thumbnail generation

### Frontend
- **TailwindCSS** - Utility-first CSS
- **Anime.js** - Smooth animations
- **Quill** - Rich text editor
- **PDF.js** - PDF viewer
- **Socket.IO Client** - Real-time sync
- **QRCode.js** - QR code generation

### Fonts
- **Outfit** - Display headings
- **DM Sans** - Body text
- **JetBrains Mono** - Code

---

## ☁️ Deployment

### Deploy to Render (Recommended)

1. Fork this repository
2. Create a [Render](https://render.com) account
3. Click **New → Web Service**
4. Connect your GitHub repo
5. Render will auto-detect the `render.yaml` config
6. Click **Create Web Service**

### Deploy to Railway

1. Fork this repository
2. Create a [Railway](https://railway.app) account
3. Click **New Project → Deploy from GitHub**
4. Select your forked repo
5. Railway will auto-detect the config
6. Done! Your app is live.

### Environment Variables

For production, set these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `FLASK_ENV` | Environment mode | `production` |
| `DATABASE_URL` | Database connection | SQLite path |
| `PORT` | Server port | 5000 |

### CI/CD with GitHub Actions

The included workflow (`.github/workflows/deploy.yml`):
1. Tests the application on every push
2. Auto-deploys to Railway/Render on main branch

To enable:
1. Add `RAILWAY_TOKEN` secret for Railway deployment
2. Add `RENDER_DEPLOY_HOOK` secret for Render deployment

---

## 📝 API Reference

### Departments
- `GET /api/departments` - List all departments
- `GET /api/departments/<slug>` - Get department by slug
- `POST /api/departments` - Create department

### Subjects
- `GET /api/departments/<slug>/subjects` - List subjects in department
- `POST /api/departments/<slug>/subjects` - Create subject

### Units
- `GET /api/subjects/<id>/units` - List units in subject
- `POST /api/subjects/<id>/units` - Create unit

### Notes
- `GET /api/units/<id>/notes` - List notes in unit
- `POST /api/units/<id>/notes` - Upload note (multipart/form-data)
- `GET /api/notes/<id>` - Get note (increments view count)
- `GET /api/notes/<id>/download` - Download note file
- `GET /api/notes/recent` - Recent uploads
- `GET /api/notes/popular` - Most viewed notes

### Live Notes
- `GET /api/live-notes` - List all live notes
- `POST /api/live-notes` - Create live note
- `GET /api/live-notes/<slug>` - Get live note
- `PUT /api/live-notes/<slug>` - Update content

### Search
- `GET /api/search?q=<query>&department=<slug>&subject=<slug>` - Search

### Stats
- `GET /api/stats` - Platform statistics

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - The web framework
- [TailwindCSS](https://tailwindcss.com/) - CSS framework
- [Anime.js](https://animejs.com/) - Animation library
- [PDF.js](https://mozilla.github.io/pdf.js/) - PDF rendering
- [Quill](https://quilljs.com/) - Rich text editor

---

<div align="center">

**Made with ❤️ for students everywhere**

No login required. Just share and learn!

</div>
