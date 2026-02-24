# Architecture & Design Decisions

## Overview
This document explains the architectural decisions made in the AI Usage Learning Platform and how they satisfy the functional and non-functional requirements.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Presentation Layer                    │
│  (Django Templates + Bootstrap 5 + Chart.js)                │
│  - Login/Register                                            │
│  - Dashboard with visualizations                             │
│  - Usage logging forms                                       │
│  - Insights display                                          │
│  - Feedback forms                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        Application Layer                     │
│  (Django Views + Forms)                                      │
│  - Authentication (login, register, logout)                  │
│  - Dashboard data aggregation                                │
│  - Usage log management                                      │
│  - Insight generation                                        │
│  - Feedback handling                                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        Business Logic Layer                  │
│  (Models + Signals)                                          │
│  - UserProfile (extended user data)                          │
│  - AIUsageLog (usage tracking)                               │
│  - AIEthicsPolicy (compliance rules)                         │
│  - ComplianceStatus (compliance evaluation)                  │
│  - UserInsight (automated insights)                          │
│  - UserFeedback (user feedback)                              │
│  - Signals (auto profile creation, insight generation)       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  (Django ORM + SQLite)                                       │
│  - User authentication data                                  │
│  - AI usage logs                                             │
│  - Policies and compliance data                              │
│  - Insights and feedback                                     │
└─────────────────────────────────────────────────────────────┘
```

## Design Patterns

### 1. Model-View-Template (MVT)
**Why**: Django's standard pattern ensures separation of concerns.

- **Models**: Data structure and business logic
- **Views**: Request handling and data processing
- **Templates**: Presentation logic

### 2. Repository Pattern (via Django ORM)
**Why**: Abstracts database operations and makes the code database-agnostic.

Example:
```python
AIUsageLog.objects.filter(user=user).order_by('-timestamp')
```

### 3. Observer Pattern (Django Signals)
**Why**: Automatically trigger actions when certain events occur.

Example:
```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
```

### 4. Form Validation Pattern
**Why**: Centralized validation and security.

Example:
```python
class AIUsageLogForm(forms.ModelForm):
    class Meta:
        model = AIUsageLog
        fields = [...]
```

## Data Model Design

### Entity Relationship Diagram

```
User (Django Auth)
  │
  ├─── 1:1 ──→ UserProfile
  │
  ├─── 1:N ──→ AIUsageLog
  │                 │
  │                 └─── N:1 ──→ AIEthicsPolicy
  │
  ├─── 1:N ──→ ComplianceStatus
  │                 │
  │                 └─── N:1 ──→ AIEthicsPolicy
  │
  ├─── 1:N ──→ UserInsight
  │                 │
  │                 └─── N:M ──→ AIUsageLog (related_usage_logs)
  │
  └─── 1:N ──→ UserFeedback
```

### Why This Structure?

1. **UserProfile extends User**: Keeps authentication separate from profile data (Single Responsibility Principle)

2. **AIEthicsPolicy is independent**: Allows multiple versions and policies to coexist

3. **AIUsageLog references Policy**: Tracks which policy was active at the time of usage

4. **ComplianceStatus is calculated**: Periodic snapshots of compliance for historical tracking

5. **UserInsight can reference logs**: Allows detailed insights based on specific usage patterns

## Functional Requirements Mapping

### 1. Personalized AI Usage Dashboard ✅
**Implementation**:
- `dashboard_view()` aggregates user-specific data
- User-filtered queries: `AIUsageLog.objects.filter(user=request.user)`
- Statistics: total, today, week, month usage counts
- Compliance percentage calculation

**Files**: 
- [views.py](dashboard/views.py) - `dashboard_view()`
- [dashboard.html](dashboard/templates/dashboard/dashboard.html)

### 2. Visualizations of AI Usage ✅
**Implementation**:
- Chart.js integration in base template
- Three chart types:
  - Line chart: Daily usage trend (30 days)
  - Pie chart: Usage by AI tool
  - Bar chart: Usage by type
- Data passed as JSON from Django to JavaScript

**Files**:
- [dashboard.html](dashboard/templates/dashboard/dashboard.html) - Chart rendering

### 3. Feedback Submission ✅
**Implementation**:
- UserFeedback model with file upload support
- Status tracking workflow
- Admin panel for reviewing feedback

**Files**:
- [models.py](dashboard/models.py) - `UserFeedback`
- [views.py](dashboard/views.py) - `feedback_view()`
- [feedback.html](dashboard/templates/dashboard/feedback.html)

### 4. Policy Management ✅
**Implementation**:
- AIEthicsPolicy model with versioning
- Admin interface for CRUD operations
- Active policy detection with date ranges
- Compliance evaluation against policies

**Files**:
- [models.py](dashboard/models.py) - `AIEthicsPolicy`
- [admin.py](dashboard/admin.py) - Admin configuration

### 5. User Login ✅
**Implementation**:
- Django authentication system
- Login, register, logout views
- Login required decorator for protected views
- Session management

**Files**:
- [views.py](dashboard/views.py) - Authentication views
- [urls.py](dashboard/urls.py) - Route configuration

### 6. AI Usage Insights ✅
**Implementation**:
- Automated insight generation via signals
- Different insight types: patterns, compliance, achievements, warnings
- Priority-based display
- Read/dismiss functionality

**Files**:
- [models.py](dashboard/models.py) - `UserInsight`
- [signals.py](dashboard/signals.py) - Automatic generation
- [insights.html](dashboard/templates/dashboard/insights.html)

## Non-Functional Requirements

### Usability ✅
**Implementation**:
- Bootstrap 5 for responsive, professional UI
- Intuitive navigation with sidebar
- Clear visual hierarchy
- Contextual help text
- Error messages and success confirmations

**Evidence**: Consistent UI patterns, clear calls-to-action, minimal clicks to complete tasks

### GDPR Compliance ✅
**Implementation**:
1. **Consent Tracking**: `data_collection_consent` field with timestamp
2. **Data Access**: Users can view all their data via dashboard
3. **Data Export**: JSON export of all user data (`export_data_view`)
4. **Data Deletion**: Cascade delete on user removal
5. **Privacy Controls**: Granular settings for analytics and notifications
6. **Transparency**: Clear privacy information in profile

**Files**:
- [models.py](dashboard/models.py) - Consent fields
- [views.py](dashboard/views.py) - `export_data_view()`
- [profile.html](dashboard/templates/dashboard/profile.html) - Privacy controls

## Security Decisions

### 1. CSRF Protection
**Why**: Prevents cross-site request forgery attacks
**How**: Django's CSRF middleware + `{% csrf_token %}` in forms

### 2. Password Security
**Why**: Protects user accounts
**How**: Django's password validators + hashing (PBKDF2)

### 3. SQL Injection Prevention
**Why**: Prevents database attacks
**How**: Django ORM automatically parameterizes queries

### 4. XSS Prevention
**Why**: Prevents script injection
**How**: Django template auto-escaping

### 5. Session Security
**Why**: Protects user sessions
**How**: HTTPOnly cookies, SameSite flag, 2-hour timeout

### 6. Login Required Decorator
**Why**: Protects sensitive views
**How**: `@login_required` on all dashboard views

## Technology Choices

### Django 4+
**Why**:
- Mature, battle-tested framework
- Excellent ORM for database operations
- Built-in authentication and admin
- Strong security features
- Large ecosystem and community

**Alternatives Considered**: Flask (too minimal), FastAPI (REST-focused)

### SQLite
**Why**:
- Zero configuration
- Perfect for development and small deployments
- Single file database (easy backup)
- Can migrate to PostgreSQL later

**Production Alternative**: PostgreSQL for better concurrency

### Bootstrap 5
**Why**:
- Professional UI components
- Responsive out of the box
- Extensive documentation
- No build process needed

**Alternatives Considered**: Tailwind (requires build), Material UI (heavier)

### Chart.js
**Why**:
- Lightweight (64KB)
- Beautiful, responsive charts
- Simple API
- No jQuery dependency

**Alternatives Considered**: D3.js (steeper learning curve), Plotly (heavier)

## Scalability Considerations

### Current Scale
- Suitable for: 100-1000 users
- Database: SQLite (up to ~100 concurrent users)
- Storage: File system for uploads

### Future Scaling

If needed to scale to 10,000+ users:

1. **Database**: Migrate to PostgreSQL
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           # ...
       }
   }
   ```

2. **Caching**: Add Redis for session storage and query caching
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

3. **File Storage**: Move to cloud storage (S3, Azure Blob)
   ```python
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   ```

4. **Load Balancing**: Deploy multiple application servers behind nginx

5. **Database Optimization**: Add indexes, use select_related/prefetch_related
   ```python
   AIUsageLog.objects.select_related('user', 'policy').filter(...)
   ```

## Testing Strategy

### Unit Tests
- Model methods (compliance checking, validation)
- Form validation
- Signal handlers

### Integration Tests
- View responses
- Authentication flow
- Dashboard data aggregation

### Manual Testing Checklist
- [ ] User registration and login
- [ ] Dashboard displays correct data
- [ ] Charts render properly
- [ ] Usage logging works
- [ ] Compliance calculation is accurate
- [ ] Insights are generated
- [ ] Feedback submission works
- [ ] Data export works
- [ ] Admin panel is functional

## Performance Optimizations

### Implemented
1. **Database Indexes**: On frequently queried fields
   ```python
   indexes = [
       models.Index(fields=['user', '-timestamp']),
   ]
   ```

2. **Query Optimization**: Limit results in recent activity
   ```python
   recent_logs = AIUsageLog.objects.filter(user=user)[:10]
   ```

3. **Pagination**: For usage history (25 per page)

4. **Chart Data Limiting**: Last 30 days only for trend chart

### Future Optimizations
1. Query result caching
2. Database connection pooling
3. Static file CDN
4. Lazy loading for images
5. Background tasks for insight generation (Celery)

## Maintenance & Extensibility

### Adding New Features

**Example: Add a new AI tool**

1. Update model choices:
   ```python
   AI_TOOL_CHOICES = [
       # ... existing
       ('new_tool', 'New AI Tool'),
   ]
   ```

2. Create and run migration:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. No template changes needed (dynamic rendering)

### Code Organization

```
dashboard/
├── models.py       # Data models (single source of truth)
├── views.py        # Request handlers (business logic)
├── forms.py        # Form validation (input handling)
├── urls.py         # URL routing (API endpoints)
├── admin.py        # Admin configuration (management)
├── signals.py      # Event handlers (automation)
└── tests.py        # Test cases (quality assurance)
```

**Benefits**:
- Clear separation of concerns
- Easy to locate functionality
- Maintainable and testable

## Deployment Checklist

Before production deployment:

- [ ] Set `DEBUG = False`
- [ ] Change `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL/MySQL
- [ ] Set up HTTPS
- [ ] Configure email backend
- [ ] Set up logging
- [ ] Use environment variables
- [ ] Run `collectstatic`
- [ ] Set up automated backups
- [ ] Configure error monitoring (Sentry)
- [ ] Load test the application

## Conclusion

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Scalability path
- ✅ Security by default
- ✅ Easy maintenance
- ✅ GDPR compliance
- ✅ Comprehensive testing
- ✅ Professional user experience

The design supports all functional requirements while maintaining code quality and extensibility.
