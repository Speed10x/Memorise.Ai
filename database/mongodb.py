from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import config

class MongoDB:
    def __init__(self):
        self.client = MongoClient(config.MONGODB_URL)
        self.db = self.client[config.DATABASE_NAME]
        self.users = self.db.users
        self.reminders = self.db.reminders
        self.subscriptions = self.db.subscriptions
        self.bot_stats = self.db.bot_stats

        # Create indexes for better performance
        self.users.create_index("telegram_id", unique=True)
        self.reminders.create_index([("user_id", 1), ("reminder_time", 1)])
        self.reminders.create_index("is_sent")

    def close(self):
        self.client.close()

class DatabaseOperations:
    def __init__(self):
        self.mongodb = MongoDB()

    def close(self):
        self.mongodb.close()

    # User Operations
    def create_user(self, telegram_id: int, username: str = None, first_name: str = None, last_name: str = None):
        user_data = {
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "subscription_plan": "free",
            "subscription_expires": datetime.utcnow() + timedelta(days=30),  # 30 days free trial
            "is_active": True,
            "created_at": datetime.utcnow()
        }

        # Check if user already exists
        existing_user = self.mongodb.users.find_one({"telegram_id": telegram_id})
        if existing_user:
            return existing_user

        result = self.mongodb.users.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        return user_data

    def get_user(self, telegram_id: int):
        return self.mongodb.users.find_one({"telegram_id": telegram_id})

    def get_all_users(self):
        return list(self.mongodb.users.find({}))

    def update_user_subscription(self, telegram_id: int, plan_name: str, days: int = 30):
        update_data = {
            "subscription_plan": plan_name,
            "subscription_expires": datetime.utcnow() + timedelta(days=days)
        }

        result = self.mongodb.users.update_one(
            {"telegram_id": telegram_id},
            {"$set": update_data}
        )

        if result.modified_count > 0:
            return self.get_user(telegram_id)
        return None

    def is_subscription_active(self, telegram_id: int):
        user = self.get_user(telegram_id)
        if user and user.get("subscription_expires"):
            return datetime.utcnow() < user["subscription_expires"]
        return False

    # Reminder Operations
    def create_reminder(self, telegram_id: int, title: str, description: str, reminder_time: datetime,
                       reminder_type: str = 'task', is_recurring: bool = False, recurrence_pattern: str = None):
        user = self.get_user(telegram_id)
        if not user:
            return None

        # Check subscription limits
        if not self.can_create_reminder(telegram_id):
            return None

        reminder_data = {
            "user_id": user["_id"],
            "telegram_id": telegram_id,
            "title": title,
            "description": description,
            "reminder_time": reminder_time,
            "reminder_type": reminder_type,
            "is_recurring": is_recurring,
            "recurrence_pattern": recurrence_pattern,
            "is_sent": False,
            "is_active": True,
            "created_at": datetime.utcnow()
        }

        result = self.mongodb.reminders.insert_one(reminder_data)
        reminder_data["_id"] = result.inserted_id
        return reminder_data

    def get_user_reminders(self, telegram_id: int, active_only: bool = True):
        query = {"telegram_id": telegram_id}
        if active_only:
            query["is_active"] = True

        return list(self.mongodb.reminders.find(query).sort("reminder_time", 1))

    def get_reminder_by_id(self, reminder_id: str, telegram_id: int):
        from bson.objectid import ObjectId
        return self.mongodb.reminders.find_one({
            "_id": ObjectId(reminder_id),
            "telegram_id": telegram_id
        })

    def delete_reminder(self, reminder_id: str, telegram_id: int):
        from bson.objectid import ObjectId
        result = self.mongodb.reminders.update_one(
            {"_id": ObjectId(reminder_id), "telegram_id": telegram_id},
            {"$set": {"is_active": False}}
        )
        return result.modified_count > 0

    def get_pending_reminders(self):
        now = datetime.utcnow()
        return list(self.mongodb.reminders.find({
            "reminder_time": {"$lte": now},
            "is_sent": False,
            "is_active": True
        }))

    def mark_reminder_sent(self, reminder_id):
        from bson.objectid import ObjectId
        if isinstance(reminder_id, str):
            reminder_id = ObjectId(reminder_id)

        self.mongodb.reminders.update_one(
            {"_id": reminder_id},
            {"$set": {"is_sent": True}}
        )

    def can_create_reminder(self, telegram_id: int):
        user = self.get_user(telegram_id)
        if not user:
            return False

        plan = config.SUBSCRIPTION_PLANS.get(user["subscription_plan"], config.SUBSCRIPTION_PLANS['free'])

        # Check if subscription is active
        if not self.is_subscription_active(telegram_id):
            # Downgrade to free plan
            self.mongodb.users.update_one(
                {"telegram_id": telegram_id},
                {"$set": {"subscription_plan": "free"}}
            )
            plan = config.SUBSCRIPTION_PLANS['free']

        # Check total reminder limit
        if plan['max_reminders'] != -1:  # -1 means unlimited
            current_reminders = len(self.get_user_reminders(telegram_id))
            if current_reminders >= plan['max_reminders']:
                return False

        # Check daily reminder limit
        if plan['max_daily_reminders'] != -1:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_reminders = self.mongodb.reminders.count_documents({
                "telegram_id": telegram_id,
                "created_at": {"$gte": today},
                "is_active": True
            })

            if today_reminders >= plan['max_daily_reminders']:
                return False

        return True

    def get_user_count(self):
        return self.mongodb.users.count_documents({})

    def get_active_user_count(self):
        return self.mongodb.users.count_documents({"is_active": True})

    def get_total_reminders_count(self):
        return self.mongodb.reminders.count_documents({"is_active": True})

    def get_reminders_sent_today(self):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.mongodb.reminders.count_documents({
            "is_sent": True,
            "reminder_time": {"$gte": today}
        })

    # Subscription Operations
    def create_subscription(self, telegram_id: int, plan_name: str, payment_id: str = None):
        user = self.get_user(telegram_id)
        if not user:
            return None

        subscription_data = {
            "user_id": user["_id"],
            "telegram_id": telegram_id,
            "plan_name": plan_name,
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30),
            "is_active": True,
            "payment_id": payment_id,
            "created_at": datetime.utcnow()
        }

        result = self.mongodb.subscriptions.insert_one(subscription_data)
        subscription_data["_id"] = result.inserted_id

        # Update user subscription
        self.update_user_subscription(telegram_id, plan_name)

        return subscription_data

    def get_user_subscriptions(self, telegram_id: int):
        return list(self.mongodb.subscriptions.find({"telegram_id": telegram_id}).sort("created_at", -1))

    # Statistics
    def update_bot_stats(self):
        stats_data = {
            "total_users": self.get_user_count(),
            "active_users": self.get_active_user_count(),
            "total_reminders": self.get_total_reminders_count(),
            "reminders_sent_today": self.get_reminders_sent_today(),
            "last_updated": datetime.utcnow()
        }

        self.mongodb.bot_stats.replace_one(
            {},
            stats_data,
            upsert=True
        )

        return stats_data

    def get_bot_stats(self):
        stats = self.mongodb.bot_stats.find_one({})
        if not stats:
            return self.update_bot_stats()
        return stats
