import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot
from telegram.error import TelegramError

from database.mongodb import DatabaseOperations
import config

logger = logging.getLogger(__name__)

class ReminderScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = DatabaseOperations()
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    async def start(self):
        """Start the reminder scheduler"""
        if self.is_running:
            return

        logger.info("🕐 Starting reminder scheduler...")

        # Schedule reminder checks every minute
        self.scheduler.add_job(
            self.check_and_send_reminders,
            trigger=IntervalTrigger(minutes=1),
            id='reminder_check',
            name='Check and send reminders',
            misfire_grace_time=30
        )

        # Schedule daily cleanup at midnight
        self.scheduler.add_job(
            self.daily_cleanup,
            trigger='cron',
            hour=0,
            minute=0,
            id='daily_cleanup',
            name='Daily cleanup and maintenance'
        )

        # Schedule stats update every hour
        self.scheduler.add_job(
            self.update_statistics,
            trigger=IntervalTrigger(hours=1),
            id='stats_update',
            name='Update bot statistics'
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("✅ Reminder scheduler started successfully")

    async def stop(self):
        """Stop the reminder scheduler"""
        if not self.is_running:
            return

        logger.info("🛑 Stopping reminder scheduler...")
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("✅ Reminder scheduler stopped")

    async def check_and_send_reminders(self):
        """Check for due reminders and send them"""
        try:
            pending_reminders = self.db.get_pending_reminders()

            if not pending_reminders:
                return

            logger.info(f"📢 Found {len(pending_reminders)} pending reminders")

            sent_count = 0
            failed_count = 0

            for reminder in pending_reminders:
                try:
                    await self.send_reminder(reminder)
                    self.db.mark_reminder_sent(reminder['_id'])
                    sent_count += 1

                    # Small delay to avoid rate limits
                    await asyncio.sleep(0.1)

                except Exception as e:
                    logger.error(f"❌ Failed to send reminder {reminder['_id']}: {e}")
                    failed_count += 1

            if sent_count > 0 or failed_count > 0:
                logger.info(f"📊 Reminder batch complete: {sent_count} sent, {failed_count} failed")

        except Exception as e:
            logger.error(f"❌ Error in check_and_send_reminders: {e}")

    async def send_reminder(self, reminder: dict):
        """Send a single reminder to user"""
        user_id = reminder.get('telegram_id')
        if not user_id:
            logger.error(f"❌ No telegram_id found for reminder {reminder['_id']}")
            return

        # Get reminder type emoji
        type_emojis = {
            'task': '✅',
            'event': '📅',
            'meeting': '👥',
            'appointment': '🏥',
            'birthday': '🎂',
            'deadline': '⚠️'
        }

        reminder_type = reminder.get('reminder_type', 'task')
        emoji = type_emojis.get(reminder_type, '📝')

        # Calculate if reminder is overdue
        reminder_time = reminder['reminder_time']
        now = datetime.utcnow()
        is_overdue = now > reminder_time

        # Create reminder message
        if is_overdue:
            time_status = f"⏰ **OVERDUE** (was due {reminder_time.strftime('%Y-%m-%d %H:%M')})"
            urgency_emoji = "🚨"
        else:
            time_status = f"⏰ **DUE NOW** ({reminder_time.strftime('%Y-%m-%d %H:%M')})"
            urgency_emoji = "🔔"

        message = f"""
{urgency_emoji} **REMINDER ALERT** {urgency_emoji}

{emoji} **{reminder['title']}**

📝 **Description:**
{reminder.get('description', 'No description provided')}

{time_status}

🏷️ **Type:** {reminder_type.title()}

━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=message.strip(),
                parse_mode='Markdown'
            )

            # Send success sticker for important reminders
            if reminder_type in ['deadline', 'appointment', 'meeting']:
                try:
                    await self.bot.send_sticker(
                        chat_id=user_id,
                        sticker="CAACAgIAAxkBAAEMxxxxxxxxxxxxxxxx"  # Alert sticker
                    )
                except:
                    pass  # Ignore sticker failures

            logger.info(f"✅ Reminder sent successfully to user {user_id}")

        except TelegramError as e:
            if "chat not found" in str(e).lower() or "blocked" in str(e).lower():
                # Mark user as inactive
                self.db.mongodb.users.update_one(
                    {"telegram_id": user_id},
                    {"$set": {"is_active": False}}
                )
                logger.warning(f"⚠️ User {user_id} blocked bot or deleted chat. Marked as inactive.")
            else:
                raise e

    async def daily_cleanup(self):
        """Perform daily maintenance tasks"""
        try:
            logger.info("🧹 Starting daily cleanup...")

            # Clean up old sent reminders (older than 30 days)
            cleanup_date = datetime.utcnow() - timedelta(days=30)

            result = self.db.mongodb.reminders.delete_many({
                "is_sent": True,
                "reminder_time": {"$lt": cleanup_date}
            })

            if result.deleted_count > 0:
                logger.info(f"🗑️ Cleaned up {result.deleted_count} old reminders")

            # Update bot statistics
            await self.update_statistics()

            logger.info("✅ Daily cleanup completed")

        except Exception as e:
            logger.error(f"❌ Error in daily cleanup: {e}")

    async def update_statistics(self):
        """Update bot statistics"""
        try:
            self.db.update_bot_stats()
            logger.debug("📊 Statistics updated")
        except Exception as e:
            logger.error(f"❌ Error updating statistics: {e}")

    async def schedule_reminder(self, reminder: dict):
        """Schedule a specific reminder (for future use)"""
        reminder_time = reminder['reminder_time']
        reminder_id = str(reminder['_id'])

        # Only schedule if reminder is in the future
        if reminder_time > datetime.utcnow():
            self.scheduler.add_job(
                self.send_single_reminder,
                trigger='date',
                run_date=reminder_time,
                args=[reminder_id],
                id=f"reminder_{reminder_id}",
                name=f"Reminder: {reminder['title'][:30]}...",
                misfire_grace_time=300  # 5 minutes grace period
            )

            logger.info(f"📅 Scheduled reminder {reminder_id} for {reminder_time}")

    async def cancel_reminder(self, reminder_id: str):
        """Cancel a scheduled reminder"""
        try:
            self.scheduler.remove_job(f"reminder_{reminder_id}")
            logger.info(f"❌ Cancelled scheduled reminder {reminder_id}")
        except:
            # Job might not exist, ignore
            pass

    async def send_single_reminder(self, reminder_id: str):
        """Send a single reminder by ID"""
        try:
            from bson.objectid import ObjectId
            reminder = self.db.mongodb.reminders.find_one({"_id": ObjectId(reminder_id)})

            if reminder and reminder.get('is_active', True) and not reminder.get('is_sent', False):
                await self.send_reminder(reminder)
                self.db.mark_reminder_sent(reminder_id)
        except Exception as e:
            logger.error(f"❌ Error sending single reminder {reminder_id}: {e}")

    def get_scheduler_status(self) -> dict:
        """Get scheduler status information"""
        if not self.is_running:
            return {"status": "stopped", "jobs": 0}

        jobs = self.scheduler.get_jobs()
        return {
            "status": "running",
            "jobs": len(jobs),
            "job_details": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }
