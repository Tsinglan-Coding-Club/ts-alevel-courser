# Computer Science Learning Platform

A comprehensive Django-based learning platform for Cambridge International A-Level and IGCSE Computer Science past papers with integrated PDF viewer, progress tracking, and multi-subject support.

## 🚀 Features

- **Multi-Subject Support**: CIE A-Level (9618) and IGCSE (0984) Computer Science
- **User Authentication**: Register, login, logout with "Remember Me" functionality
- **Unit-based Organization**: 20 units covering all CS topics per subject
- **Question Browser**: Browse past paper questions by unit and year
- **Integrated PDF Viewer**: View questions, mark schemes, and syllabus with page navigation
- **Progress Tracking**: Mark questions and past papers as "Kill" (completed) or "Save" (bookmarked)
- **History Tracking**: Track recently viewed questions
- **Search Functionality**: Search questions by code
- **Responsive Design**: Optimized for all devices including landscape mode
- **Admin Dashboard**: Comprehensive backend for content management

## 🛠️ Technology Stack

### Backend
- **Django 5.2**: Web framework
- **Python 3.11+**: Programming language
- **SQLite**: Database (development)
- **uv**: Fast package manager (10-100x faster than pip)

### Frontend
- **Bootstrap 5.3.0**: CSS framework (local)
- **Vanilla JavaScript**: No frontend framework dependencies
- **PDF.js 3.11.174**: PDF rendering (local)

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- uv package manager

### Quick Start

1. **Install uv** (if not already installed):
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Clone and setup**:
```bash
git clone https://github.com/Tsinglan-Coding-Club/ts-alevel-courser.git
cd ts-alevel-courser
```

3. **Install dependencies**:
```bash
uv sync
```

4. **Initialize database**:
```bash
uv run python manage.py migrate
```

5. **Create admin user**:
```bash
uv run python manage.py createsuperuser
```

6. **Load sample data**:
```bash
uv run python populate_data_v2.py
```

7. **Run development server**:
```bash
uv run python manage.py runserver
```

8. **Access the application**:
- Main site: http://localhost:8000/
- Admin panel: http://localhost:8000/admin/

## 📁 Project Structure

```
ts-alevel-courser/
|-- accounts/              # User authentication app
|   |-- models.py          # UserProfile model
|   |-- views.py           # Login, register, profile views
|   |-- forms.py           # Authentication forms
|   \-- urls.py            # Account URLs
|-- pastpaper/             # Core functionality app
|   |-- models.py          # Subject, Unit, Question, PastPaper, UserTag, PastPaperTag
|   |-- views.py           # Home view & AJAX/API endpoints
|   |-- admin.py           # Admin configurations
|   \-- urls.py            # Past paper URLs
|-- config/                # Project configuration
|   |-- settings.py        # Django settings
|   |-- urls.py            # Root URL configuration
|   \-- wsgi.py            # WSGI configuration
|-- templates/             # HTML templates
|   |-- base.html          # Base template with dynamic navigation
|   |-- accounts/          # Account templates
|   \-- pastpaper/         # Past paper templates
|-- static/                # Static files (local)
|   |-- css/               # Bootstrap 5.3.0
|   |-- js/                # PDF.js 3.11.174
|   \-- images/            # Images
|-- media/                 # PDF files + avatar
|-- manage.py              # Django management script
|-- populate_data_v2.py    # Sample data script
|-- pyproject.toml         # Project configuration
|-- uv.lock                # Locked dependencies
\-- README.md              # This file
```

## 🗄️ Database Schema

### Core Models

**Subject**
- `code`: Subject code (e.g., "cs", "ig")
- `name`: Full subject name
- `exam_code`: Exam code / syllabus identifier (e.g., 9618)

**Unit**
- `subject`: Foreign key to Subject
- `unit_num`: Integer (1-20)
- `name`: Unit name (displays with subject code)

**Question**
- `code`: Question code (e.g., "9618_s23_11-Q1")
- `subject`: Foreign key to Subject
- `unit`: Foreign key to Unit
- `qpage`: Question paper page number
- `apage`: Mark scheme page number
- `spage`: Syllabus page number

**PastPaper**
- `code`: Paper code (e.g., "9618_s23_11")
- `subject`: Foreign key to Subject
- `year`: Year (e.g., 2023)
- `session`: Session (e.g., "s" for summer)
- `paper_num`: Paper number (e.g., 11)

**PastPaperTag**
- `user`: Foreign key to User
- `past_paper`: Foreign key to PastPaper
- `kill`: Boolean (completed)
- `saved`: Boolean (bookmarked)

**UserTag**
- `user`: Foreign key to User
- `question`: Foreign key to Question
- `kill`: Boolean (completed)
- `saved`: Boolean (bookmarked)

**HistoryRecord**
- `user`: Foreign key to User
- `question`: Foreign key to Question
- `visited_at`: Timestamp

## 🔌 API Endpoints

### POST Endpoints

- `/get_units/`: Get list of units for current subject
- `/get_list/`: Get questions for a unit
- `/get_past_papers/`: Fetch past papers plus each paper's Kill/Save state for the current user
- `/update_user_tags/`: Update tags for questions or past papers (Kill/Save)
- `/get_history/`: Get user's browsing history
- `/update_history/`: Add question to history
- `/get_question_info/`: Get question details

## 🎨 UI Features

### Color-coded Questions
- **Green background**: Completed (Kill)
- **Yellow background**: Bookmarked (Save)
- **Blue background**: Currently selected
- Works the same for questions and full past papers

### PDF Controls
- **Question Paper**: View question PDF with page navigation
- **Mark Scheme**: View mark scheme PDF
- **Syllabus**: View syllabus PDF with specific page
- **PPT**: View unit presentation (if available)

### Subject Switching
- Dynamic navigation bar showing current subject
- Switch between A-Level and IGCSE seamlessly
- Empty subjects display properly with blank data

## 🔐 Default Credentials

**Admin Account**
- Username: `admin`
- Password: `admin123`

**Test User**
- Username: `testuser`
- Password: `test123`

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
X_FRAME_OPTIONS=SAMEORIGIN
```

2. **Database**: Use PostgreSQL or MySQL instead of SQLite

3. **Static Files**: Configure Nginx to serve static files

4. **HTTPS**: Set up SSL certificate

5. **Dependencies**: Install production dependencies
```bash
uv sync --no-dev
```

See `DEPLOYMENT.md` for detailed deployment guide.

## 📚 Documentation

- **CHANGELOG.md**: Version history and updates
- **CONTRIBUTING.md**: Contribution guidelines
- **DEPLOYMENT.md**: Production deployment guide
- **UV_USAGE.md**: uv package manager usage guide
- **ADMIN_TEST_REPORT.md**: Admin backend test report

## 🧪 Testing

All core features have been tested:
- User authentication and authorization
- Subject switching and navigation
- PDF loading and page navigation
- Kill/Save functionality for questions and past papers
- Admin backend (all models)
- Responsive layout (including landscape devices)

## 🔧 Development

### Using uv

```bash
# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Update dependencies
uv lock --upgrade

# Run Django commands
uv run python manage.py <command>

# Run tests
uv run pytest
```

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use Flake8 for linting

## 📊 Project Statistics

- **Version**: 1.2.0
- **Python Files**: 243
- **PDF Files**: 21 (9618 subject)
- **Static Resources**: Local (no CDN)
- **Database**: SQLite with sample data
- **Package Manager**: uv 0.9.5

## 🐛 Known Issues

None - All reported bugs have been fixed in v1.2.0

## 🔮 Future Enhancements

- [ ] Add more subjects (0984, 9608, etc.)
- [ ] Bulk question import functionality
- [ ] Learning progress analytics
- [ ] Question notes feature
- [ ] REST API endpoints
- [ ] Mobile app support

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Bootstrap 5 for UI components
- PDF.js for PDF rendering
- Django community for excellent documentation
- uv team for blazing-fast package management

## 📧 Support

For issues and questions:
1. Check documentation in `/docs`
2. Review `CHANGELOG.md` for known issues
3. Submit an issue on GitHub

---

**Built with ❤️ for Computer Science students**
