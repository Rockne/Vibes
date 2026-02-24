"""
URL configuration for dashboard app.
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # AI Usage Logging
    path('log-usage/', views.log_usage_view, name='log_usage'),
    path('usage-history/', views.usage_history_view, name='usage_history'),
    
    # Insights
    path('insights/', views.insights_view, name='insights'),
    path('insights/<int:insight_id>/dismiss/', views.dismiss_insight_view, name='dismiss_insight'),
    
    # Feedback
    path('feedback/', views.feedback_view, name='feedback'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('export-data/', views.export_data_view, name='export_data'),
]
