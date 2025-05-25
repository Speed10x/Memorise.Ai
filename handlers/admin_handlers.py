from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database.mongodb import DatabaseOperations
import config
from utils.helpers import is_admin, format_user_info

class AdminHandlers:
    def __init__(self):
        self.db = DatabaseOperations()

    async def admin_panel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return

        stats = self.db.get_bot_stats()

        admin_text = f"""
🔧 **Admin Panel**

📊 **Bot Statistics:**
• Total Users: {stats['total_users']}
• Active Users: {stats['active_users']}
• Total Reminders: {stats['total_reminders']}
• Reminders Sent Today: {stats['reminders_sent_today']}

📋 **Admin Commands:**
/users - List all users
/stats - Detailed statistics
/broadcast - Send message to all users
/grant [user_id] [plan] [days] - Grant subscription
/revoke [user_id] - Revoke subscription
/userinfo [user_id] - Get user information
/backup - Create database backup
/logs - View recent logs

🕒 Last Updated: {stats['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}
        """

        await update.message.reply_text(admin_text, parse_mode='Markdown')

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return

        # Update and get fresh stats
        stats = self.db.update_bot_stats()

        # Get subscription breakdown
        users = self.db.get_all_users()
        plan_counts = {"free": 0, "premium": 0, "unlimited": 0}
        active_subscriptions = 0

        for user in users:
            plan = user.get("subscription_plan", "free")
            plan_counts[plan] = plan_counts.get(plan, 0) + 1

            if self.db.is_subscription_active(user["telegram_id"]):
                active_subscriptions += 1

        # Calculate today's registrations
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_registrations = len([u for u in users if u.get("created_at", datetime.min) >= today])

        detailed_stats = f"""
📊 **Detailed Bot Statistics**

👥 **Users:**
• Total Users: {stats['total_users']}
• Active Users: {stats['active_users']}
• New Today: {today_registrations}
• Active Subscriptions: {active_subscriptions}

📋 **Subscription Plans:**
• Free Plan: {plan_counts['free']} users
• Premium Plan: {plan_counts['premium']} users
• Unlimited Plan: {plan_counts['unlimited']} users

⏰ **Reminders:**
• Total Active: {stats['total_reminders']}
• Sent Today: {stats['reminders_sent_today']}

🕒 **Last Updated:** {stats['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}
        """

        await update.message.reply_text(detailed_stats, parse_mode='Markdown')

    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /users command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return

        users = self.db.get_all_users()

        if not users:
            await update.message.reply_text("No users found.")
            return

        # Sort users by registration date (newest first)
        users.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)

        users_text = "👥 **All Users** (Latest 20):\n\n"

        for user in users[:20]:  # Show latest 20 users
            user_info = format_user_info(user)
            users_text += user_info + "\n"

        if len(users) > 20:
            users_text += f"\n... and {len(users) - 20} more users."

        await update.message.reply_text(users_text, parse_mode='Markdown')

    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /broadcast command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return

        if not context.args:
            await update.message.reply_text(
                "📢 **Broadcast Message**\n\n"
                "Usage: `/broadcast Your message here`\n\n"
                "This will send the message to all active users."
            )
            return

        message = " ".join(context.args)
        users = self.db.get_all_users()
        active_users = [u for u in users if u.get("is_active", True)]

        sent_count = 0
        failed_count = 0

        # Send broadcast message
        broadcast_text = f"📢 **Broadcast Message**\n\n{message}"

        for user in active_users:
            try:
                await context.bot.send_message(
                    chat_id=user["telegram_id"],
                    text=broadcast_text,
                    parse_mode='Markdown'
                )
                sent_count += 1
            except Exception as e:
                failed_count += 1
                # Optionally mark user as inactive if message fails
                if "chat not found" in str(e).lower() or "blocked" in str(e).lower():
                    self.db.mongodb.users.update_one(
                        {"telegram_id": user["telegram_id"]},
                        {"$set": {"is_active": False}}
                    )

        await update.message.reply_text(
            f"📢 **Broadcast Complete**\n\n"
            f"✅ Sent: {sent_count}\n"
            f"❌ Failed: {failed_count}\n"
            f"📊 Total: {len(active_users)}"
        )

    async def grant_subscription_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /grant command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return

        if len(context.args) < 2:
            await update.message.reply_text(
                "💳 **Grant Subscription**\n\n"
                "Usage: `/grant [user_id] [plan] [days]`\n\n"
                "Plans: free, premium, unlimited\n"
                "Days: Number of days (default: 30)\n\n"
                "Example: `/grant 123456789 premium 30`"
            )
            return

        try:
            user_id = int(context.args[0])
            plan = context.args[1].lower()
            days = int(context.args[2]) if len(context.args) > 2 else 30

            if plan not in config.SUBSCRIPTION_PLANS:
                await update.message.reply_text(
                    f"❌ Invalid plan. Available plans: {', '.join(config.SUBSCRIPTION_PLANS.keys())}"
                )
                return

            # Check if user exists
            user = self.db.get_user(user_id)
            if not user:
                await update.message.reply_text("❌ User not found.")
                return

            # Update subscription
            updated_user = self.db.update_user_subscription(user_id, plan, days)

            if updated_user:
                plan_info = config.SUBSCRIPTION_PLANS[plan]

                await update.message.reply_text(
                    f"✅ **Subscription Granted**\n\n"
                    f"👤 User: {user['first_name']} ({user_id})\n"
                    f"📦 Plan: {plan_info['name']}\n"
                    f"⏰ Duration: {days} days\n"
                    f"📅 Expires: {updated_user['subscription_expires'].strftime('%Y-%m-%d %H:%M')}"
                )

                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🎉 **Subscription Granted!**\n\n"
                             f"You've been granted the **{plan_info['name']}** for {days} days!\n\n"
                             f"New limits:\n"
                             f"• Max Reminders: {'Unlimited' if plan_info['max_reminders'] == -1 else plan_info['max_reminders']}\n"
                             f"• Daily Limit: {'Unlimited' if plan_info['max_daily_reminders'] == -1 else plan_info['max_daily_reminders']}\n\n"
                             f"Enjoy your upgraded experience! 🚀"
                    )
                except:
                    pass  # User might have blocked the bot
            else:
                await update.message.reply_text("❌ Failed to grant subscription.")

        except ValueError:
            await update.message.reply_text("❌ Invalid user ID or days format.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def revoke_subscription_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /revoke command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return

        if not context.args:
            await update.message.reply_text(
                "🚫 **Revoke Subscription**\n\n"
                "Usage: `/revoke [user_id]`\n\n"
                "This will downgrade the user to free plan."
            )
            return

        try:
            user_id = int(context.args[0])

            # Check if user exists
            user = self.db.get_user(user_id)
            if not user:
                await update.message.reply_text("❌ User not found.")
                return

            # Downgrade to free plan
            updated_user = self.db.update_user_subscription(user_id, "free", 0)

            if updated_user:
                await update.message.reply_text(
                    f"✅ **Subscription Revoked**\n\n"
                    f"👤 User: {user['first_name']} ({user_id})\n"
                    f"📦 New Plan: Free Plan"
                )

                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="📢 **Subscription Update**\n\n"
                             "Your subscription has been changed to the Free Plan.\n\n"
                             "Free Plan limits:\n"
                             f"• Max Reminders: {config.SUBSCRIPTION_PLANS['free']['max_reminders']}\n"
                             f"• Daily Limit: {config.SUBSCRIPTION_PLANS['free']['max_daily_reminders']}\n\n"
                             "Contact support if you believe this is an error."
                    )
                except:
                    pass
            else:
                await update.message.reply_text("❌ Failed to revoke subscription.")

        except ValueError:
            await update.message.reply_text("❌ Invalid user ID format.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def userinfo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /userinfo command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return

        if not context.args:
            await update.message.reply_text(
                "👤 **User Information**\n\n"
                "Usage: `/userinfo [user_id]`"
            )
            return

        try:
            user_id = int(context.args[0])
            user = self.db.get_user(user_id)

            if not user:
                await update.message.reply_text("❌ User not found.")
                return

            # Get user reminders
            reminders = self.db.get_user_reminders(user_id)
            subscriptions = self.db.get_user_subscriptions(user_id)

            plan_info = config.SUBSCRIPTION_PLANS.get(user["subscription_plan"], config.SUBSCRIPTION_PLANS['free'])

            user_info_text = f"""
👤 **User Information**

**Basic Info:**
• ID: {user['telegram_id']}
• Name: {user.get('first_name', 'N/A')} {user.get('last_name', '') or ''}
• Username: @{user.get('username', 'N/A')}
• Registered: {user.get('created_at', 'N/A')}
• Status: {'Active' if user.get('is_active', True) else 'Inactive'}

**Subscription:**
• Current Plan: {plan_info['name']}
• Expires: {user.get('subscription_expires', 'N/A')}
• Is Active: {'Yes' if self.db.is_subscription_active(user_id) else 'No'}

**Usage Stats:**
• Total Reminders: {len(reminders)}
• Active Reminders: {len([r for r in reminders if r.get('is_active', True)])}
• Total Subscriptions: {len(subscriptions)}
            """

            await update.message.reply_text(user_info_text, parse_mode='Markdown')

        except ValueError:
            await update.message.reply_text("❌ Invalid user ID format.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /backup command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return

        try:
            # Create a simple backup report
            stats = self.db.get_bot_stats()
            backup_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            backup_info = f"""
💾 **Database Backup Report**

📅 **Backup Time:** {backup_time}

📊 **Current Statistics:**
• Total Users: {stats['total_users']}
• Active Users: {stats['active_users']}
• Total Reminders: {stats['total_reminders']}
• Reminders Sent Today: {stats['reminders_sent_today']}

✅ **Status:** Backup information generated
⚠️ **Note:** For full database backup, use your MongoDB backup tools

🔧 **MongoDB Commands:**
```
mongodump --uri="{config.MONGODB_URL}" --db={config.DATABASE_NAME}
```
            """

            await update.message.reply_text(backup_info, parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"❌ Backup error: {str(e)}")

# Create instance for easy import
admin_handlers = AdminHandlers()
