from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database.mongodb import DatabaseOperations
import config
from utils.helpers import parse_datetime, format_reminder_text, get_subscription_info

class UserHandlers:
    def __init__(self):
        self.db = DatabaseOperations()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user

        # Create or get user from database
        db_user = self.db.create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

        welcome_text = f"""
🎉 Welcome to Reminder Bot, {user.first_name}!

I can help you manage your reminders and never forget important tasks or events.

📋 **Available Commands:**
/help - Show all commands
/add - Add a new reminder
/list - View your reminders
/delete - Delete a reminder
/subscription - Check your subscription status
/plans - View subscription plans

🆓 You're currently on the **Free Plan** with {config.SUBSCRIPTION_PLANS['free']['max_reminders']} reminders limit.

Type /help to see all available commands!
        """

        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **Reminder Bot Help**

**Basic Commands:**
/start - Start the bot
/help - Show this help message
/add - Add a new reminder
/list - View all your reminders
/delete - Delete a reminder
/subscription - Check subscription status
/plans - View available plans

**Adding Reminders:**
Format: `/add Title | Description | Date Time | Type`

Examples:
• `/add Meeting | Team standup | 2024-12-25 14:30 | event`
• `/add Buy groceries | Milk, bread, eggs | tomorrow 10:00 | task`
• `/add Call mom | Weekly call | 2024-12-20 18:00 | task`

**Date Formats:**
• `2024-12-25 14:30` (YYYY-MM-DD HH:MM)
• `tomorrow 10:00`
• `next monday 15:30`
• `in 2 hours`

**Reminder Types:**
• `task` - General tasks
• `event` - Important events

**Subscription Plans:**
• Free: {config.SUBSCRIPTION_PLANS['free']['max_reminders']} reminders
• Premium: {config.SUBSCRIPTION_PLANS['premium']['max_reminders']} reminders (${config.SUBSCRIPTION_PLANS['premium']['price']}/month)
• Unlimited: Unlimited reminders (${config.SUBSCRIPTION_PLANS['unlimited']['price']}/month)
        """

        await update.message.reply_text(help_text)

    async def add_reminder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add command"""
        user_id = update.effective_user.id

        # Check if user can create reminder
        if not self.db.can_create_reminder(user_id):
            user = self.db.get_user(user_id)
            plan = config.SUBSCRIPTION_PLANS.get(user["subscription_plan"], config.SUBSCRIPTION_PLANS['free'])

            await update.message.reply_text(
                f"❌ You've reached your reminder limit!\n\n"
                f"Current plan: **{plan['name']}**\n"
                f"Max reminders: {plan['max_reminders']}\n"
                f"Max daily reminders: {plan['max_daily_reminders']}\n\n"
                f"Upgrade your plan with /plans to create more reminders!"
            )
            return

        # Parse command arguments
        if not context.args:
            await update.message.reply_text(
                "📝 **Add a New Reminder**\n\n"
                "Format: `/add Title | Description | Date Time | Type`\n\n"
                "Example:\n"
                "`/add Meeting | Team standup | 2024-12-25 14:30 | event`\n\n"
                "Type can be: `task` or `event`"
            )
            return

        try:
            # Join all arguments and split by |
            full_text = " ".join(context.args)
            parts = [part.strip() for part in full_text.split("|")]

            if len(parts) < 3:
                await update.message.reply_text(
                    "❌ Invalid format! Please use:\n"
                    "`/add Title | Description | Date Time | Type`"
                )
                return

            title = parts[0]
            description = parts[1] if len(parts) > 1 else ""
            datetime_str = parts[2] if len(parts) > 2 else ""
            reminder_type = parts[3].lower() if len(parts) > 3 else "task"

            # Validate reminder type
            if reminder_type not in ["task", "event"]:
                reminder_type = "task"

            # Parse datetime
            reminder_time = parse_datetime(datetime_str)
            if not reminder_time:
                await update.message.reply_text(
                    "❌ Invalid date format! Please use:\n"
                    "• `2024-12-25 14:30`\n"
                    "• `tomorrow 10:00`\n"
                    "• `next monday 15:30`\n"
                    "• `in 2 hours`"
                )
                return

            # Check if reminder time is in the past
            if reminder_time <= datetime.utcnow():
                await update.message.reply_text(
                    "❌ Reminder time cannot be in the past!"
                )
                return

            # Create reminder
            reminder = self.db.create_reminder(
                telegram_id=user_id,
                title=title,
                description=description,
                reminder_time=reminder_time,
                reminder_type=reminder_type
            )

            if reminder:
                await update.message.reply_text(
                    f"✅ **Reminder Created Successfully!**\n\n"
                    f"📋 **Title:** {title}\n"
                    f"📝 **Description:** {description}\n"
                    f"⏰ **Time:** {reminder_time.strftime('%Y-%m-%d %H:%M')}\n"
                    f"🏷️ **Type:** {reminder_type.title()}\n\n"
                    f"I'll remind you at the specified time!"
                )
            else:
                await update.message.reply_text(
                    "❌ Failed to create reminder. Please try again."
                )

        except Exception as e:
            await update.message.reply_text(
                f"❌ Error creating reminder: {str(e)}\n\n"
                "Please check the format and try again."
            )

    async def list_reminders_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command"""
        user_id = update.effective_user.id
        reminders = self.db.get_user_reminders(user_id)

        if not reminders:
            await update.message.reply_text(
                "📭 You don't have any active reminders.\n\n"
                "Use /add to create your first reminder!"
            )
            return

        text = "📋 **Your Active Reminders:**\n\n"

        for i, reminder in enumerate(reminders[:20], 1):  # Limit to 20 reminders
            reminder_text = format_reminder_text(reminder, i)
            text += reminder_text + "\n"

        if len(reminders) > 20:
            text += f"\n... and {len(reminders) - 20} more reminders."

        text += f"\n\nTotal: {len(reminders)} reminders"

        await update.message.reply_text(text, parse_mode='Markdown')

    async def delete_reminder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /delete command"""
        user_id = update.effective_user.id

        if not context.args:
            # Show list of reminders with delete buttons
            reminders = self.db.get_user_reminders(user_id)

            if not reminders:
                await update.message.reply_text(
                    "📭 You don't have any reminders to delete."
                )
                return

            # Create inline keyboard with reminder options
            keyboard = []
            for reminder in reminders[:10]:  # Limit to 10 for better UX
                button_text = f"{reminder['title'][:30]}... - {reminder['reminder_time'].strftime('%m/%d %H:%M')}"
                callback_data = f"delete_{reminder['_id']}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

            keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "🗑️ **Select a reminder to delete:**",
                reply_markup=reply_markup
            )
        else:
            # Direct delete by ID (if provided)
            try:
                reminder_id = context.args[0]
                if self.db.delete_reminder(reminder_id, user_id):
                    await update.message.reply_text(
                        "✅ Reminder deleted successfully!"
                    )
                else:
                    await update.message.reply_text(
                        "❌ Reminder not found or already deleted."
                    )
            except Exception as e:
                await update.message.reply_text(
                    "❌ Invalid reminder ID format."
                )

    async def subscription_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscription command"""
        user_id = update.effective_user.id
        user = self.db.get_user(user_id)

        if not user:
            await update.message.reply_text("❌ User not found. Please use /start first.")
            return

        subscription_info = get_subscription_info(user)

        await update.message.reply_text(subscription_info, parse_mode='Markdown')

    async def plans_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /plans command"""
        plans_text = "💳 **Available Subscription Plans:**\n\n"

        for plan_key, plan in config.SUBSCRIPTION_PLANS.items():
            emoji = "🆓" if plan_key == "free" else "⭐" if plan_key == "premium" else "💎"

            max_reminders = "Unlimited" if plan['max_reminders'] == -1 else str(plan['max_reminders'])
            max_daily = "Unlimited" if plan['max_daily_reminders'] == -1 else str(plan['max_daily_reminders'])

            plans_text += f"{emoji} **{plan['name']}**\n"
            plans_text += f"• Max Reminders: {max_reminders}\n"
            plans_text += f"• Daily Limit: {max_daily}\n"

            if plan['price'] > 0:
                plans_text += f"• Price: ${plan['price']}/month\n"
            else:
                plans_text += f"• Price: Free\n"

            plans_text += "\n"

        plans_text += "💬 Contact admin to upgrade your plan: @your_admin_username"

        await update.message.reply_text(plans_text, parse_mode='Markdown')

    # Callback query handlers
    async def handle_delete_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle delete reminder callback"""
        query = update.callback_query
        await query.answer()

        if query.data == "cancel_delete":
            await query.edit_message_text("❌ Delete operation cancelled.")
            return

        if query.data.startswith("delete_"):
            reminder_id = query.data.replace("delete_", "")
            user_id = query.from_user.id

            if self.db.delete_reminder(reminder_id, user_id):
                await query.edit_message_text("✅ Reminder deleted successfully!")
            else:
                await query.edit_message_text("❌ Failed to delete reminder.")

# Create instance for easy import
user_handlers = UserHandlers()
