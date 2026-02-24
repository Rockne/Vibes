# Quick Start Guide - AI Usage Learning Platform

## 🚀 Get Started in 5 Minutes

### Step 1: Open PowerShell in Project Directory
```powershell
cd "C:\Users\krist\OneDrive\Documents\GitHub\Vibes"
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Set Up Database
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Admin Account
```powershell
python manage.py createsuperuser
```

Enter your details when prompted:
- Username: admin
- Email: admin@example.com
- Password: (choose a secure password)

### Step 6: Start Server
```powershell
python manage.py runserver
```

### Step 7: Access the Application

Open your browser and go to:
- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📝 First Steps

### 1. Create a Student Account
1. Go to http://127.0.0.1:8000/register/
2. Fill in the registration form
3. Click "Create Account"
4. Login with your new credentials

### 2. Create AI Ethics Policy (Admin)
1. Login to admin panel: http://127.0.0.1:8000/admin/
2. Go to "AI Ethics Policies"
3. Click "Add AI Ethics Policy"
4. Fill in:
   - Title: "Institutional AI Usage Policy"
   - Description: "Guidelines for responsible AI usage"
   - Version: "1.0"
   - Status: "Active"
   - Max daily usage: 50
   - Max weekly usage: 200
   - Effective from: (today's date)
5. Click "Save"

### 3. Log Your First AI Usage
1. Go to main dashboard
2. Click "Log AI Usage" button
3. Fill in the form:
   - AI Tool: ChatGPT
   - Usage Type: Code Generation
   - Description: "Asked for help with Python function"
   - Duration: 15 minutes
4. Click "Log Usage"

### 4. View Your Dashboard
Your dashboard now shows:
- ✅ Usage statistics
- ✅ Compliance status
- ✅ Interactive charts
- ✅ Recent activity
- ✅ Personalized insights

## 🎯 Common Tasks

### Add Sample Data (Optional)
```powershell
python manage.py shell
```

Then paste:
```python
from django.contrib.auth.models import User
from dashboard.models import AIEthicsPolicy, AIUsageLog
from django.utils import timezone

# Get your user
user = User.objects.get(username='yourusername')  # Change this

# Create policy if not exists
policy, created = AIEthicsPolicy.objects.get_or_create(
    title="Institutional AI Usage Policy",
    defaults={
        'description': "Guidelines for responsible AI tool usage",
        'version': "1.0",
        'status': "active",
        'max_daily_usage': 50,
        'max_weekly_usage': 200,
        'effective_from': timezone.now().date(),
    }
)

# Create sample logs
tools = ['chatgpt', 'copilot', 'claude', 'gemini']
types = ['code_generation', 'code_explanation', 'debugging', 'learning']

for i in range(20):
    AIUsageLog.objects.create(
        user=user,
        ai_tool=tools[i % len(tools)],
        usage_type=types[i % len(types)],
        description=f'Sample usage log {i+1}',
        duration_minutes=10 + (i * 2),
        policy=policy
    )

print("✅ Sample data created!")
exit()
```

### Run Tests
```powershell
python manage.py test dashboard
```

### Access Different Pages
- Dashboard: http://127.0.0.1:8000/
- Log Usage: http://127.0.0.1:8000/log-usage/
- Usage History: http://127.0.0.1:8000/usage-history/
- Insights: http://127.0.0.1:8000/insights/
- Feedback: http://127.0.0.1:8000/feedback/
- Profile: http://127.0.0.1:8000/profile/
- Admin: http://127.0.0.1:8000/admin/

## 🛠️ Troubleshooting

### Issue: "No module named django"
**Solution**: Make sure virtual environment is activated
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Table doesn't exist" error
**Solution**: Run migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Issue: Port 8000 already in use
**Solution**: Use a different port
```powershell
python manage.py runserver 8080
```

### Issue: Cannot activate virtual environment
**Solution**: Change execution policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📚 Next Steps

1. **Explore the Dashboard**: Check out the charts and statistics
2. **Log More Usage**: Add various types of AI interactions
3. **Check Insights**: See automated recommendations
4. **Submit Feedback**: Test the feedback system
5. **Manage Policies**: Create different AI ethics policies in admin
6. **Export Data**: Try the GDPR-compliant data export

## 🎓 Learning Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Bootstrap Docs**: https://getbootstrap.com/docs/
- **Chart.js Guide**: https://www.chartjs.org/docs/

## 💡 Tips

- Use Chrome/Firefox DevTools to inspect the dashboard
- Check the admin panel to see all database entries
- Review `ARCHITECTURE.md` for design decisions
- Read `README.md` for detailed documentation

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Can register new user
- [ ] Can login successfully
- [ ] Dashboard displays statistics
- [ ] Charts render properly
- [ ] Can log AI usage
- [ ] Can view usage history
- [ ] Can see insights
- [ ] Can submit feedback
- [ ] Can edit profile
- [ ] Can export data
- [ ] Admin panel accessible

## Need Help?

- Check `README.md` for detailed documentation
- Review `ARCHITECTURE.md` for technical details
- Check `dashboard/tests.py` for usage examples
- Submit feedback through the app's feedback form

---

**Enjoy using the AI Usage Learning Platform!** 🎉
