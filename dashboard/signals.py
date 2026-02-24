"""
Signal handlers for the dashboard app.

Automatically creates user profiles and generates insights.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, AIUsageLog, UserInsight


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=AIUsageLog)
def generate_usage_insights(sender, instance, created, **kwargs):
    """Generate insights when AI usage patterns are detected."""
    if not created:
        return
    
    user = instance.user
    
    # Check if user has excessive usage today
    from django.utils import timezone
    from datetime import timedelta
    
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_usage = AIUsageLog.objects.filter(
        user=user,
        timestamp__gte=today_start
    ).count()
    
    # Generate warning insight if usage is high
    if today_usage >= 50 and not UserInsight.objects.filter(
        user=user,
        insight_type='warning',
        generated_at__gte=today_start
    ).exists():
        UserInsight.objects.create(
            user=user,
            insight_type='warning',
            title='High AI Usage Today',
            message=f'You have logged {today_usage} AI interactions today. Consider taking breaks and reflecting on your learning process.',
            priority='high'
        )
    
    # Check for milestone achievements
    total_usage = AIUsageLog.objects.filter(user=user).count()
    milestones = [10, 50, 100, 250, 500, 1000]
    
    if total_usage in milestones:
        UserInsight.objects.create(
            user=user,
            insight_type='achievement',
            title=f'Milestone: {total_usage} AI Interactions!',
            message=f'Congratulations! You have logged {total_usage} AI interactions. Keep learning responsibly!',
            priority='medium'
        )
