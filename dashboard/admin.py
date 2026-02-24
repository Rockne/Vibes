from django.contrib import admin
from .models import (
    UserProfile,
    AIEthicsPolicy,
    AIUsageLog,
    ComplianceStatus,
    UserInsight,
    UserFeedback
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'department', 'data_collection_consent', 'created_at']
    list_filter = ['data_collection_consent', 'allow_analytics', 'created_at']
    search_fields = ['user__username', 'user__email', 'student_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AIEthicsPolicy)
class AIEthicsPolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'version', 'status', 'effective_from', 'effective_until', 'is_active']
    list_filter = ['status', 'effective_from']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'version', 'status')
        }),
        ('Rules and Thresholds', {
            'fields': ('rules', 'max_daily_usage', 'max_weekly_usage')
        }),
        ('Effective Dates', {
            'fields': ('effective_from', 'effective_until')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'ai_tool', 'usage_type', 'is_compliant', 'timestamp']
    list_filter = ['ai_tool', 'usage_type', 'is_compliant', 'timestamp']
    search_fields = ['user__username', 'description', 'course_code']
    readonly_fields = ['timestamp', 'is_compliant', 'compliance_notes']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Usage Details', {
            'fields': ('ai_tool', 'usage_type', 'description', 'duration_minutes', 'tokens_used')
        }),
        ('Context', {
            'fields': ('course_code', 'assignment_id')
        }),
        ('Compliance', {
            'fields': ('policy', 'is_compliant', 'compliance_notes')
        }),
        ('Metadata', {
            'fields': ('timestamp', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ComplianceStatus)
class ComplianceStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'compliance_level', 'compliance_score', 'period_start', 'period_end', 'calculated_at']
    list_filter = ['compliance_level', 'calculated_at']
    search_fields = ['user__username']
    readonly_fields = ['calculated_at']


@admin.register(UserInsight)
class UserInsightAdmin(admin.ModelAdmin):
    list_display = ['user', 'insight_type', 'title', 'priority', 'is_read', 'generated_at']
    list_filter = ['insight_type', 'priority', 'is_read', 'is_dismissed', 'generated_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['generated_at']
    filter_horizontal = ['related_usage_logs']


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'feedback_type', 'title', 'status', 'submitted_at']
    list_filter = ['feedback_type', 'status', 'submitted_at']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['submitted_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Feedback Details', {
            'fields': ('feedback_type', 'title', 'description', 'url', 'screenshot')
        }),
        ('Status', {
            'fields': ('status', 'admin_response', 'resolved_at')
        }),
        ('Metadata', {
            'fields': ('submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
