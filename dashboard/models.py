"""
Models for AI Usage Learning Platform

This module defines the data models for tracking AI usage, compliance policies,
user insights, and feedback. Designed with GDPR compliance in mind.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import json


class UserProfile(models.Model):
    """
    Extended user profile with AI usage preferences and settings.
    
    Designed for GDPR compliance with user consent tracking and data export capabilities.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    
    # Privacy and GDPR settings
    data_collection_consent = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    allow_analytics = models.BooleanField(default=True)
    
    # User preferences
    email_notifications = models.BooleanField(default=True)
    weekly_summary = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - Profile"
    
    def get_usage_summary(self):
        """Get summary of AI usage for this user."""
        total_usage = self.user.ai_usage_logs.count()
        this_week = self.user.ai_usage_logs.filter(
            timestamp__gte=timezone.now() - timedelta(days=7)
        ).count()
        return {'total': total_usage, 'this_week': this_week}


class AIEthicsPolicy(models.Model):
    """
    AI Ethics Policies for compliance evaluation.
    
    Administrators can create and manage policies that define ethical AI usage.
    """
    POLICY_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    version = models.CharField(max_length=20, default='1.0')
    status = models.CharField(max_length=20, choices=POLICY_STATUS_CHOICES, default='draft')
    
    # Policy rules (stored as JSON for flexibility)
    rules = models.JSONField(default=dict, help_text='Policy rules in JSON format')
    
    # Compliance thresholds
    max_daily_usage = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text='Maximum AI interactions per day'
    )
    max_weekly_usage = models.IntegerField(
        default=500,
        validators=[MinValueValidator(1)],
        help_text='Maximum AI interactions per week'
    )
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_policies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_ethics_policy'
        verbose_name = 'AI Ethics Policy'
        verbose_name_plural = 'AI Ethics Policies'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def is_active(self):
        """Check if policy is currently active."""
        today = timezone.now().date()
        if self.status != 'active':
            return False
        if self.effective_from > today:
            return False
        if self.effective_until and self.effective_until < today:
            return False
        return True


class AIUsageLog(models.Model):
    """
    Tracks individual AI usage events for students.
    
    Each interaction with an AI tool is logged with metadata for analysis and compliance.
    """
    AI_TOOL_CHOICES = [
        ('chatgpt', 'ChatGPT'),
        ('copilot', 'GitHub Copilot'),
        ('claude', 'Claude'),
        ('gemini', 'Google Gemini'),
        ('other', 'Other AI Tool'),
    ]
    
    USAGE_TYPE_CHOICES = [
        ('code_generation', 'Code Generation'),
        ('code_explanation', 'Code Explanation'),
        ('debugging', 'Debugging Assistance'),
        ('documentation', 'Documentation'),
        ('learning', 'Learning/Tutorial'),
        ('research', 'Research'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage_logs')
    
    # Usage details
    ai_tool = models.CharField(max_length=50, choices=AI_TOOL_CHOICES)
    usage_type = models.CharField(max_length=50, choices=USAGE_TYPE_CHOICES)
    description = models.TextField(blank=True, help_text='Brief description of what was done')
    
    # Context
    course_code = models.CharField(max_length=50, blank=True)
    assignment_id = models.CharField(max_length=50, blank=True)
    
    # Metrics
    duration_minutes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Duration of AI tool usage in minutes'
    )
    tokens_used = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Approximate tokens/API calls used'
    )
    
    # Compliance
    policy = models.ForeignKey(
        AIEthicsPolicy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usage_logs'
    )
    is_compliant = models.BooleanField(default=True)
    compliance_notes = models.TextField(blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'ai_usage_log'
        verbose_name = 'AI Usage Log'
        verbose_name_plural = 'AI Usage Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['ai_tool']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.ai_tool} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        """Check compliance before saving."""
        if self.policy:
            self.check_compliance()
        super().save(*args, **kwargs)
    
    def check_compliance(self):
        """Check if this usage complies with the policy."""
        if not self.policy or not self.policy.is_active():
            self.is_compliant = True
            return
        
        # Check daily usage limit
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_count = AIUsageLog.objects.filter(
            user=self.user,
            timestamp__gte=today_start
        ).count()
        
        if daily_count >= self.policy.max_daily_usage:
            self.is_compliant = False
            self.compliance_notes = f"Exceeded daily usage limit of {self.policy.max_daily_usage}"
            return
        
        # Check weekly usage limit
        week_start = timezone.now() - timedelta(days=7)
        weekly_count = AIUsageLog.objects.filter(
            user=self.user,
            timestamp__gte=week_start
        ).count()
        
        if weekly_count >= self.policy.max_weekly_usage:
            self.is_compliant = False
            self.compliance_notes = f"Exceeded weekly usage limit of {self.policy.max_weekly_usage}"
            return
        
        self.is_compliant = True
        self.compliance_notes = "Usage within policy limits"


class ComplianceStatus(models.Model):
    """
    Tracks overall compliance status for each user.
    
    Updated periodically to reflect current compliance with AI ethics policies.
    """
    COMPLIANCE_LEVEL_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('warning', 'Warning'),
        ('violation', 'Violation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compliance_statuses')
    policy = models.ForeignKey(AIEthicsPolicy, on_delete=models.CASCADE, related_name='compliance_statuses')
    
    # Compliance metrics
    compliance_level = models.CharField(max_length=20, choices=COMPLIANCE_LEVEL_CHOICES)
    compliance_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Compliance score (0-100)'
    )
    
    # Usage statistics
    total_usage_count = models.IntegerField(default=0)
    compliant_usage_count = models.IntegerField(default=0)
    violation_count = models.IntegerField(default=0)
    
    # Time periods
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Additional details
    notes = models.TextField(blank=True)
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'compliance_status'
        verbose_name = 'Compliance Status'
        verbose_name_plural = 'Compliance Statuses'
        ordering = ['-calculated_at']
        unique_together = ['user', 'policy', 'period_start']
    
    def __str__(self):
        return f"{self.user.username} - {self.compliance_level} ({self.compliance_score}%)"
    
    def calculate_score(self):
        """Calculate compliance score based on usage patterns."""
        if self.total_usage_count == 0:
            self.compliance_score = 100
        else:
            self.compliance_score = int(
                (self.compliant_usage_count / self.total_usage_count) * 100
            )
        
        # Determine compliance level
        if self.compliance_score >= 90:
            self.compliance_level = 'excellent'
        elif self.compliance_score >= 75:
            self.compliance_level = 'good'
        elif self.compliance_score >= 50:
            self.compliance_level = 'warning'
        else:
            self.compliance_level = 'violation'
        
        self.save()


class UserInsight(models.Model):
    """
    Personalized insights and recommendations for users based on their AI usage.
    
    Generated automatically by the system to help users reflect on their AI usage patterns.
    """
    INSIGHT_TYPE_CHOICES = [
        ('usage_pattern', 'Usage Pattern'),
        ('compliance', 'Compliance'),
        ('recommendation', 'Recommendation'),
        ('achievement', 'Achievement'),
        ('warning', 'Warning'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insights')
    
    # Insight details
    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Related data
    related_usage_logs = models.ManyToManyField(AIUsageLog, blank=True, related_name='insights')
    data = models.JSONField(
        default=dict,
        help_text='Additional data for the insight (charts, metrics, etc.)'
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_insight'
        verbose_name = 'User Insight'
        verbose_name_plural = 'User Insights'
        ordering = ['-priority', '-generated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark insight as read."""
        self.is_read = True
        self.save()


class UserFeedback(models.Model):
    """
    User feedback for system improvement.
    
    Allows users to report issues, suggest features, and provide general feedback.
    """
    FEEDBACK_TYPE_CHOICES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('improvement', 'Improvement Suggestion'),
        ('general', 'General Feedback'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('reviewing', 'Under Review'),
        ('planned', 'Planned'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    
    # Feedback details
    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Additional context
    url = models.URLField(blank=True, help_text='URL where issue occurred')
    screenshot = models.ImageField(upload_to='feedback_screenshots/', blank=True, null=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_response = models.TextField(blank=True)
    
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_feedback'
        verbose_name = 'User Feedback'
        verbose_name_plural = 'User Feedback'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.feedback_type} - {self.title}"
