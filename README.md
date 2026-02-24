# AI Usage Learning Platform

A comprehensive Django-based platform for tracking and analyzing AI tool usage in educational settings. This platform helps students monitor their AI usage, maintain compliance with ethical AI policies, and receive personalized insights about their learning behavior.

## Features

### ✨ Core Features
- **Personalized AI Usage Dashboard**: View individual AI usage statistics and trends
- **Visual Analytics**: Interactive charts using Chart.js for usage patterns and trends
- **Compliance Tracking**: Monitor compliance with AI ethics policies
- **Personalized Insights**: Receive automated recommendations based on usage patterns
- **Feedback System**: Submit feedback, bug reports, and feature requests
- **GDPR Compliant**: Full data export and privacy controls

### 📊 Dashboard Features
- Real-time usage statistics (today, week, month, total)
- Compliance status indicators
- Usage trends over time (line chart)
- AI tool distribution (pie chart)
- Usage type analysis (bar chart)
- Recent activity log
- Personalized insights

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development)
- **Frontend**: Django Templates + Bootstrap 5
- **Charts**: Chart.js 4.3
- **Icons**: Bootstrap Icons
- **Authentication**: Django Auth System

## Project Structure

```
Vibes/
├── manage.py
├── requirements.txt
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── dashboard/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── forms.py
    ├── signals.py
    ├── tests.py
    ├── migrations/
    │   └── __init__.py
    └── templates/
        └── dashboard/
            ├── base.html
            ├── login.html
            ├── register.html
            ├── dashboard.html
            ├── log_usage.html
            ├── usage_history.html
            ├── insights.html
            ├── feedback.html
            └── profile.html
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)

### Step 1: Clone or Download the Project

```bash
cd "C:\Users\krist\OneDrive\Documents\GitHub\Vibes"
```

### Step 2: Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 6: Create Sample Data (Optional)

```bash
python manage.py shell
```

Then in the Python shell:

```python
from django.contrib.auth.models import User
from dashboard.models import AIEthicsPolicy, AIUsageLog
from django.utils import timezone
from datetime import timedelta

# Create a sample AI ethics policy
policy = AIEthicsPolicy.objects.create(
    title="Institutional AI Usage Policy",
    description="Guidelines for responsible AI tool usage in academic work.",
    version="1.0",
    status="active",
    max_daily_usage=50,
    max_weekly_usage=200,
    effective_from=timezone.now().date(),
    rules={
        "citation_required": True,
        "plagiarism_check": True,
        "transparency": True
    }
)

# Create sample usage logs for your user (replace 'yourusername')
user = User.objects.get(username='yourusername')

for i in range(10):
    AIUsageLog.objects.create(
        user=user,
        ai_tool='chatgpt',
        usage_type='code_generation',
        description=f'Sample usage log {i+1}',
        duration_minutes=15,
        policy=policy
    )

print("Sample data created successfully!")
exit()
```

### Step 7: Run the Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

### Step 8: Access the Application

- **Main Dashboard**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/login/
- **Register**: http://127.0.0.1:8000/register/

## Usage Guide

### For Students

1. **Register an Account**: Create your account using the registration page
2. **Log AI Usage**: Click "Log AI Usage" to record your interactions with AI tools
3. **View Dashboard**: Monitor your usage statistics and compliance status
4. **Check Insights**: Review personalized insights and recommendations
5. **Submit Feedback**: Report issues or suggest improvements
6. **Manage Profile**: Update your preferences and privacy settings

### For Administrators

1. **Access Admin Panel**: Navigate to /admin/ and log in with superuser credentials
2. **Manage Policies**: Create and update AI ethics policies
3. **Monitor Compliance**: Review user compliance status
4. **Review Feedback**: Respond to user feedback and bug reports
5. **Generate Reports**: Analyze usage patterns across all users

## Data Models

### UserProfile
- Extended user information
- Privacy and consent settings
- Notification preferences

### AIEthicsPolicy
- Policy definitions and rules
- Usage thresholds (daily/weekly limits)
- Effective date ranges

### AIUsageLog
- Individual AI tool usage records
- Compliance status
- Context (course, assignment)
- Metadata (duration, tokens)

### ComplianceStatus
- Periodic compliance evaluation
- Compliance scores and levels
- Violation tracking

### UserInsight
- Automated personalized insights
- Usage pattern analysis
- Recommendations and warnings

### UserFeedback
- User-submitted feedback
- Bug reports and feature requests
- Status tracking

## API Endpoints (URLs)

| Endpoint | View | Description |
|----------|------|-------------|
| `/` | dashboard_view | Main dashboard |
| `/login/` | login_view | User login |
| `/register/` | register_view | User registration |
| `/logout/` | logout_view | User logout |
| `/log-usage/` | log_usage_view | Log new AI usage |
| `/usage-history/` | usage_history_view | View usage history |
| `/insights/` | insights_view | View insights |
| `/insights/<id>/dismiss/` | dismiss_insight_view | Dismiss insight |
| `/feedback/` | feedback_view | Submit feedback |
| `/profile/` | profile_view | Manage profile |
| `/export-data/` | export_data_view | Export user data (GDPR) |

## GDPR Compliance

This platform implements GDPR requirements:

- ✅ **User Consent**: Data collection requires explicit consent
- ✅ **Data Access**: Users can view all their stored data
- ✅ **Data Export**: Users can export their data in JSON format
- ✅ **Data Deletion**: Administrators can delete user data upon request
- ✅ **Privacy Controls**: Users can control analytics and notifications
- ✅ **Transparent Processing**: Clear information about data usage
- ✅ **Secure Storage**: Password hashing, session security

## Security Features

- CSRF protection enabled
- Session security (HTTPOnly cookies, SameSite)
- Password validation requirements
- SQL injection protection (Django ORM)
- XSS protection (template auto-escaping)
- Secure headers configuration

## Testing

Run tests using:

```bash
python manage.py test dashboard
```

## Customization

### Modifying Compliance Thresholds

Edit policies in the admin panel or modify default values in `models.py`:

```python
max_daily_usage = models.IntegerField(default=100)  # Change default
max_weekly_usage = models.IntegerField(default=500)  # Change default
```

### Adding New AI Tools

Add to `AIUsageLog.AI_TOOL_CHOICES` in `models.py`:

```python
AI_TOOL_CHOICES = [
    ('chatgpt', 'ChatGPT'),
    ('copilot', 'GitHub Copilot'),
    ('your_tool', 'Your AI Tool'),  # Add here
    # ...
]
```

### Customizing Colors

Modify CSS variables in `base.html`:

```css
:root {
    --primary-color: #4f46e5;  /* Change primary color */
    --secondary-color: #7c3aed;  /* Change secondary color */
    /* ... */
}
```

## Troubleshooting

### Migration Issues

```bash
python manage.py makemigrations --empty dashboard
python manage.py migrate --fake dashboard
```

### Database Reset

```bash
# Delete database
del db.sqlite3  # Windows
rm db.sqlite3    # macOS/Linux

# Recreate
python manage.py migrate
python manage.py createsuperuser
```

### Static Files Issues

```bash
python manage.py collectstatic --noinput
```

## Production Deployment

Before deploying to production:

1. **Set DEBUG to False** in `settings.py`
2. **Change SECRET_KEY** to a secure random value
3. **Configure ALLOWED_HOSTS** with your domain
4. **Use PostgreSQL or MySQL** instead of SQLite
5. **Set up HTTPS** (SECURE_SSL_REDIRECT = True)
6. **Configure email backend** for notifications
7. **Set up proper logging**
8. **Use environment variables** for sensitive settings

## Architecture Decisions

### Why Django?
- Robust ORM for database management
- Built-in authentication system
- Excellent security features
- Admin panel for easy management
- Scalable and maintainable

### Why SQLite?
- Zero configuration for development
- Perfect for small to medium deployments
- Easy to backup (single file)
- Can migrate to PostgreSQL/MySQL if needed

### Why Bootstrap + Chart.js?
- Bootstrap: Professional UI with minimal effort
- Chart.js: Lightweight, responsive charts
- CDN delivery: No build process required
- Wide browser compatibility

### Design Patterns Used
- **MVT (Model-View-Template)**: Django's standard pattern
- **Signals**: Automatic profile creation and insight generation
- **Form Handling**: Django forms for validation and security
- **Middleware**: Security and session management
- **ORM**: Database abstraction and query optimization

## Requirements Mapping

| Requirement | Implementation |
|-------------|----------------|
| Personalized dashboard | ✅ Dashboard view with user-specific stats |
| Usage visualizations | ✅ Chart.js charts (line, pie, bar) |
| Feedback submission | ✅ Feedback form with file upload |
| Policy management | ✅ Admin panel for policy CRUD |
| User login | ✅ Django authentication |
| Usage insights | ✅ Automated insight generation |
| Easy to use | ✅ Intuitive Bootstrap UI |
| GDPR compliance | ✅ Consent tracking, data export |

## License

This project is created for educational purposes.

## Support

For issues, questions, or contributions:
- Create an issue in the repository
- Contact via the feedback form in the application

## Contributors

- Initial development: Your Name
- Framework: Django
- UI: Bootstrap 5
- Charts: Chart.js

## Version History

- **v1.0.0** (2024): Initial release
  - User dashboard with visualizations
  - AI usage tracking
  - Compliance monitoring
  - Insights generation
  - Feedback system
  - GDPR compliance features
