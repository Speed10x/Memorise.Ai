from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
import config
from .helpers import get_plan_emoji, create_progress_bar, format_time_remaining
from .animations import AnimationHelper

class UIComponents:

    @staticmethod
    def loading_animation(step: int = 0) -> str:
        """Create loading animation"""
        frames = ["⏳", "⌛", "⏳", "⌛"]
        return frames[step % len(frames)]

    @staticmethod
    def success_message(title: str, message: str) -> str:
        """Create success message with animation"""
        return f"""
✨ **{title}** ✨

{message}

━━━━━━━━━━━━━━━━━━━━
        """

    @staticmethod
    def error_message(title: str, message: str) -> str:
        """Create error message"""
        return f"""
❌ **{title}**

{message}

💡 **Need Help?** Use /help for guidance
━━━━━━━━━━━━━━━━━━━━
        """

    @staticmethod
    def info_box(title: str, content: str, emoji: str = "ℹ️") -> str:
        """Create info box"""
        return f"""
{emoji} **{title}**

{content}

━━━━━━━━━━━━━━━━━━━━
        """

    @staticmethod
    def create_main_menu() -> InlineKeyboardMarkup:
        """Create animated main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("✨ Add Reminder", callback_data="add_reminder"),
                InlineKeyboardButton("📋 My Reminders", callback_data="list_reminders")
            ],
            [
                InlineKeyboardButton("💎 Subscription", callback_data="subscription"),
                InlineKeyboardButton("🚀 Upgrade", callback_data="plans")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                InlineKeyboardButton("💬 Help", callback_data="help")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="user_stats")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_add_reminder_quick_button() -> InlineKeyboardMarkup:
        """Create quick add reminder button"""
        keyboard = [
            [InlineKeyboardButton("🎯 Create Your First Reminder", callback_data="add_reminder")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_back_button(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
        """Create back button"""
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data=callback_data)]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_reminder_type_menu() -> InlineKeyboardMarkup:
        """Create reminder type selection menu"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Task", callback_data="type_task"),
                InlineKeyboardButton("📅 Event", callback_data="type_event")
            ],
            [
                InlineKeyboardButton("👥 Meeting", callback_data="type_meeting"),
                InlineKeyboardButton("🏥 Appointment", callback_data="type_appointment")
            ],
            [
                InlineKeyboardButton("🎂 Birthday", callback_data="type_birthday"),
                InlineKeyboardButton("⚠️ Deadline", callback_data="type_deadline")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_quick_time_menu() -> InlineKeyboardMarkup:
        """Create quick time selection menu"""
        now = datetime.utcnow()
        keyboard = [
            [
                InlineKeyboardButton("⏰ 1 Hour", callback_data=f"quicktime_{(now + timedelta(hours=1)).strftime('%Y-%m-%d_%H:%M')}"),
                InlineKeyboardButton("⏰ 3 Hours", callback_data=f"quicktime_{(now + timedelta(hours=3)).strftime('%Y-%m-%d_%H:%M')}")
            ],
            [
                InlineKeyboardButton("🌅 Tomorrow 9AM", callback_data=f"quicktime_{(now + timedelta(days=1)).replace(hour=9, minute=0).strftime('%Y-%m-%d_%H:%M')}"),
                InlineKeyboardButton("📅 Next Week", callback_data=f"quicktime_{(now + timedelta(weeks=1)).strftime('%Y-%m-%d_%H:%M')}")
            ],
            [
                InlineKeyboardButton("📝 Custom Time", callback_data="custom_time"),
                InlineKeyboardButton("🔙 Back", callback_data="back_to_add")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_reminder_actions_menu(reminder_id: str) -> InlineKeyboardMarkup:
        """Create reminder action menu"""
        keyboard = [
            [
                InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{reminder_id}"),
                InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{reminder_id}")
            ],
            [
                InlineKeyboardButton("⏰ Reschedule", callback_data=f"reschedule_{reminder_id}"),
                InlineKeyboardButton("📋 Details", callback_data=f"details_{reminder_id}")
            ],
            [
                InlineKeyboardButton("🔙 Back to List", callback_data="list_reminders")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_subscription_menu() -> InlineKeyboardMarkup:
        """Create subscription management menu"""
        keyboard = [
            [
                InlineKeyboardButton("💳 Upgrade Plan", callback_data="upgrade_plan"),
                InlineKeyboardButton("📊 Usage Stats", callback_data="usage_stats")
            ],
            [
                InlineKeyboardButton("💰 Billing History", callback_data="billing_history"),
                InlineKeyboardButton("📧 Contact Support", callback_data="contact_support")
            ],
            [
                InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_admin_menu() -> InlineKeyboardMarkup:
        """Create admin menu"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton("💳 Manage Subs", callback_data="admin_subscriptions")
            ],
            [
                InlineKeyboardButton("💾 Backup", callback_data="admin_backup"),
                InlineKeyboardButton("🔧 Settings", callback_data="admin_settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def format_welcome_message(user_name: str) -> str:
        """Create animated welcome message"""
        return f"""
🎉 **Welcome to RemindMeBot!** 🎉

Hello **{user_name}**! 👋

I'm your personal reminder assistant, here to help you never forget important tasks and events again!

✨ **What I can do for you:**
• 📝 Create smart reminders
• 📅 Manage events & tasks
• ⏰ Send timely notifications
• 📊 Track your productivity
• 🔄 Set recurring reminders

🆓 **You're on the Free Plan:**
• {config.SUBSCRIPTION_PLANS['free']['max_reminders']} reminders maximum
• {config.SUBSCRIPTION_PLANS['free']['max_daily_reminders']} daily reminders
• Basic features included

🚀 **Ready to get started?**
Use the menu below or type /help for commands!

━━━━━━━━━━━━━━━━━━━━━━━━━
        """

    @staticmethod
    def format_reminder_card(reminder: dict, index: int = None) -> str:
        """Create a beautiful reminder card"""
        emoji = {
            'task': '✅',
            'event': '📅',
            'meeting': '👥',
            'appointment': '🏥',
            'birthday': '🎂',
            'deadline': '⚠️'
        }.get(reminder.get('reminder_type', 'task'), '📝')

        time_remaining = format_time_remaining(reminder['reminder_time'])

        index_str = f"**{index}.** " if index else ""

        card = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ {index_str}{emoji} **{reminder['title']}**
┃
┃ 📝 {reminder.get('description', 'No description')}
┃
┃ ⏰ {reminder['reminder_time'].strftime('%Y-%m-%d %H:%M')}
┃ {time_remaining}
┃
┃ 🏷️ Type: {reminder.get('reminder_type', 'task').title()}
┃ 🆔 ID: `{reminder['_id']}`
┗━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
        return card

    @staticmethod
    def format_subscription_card(user: dict, stats: dict = None) -> str:
        """Create subscription status card"""
        plan_key = user.get('subscription_plan', 'free')
        plan = config.SUBSCRIPTION_PLANS.get(plan_key, config.SUBSCRIPTION_PLANS['free'])
        emoji = get_plan_emoji(plan_key)

        # Calculate usage if stats provided
        usage_info = ""
        if stats:
            reminder_progress = create_progress_bar(
                stats.get('total_reminders', 0),
                plan['max_reminders']
            )
            daily_progress = create_progress_bar(
                stats.get('daily_reminders', 0),
                plan['max_daily_reminders']
            )

            usage_info = f"""
┃ 📊 **Current Usage:**
┃ Total: {reminder_progress}
┃ Daily: {daily_progress}
┃
"""

        expires = user.get('subscription_expires')
        if expires and isinstance(expires, datetime):
            expires_str = expires.strftime('%Y-%m-%d')
            days_left = (expires - datetime.utcnow()).days
            status = "🟢 Active" if days_left > 0 else "🔴 Expired"
        else:
            expires_str = "Never"
            days_left = "∞"
            status = "🟢 Active"

        card = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ {emoji} **{plan['name']}**
┃
┃ 📊 **Status:** {status}
┃ 📅 **Expires:** {expires_str}
┃ ⏳ **Days Left:** {days_left}
┃
{usage_info}┃ 🎯 **Features:**
┃ • Max Reminders: {'∞' if plan['max_reminders'] == -1 else plan['max_reminders']}
┃ • Daily Limit: {'∞' if plan['max_daily_reminders'] == -1 else plan['max_daily_reminders']}
┃ • Priority Support: {'✅' if plan_key != 'free' else '❌'}
┃
┃ 💰 **Cost:** {'Free' if plan['price'] == 0 else f'${plan["price"]}/month'}
┗━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
        return card

    @staticmethod
    def format_stats_dashboard(stats: dict) -> str:
        """Create admin stats dashboard"""
        return f"""
📊 **Bot Statistics Dashboard**

┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 👥 **Users**
┃ • Total: {stats.get('total_users', 0):,}
┃ • Active: {stats.get('active_users', 0):,}
┃ • Growth: +{stats.get('new_users_today', 0)} today
┃
┃ 📋 **Reminders**
┃ • Total Active: {stats.get('total_reminders', 0):,}
┃ • Sent Today: {stats.get('reminders_sent_today', 0):,}
┃ • Success Rate: {stats.get('success_rate', 95)}%
┃
┃ 💳 **Subscriptions**
┃ • Free Users: {stats.get('free_users', 0):,}
┃ • Premium Users: {stats.get('premium_users', 0):,}
┃ • Unlimited Users: {stats.get('unlimited_users', 0):,}
┃
┃ 🕒 **Last Updated**
┃ {stats.get('last_updated', datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')}
┗━━━━━━━━━━━━━━━━━━━━━━━━┛
        """

    @staticmethod
    def create_confirmation_dialog(action: str, item: str) -> InlineKeyboardMarkup:
        """Create confirmation dialog"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes, Continue", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def format_help_message() -> str:
        """Create comprehensive help message"""
        return f"""
🤖 **RemindMeBot - Complete Guide**

━━━━━ **Quick Start** ━━━━━
🎯 Use the menu buttons below for easy navigation!

━━━━━ **Commands** ━━━━━
📝 `/add` - Create new reminder
📋 `/list` - View all reminders
🗑️ `/delete` - Remove reminder
💳 `/subscription` - Check your plan
📊 `/plans` - View upgrade options
⚙️ `/settings` - Bot preferences

━━━━━ **Adding Reminders** ━━━━━
**Format:** `/add Title | Description | Time | Type`

**Examples:**
• `/add Team Meeting | Daily standup | tomorrow 10:00 | meeting`
• `/add Buy Groceries | Milk, bread, eggs | 2024-12-25 18:00 | task`
• `/add Mom's Birthday | Call and wish | next monday 12:00 | birthday`

━━━━━ **Time Formats** ━━━━━
✅ `2024-12-25 14:30` (Full date/time)
✅ `tomorrow 10:00` (Relative)
✅ `next monday 15:30` (Next weekday)
✅ `in 2 hours` (Relative time)

━━━━━ **Reminder Types** ━━━━━
• `task` - General tasks ✅
• `event` - Important events 📅
• `meeting` - Meetings 👥
• `appointment` - Appointments 🏥
• `birthday` - Birthdays 🎂
• `deadline` - Deadlines ⚠️

━━━━━ **Subscription Plans** ━━━━━
🆓 **Free:** {config.SUBSCRIPTION_PLANS['free']['max_reminders']} reminders
⭐ **Premium:** {config.SUBSCRIPTION_PLANS['premium']['max_reminders']} reminders (${config.SUBSCRIPTION_PLANS['premium']['price']}/mo)
💎 **Unlimited:** ∞ reminders (${config.SUBSCRIPTION_PLANS['unlimited']['price']}/mo)

━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **Pro Tip:** Use the interactive menu for the best experience!
        """

# Create global instance
ui = UIComponents()
