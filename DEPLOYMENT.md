# 🚀 Deployment Guide

This guide covers deploying the RemindMeBot to various cloud platforms.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Telegram Bot Token** from [@BotFather](https://t.me/botfather)
2. **MongoDB Database** (MongoDB Atlas recommended)
3. **Your Telegram User ID** (get from [@userinfobot](https://t.me/userinfobot))

---

## 🌐 Koyeb Deployment (Recommended)

Koyeb offers free tier hosting perfect for Telegram bots.

### Step 1: Prepare Repository
```bash
git clone https://github.com/yourusername/reminder-telegram-bot.git
cd reminder-telegram-bot
git push origin main
```

### Step 2: Create Koyeb Account
1. Visit [koyeb.com](https://www.koyeb.com)
2. Sign up with GitHub
3. Verify your account

### Step 3: Deploy from GitHub
1. **Create New App**
   - Click "Create App"
   - Select "GitHub" as source

2. **Configure Repository**
   - Connect GitHub account
   - Select `reminder-telegram-bot` repository
   - Branch: `main`

3. **Set Environment Variables**
   ```
   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ADMIN_ID=123456789
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
   DATABASE_NAME=reminder_bot
   DEBUG=False
   TIMEZONE=UTC
   ```

4. **Configure Build**
   - Build command: `pip install -r requirements.txt`
   - Run command: `python main.py`
   - Port: `8000` (auto-detected from Procfile)

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Check logs for any errors

### Step 4: Verify Deployment
1. Check deployment logs
2. Test bot by sending `/start`
3. Monitor for 24 hours

---

## 🚂 Railway Deployment

Railway offers excellent Python support with automatic deployments.

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Login and Initialize
```bash
railway login
railway init
```

### Step 3: Configure Environment
```bash
railway add
railway variables set BOT_TOKEN=your_bot_token
railway variables set ADMIN_ID=your_user_id
railway variables set MONGODB_URL=your_mongo_url
railway variables set DATABASE_NAME=reminder_bot
```

### Step 4: Deploy
```bash
git add .
git commit -m "Initial deployment"
railway up
```

---

## 🟣 Heroku Deployment

### Step 1: Install Heroku CLI
Download from [heroku.com/cli](https://devcenter.heroku.com/articles/heroku-cli)

### Step 2: Create App
```bash
heroku login
heroku create your-bot-name
```

### Step 3: Set Environment Variables
```bash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set ADMIN_ID=your_user_id
heroku config:set MONGODB_URL=your_mongo_url
heroku config:set DATABASE_NAME=reminder_bot
```

### Step 4: Deploy
```bash
git push heroku main
```

### Step 5: Scale Dynos
```bash
heroku ps:scale web=1
```

---

## 🗄️ MongoDB Setup

### Option 1: MongoDB Atlas (Recommended)

1. **Create Account**
   - Visit [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for free

2. **Create Cluster**
   - Choose "Shared" (free tier)
   - Select region closest to your deployment
   - Create cluster

3. **Configure Access**
   - Database Access → Add user
   - Network Access → Add IP (0.0.0.0/0 for all IPs)

4. **Get Connection String**
   - Clusters → Connect → Connect your application
   - Copy connection string
   - Replace `<password>` with your database password

### Option 2: Local MongoDB
```bash
# Install MongoDB
brew install mongodb/brew/mongodb-community  # macOS
sudo apt-get install mongodb                 # Ubuntu

# Start MongoDB
brew services start mongodb-community        # macOS
sudo systemctl start mongod                  # Ubuntu

# Connection string
MONGODB_URL=mongodb://localhost:27017/
```

---

## 🔧 Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `BOT_TOKEN` | Telegram bot token from BotFather | ✅ | `1234567890:ABC...` |
| `ADMIN_ID` | Your Telegram user ID | ✅ | `123456789` |
| `MONGODB_URL` | MongoDB connection string | ✅ | `mongodb+srv://...` |
| `DATABASE_NAME` | Database name | ❌ | `reminder_bot` |
| `DEBUG` | Enable debug logging | ❌ | `False` |
| `TIMEZONE` | Bot timezone | ❌ | `UTC` |
| `WEBHOOK_URL` | Webhook URL (auto-set) | ❌ | `https://app.koyeb.com/...` |
| `PORT` | Port number (auto-set) | ❌ | `8000` |

---

## 🔍 Troubleshooting

### Common Issues

**Bot doesn't start**
```
Error: Invalid bot token
Solution: Verify BOT_TOKEN is correct and active
```

**Database connection failed**
```
Error: MongoDB connection timeout
Solution: Check MONGODB_URL and network access settings
```

**Bot responds but reminders don't send**
```
Error: Scheduler not working
Solution: Check logs for scheduler errors, verify timezone settings
```

**Permission denied**
```
Error: Admin commands not working
Solution: Verify ADMIN_ID matches your Telegram user ID exactly
```

### Debugging Steps

1. **Check Logs**
   ```bash
   # Koyeb
   View logs in Koyeb dashboard

   # Railway
   railway logs

   # Heroku
   heroku logs --tail
   ```

2. **Test Components**
   ```python
   # Test bot token
   import requests
   r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
   print(r.json())

   # Test MongoDB
   from pymongo import MongoClient
   client = MongoClient(MONGODB_URL)
   print(client.list_database_names())
   ```

3. **Verify Environment**
   ```bash
   # Print environment variables (remove sensitive data)
   env | grep -E "(BOT_TOKEN|ADMIN_ID|MONGODB_URL)"
   ```

---

## 📊 Monitoring

### Health Checks

Add these endpoints for monitoring:

```python
# In bot.py
@app.route('/health')
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.route('/metrics')
def metrics():
    stats = db.get_bot_stats()
    return stats
```

### Uptime Monitoring

Use services like:
- [UptimeRobot](https://uptimerobot.com/) (free)
- [Pingdom](https://www.pingdom.com/)
- [StatusCake](https://www.statuscake.com/)

---

## 🔄 Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Koyeb

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Deploy to Koyeb
      uses: koyeb/action-git-deploy@v1
      with:
        api-token: ${{ secrets.KOYEB_TOKEN }}
        app-name: reminder-bot
        service-name: web
```

### Auto-deployment Setup

1. **Koyeb**: Automatically deploys on git push
2. **Railway**: Automatic deployments enabled by default
3. **Heroku**: Enable auto-deploy in dashboard

---

## 🛡️ Security Best Practices

### Environment Security
- Never commit `.env` files
- Use platform-specific secret management
- Regularly rotate API keys
- Enable 2FA on all accounts

### Bot Security
- Validate all user inputs
- Rate limit API calls
- Log security events
- Monitor for suspicious activity

### Database Security
- Enable authentication
- Use SSL connections
- Regular backups
- Monitor access patterns

---

## 📈 Scaling

### Performance Optimization
- Use connection pooling
- Implement caching
- Optimize database queries
- Monitor memory usage

### Load Testing
```bash
# Install dependencies
pip install locust

# Create load test
# locustfile.py
from locust import HttpUser, task

class BotUser(HttpUser):
    @task
    def send_message(self):
        # Simulate bot usage
        pass
```

### Horizontal Scaling
- Use webhook mode for multiple instances
- Implement job queues for reminders
- Use Redis for session storage
- Load balance with nginx

---

## 📞 Support

If you encounter issues:

1. 📖 Check this deployment guide
2. 🐛 Search [GitHub Issues](https://github.com/yourusername/reminder-telegram-bot/issues)
3. 💬 Create new issue with:
   - Platform (Koyeb/Railway/Heroku)
   - Error logs
   - Environment (redacted)
   - Steps to reproduce

---

## ✅ Post-Deployment Checklist

- [ ] Bot responds to `/start`
- [ ] Database connection working
- [ ] Reminders being sent
- [ ] Admin commands functional
- [ ] Logs being generated
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] Documentation updated

---

**🎉 Congratulations! Your bot is now live and ready to help users manage their reminders!**
