import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from datetime import datetime, timedelta
from database.mongodb import DatabaseOperations
import config
from utils.helpers import parse_datetime, format_reminder_text, get_subscription_info, validate_reminder_input
from utils.ui_components import ui
from utils.animations import AnimationHelper

class EnhancedUserHandlers:
    def __init__(self):
        self.db = DatabaseOperations()
        self.animation = AnimationHelper()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command with animations"""
        user = update.effective_user
        chat_id = update.effective_chat.id

        # Show typing animation
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(1)

        # Create or get user from database
        db_user = self.db.create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

        # Send welcome sticker first
        try:
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker="CAACAgIAAxkBAAEMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Welcome sticker
            )
        except:
            pass  # Fallback if sticker fails

        # Create main keyboard
        keyboard = [
            [KeyboardButton("➕ Add Reminder"), KeyboardButton("📋 My Reminders")],
            [KeyboardButton("💳 Subscription"), KeyboardButton("📊 Plans")],
            [KeyboardButton("⚙️ Settings"), KeyboardButton("❓ Help")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

        # Send animated welcome message
        welcome_messages = [
            f"🎉 Welcome {user.first_name}!",
            "⚡ Initializing your personal reminder assistant...",
            "🚀 Ready! Let's help you stay organized!"
        ]

        for i, msg in enumerate(welcome_messages):
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(0.8)

            if i == len(welcome_messages) - 1:
                # Final message with full welcome
                full_welcome = ui.format_welcome_message(user.first_name)
                await update.message.reply_text(
                    full_welcome,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(msg)

    async def add_reminder_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced add reminder with step-by-step flow"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        # Check limits first
        if not self.db.can_create_reminder(user_id):
            await self._show_limit_reached(update, context)
            return

        # Start the flow with typing animation
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(1)

        # Step 1: Choose reminder type
        await update.message.reply_text(
            "🎯 **Let's create your reminder!**\n\n"
            "First, what type of reminder is this?",
            reply_markup=ui.create_reminder_type_menu(),
            parse_mode='Markdown'
        )

        # Store user state
        context.user_data['creating_reminder'] = True
        context.user_data['reminder_step'] = 'type'

    async def handle_reminder_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle reminder type selection"""
        query = update.callback_query
        await query.answer()

        reminder_type = query.data.replace('type_', '')
        context.user_data['reminder_type'] = reminder_type
        context.user_data['reminder_step'] = 'title'

        # Show typing animation
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(0.5)

        type_emoji = {
            'task': '✅', 'event': '📅', 'meeting': '👥',
            'appointment': '🏥', 'birthday': '🎂', 'deadline': '⚠️'
        }.get(reminder_type, '📝')

        await query.edit_message_text(
            f"{type_emoji} **Great choice!** You selected: **{reminder_type.title()}**\n\n"
            f"📝 Now, what's the title of your reminder?\n\n"
            f"💡 *Example: Team meeting, Buy groceries, Call mom*",
            parse_mode='Markdown'
        )

    async def process_reminder_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process reminder title input"""
        if not context.user_data.get('creating_reminder') or context.user_data.get('reminder_step') != 'title':
            return

        title = update.message.text.strip()

        # Validate title
        if len(title) > 200:
            await update.message.reply_text(
                "❌ Title too long! Please keep it under 200 characters.",
                reply_markup=ui.create_back_button("back_to_type")
            )
            return

        context.user_data['reminder_title'] = title
        context.user_data['reminder_step'] = 'description'

        # Show progress
        progress = self.animation.create_progress_bar(2, 5)

        await update.message.reply_text(
            f"✅ **Title saved:** {title}\n\n"
            f"{progress}\n\n"
            f"📝 Now add a description (optional):\n\n"
            f"💡 *Example: Discuss project timeline, Get milk and bread*\n\n"
            f"Or type 'skip' to continue without description.",
            parse_mode='Markdown'
        )

    async def process_reminder_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process reminder description"""
        if not context.user_data.get('creating_reminder') or context.user_data.get('reminder_step') != 'description':
            return

        description = update.message.text.strip()

        if description.lower() == 'skip':
            description = ""

        context.user_data['reminder_description'] = description
        context.user_data['reminder_step'] = 'time'

        # Show progress
        progress = self.animation.create_progress_bar(3, 5)

        await update.message.reply_text(
            f"✅ **Description saved**\n\n"
            f"{progress}\n\n"
            f"⏰ When should I remind you?\n\n"
            f"Choose a quick option or set custom time:",
            reply_markup=ui.create_quick_time_menu(),
            parse_mode='Markdown'
        )

    async def handle_quick_time_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quick time selection"""
        query = update.callback_query
        await query.answer()

        if query.data == "custom_time":
            await query.edit_message_text(
                "🕐 **Custom Time Setup**\n\n"
                "Please enter your preferred date and time:\n\n"
                "📅 **Formats you can use:**\n"
                "• `2024-12-25 14:30`\n"
                "• `tomorrow 10:00`\n"
                "• `next monday 15:30`\n"
                "• `in 2 hours`\n\n"
                "💡 *Example: tomorrow 09:00*",
                parse_mode='Markdown'
            )
            context.user_data['reminder_step'] = 'custom_time'
            return

        # Process quick time
        time_str = query.data.replace('quicktime_', '').replace('_', ' ')
        reminder_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')

        await self._finalize_reminder(query, context, reminder_time)

    async def process_custom_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process custom time input"""
        if not context.user_data.get('creating_reminder') or context.user_data.get('reminder_step') != 'custom_time':
            return

        time_input = update.message.text.strip()
        reminder_time = parse_datetime(time_input)

        if not reminder_time:
            await update.message.reply_text(
                "❌ **Invalid time format!**\n\n"
                "Please try again with one of these formats:\n"
                "• `2024-12-25 14:30`\n"
                "• `tomorrow 10:00`\n"
                "• `next monday 15:30`\n"
                "• `in 2 hours`",
                parse_mode='Markdown'
            )
            return

        if reminder_time <= datetime.utcnow():
            await update.message.reply_text(
                "❌ **Time cannot be in the past!**\n\n"
                "Please choose a future date and time.",
                parse_mode='Markdown'
            )
            return

        await self._finalize_reminder(update, context, reminder_time)

    async def _finalize_reminder(self, update_or_query, context: ContextTypes.DEFAULT_TYPE, reminder_time: datetime):
        """Finalize reminder creation with animation"""
        user_data = context.user_data
        user_id = update_or_query.from_user.id if hasattr(update_or_query, 'from_user') else update_or_query.effective_user.id

        # Show creation animation
        chat_id = update_or_query.message.chat_id if hasattr(update_or_query, 'message') else update_or_query.effective_chat.id

        # Animation sequence
        animation_steps = [
            "⏳ Creating your reminder...",
            "🔧 Setting up notification...",
            "✨ Almost done..."
        ]

        message = await context.bot.send_message(chat_id=chat_id, text=animation_steps[0])

        for i, step in enumerate(animation_steps[1:], 1):
            await asyncio.sleep(0.8)
            await message.edit_text(step)

        # Create reminder
        reminder = self.db.create_reminder(
            telegram_id=user_id,
            title=user_data['reminder_title'],
            description=user_data['reminder_description'],
            reminder_time=reminder_time,
            reminder_type=user_data['reminder_type']
        )

        # Clear user state
        context.user_data.clear()

        if reminder:
            # Success animation
            await asyncio.sleep(0.5)
            await message.edit_text(
                ui.success_message(
                    "Reminder Created Successfully! 🎉",
                    f"🎯 **{reminder['title']}**\n"
                    f"📝 {reminder['description'] or 'No description'}\n"
                    f"⏰ {reminder_time.strftime('%Y-%m-%d %H:%M')}\n"
                    f"🏷️ Type: {reminder['reminder_type'].title()}\n\n"
                    f"I'll remind you at the perfect time! ⚡"
                ),
                parse_mode='Markdown'
            )

            # Send success sticker
            try:
                await context.bot.send_sticker(
                    chat_id=chat_id,
                    sticker="CAACAgIAAxkBAAEMxxxxxxxxxx"  # Success sticker
                )
            except:
                pass

        else:
            await message.edit_text(
                ui.error_message(
                    "Creation Failed",
                    "Something went wrong. Please try again!"
                )
            )

    async def list_reminders_enhanced(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced reminder list with pagination"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        reminders = self.db.get_user_reminders(user_id)

        if not reminders:
            await update.message.reply_text(
                ui.info_box(
                    "No Reminders Yet",
                    "🌟 Create your first reminder to get started!\n\n"
                    "Use the '➕ Add Reminder' button below.",
                    "📭"
                ),
                reply_markup=ui.create_add_reminder_quick_button(),
                parse_mode='Markdown'
            )
            return

        # Show reminders with pagination
        page = context.user_data.get('reminder_page', 0)
        per_page = 5
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_reminders = reminders[start_idx:end_idx]

        reminder_text = f"📋 **Your Reminders** ({len(reminders)} total)\n\n"

        for i, reminder in enumerate(page_reminders, start_idx + 1):
            card = ui.format_reminder_card(reminder, i)
            reminder_text += card + "\n"

        # Create pagination keyboard
        keyboard = []
        nav_buttons = []

        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"page_{page-1}"))

        if end_idx < len(reminders):
            nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"page_{page+1}"))

        if nav_buttons:
            keyboard.append(nav_buttons)

        keyboard.append([
            InlineKeyboardButton("➕ Add New", callback_data="add_reminder"),
            InlineKeyboardButton("🗑️ Delete", callback_data="delete_reminder")
        ])

        await update.message.reply_text(
            reminder_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def _show_limit_reached(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show limit reached message with upgrade options"""
        user = self.db.get_user(update.effective_user.id)
        plan = config.SUBSCRIPTION_PLANS.get(user["subscription_plan"], config.SUBSCRIPTION_PLANS['free'])

        limit_message = ui.error_message(
            "Reminder Limit Reached! 🚫",
            f"You've reached your **{plan['name']}** limits:\n\n"
            f"📊 Max Reminders: {plan['max_reminders']}\n"
            f"📊 Daily Limit: {plan['max_daily_reminders']}\n\n"
            f"🚀 **Upgrade to get more reminders!**"
        )

        keyboard = [
            [InlineKeyboardButton("⭐ Upgrade Plan", callback_data="upgrade_plan")],
            [InlineKeyboardButton("📊 View Plans", callback_data="view_plans")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]

        await update.message.reply_text(
            limit_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# Create instance
enhanced_user_handlers = EnhancedUserHandlers()
