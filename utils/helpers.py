from datetime import datetime, timedelta
import re
from typing import Optional
import config

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == config.ADMIN_ID

def parse_datetime(datetime_str: str) -> Optional[datetime]:
    """Parse various datetime formats"""
    datetime_str = datetime_str.lower().strip()
    now = datetime.utcnow()

    # Handle relative times
    if 'tomorrow' in datetime_str:
        base_date = now + timedelta(days=1)
        time_part = datetime_str.replace('tomorrow', '').strip()
        if time_part:
            try:
                time_obj = datetime.strptime(time_part, '%H:%M').time()
                return datetime.combine(base_date.date(), time_obj)
            except:
                return base_date.replace(hour=9, minute=0, second=0, microsecond=0)
        return base_date.replace(hour=9, minute=0, second=0, microsecond=0)

    # Handle "in X hours/minutes"
    if 'in ' in datetime_str:
        time_match = re.search(r'in (\d+) (hour|minute|day)s?', datetime_str)
        if time_match:
            amount = int(time_match.group(1))
            unit = time_match.group(2)

            if unit == 'minute':
                return now + timedelta(minutes=amount)
            elif unit == 'hour':
                return now + timedelta(hours=amount)
            elif unit == 'day':
                return now + timedelta(days=amount)

    # Handle next weekday
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for i, day in enumerate(weekdays):
        if f'next {day}' in datetime_str:
            days_ahead = i - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            target_date = now + timedelta(days=days_ahead)

            time_part = datetime_str.replace(f'next {day}', '').strip()
            if time_part:
                try:
                    time_obj = datetime.strptime(time_part, '%H:%M').time()
                    return datetime.combine(target_date.date(), time_obj)
                except:
                    pass
            return target_date.replace(hour=9, minute=0, second=0, microsecond=0)

    # Handle standard formats
    formats = [
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d-%m-%Y %H:%M',
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y'
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(datetime_str, fmt)
            # If no time specified, set to 9 AM
            if fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                parsed = parsed.replace(hour=9, minute=0, second=0, microsecond=0)
            return parsed
        except ValueError:
            continue

    return None

def format_reminder_text(reminder: dict, index: int = None) -> str:
    """Format reminder for display"""
    emoji = "📅" if reminder.get('reminder_type') == 'event' else "✅"

    # Time formatting
    time_str = reminder['reminder_time'].strftime('%Y-%m-%d %H:%M')
    now = datetime.utcnow()
    time_diff = reminder['reminder_time'] - now

    if time_diff.days > 0:
        time_display = f"in {time_diff.days} days"
    elif time_diff.seconds > 3600:
        hours = time_diff.seconds // 3600
        time_display = f"in {hours} hours"
    elif time_diff.seconds > 60:
        minutes = time_diff.seconds // 60
        time_display = f"in {minutes} minutes"
    else:
        time_display = "very soon"

    index_str = f"{index}. " if index else ""

    text = f"{index_str}{emoji} **{reminder['title']}**\n"
    if reminder.get('description'):
        text += f"📝 {reminder['description']}\n"
    text += f"⏰ {time_str} ({time_display})\n"
    text += f"🏷️ {reminder.get('reminder_type', 'task').title()}\n"
    text += f"🆔 ID: `{reminder['_id']}`\n"

    return text

def format_user_info(user: dict) -> str:
    """Format user information for admin display"""
    name = f"{user.get('first_name', 'N/A')} {user.get('last_name', '') or ''}".strip()
    username = f"@{user.get('username')}" if user.get('username') else "No username"

    plan_emoji = "🆓" if user.get('subscription_plan') == 'free' else "⭐" if user.get('subscription_plan') == 'premium' else "💎"
    status_emoji = "🟢" if user.get('is_active', True) else "🔴"

    return (
        f"{status_emoji} **{name}** ({username})\n"
        f"🆔 ID: `{user['telegram_id']}`\n"
        f"{plan_emoji} Plan: {user.get('subscription_plan', 'free').title()}\n"
        f"📅 Joined: {user.get('created_at', 'N/A')}\n"
    )

def get_subscription_info(user: dict) -> str:
    """Get formatted subscription information"""
    plan_key = user.get('subscription_plan', 'free')
    plan = config.SUBSCRIPTION_PLANS.get(plan_key, config.SUBSCRIPTION_PLANS['free'])

    emoji = "🆓" if plan_key == 'free' else "⭐" if plan_key == 'premium' else "💎"

    max_reminders = "Unlimited" if plan['max_reminders'] == -1 else str(plan['max_reminders'])
    max_daily = "Unlimited" if plan['max_daily_reminders'] == -1 else str(plan['max_daily_reminders'])

    expires = user.get('subscription_expires')
    if expires:
        if isinstance(expires, str):
            expires_str = expires
        else:
            expires_str = expires.strftime('%Y-%m-%d %H:%M')

        now = datetime.utcnow()
        if isinstance(expires, datetime):
            is_active = now < expires
            days_left = (expires - now).days if is_active else 0
        else:
            is_active = True
            days_left = "N/A"
    else:
        expires_str = "Never"
        is_active = False
        days_left = 0

    status = "🟢 Active" if is_active else "🔴 Expired"

    text = f"""
💳 **Your Subscription Details**

{emoji} **Plan:** {plan['name']}
📊 **Status:** {status}
📅 **Expires:** {expires_str}
⏳ **Days Left:** {days_left if days_left != "N/A" else "N/A"}

📋 **Plan Features:**
• Max Reminders: {max_reminders}
• Daily Limit: {max_daily}
• Priority Support: {'Yes' if plan_key != 'free' else 'No'}
• Advanced Features: {'Yes' if plan_key == 'unlimited' else 'No'}

💰 **Monthly Cost:** {'Free' if plan['price'] == 0 else f'${plan["price"]}'}
    """

    return text

def create_progress_bar(current: int, maximum: int, length: int = 10) -> str:
    """Create a progress bar"""
    if maximum == -1:  # Unlimited
        return "∞ Unlimited"

    if maximum == 0:
        return "█" * length + " 0/0"

    progress = min(current / maximum, 1.0)
    filled = int(progress * length)
    bar = "█" * filled + "░" * (length - filled)

    return f"{bar} {current}/{maximum}"

def get_plan_emoji(plan_name: str) -> str:
    """Get emoji for subscription plan"""
    emojis = {
        'free': '🆓',
        'premium': '⭐',
        'unlimited': '💎'
    }
    return emojis.get(plan_name, '📦')

def get_reminder_type_emoji(reminder_type: str) -> str:
    """Get emoji for reminder type"""
    emojis = {
        'task': '✅',
        'event': '📅',
        'meeting': '👥',
        'appointment': '🏥',
        'birthday': '🎂',
        'deadline': '⚠️'
    }
    return emojis.get(reminder_type, '📝')

def format_time_remaining(target_time: datetime) -> str:
    """Format time remaining until target time"""
    now = datetime.utcnow()
    diff = target_time - now

    if diff.total_seconds() < 0:
        return "⏰ Overdue!"

    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"⏳ {days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"⏳ {hours}h {minutes}m"
    elif minutes > 0:
        return f"⏳ {minutes}m"
    else:
        return "⏰ Very soon!"

def validate_reminder_input(title: str, description: str, datetime_str: str) -> tuple[bool, str]:
    """Validate reminder input and return success status and error message"""
    if not title or len(title.strip()) == 0:
        return False, "❌ Title cannot be empty!"

    if len(title) > 200:
        return False, "❌ Title too long! Maximum 200 characters."

    if description and len(description) > 1000:
        return False, "❌ Description too long! Maximum 1000 characters."

    reminder_time = parse_datetime(datetime_str)
    if not reminder_time:
        return False, "❌ Invalid date format!"

    if reminder_time <= datetime.utcnow():
        return False, "❌ Reminder time cannot be in the past!"

    return True, "✅ Valid input"

def generate_quick_time_buttons() -> list:
    """Generate quick time selection buttons"""
    now = datetime.utcnow()
    buttons = []

    # Quick time options
    times = [
        ("1 hour", now + timedelta(hours=1)),
        ("3 hours", now + timedelta(hours=3)),
        ("Tomorrow 9AM", (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)),
        ("Next week", now + timedelta(weeks=1)),
    ]

    for label, time in times:
        buttons.append({
            'text': f"⏰ {label}",
            'callback_data': f"quicktime_{time.strftime('%Y-%m-%d_%H:%M')}"
        })

    return buttons
