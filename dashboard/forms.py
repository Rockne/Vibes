"""
Forms for the dashboard app.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import AIUsageLog, UserProfile, UserFeedback


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class AIUsageLogForm(forms.ModelForm):
    """Form for logging AI usage."""
    
    class Meta:
        model = AIUsageLog
        fields = [
            'ai_tool',
            'usage_type',
            'description',
            'course_code',
            'assignment_id',
            'duration_minutes',
            'tokens_used',
        ]
        widgets = {
            'ai_tool': forms.Select(attrs={'class': 'form-select'}),
            'usage_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of what you did with the AI tool...'
            }),
            'course_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CS101'
            }),
            'assignment_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Assignment 3'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Minutes spent'
            }),
            'tokens_used': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Approximate tokens/calls'
            }),
        }
        help_texts = {
            'description': 'Provide a brief description of how you used the AI tool.',
            'duration_minutes': 'Approximate time spent using the AI tool.',
            'tokens_used': 'Approximate number of API calls or tokens (optional).',
        }


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    
    class Meta:
        model = UserProfile
        fields = [
            'student_id',
            'department',
            'data_collection_consent',
            'allow_analytics',
            'email_notifications',
            'weekly_summary',
        ]
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your student ID'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computer Science'
            }),
            'data_collection_consent': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_analytics': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'weekly_summary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'data_collection_consent': 'Required to use the platform (GDPR compliance).',
            'allow_analytics': 'Allow us to analyze your usage patterns to provide better insights.',
            'email_notifications': 'Receive email notifications about important updates.',
            'weekly_summary': 'Receive a weekly summary of your AI usage.',
        }


class UserFeedbackForm(forms.ModelForm):
    """Form for submitting feedback."""
    
    class Meta:
        model = UserFeedback
        fields = [
            'feedback_type',
            'title',
            'description',
            'url',
            'screenshot',
        ]
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title for your feedback'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Please provide detailed information...'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL where the issue occurred (optional)'
            }),
            'screenshot': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        help_texts = {
            'screenshot': 'Optional: Upload a screenshot to help us understand the issue better.',
        }
