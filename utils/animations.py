import asyncio
from typing import List
from datetime import datetime

class AnimationHelper:
    """Helper class for creating smooth animations in Telegram bot"""

    @staticmethod
    def create_progress_bar(current: int, total: int, length: int = 10, filled_char: str = "█", empty_char: str = "░") -> str:
        """Create animated progress bar"""
        if total == 0:
            return f"{empty_char * length} 0/0"

        progress = min(current / total, 1.0)
        filled_length = int(progress * length)

        bar = filled_char * filled_length + empty_char * (length - filled_length)
        percentage = int(progress * 100)

        return f"{bar} {current}/{total} ({percentage}%)"

    @staticmethod
    def create_loading_dots(step: int) -> str:
        """Create animated loading dots"""
        dots = ["   ", ".  ", ".. ", "..."]
        return f"Loading{dots[step % len(dots)]}"

    @staticmethod
    def create_spinner(step: int) -> str:
        """Create spinning animation"""
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        return spinners[step % len(spinners)]

    @staticmethod
    def create_pulse_emoji(step: int) -> str:
        """Create pulsing emoji effect"""
        small_large = ["🔴", "🟠", "🟡", "🟢", "🔵", "🟣"]
        return small_large[step % len(small_large)]

    @staticmethod
    def create_typing_indicator(text: str, step: int) -> str:
        """Create typing indicator animation"""
        if step % 4 == 0:
            return f"{text}_"
        elif step % 4 == 1:
            return f"{text}"
        elif step % 4 == 2:
            return f"{text}_"
        else:
            return f"{text}"

    @staticmethod
    def create_wave_effect(step: int) -> str:
        """Create wave animation effect"""
        waves = ["🌊", "🌀", "💫", "✨", "⭐", "🌟"]
        return waves[step % len(waves)]

    @staticmethod
    def create_countdown_animation(seconds: int) -> List[str]:
        """Create countdown animation frames"""
        frames = []
        emojis = ["3️⃣", "2️⃣", "1️⃣", "🚀"]

        for i, emoji in enumerate(emojis):
            if i < 3:
                frames.append(f"{emoji} Starting in {3-i}...")
            else:
                frames.append(f"{emoji} Let's go!")

        return frames

    @staticmethod
    def create_success_animation() -> List[str]:
        """Create success animation sequence"""
        return [
            "⏳ Processing...",
            "🔄 Almost there...",
            "✅ Success!",
            "🎉 Done!"
        ]

    @staticmethod
    def create_error_animation() -> List[str]:
        """Create error animation sequence"""
        return [
            "⏳ Processing...",
            "⚠️ Something went wrong...",
            "❌ Error occurred!",
            "🔧 Please try again"
        ]

    @staticmethod
    def create_thinking_animation() -> List[str]:
        """Create thinking/processing animation"""
        return [
            "🤔 Thinking...",
            "💭 Processing your request...",
            "🧠 Analyzing...",
            "⚡ Almost ready!"
        ]

    @staticmethod
    def create_celebration_emojis() -> List[str]:
        """Create celebration emoji sequence"""
        return ["🎉", "🥳", "🎊", "✨", "🌟", "💫", "🎈", "🎁"]

    @staticmethod
    def create_time_based_greeting() -> str:
        """Create time-based greeting with emoji"""
        hour = datetime.now().hour

        if 5 <= hour < 12:
            return "🌅 Good morning!"
        elif 12 <= hour < 17:
            return "☀️ Good afternoon!"
        elif 17 <= hour < 21:
            return "🌅 Good evening!"
        else:
            return "🌙 Good night!"

    @staticmethod
    def create_usage_meter(used: int, limit: int, width: int = 10) -> str:
        """Create usage meter visualization"""
        if limit == -1:  # Unlimited
            return "∞ Unlimited"

        if limit == 0:
            return "🚫 No limit set"

        percentage = min(used / limit, 1.0)
        filled = int(percentage * width)

        # Color coding based on usage
        if percentage < 0.5:
            fill_char = "🟢"
        elif percentage < 0.8:
            fill_char = "🟡"
        else:
            fill_char = "🔴"

        empty_char = "⚪"

        meter = fill_char * filled + empty_char * (width - filled)
        return f"{meter} {used}/{limit}"

    @staticmethod
    def create_notification_badge(count: int) -> str:
        """Create notification badge"""
        if count == 0:
            return ""
        elif count <= 9:
            return f"🔴{count}"
        else:
            return "🔴9+"

    @staticmethod
    def create_priority_indicator(priority: str) -> str:
        """Create priority indicator"""
        indicators = {
            "low": "🟢 Low",
            "medium": "🟡 Medium",
            "high": "🟠 High",
            "urgent": "🔴 Urgent"
        }
        return indicators.get(priority.lower(), "⚪ Normal")

    @staticmethod
    def create_status_indicator(status: str) -> str:
        """Create status indicator"""
        indicators = {
            "active": "🟢 Active",
            "pending": "🟡 Pending",
            "completed": "✅ Completed",
            "cancelled": "❌ Cancelled",
            "expired": "⏰ Expired"
        }
        return indicators.get(status.lower(), "⚪ Unknown")

    @staticmethod
    async def animate_message_sequence(bot, chat_id: int, messages: List[str], delay: float = 1.0):
        """Animate a sequence of messages"""
        message = None

        for i, text in enumerate(messages):
            if i == 0:
                message = await bot.send_message(chat_id=chat_id, text=text)
            else:
                await asyncio.sleep(delay)
                await message.edit_text(text)

        return message

    @staticmethod
    def create_divider(style: str = "line") -> str:
        """Create visual dividers"""
        dividers = {
            "line": "━━━━━━━━━━━━━━━━━━━━",
            "dots": "• • • • • • • • • • • • • • • • • • • •",
            "stars": "⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐",
            "waves": "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
            "sparkles": "✨ ✨ ✨ ✨ ✨ ✨ ✨ ✨ ✨ ✨"
        }
        return dividers.get(style, "━━━━━━━━━━━━━━━━━━━━")

    @staticmethod
    def create_feature_highlight(feature: str, is_available: bool) -> str:
        """Create feature availability highlight"""
        icon = "✅" if is_available else "❌"
        status = "Available" if is_available else "Premium Only"
        return f"{icon} {feature} - {status}"

    @staticmethod
    def create_step_indicator(current_step: int, total_steps: int) -> str:
        """Create step indicator for multi-step processes"""
        steps = []
        for i in range(1, total_steps + 1):
            if i < current_step:
                steps.append("✅")
            elif i == current_step:
                steps.append("🔄")
            else:
                steps.append("⭕")

        return " ".join(steps) + f" Step {current_step}/{total_steps}"

    @staticmethod
    def create_calendar_emoji(day: int) -> str:
        """Create calendar emoji for day"""
        calendar_emojis = {
            1: "📅", 2: "📅", 3: "📅", 4: "📅", 5: "📅",
            6: "📅", 7: "📅", 8: "📅", 9: "📅", 10: "📅",
            # Add more as needed
        }
        return calendar_emojis.get(day, "📅")

    @staticmethod
    def create_weather_emoji(condition: str) -> str:
        """Create weather emoji (for future weather-based reminders)"""
        weather_emojis = {
            "sunny": "☀️",
            "cloudy": "☁️",
            "rainy": "🌧️",
            "snowy": "❄️",
            "stormy": "⛈️"
        }
        return weather_emojis.get(condition.lower(), "🌤️")
