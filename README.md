# 🤖 RemindMeBot - Telegram Reminder Assistant

<div align="center">

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green.svg)

**A powerful, feature-rich Telegram bot for managing reminders with subscription plans**

[Features](#-features) • [Installation](#-installation) • [Configuration](#-configuration) • [Deployment](#-deployment) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

---

## 🌟 Features

### 📝 **Reminder Management**
- ✅ Create reminders with intuitive step-by-step flow
- 📅 Multiple reminder types (Tasks, Events, Meetings, Birthdays, etc.)
- ⏰ Flexible time formats (natural language supported)
- 🔄 Recurring reminders (coming soon)
- 🗑️ Easy reminder deletion and management

### 💳 **Subscription System**
- 🆓 **Free Plan**: 5 reminders, 3 daily limit
- ⭐ **Premium Plan**: 100 reminders, 50 daily limit ($9.99/month)
- 💎 **Unlimited Plan**: Unlimited reminders ($19.99/month)

### 🎨 **Modern UI/UX**
- 🖱️ Interactive inline keyboards
- 📊 Beautiful progress bars and animations
- 💬 Smooth typing indicators
- 🎉 Success/error animations
- 📱 Mobile-optimized interface

### 👑 **Admin Features**
- 📊 Comprehensive analytics dashboard
- 👥 User management
- 📢 Broadcast messaging
- 💳 Subscription management
- 📈 Real-time statistics

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB database
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/reminder-telegram-bot.git
cd reminder-telegram-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
MONGODB_URL=mongodb://localhost:27017/
DATABASE_NAME=reminder_bot
```

### 4. Run the Bot
```bash
python main.py
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BOT_TOKEN` | Telegram Bot Token from BotFather | ✅ | - |
| `ADMIN_ID` | Your Telegram User ID (admin) | ✅ | - |
| `MONGODB_URL` | MongoDB connection string | ✅ | `mongodb://localhost:27017/` |
| `DATABASE_NAME` | MongoDB database name | ❌ | `reminder_bot` |
| `TIMEZONE` | Bot timezone | ❌ | `UTC` |
| `DEBUG` | Enable debug mode | ❌ | `False` |
| `WEBHOOK_URL` | Webhook URL for deployment | ❌ | - |
| `PORT` | Port for webhook | ❌ | `8000` |

### Getting Your Telegram User ID
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your user ID to the `ADMIN_ID` environment variable

---

## 📁 Project Structure

```
reminder-telegram-bot/
│
├── handlers/                    # Command handlers
│   ├── user_handlers.py        # User commands
│   ├── admin_handlers.py       # Admin commands
│   └── enhanced_user_handlers.py # Enhanced UI handlers
│
├── database/                    # Database layer
│   └── mongodb.py              # MongoDB operations
│
├── utils/                       # Utilities
│   ├── helpers.py              # Helper functions
│   ├── ui_components.py        # UI components
│   └── animations.py           # Animation helpers
│
├── main.py                     # Entry point
├── bot.py                      # Bot router
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
└── Procfile                   # Deployment config
```

---

## 🚀 Deployment

### Deploy on Koyeb

1. **Create a Koyeb Account**
   - Sign up at [koyeb.com](https://www.koyeb.com)

2. **Connect GitHub Repository**
   - Link your GitHub repository
   - Select this repository

3. **Configure Environment Variables**
   ```
   BOT_TOKEN=your_bot_token
   ADMIN_ID=your_user_id
   MONGODB_URL=your_mongodb_url
   DATABASE_NAME=reminder_bot
   ```

4. **Deploy**
   - Click "Deploy"
   - Koyeb will automatically use the `Procfile`

### Deploy on Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway add
```

### Deploy on Heroku

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-bot-name

# Set environment variables
heroku config:set BOT_TOKEN=your_token
heroku config:set ADMIN_ID=your_id
heroku config:set MONGODB_URL=your_mongo_url

# Deploy
git push heroku main
```

---

## 💻 Usage

### User Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start the bot | `/start` |
| `/help` | Show help message | `/help` |
| `/add` | Create new reminder | `/add Meeting \| Daily standup \| tomorrow 10:00 \| meeting` |
| `/list` | View your reminders | `/list` |
| `/subscription` | Check subscription status | `/subscription` |
| `/plans` | View available plans | `/plans` |
| `/stats` | View your statistics | `/stats` |

### Admin Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/admin` | Admin dashboard | `/admin` |
| `/adminstats` | Detailed statistics | `/adminstats` |
| `/users` | List all users | `/users` |
| `/broadcast` | Send message to all users | `/broadcast Important update!` |
| `/grant` | Grant subscription | `/grant 123456789 premium 30` |
| `/userinfo` | Get user information | `/userinfo 123456789` |

### Time Formats

The bot supports various time formats:

```
✅ 2024-12-25 14:30      (Full date and time)
✅ tomorrow 10:00        (Relative date)
✅ next monday 15:30     (Next weekday)
✅ in 2 hours           (Relative time)
✅ 25/12/2024 14:30     (DD/MM/YYYY format)
```

### Reminder Types

- 📝 **Task** - General tasks and to-dos
- 📅 **Event** - Important events and occasions
- 👥 **Meeting** - Business meetings and calls
- 🏥 **Appointment** - Medical and official appointments
- 🎂 **Birthday** - Birthday reminders
- ⚠️ **Deadline** - Important deadlines

---

## 🛠️ Development

### Setting Up Development Environment

1. **Clone and Setup**
   ```bash
   git clone https://github.com/yourusername/reminder-telegram-bot.git
   cd reminder-telegram-bot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   # Start MongoDB locally
   mongod --dbpath /path/to/your/db
   ```

3. **Run Development Server**
   ```bash
   export DEBUG=True  # On Windows: set DEBUG=True
   python main.py
   ```

### Adding New Features

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make Changes**
   - Add your code
   - Update tests if applicable
   - Update documentation

3. **Test Changes**
   ```bash
   python main.py
   ```

4. **Submit Pull Request**
   - Push to your fork
   - Create pull request
   - Describe your changes

---

## 📊 Monitoring & Analytics

### Built-in Analytics
- 👥 User growth tracking
- 📈 Reminder usage statistics
- 💳 Subscription analytics
- 📊 Performance metrics

### Logs
The bot creates detailed logs in `bot.log`:
- User interactions
- Error tracking
- Performance metrics
- Admin actions

---

## 🔧 Troubleshooting

### Common Issues

**Bot doesn't respond**
```bash
# Check if bot token is correct
# Verify bot is added to chat
# Check logs for errors
tail -f bot.log
```

**Database connection failed**
```bash
# Verify MongoDB is running
# Check connection string
# Ensure database permissions
```

**Permission denied errors**
```bash
# Check ADMIN_ID is set correctly
# Verify user ID format
```

### Getting Support

1. 📖 Check this README
2. 🐛 Search existing [Issues](https://github.com/yourusername/reminder-telegram-bot/issues)
3. 💬 Create new issue with:
   - Bot version
   - Error logs
   - Steps to reproduce

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

### Ways to Contribute
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit code changes
- 🌍 Add translations

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests (if applicable)
5. Update documentation
6. Submit pull request

### Code Guidelines
- Follow PEP 8 style guide
- Add docstrings to functions
- Use type hints where possible
- Keep functions focused and small
- Add comments for complex logic

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [pymongo](https://github.com/mongodb/mongo-python-driver) - MongoDB driver
- [APScheduler](https://github.com/agronholm/apscheduler) - Job scheduling

---

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/reminder-telegram-bot/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/reminder-telegram-bot/discussions)
- 📧 **Email**: your-email@example.com
- 💬 **Telegram**: [@yourusername](https://t.me/yourusername)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by [Your Name](https://github.com/yourusername)

</div>
