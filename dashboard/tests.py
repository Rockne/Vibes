"""
Tests for the dashboard app.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserProfile,
    AIEthicsPolicy,
    AIUsageLog,
    ComplianceStatus,
    UserInsight,
    UserFeedback
)


class UserProfileModelTest(TestCase):
    """Test UserProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_created_automatically(self):
        """Test that profile is created automatically when user is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_profile_string_representation(self):
        """Test the string representation of UserProfile."""
        expected = f"{self.user.username} - Profile"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_get_usage_summary(self):
        """Test usage summary calculation."""
        summary = self.user.profile.get_usage_summary()
        self.assertEqual(summary['total'], 0)
        self.assertEqual(summary['this_week'], 0)


class AIEthicsPolicyModelTest(TestCase):
    """Test AIEthicsPolicy model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            password='adminpass123'
        )
        self.policy = AIEthicsPolicy.objects.create(
            title='Test Policy',
            description='Test description',
            version='1.0',
            status='active',
            max_daily_usage=50,
            max_weekly_usage=200,
            effective_from=timezone.now().date(),
            created_by=self.user
        )
    
    def test_policy_creation(self):
        """Test policy is created correctly."""
        self.assertEqual(self.policy.title, 'Test Policy')
        self.assertEqual(self.policy.max_daily_usage, 50)
    
    def test_is_active(self):
        """Test is_active method."""
        self.assertTrue(self.policy.is_active())
        
        # Test inactive policy
        self.policy.status = 'draft'
        self.policy.save()
        self.assertFalse(self.policy.is_active())


class AIUsageLogModelTest(TestCase):
    """Test AIUsageLog model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.policy = AIEthicsPolicy.objects.create(
            title='Test Policy',
            description='Test',
            version='1.0',
            status='active',
            max_daily_usage=5,
            max_weekly_usage=20,
            effective_from=timezone.now().date()
        )
    
    def test_usage_log_creation(self):
        """Test creating a usage log."""
        log = AIUsageLog.objects.create(
            user=self.user,
            ai_tool='chatgpt',
            usage_type='code_generation',
            description='Test log',
            duration_minutes=15,
            policy=self.policy
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.ai_tool, 'chatgpt')
        self.assertTrue(log.is_compliant)
    
    def test_compliance_checking(self):
        """Test compliance checking."""
        # Create logs up to the daily limit
        for i in range(6):
            AIUsageLog.objects.create(
                user=self.user,
                ai_tool='chatgpt',
                usage_type='code_generation',
                description=f'Log {i}',
                policy=self.policy
            )
        
        # The 6th log should be non-compliant
        latest_log = AIUsageLog.objects.filter(user=self.user).latest('timestamp')
        self.assertFalse(latest_log.is_compliant)


class DashboardViewTest(TestCase):
    """Test dashboard views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_required(self):
        """Test that dashboard requires login."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_access(self):
        """Test authenticated user can access dashboard."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My AI Usage Dashboard')
    
    def test_login_view(self):
        """Test login view."""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')
    
    def test_register_view(self):
        """Test registration view."""
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')


class UserInsightModelTest(TestCase):
    """Test UserInsight model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_insight_creation(self):
        """Test creating an insight."""
        insight = UserInsight.objects.create(
            user=self.user,
            insight_type='usage_pattern',
            title='High Usage',
            message='You have been using AI tools frequently.',
            priority='high'
        )
        self.assertEqual(insight.user, self.user)
        self.assertFalse(insight.is_read)
    
    def test_mark_as_read(self):
        """Test marking insight as read."""
        insight = UserInsight.objects.create(
            user=self.user,
            insight_type='achievement',
            title='Milestone',
            message='Congratulations!',
            priority='medium'
        )
        insight.mark_as_read()
        self.assertTrue(insight.is_read)


class UserFeedbackModelTest(TestCase):
    """Test UserFeedback model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_feedback_creation(self):
        """Test creating feedback."""
        feedback = UserFeedback.objects.create(
            user=self.user,
            feedback_type='bug',
            title='Test Bug',
            description='This is a test bug report.'
        )
        self.assertEqual(feedback.user, self.user)
        self.assertEqual(feedback.status, 'new')
