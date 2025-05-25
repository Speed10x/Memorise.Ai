# 🤝 Contributing to RemindMeBot

First off, thank you for considering contributing to RemindMeBot! It's people like you that make this project better for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Issue Guidelines](#issue-guidelines)

---

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Pledge
- **Be Respectful**: Treat everyone with respect and kindness
- **Be Inclusive**: Welcome newcomers and help them learn
- **Be Collaborative**: Work together towards common goals
- **Be Patient**: Remember everyone was a beginner once

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- MongoDB (local or Atlas)
- Telegram Bot Token

### Quick Setup
```bash
# 1. Fork and clone the repository
git clone https://github.com/yourusername/reminder-telegram-bot.git
cd reminder-telegram-bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 5. Run the bot
python main.py
```

---

## 🛠️ How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates.

**Great Bug Reports Include:**
- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, etc.)
- Error logs or stack traces

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Windows 10, macOS, Ubuntu]
- Python version: [e.g. 3.9.0]
- Bot version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

### 💡 Suggesting Features

We love feature suggestions! Before suggesting:
- Check if the feature already exists
- Look through existing feature requests
- Consider if it fits the project's scope

**Feature Request Template:**
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context, mockups, or examples.
```

### 🔧 Contributing Code

1. **Choose an Issue**
   - Look for issues labeled `good first issue` for beginners
   - Check `help wanted` for issues that need attention
   - Ask to be assigned before starting work

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make Changes**
   - Write clean, readable code
   - Follow the style guidelines
   - Add tests if applicable
   - Update documentation

4. **Test Your Changes**
   ```bash
   # Run the bot locally
   python main.py

   # Test specific functionality
   # (Add specific test commands here)
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Use the PR template
   - Link related issues
   - Describe changes clearly

---

## 🏗️ Development Setup

### Local Development Environment

1. **Database Setup**
   ```bash
   # Option 1: Local MongoDB
   mongod --dbpath /path/to/data

   # Option 2: MongoDB Atlas (recommended)
   # Use connection string in .env
   ```

2. **Environment Variables**
   ```bash
   # Required
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_ID=your_telegram_user_id
   MONGODB_URL=mongodb://localhost:27017/

   # Optional
   DEBUG=True
   TIMEZONE=UTC
   DATABASE_NAME=reminder_bot_dev
   ```

3. **Development Tools**
   ```bash
   # Install development dependencies
   pip install black flake8 pytest

   # Format code
   black .

   # Check code style
   flake8 .

   # Run tests
   pytest
   ```

### Project Structure Understanding

```
reminder-telegram-bot/
├── handlers/           # Command handlers
│   ├── user_handlers.py         # Basic user commands
│   ├── admin_handlers.py        # Admin functionality
│   └── enhanced_user_handlers.py # Advanced UI flows
├── database/          # Database layer
│   └── mongodb.py              # MongoDB operations
├── utils/             # Utilities and helpers
│   ├── helpers.py              # General helpers
│   ├── ui_components.py        # UI building blocks
│   ├── animations.py           # Animation helpers
│   └── reminder_scheduler.py   # Reminder scheduling
├── main.py            # Application entry point
├── bot.py             # Bot initialization and routing
└── config.py          # Configuration management
```

---

## 📝 Pull Request Process

### Before Submitting

1. **Update Documentation**
   - Update README if adding features
   - Add docstrings to new functions
   - Update CHANGELOG.md

2. **Test Thoroughly**
   - Test new features manually
   - Ensure existing functionality works
   - Test edge cases

3. **Code Quality**
   - Follow PEP 8 style guide
   - Use meaningful variable names
   - Add comments for complex logic
   - Remove debug code and print statements

### PR Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests that you ran to verify your changes.

## Checklist:
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Related Issues
Fixes #(issue number)
```

---

## 🎨 Style Guidelines

### Python Code Style

1. **Follow PEP 8**
   ```python
   # Good
   def create_reminder(user_id: int, title: str) -> dict:
       """Create a new reminder for the user."""
       return {"status": "success"}

   # Bad
   def createReminder(userId,title):
       return dict(status="success")
   ```

2. **Use Type Hints**
   ```python
   # Good
   async def send_message(chat_id: int, text: str) -> bool:
       try:
           await bot.send_message(chat_id, text)
           return True
       except Exception:
           return False
   ```

3. **Meaningful Names**
   ```python
   # Good
   active_reminders = get_user_reminders(user_id, active_only=True)

   # Bad
   data = get_data(id, True)
   ```

4. **Error Handling**
   ```python
   # Good
   try:
       result = database_operation()
   except DatabaseError as e:
       logger.error(f"Database operation failed: {e}")
       return None
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
       raise
   ```

### Commit Message Guidelines

```bash
# Format
type(scope): brief description

# Examples
feat(reminders): add recurring reminder support
fix(auth): resolve admin permission checking
docs(readme): update installation instructions
style(ui): improve button layout consistency
refactor(database): optimize reminder queries
test(handlers): add user command tests
```

### Documentation Style

1. **Function Docstrings**
   ```python
   async def create_reminder(user_id: int, title: str, reminder_time: datetime) -> dict:
       """
       Create a new reminder for the user.

       Args:
           user_id: Telegram user ID
           title: Reminder title
           reminder_time: When to send the reminder

       Returns:
           dict: Created reminder object or None if failed

       Raises:
           DatabaseError: If database operation fails
       """
   ```

2. **Comment Guidelines**
   ```python
   # Good: Explain why, not what
   # Check subscription limits before creating reminder
   if not self.can_create_reminder(user_id):
       return None

   # Bad: Obvious comments
   # Set user_id to user.id
   user_id = user.id
   ```

---

## 🐛 Issue Guidelines

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `documentation` - Improvements or additions to documentation
- `duplicate` - This issue already exists
- `invalid` - This doesn't seem right
- `wontfix` - This will not be worked on

### Priority Labels

- `priority: high` - Should be fixed ASAP
- `priority: medium` - Should be fixed soon
- `priority: low` - Nice to have

### Component Labels

- `component: ui` - User interface related
- `component: database` - Database related
- `component: admin` - Admin functionality
- `component: reminders` - Reminder system
- `component: deployment` - Deployment related

---

## 📊 Development Workflow

### Feature Development
1. **Discussion**: Discuss feature in issue or discussion
2. **Design**: Plan implementation approach
3. **Development**: Write code following guidelines
4. **Testing**: Test thoroughly
5. **Review**: Code review and feedback
6. **Merge**: Merge when approved

### Bug Fixes
1. **Reproduce**: Confirm the bug exists
2. **Investigate**: Find root cause
3. **Fix**: Implement solution
4. **Test**: Verify fix works
5. **Review**: Code review
6. **Merge**: Deploy fix

---

## 🏆 Recognition

Contributors will be recognized in:
- GitHub contributors list
- CHANGELOG.md acknowledgments
- README.md contributors section
- Special thanks in releases

### Hall of Fame
Outstanding contributors may receive:
- Special contributor badge
- Mention in project announcements
- Priority support for their issues
- Early access to new features

---

## ❓ Questions?

- 💬 **General Questions**: [GitHub Discussions](https://github.com/yourusername/reminder-telegram-bot/discussions)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/reminder-telegram-bot/issues)
- 📧 **Direct Contact**: maintainer@reminderbot.com
- 💬 **Telegram**: [@YourBotDev](https://t.me/YourBotDev)

---

## 🙏 Thank You

Thank you for taking the time to contribute to RemindMeBot! Every contribution, no matter how small, makes a difference.

**Happy Coding! 🚀**
