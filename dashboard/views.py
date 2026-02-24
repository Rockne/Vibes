"""
Views for AI Usage Learning Platform Dashboard.

Implements personalized dashboards, usage tracking, insights, and feedback.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta, datetime
import json

from .models import (
    UserProfile,
    AIUsageLog,
    AIEthicsPolicy,
    ComplianceStatus,
    UserInsight,
    UserFeedback
)
from .forms import (
    AIUsageLogForm,
    UserProfileForm,
    UserFeedbackForm,
    UserRegistrationForm
)


def login_view(request):
    """
    Handle user login.
    
    GET: Display login form
    POST: Authenticate and log in user
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'dashboard/login.html', {'form': form})


def register_view(request):
    """
    Handle user registration.
    
    GET: Display registration form
    POST: Create new user account
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('dashboard:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'dashboard/register.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('dashboard:login')


@login_required
def dashboard_view(request):
    """
    Main personalized dashboard view.
    
    Displays:
    - AI usage statistics
    - Compliance status
    - Recent activity
    - Insights and recommendations
    - Usage trends (charts)
    """
    user = request.user
    
    # Get active policy
    active_policy = AIEthicsPolicy.objects.filter(
        status='active',
        effective_from__lte=timezone.now().date()
    ).filter(
        Q(effective_until__gte=timezone.now().date()) | Q(effective_until__isnull=True)
    ).first()
    
    # Get usage statistics
    total_usage = AIUsageLog.objects.filter(user=user).count()
    
    # Today's usage
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_usage = AIUsageLog.objects.filter(user=user, timestamp__gte=today_start).count()
    
    # This week's usage
    week_start = timezone.now() - timedelta(days=7)
    week_usage = AIUsageLog.objects.filter(user=user, timestamp__gte=week_start).count()
    
    # This month's usage
    month_start = timezone.now() - timedelta(days=30)
    month_usage = AIUsageLog.objects.filter(user=user, timestamp__gte=month_start).count()
    
    # Compliance status
    compliance_status = None
    compliance_percentage = 100
    if active_policy:
        # Calculate compliance
        recent_logs = AIUsageLog.objects.filter(
            user=user,
            timestamp__gte=week_start
        )
        total_recent = recent_logs.count()
        compliant_recent = recent_logs.filter(is_compliant=True).count()
        
        if total_recent > 0:
            compliance_percentage = int((compliant_recent / total_recent) * 100)
        
        # Determine compliance level
        if compliance_percentage >= 90:
            compliance_level = 'excellent'
        elif compliance_percentage >= 75:
            compliance_level = 'good'
        elif compliance_percentage >= 50:
            compliance_level = 'warning'
        else:
            compliance_level = 'violation'
        
        compliance_status = {
            'level': compliance_level,
            'percentage': compliance_percentage,
            'policy': active_policy
        }
    
    # Recent activity (last 10 logs)
    recent_logs = AIUsageLog.objects.filter(user=user).order_by('-timestamp')[:10]
    
    # Unread insights
    unread_insights = UserInsight.objects.filter(
        user=user,
        is_read=False,
        is_dismissed=False
    ).order_by('-priority', '-generated_at')[:5]
    
    # Usage by tool (pie chart data)
    usage_by_tool = AIUsageLog.objects.filter(user=user).values('ai_tool').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Usage by type (bar chart data)
    usage_by_type = AIUsageLog.objects.filter(user=user).values('usage_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Daily usage trend (last 30 days for line chart)
    daily_usage = []
    for i in range(29, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        date_start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        date_end = timezone.make_aware(datetime.combine(date, datetime.max.time()))
        count = AIUsageLog.objects.filter(
            user=user,
            timestamp__gte=date_start,
            timestamp__lte=date_end
        ).count()
        daily_usage.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    context = {
        'total_usage': total_usage,
        'today_usage': today_usage,
        'week_usage': week_usage,
        'month_usage': month_usage,
        'compliance_status': compliance_status,
        'recent_logs': recent_logs,
        'unread_insights': unread_insights,
        'usage_by_tool': json.dumps(list(usage_by_tool)),
        'usage_by_type': json.dumps(list(usage_by_type)),
        'daily_usage': json.dumps(daily_usage),
        'active_policy': active_policy,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def log_usage_view(request):
    """
    Log new AI usage entry.
    
    GET: Display form to log usage
    POST: Create new usage log
    """
    if request.method == 'POST':
        form = AIUsageLogForm(request.POST)
        if form.is_valid():
            usage_log = form.save(commit=False)
            usage_log.user = request.user
            
            # Get active policy
            active_policy = AIEthicsPolicy.objects.filter(
                status='active',
                effective_from__lte=timezone.now().date()
            ).filter(
                Q(effective_until__gte=timezone.now().date()) | Q(effective_until__isnull=True)
            ).first()
            
            if active_policy:
                usage_log.policy = active_policy
            
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                usage_log.ip_address = x_forwarded_for.split(',')[0]
            else:
                usage_log.ip_address = request.META.get('REMOTE_ADDR')
            
            # Get user agent
            usage_log.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            usage_log.save()
            messages.success(request, 'AI usage logged successfully!')
            return redirect('dashboard:dashboard')
    else:
        form = AIUsageLogForm()
    
    return render(request, 'dashboard/log_usage.html', {'form': form})


@login_required
def usage_history_view(request):
    """
    Display full usage history with filtering and pagination.
    """
    usage_logs = AIUsageLog.objects.filter(user=request.user).order_by('-timestamp')
    
    # Filter by AI tool
    tool_filter = request.GET.get('tool')
    if tool_filter:
        usage_logs = usage_logs.filter(ai_tool=tool_filter)
    
    # Filter by usage type
    type_filter = request.GET.get('type')
    if type_filter:
        usage_logs = usage_logs.filter(usage_type=type_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        usage_logs = usage_logs.filter(timestamp__gte=date_from)
    if date_to:
        usage_logs = usage_logs.filter(timestamp__lte=date_to)
    
    # Pagination
    paginator = Paginator(usage_logs, 25)  # Show 25 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter choices
    ai_tools = AIUsageLog.AI_TOOL_CHOICES
    usage_types = AIUsageLog.USAGE_TYPE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'ai_tools': ai_tools,
        'usage_types': usage_types,
        'current_filters': {
            'tool': tool_filter,
            'type': type_filter,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    
    return render(request, 'dashboard/usage_history.html', context)


@login_required
def insights_view(request):
    """
    Display personalized insights and recommendations.
    """
    insights = UserInsight.objects.filter(
        user=request.user,
        is_dismissed=False
    ).order_by('-priority', '-generated_at')
    
    # Mark insights as read when viewed
    unread_insights = insights.filter(is_read=False)
    unread_insights.update(is_read=True)
    
    context = {
        'insights': insights,
    }
    
    return render(request, 'dashboard/insights.html', context)


@login_required
def dismiss_insight_view(request, insight_id):
    """Dismiss an insight."""
    insight = get_object_or_404(UserInsight, id=insight_id, user=request.user)
    insight.is_dismissed = True
    insight.save()
    messages.success(request, 'Insight dismissed.')
    return redirect('dashboard:insights')


@login_required
def feedback_view(request):
    """
    Submit feedback.
    
    GET: Display feedback form
    POST: Submit feedback
    """
    if request.method == 'POST':
        form = UserFeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback! We will review it shortly.')
            return redirect('dashboard:dashboard')
    else:
        form = UserFeedbackForm()
    
    # Get user's previous feedback
    previous_feedback = UserFeedback.objects.filter(user=request.user).order_by('-submitted_at')[:10]
    
    context = {
        'form': form,
        'previous_feedback': previous_feedback,
    }
    
    return render(request, 'dashboard/feedback.html', context)


@login_required
def profile_view(request):
    """
    View and edit user profile.
    """
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    # Get usage summary
    usage_summary = profile.get_usage_summary()
    
    context = {
        'form': form,
        'profile': profile,
        'usage_summary': usage_summary,
    }
    
    return render(request, 'dashboard/profile.html', context)


@login_required
def export_data_view(request):
    """
    Export user data (GDPR compliance).
    
    Allows users to download all their data in JSON format.
    """
    import json
    from django.http import HttpResponse
    
    user = request.user
    profile = user.profile
    
    # Collect all user data
    data = {
        'user': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
        },
        'profile': {
            'student_id': profile.student_id,
            'department': profile.department,
            'enrollment_date': profile.enrollment_date.isoformat(),
            'data_collection_consent': profile.data_collection_consent,
            'consent_date': profile.consent_date.isoformat() if profile.consent_date else None,
        },
        'usage_logs': list(AIUsageLog.objects.filter(user=user).values(
            'ai_tool', 'usage_type', 'description', 'course_code',
            'duration_minutes', 'tokens_used', 'is_compliant', 'timestamp'
        )),
        'insights': list(UserInsight.objects.filter(user=user).values(
            'insight_type', 'title', 'message', 'priority', 'generated_at'
        )),
        'feedback': list(UserFeedback.objects.filter(user=user).values(
            'feedback_type', 'title', 'description', 'status', 'submitted_at'
        )),
    }
    
    # Convert to JSON
    json_data = json.dumps(data, indent=2, default=str)
    
    # Create response
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="ai_usage_data_{user.username}.json"'
    
    messages.success(request, 'Your data has been exported.')
    return response
