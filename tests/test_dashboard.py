"""
Tests for the dashboard app.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from dashboard.models import (
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

    def test_str(self):
        """Test the string representation of AIEthicsPolicy."""
        self.assertEqual(str(self.policy), 'Test Policy (v1.0)')

    def test_is_active(self):
        """Test is_active method."""
        self.assertTrue(self.policy.is_active())

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


class LoginViewTest(TestCase):
    """Test login view branches."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_authenticated_user_redirects(self):
        """Test that authenticated user is redirected from login."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/') or 'dashboard' in response.url)
    
    def test_login_valid_credentials(self):
        """Test login with valid credentials."""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_login_invalid_password(self):
        """Test login with invalid password."""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'wrongpass'
        }, follow=False)
        self.assertFalse(self.client.session.get('_auth_user_id'))


class RegisterViewTest(TestCase):
    """Test register view branches."""
    
    def setUp(self):
        self.client = Client()
    
    def test_register_get_request(self):
        """Test GET request to register view."""
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')
    
    def test_register_valid_data(self):
        """Test registration with valid data."""
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123!@',
            'password2': 'complexpass123!@'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_authenticated_user_redirects(self):
        """Test that authenticated user is redirected from register."""
        user = User.objects.create_user(username='existing', password='pass123')
        self.client.login(username='existing', password='pass123')
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 302)
    
    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords."""
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123!@',
            'password2': 'differentpass123!@'
        }, follow=False)
        self.assertFalse(User.objects.filter(username='newuser').exists())


class LogoutViewTest(TestCase):
    """Test logout view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_logout(self):
        """Test user logout."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.client.session.get('_auth_user_id'))


class LogUsageViewTest(TestCase):
    """Test log usage view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.policy = AIEthicsPolicy.objects.create(
            title='Test Policy',
            description='Test',
            version='1.0',
            status='active',
            max_daily_usage=10,
            effective_from=timezone.now().date()
        )
    
    def test_log_usage_get(self):
        """Test GET request to log usage view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/log-usage/')
        self.assertEqual(response.status_code, 200)
    
    def test_log_usage_post_valid(self):
        """Test POST with valid data."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/log-usage/', {
            'ai_tool': 'chatgpt',
            'usage_type': 'code_generation',
            'description': 'Test usage',
            'course_code': 'CS101',
            'assignment_id': 'A1',
            'duration_minutes': 15,
            'tokens_used': 100
        }, follow=True)
        # Check that usage log was created
        self.assertTrue(
            AIUsageLog.objects.filter(user=self.user, ai_tool='chatgpt').exists()
        )
    
    def test_log_usage_post_invalid(self):
        """Test POST with invalid data."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/log-usage/', {
            'ai_tool': '',  # Required field missing
            'usage_type': 'code_generation',
            'description': 'Test'
        }, follow=False)
        self.assertEqual(response.status_code, 200)


class UsageHistoryViewTest(TestCase):
    """Test usage history view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.policy = AIEthicsPolicy.objects.create(
            title='Test Policy',
            description='Test',
            version='1.0',
            status='active',
            effective_from=timezone.now().date()
        )
        
        # Create sample usage logs
        for i in range(5):
            AIUsageLog.objects.create(
                user=self.user,
                ai_tool='chatgpt' if i % 2 == 0 else 'codex',
                usage_type='code_generation' if i % 2 == 0 else 'explanation',
                description=f'Test log {i}',
                policy=self.policy
            )
    
    def test_usage_history_no_filter(self):
        """Test usage history without filters."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/usage-history/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test log')
    
    def test_usage_history_filter_by_tool(self):
        """Test usage history filtered by tool."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/usage-history/?tool=chatgpt')
        self.assertEqual(response.status_code, 200)
    
    def test_usage_history_filter_by_type(self):
        """Test usage history filtered by type."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/usage-history/?type=code_generation')
        self.assertEqual(response.status_code, 200)
    
    def test_usage_history_filter_by_date(self):
        """Test usage history filtered by date range."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            '/usage-history/?date_from=2026-01-01&date_to=2026-12-31'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_usage_history_pagination(self):
        """Test usage history pagination."""
        self.client.login(username='testuser', password='testpass123')
        # Create more logs to test pagination
        for i in range(30):
            AIUsageLog.objects.create(
                user=self.user,
                ai_tool='chatgpt',
                usage_type='code_generation',
                description=f'Log {i}',
                policy=self.policy
            )
        
        response = self.client.get('/usage-history/?page=2')
        self.assertEqual(response.status_code, 200)


class InsightsViewTest(TestCase):
    """Test insights view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create sample insights
        UserInsight.objects.create(
            user=self.user,
            insight_type='usage_pattern',
            title='High Usage',
            message='You are using AI tools frequently.',
            priority='high',
            is_read=False
        )
        UserInsight.objects.create(
            user=self.user,
            insight_type='compliance',
            title='Compliance Alert',
            message='Watch your usage.',
            priority='medium',
            is_read=False
        )
    
    def test_insights_view(self):
        """Test insights view displays insights."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/insights/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'High Usage')
        self.assertContains(response, 'Compliance Alert')
    
    def test_insights_marked_as_read(self):
        """Test that insights are marked as read when viewed."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/insights/')
        
        # Check that unread insights were marked as read
        unread = UserInsight.objects.filter(user=self.user, is_read=False)
        self.assertEqual(unread.count(), 0)


class DismissInsightViewTest(TestCase):
    """Test dismiss insight view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.insight = UserInsight.objects.create(
            user=self.user,
            insight_type='usage_pattern',
            title='High Usage',
            message='You are using AI tools frequently.',
            priority='high'
        )
    
    def test_dismiss_insight(self):
        """Test dismissing an insight."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/insights/{self.insight.id}/dismiss/')
        self.assertEqual(response.status_code, 302)
        
        self.insight.refresh_from_db()
        self.assertTrue(self.insight.is_dismissed)


class FeedbackViewTest(TestCase):
    """Test feedback view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_feedback_view_get(self):
        """Test GET request to feedback view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/feedback/')
        self.assertEqual(response.status_code, 200)
    
    def test_feedback_post_valid(self):
        """Test POST with valid feedback."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/feedback/', {
            'feedback_type': 'feature',
            'title': 'Feature Suggestion',
            'description': 'Add dark mode support to the dashboard.'
        }, follow=True)
        # Check that feedback was created
        self.assertTrue(
            UserFeedback.objects.filter(user=self.user, title='Feature Suggestion').exists()
        )


class ProfileViewTest(TestCase):
    """Test profile view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_profile_view_get(self):
        """Test GET request to profile view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
    
    def test_profile_view_post(self):
        """Test POST to update profile."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/profile/', {
            'department': 'Engineering',
            'data_collection_consent': True
        })
        self.assertEqual(response.status_code, 302)
        
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.department, 'Engineering')


class ExportDataViewTest(TestCase):
    """Test export data view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.policy = AIEthicsPolicy.objects.create(
            title='Test Policy',
            description='Test',
            version='1.0',
            status='active',
            effective_from=timezone.now().date()
        )
        
        # Create sample data
        AIUsageLog.objects.create(
            user=self.user,
            ai_tool='chatgpt',
            usage_type='code_generation',
            description='Test',
            policy=self.policy
        )
    
    def test_export_data(self):
        """Test data export functionality."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/export-data/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('ai_usage_data_testuser.json', response['Content-Disposition'])


class DashboardComplianceLevelsTest(TestCase):
    """Test dashboard view compliance level branches."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.policy = AIEthicsPolicy.objects.create(
            title='Test Policy',
            description='Test',
            version='1.0',
            status='active',
            max_daily_usage=1,
            max_weekly_usage=10,
            effective_from=timezone.now().date()
        )
    
    def test_dashboard_compliance_excellent(self):
        """Test dashboard with excellent compliance (>=90%)."""
        self.client.login(username='testuser', password='testpass123')
        # Create 1 compliant log (no violations)
        AIUsageLog.objects.create(
            user=self.user,
            ai_tool='chatgpt',
            usage_type='code_generation',
            description='Test',
            policy=self.policy,
            is_compliant=True
        )
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_compliance_good(self):
        """Test dashboard with good compliance (75-89%)."""
        self.client.login(username='testuser', password='testpass123')
        # Create logs to get 75-89% compliance
        for i in range(3):
            AIUsageLog.objects.create(
                user=self.user,
                ai_tool='chatgpt',
                usage_type='code_generation',
                description=f'Test {i}',
                policy=self.policy,
                is_compliant=True if i < 3 else False
            )
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_compliance_warning(self):
        """Test dashboard with warning compliance (50-74%)."""
        self.client.login(username='testuser', password='testpass123')
        # Create logs to get 50-74% compliance
        for i in range(4):
            AIUsageLog.objects.create(
                user=self.user,
                ai_tool='chatgpt',
                usage_type='code_generation',
                description=f'Test {i}',
                policy=self.policy,
                is_compliant=True if i < 2 else False
            )
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_compliance_violation(self):
        """Test dashboard with violation compliance (<50%)."""
        self.client.login(username='testuser', password='testpass123')
        # Create logs to get <50% compliance
        for i in range(5):
            AIUsageLog.objects.create(
                user=self.user,
                ai_tool='chatgpt',
                usage_type='code_generation',
                description=f'Test {i}',
                policy=self.policy,
                is_compliant=True if i < 1 else False
            )
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class LogUsageIPAddressTest(TestCase):
    """Test IP address extraction in log usage view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.policy = AIEthicsPolicy.objects.create(
            title='Test Policy',
            description='Test',
            version='1.0',
            status='active',
            effective_from=timezone.now().date()
        )
    
    def test_log_usage_ip_from_remote_addr(self):
        """Test that IP is extracted from REMOTE_ADDR when X-Forwarded-For is absent."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            '/log-usage/',
            {
                'ai_tool': 'chatgpt',
                'usage_type': 'code_generation',
                'description': 'Test usage',
                'course_code': 'CS101',
                'assignment_id': 'A1',
                'duration_minutes': 15,
                'tokens_used': 100
            },
            REMOTE_ADDR='127.0.0.1'
        )
        # Check that the log was created
        log = AIUsageLog.objects.filter(user=self.user, ai_tool='chatgpt').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.ip_address, '127.0.0.1')
