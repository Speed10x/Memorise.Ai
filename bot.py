import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ChatAction
from datetime import datetime

import config
from handlers.enhanced_user_handlers import enhanced_user_handlers
from handlers.admin_handlers import admin_handlers
from database.mongodb import DatabaseOperations
from utils.helpers import is_admin
from utils.ui_components import ui
from utils.animations import AnimationHelper

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ReminderBot:
    def __init__(self):
        self.application = Application.builder().token(config.BOT_TOKEN).build()
        self.db = DatabaseOperations()
        self.animation = AnimationHelper()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup all command and message handlers"""

        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_handler))
        self.application.add_handler(CommandHandler("help", self.help_handler))
        self.application.add_handler(CommandHandler("add", enhanced_user_handlers.add_reminder_flow))
        self.application.add_handler(CommandHandler("list", enhanced_user_handlers.list_reminders_enhanced))
        self.application.add_handler(CommandHandler("subscription", self.subscription_handler))
        self.application.add_handler(CommandHandler("plans", self.plans_handler))
        self.application.add_handler(CommandHandler("stats", self.user_stats_handler))

        # Admin commands
        self.application.add_handler(CommandHandler("admin", admin_handlers.admin_panel_command))
        self.application.add_handler(CommandHandler("adminstats", admin_handlers.stats_command))
        self.application.add_handler(CommandHandler("users", admin_handlers.users_command))
        self.application.add_handler(CommandHandler("broadcast", admin_handlers.broadcast_command))
        self.application.add_handler(CommandHandler("grant", admin_handlers.grant_subscription_command))
        self.application.add_handler(CommandHandler("revoke", admin_handlers.revoke_subscription_command))
        self.application.add_handler(CommandHandler("userinfo", admin_handlers.userinfo_command))

        # Message handlers for interactive flows
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_messages
        ))

        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_queries))

        # Error handler
        self.application.add_error_handler(self.error_handler)

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command with animations"""
        await enhanced_user_handlers.start_command(update, context)

    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced help command"""
        chat_id = update.effective_chat.id

        # Show typing animation
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(1)

        help_message = ui.format_help_message()

        await update.message.reply_text(
            help_message,
            reply_markup=ui.create_main_menu(),
            parse_mode='Markdown'
        )

    async def subscription_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle subscription command"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        user = self.db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ User not found. Please use /start first.")
            return

        # Get usage stats
        reminders = self.db.get_user_reminders(user_id)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_reminders = len([r for r in reminders if r.get('created_at', datetime.min) >= today])

        stats = {
            'total_reminders': len(reminders),
            'daily_reminders': today_reminders
        }

        subscription_card = ui.format_subscription_card(user, stats)

        await update.message.reply_text(
            subscription_card,
            reply_markup=ui.create_subscription_menu(),
            parse_mode='Markdown'
        )

    async def plans_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle plans command with enhanced UI"""
        chat_id = update.effective_chat.id

        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(1)

        plans_text = "💎 **Choose Your Perfect Plan** 💎\n\n"

        for plan_key, plan in config.SUBSCRIPTION_PLANS.items():
            emoji = "🆓" if plan_key == "free" else "⭐" if plan_key == "premium" else "💎"

            max_reminders = "∞ Unlimited" if plan['max_reminders'] == -1 else f"{plan['max_reminders']} reminders"
            max_daily = "∞ Unlimited" if plan['max_daily_reminders'] == -1 else f"{plan['max_daily_reminders']} per day"

            features = []
            if plan_key != 'free':
                features.append("✅ Priority Support")
                features.append("✅ Advanced Features")
                if plan_key == 'unlimited':
                    features.append("✅ API Access")
                    features.append("✅ Custom Integrations")

            feature_text = "\n".join(features) if features else "✅ Basic Features"

            plans_text += f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ {emoji} **{plan['name']}**
┃
┃ 📊 **Limits:**
┃ • {max_reminders}
┃ • {max_daily}
┃
┃ 🎯 **Features:**
┃ {feature_text}
┃
┃ 💰 **Price:** {'FREE' if plan['price'] == 0 else f'${plan["price"]}/month'}
┗━━━━━━━━━━━━━━━━━━━━━━━━┛

"""

        plans_text += "\n💬 **Contact admin to upgrade:** @your_admin_username"

        keyboard = [
            [InlineKeyboardButton("💳 Check My Plan", callback_data="subscription")],
            [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/your_admin_username")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]

        await update.message.reply_text(
            plans_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def user_stats_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user stats command"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        user = self.db.get_user(user_id)
        reminders = self.db.get_user_reminders(user_id)

        # Calculate stats
        total_reminders = len(reminders)
        completed_reminders = len([r for r in reminders if r.get('is_sent', False)])
        active_reminders = len([r for r in reminders if r.get('is_active', True) and not r.get('is_sent', False)])

        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_reminders = len([r for r in reminders if r.get('created_at', datetime.min) >= today])

        # Usage progress
        plan = config.SUBSCRIPTION_PLANS.get(user.get('subscription_plan', 'free'))
        usage_progress = self.animation.create_usage_meter(total_reminders, plan['max_reminders'])
        daily_progress = self.animation.create_usage_meter(today_reminders, plan['max_daily_reminders'])

        stats_text = f"""
📊 **Your Personal Stats** 📊

┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 👤 **Account Info**
┃ • Name: {user.get('first_name', 'Unknown')}
┃ • Plan: {plan['name']}
┃ • Member since: {user.get('created_at', 'Unknown')[:10] if user.get('created_at') else 'Unknown'}
┃
┃ 📋 **Reminder Stats**
┃ • Total Created: {total_reminders}
┃ • Active: {active_reminders}
┃ • Completed: {completed_reminders}
┃ • Today: {today_reminders}
┃
┃ 📊 **Usage**
┃ • Total: {usage_progress}
┃ • Daily: {daily_progress}
┃
┃ 🎯 **Success Rate**
┃ • {(completed_reminders/total_reminders*100) if total_reminders > 0 else 0:.1f}% completed
┗━━━━━━━━━━━━━━━━━━━━━━━━┛
        """

        keyboard = [
            [
                InlineKeyboardButton("📋 View Reminders", callback_data="list_reminders"),
                InlineKeyboardButton("➕ Add New", callback_data="add_reminder")
            ],
            [
                InlineKeyboardButton("💳 Subscription", callback_data="subscription"),
                InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
            ]
        ]

        await update.message.reply_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def handle_text_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages for interactive flows"""
        text = update.message.text.lower().strip()

        # Handle keyboard button presses
        if text == "➕ add reminder":
            await enhanced_user_handlers.add_reminder_flow(update, context)
        elif text == "📋 my reminders":
            await enhanced_user_handlers.list_reminders_enhanced(update, context)
        elif text == "💳 subscription":
            await self.subscription_handler(update, context)
        elif text == "📊 plans":
            await self.plans_handler(update, context)
        elif text == "⚙️ settings":
            await self.settings_handler(update, context)
        elif text == "❓ help":
            await self.help_handler(update, context)
        else:
            # Handle reminder creation flow
            if context.user_data.get('creating_reminder'):
                if context.user_data.get('reminder_step') == 'title':
                    await enhanced_user_handlers.process_reminder_title(update, context)
                elif context.user_data.get('reminder_step') == 'description':
                    await enhanced_user_handlers.process_reminder_description(update, context)
                elif context.user_data.get('reminder_step') == 'custom_time':
                    await enhanced_user_handlers.process_custom_time(update, context)
            else:
                # Default response with suggestions
                await self.handle_unknown_message(update, context)

    async def handle_callback_queries(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()

        data = query.data

        # Main menu callbacks
        if data == "main_menu":
            await query.edit_message_text(
                "🏠 **Main Menu**\n\nChoose an option:",
                reply_markup=ui.create_main_menu(),
                parse_mode='Markdown'
            )

        # Reminder type selection
        elif data.startswith("type_"):
            await enhanced_user_handlers.handle_reminder_type_selection(update, context)

        # Quick time selection
        elif data.startswith("quicktime_"):
            await enhanced_user_handlers.handle_quick_time_selection(update, context)

        # Add reminder flow
        elif data == "add_reminder":
            # Convert to message-like object for handler
            fake_update = type('FakeUpdate', (), {
                'effective_user': query.from_user,
                'effective_chat': query.message.chat,
                'message': type('FakeMessage', (), {'reply_text': query.message.reply_text})()
            })()
            await enhanced_user_handlers.add_reminder_flow(fake_update, context)

        # Other callbacks
        elif data == "subscription":
            await self._handle_subscription_callback(query, context)
        elif data == "plans":
            await self._handle_plans_callback(query, context)
        elif data == "list_reminders":
            await self._handle_list_reminders_callback(query, context)
        elif data == "user_stats":
            await self._handle_user_stats_callback(query, context)

        # Admin callbacks
        elif data.startswith("admin_") and is_admin(query.from_user.id):
            await self._handle_admin_callbacks(query, context)

    async def _handle_subscription_callback(self, query, context):
        """Handle subscription callback"""
        user_id = query.from_user.id
        user = self.db.get_user(user_id)

        if user:
            reminders = self.db.get_user_reminders(user_id)
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_reminders = len([r for r in reminders if r.get('created_at', datetime.min) >= today])

            stats = {
                'total_reminders': len(reminders),
                'daily_reminders': today_reminders
            }

            subscription_card = ui.format_subscription_card(user, stats)

            await query.edit_message_text(
                subscription_card,
                reply_markup=ui.create_subscription_menu(),
                parse_mode='Markdown'
            )

    async def _handle_admin_callbacks(self, query, context):
        """Handle admin callbacks"""
        data = query.data

        if data == "admin_stats":
            stats = self.db.update_bot_stats()
            stats_text = ui.format_stats_dashboard(stats)

            await query.edit_message_text(
                stats_text,
                reply_markup=ui.create_admin_menu(),
                parse_mode='Markdown'
            )

    async def settings_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings command"""
        settings_text = """
⚙️ **Bot Settings**

🔧 **Available Settings:**
• Notification preferences
• Time zone settings
• Reminder frequency
• Privacy options

🚧 **Coming Soon:**
More customization options will be available in future updates!
        """

        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]

        await update.message.reply_text(
            settings_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def handle_unknown_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown messages with helpful suggestions"""
        suggestions = [
            "➕ Create a new reminder",
            "📋 View your reminders",
            "💳 Check subscription",
            "❓ Get help"
        ]

        keyboard = [
            [InlineKeyboardButton(suggestions[0], callback_data="add_reminder")],
            [InlineKeyboardButton(suggestions[1], callback_data="list_reminders")],
            [InlineKeyboardButton(suggestions[2], callback_data="subscription")],
            [InlineKeyboardButton(suggestions[3], callback_data="help")]
        ]

        await update.message.reply_text(
            "🤔 I didn't understand that.\n\n"
            "Here's what you can do:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        logger.error("Exception while handling an update:", exc_info=context.error)

        # Inform user about the error
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "🚫 **Oops! Something went wrong.**\n\n"
                "Our team has been notified. Please try again in a moment.\n\n"
                "If the problem persists, contact support.",
                parse_mode='Markdown'
            )

    def run(self):
        """Start the bot"""
        logger.info("Starting RemindMeBot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

# Create bot instance
reminder_bot = ReminderBot()
