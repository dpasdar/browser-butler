"""Telegram notification service."""
import logging
from aiogram import Bot
from aiogram.enums import ParseMode

from src.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending Telegram notifications."""

    def __init__(self):
        """Initialize the notification service."""
        self._bot: Bot | None = None

    @property
    def bot(self) -> Bot | None:
        """Get or create bot instance."""
        if self._bot is None and settings.telegram_bot_token:
            self._bot = Bot(token=settings.telegram_bot_token)
        return self._bot

    @property
    def is_configured(self) -> bool:
        """Check if Telegram is configured."""
        return bool(settings.telegram_bot_token and settings.telegram_chat_id)

    async def send_message(
        self,
        message: str,
        chat_id: str | None = None,
        parse_mode: ParseMode = ParseMode.HTML,
    ) -> bool:
        """Send a Telegram message."""
        if not self.bot:
            logger.warning("Telegram bot not configured")
            return False

        target_chat = chat_id or settings.telegram_chat_id
        if not target_chat:
            logger.warning("No Telegram chat ID configured")
            return False

        try:
            await self.bot.send_message(
                chat_id=target_chat,
                text=message,
                parse_mode=parse_mode,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    async def notify_task_success(
        self,
        task_name: str,
        result_summary: str | None = None,
        duration_seconds: float | None = None,
        chat_id: str | None = None,
    ) -> bool:
        """Send a task success notification."""
        duration_str = f"{duration_seconds:.1f}s" if duration_seconds else "N/A"

        message = f"""✅ <b>Task Completed Successfully</b>

<b>Task:</b> {task_name}
<b>Duration:</b> {duration_str}"""

        if result_summary:
            message += f"\n\n<b>Result:</b>\n{result_summary[:500]}"

        return await self.send_message(message, chat_id)

    async def notify_task_failure(
        self,
        task_name: str,
        error_message: str | None = None,
        duration_seconds: float | None = None,
        chat_id: str | None = None,
    ) -> bool:
        """Send a task failure notification."""
        duration_str = f"{duration_seconds:.1f}s" if duration_seconds else "N/A"

        message = f"""❌ <b>Task Failed</b>

<b>Task:</b> {task_name}
<b>Duration:</b> {duration_str}"""

        if error_message:
            message += f"\n\n<b>Error:</b>\n<code>{error_message[:500]}</code>"

        return await self.send_message(message, chat_id)

    async def notify_task_timeout(
        self,
        task_name: str,
        timeout_seconds: int,
        chat_id: str | None = None,
    ) -> bool:
        """Send a task timeout notification."""
        message = f"""⏱️ <b>Task Timed Out</b>

<b>Task:</b> {task_name}
<b>Timeout:</b> {timeout_seconds}s

The task was terminated because it exceeded the configured timeout."""

        return await self.send_message(message, chat_id)

    async def close(self) -> None:
        """Close the bot session."""
        if self._bot:
            await self._bot.session.close()
            self._bot = None


# Global instance
notification_service = NotificationService()
