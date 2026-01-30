"""AI Agent executor using browser-use library."""
import asyncio
import logging
from collections.abc import Callable
from datetime import datetime
from pydantic import BaseModel

from browser_use import Agent, Browser, Controller
from browser_use.llm import ChatOpenAI

from src.config import settings
from src.db.models import Task
from src.schemas.log import LogStatus
from src.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class SendTelegramMessage(BaseModel):
    """Parameters for sending a Telegram message."""
    message: str


def create_controller(chat_id: str | None = None) -> Controller:
    """Create a controller with custom actions including Telegram."""
    controller = Controller()

    @controller.action(
        "Send a Telegram notification message to the user. Use this when you need to alert "
        "the user about something important, like a price change, availability update, or "
        "any condition that was requested to be monitored. You can format the message with "
        "emojis and include any relevant data you found.",
        param_model=SendTelegramMessage,
    )
    async def send_telegram_notification(params: SendTelegramMessage) -> str:
        """Send a custom Telegram message."""
        if not notification_service.is_configured:
            return "Telegram is not configured. Message not sent."

        msg = params.message
        success = await notification_service.send_message(
            message=msg,
            chat_id=chat_id,
        )

        if success:
            logger.info(f"Telegram message sent: {msg[:50]}...")
            return "Telegram message sent successfully."
        else:
            logger.error("Failed to send Telegram message")
            return "Failed to send Telegram message."

    return controller


class AgentExecutor:
    """Service for executing browser automation tasks using AI."""

    def __init__(self):
        """Initialize the agent executor."""
        self._llm = None

    @property
    def llm(self) -> ChatOpenAI:
        """Get or create LLM instance."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model="gpt-4o",
                api_key=settings.openai_api_key,
                temperature=0.2,
            )
        return self._llm

    async def execute(
        self,
        task: Task,
        on_step: Callable | None = None,
    ) -> tuple[LogStatus, str | None, str | None, list[dict]]:
        """
        Execute a browser automation task.

        Args:
            task: The task to execute
            on_step: Optional callback for step updates

        Returns:
            Tuple of (status, result_summary, error_message, agent_steps)
        """
        steps: list[dict] = []
        status = LogStatus.FAILURE
        result_summary = None
        error_message = None

        browser = None
        try:
            # Build the task prompt
            prompt = self._build_prompt(task)

            # Configure browser to use system Chrome
            browser_kwargs = {
                "headless": task.headless,
            }

            # Add channel if configured (chrome, msedge, etc.)
            if settings.browser_channel:
                browser_kwargs["channel"] = settings.browser_channel

            browser = Browser(**browser_kwargs)

            # Create controller with custom Telegram action
            controller = create_controller(
                chat_id=task.telegram_chat_id if task.telegram_enabled else None
            )

            # Create agent with browser and custom controller
            agent = Agent(
                task=prompt,
                llm=self.llm,
                browser=browser,
                controller=controller,
            )

            # Execute with timeout
            try:
                result = await asyncio.wait_for(
                    agent.run(),
                    timeout=task.timeout_seconds,
                )

                # Process result
                if result:
                    status = LogStatus.SUCCESS
                    result_summary = self._extract_result_summary(result)
                    steps = self._extract_steps(result)
                else:
                    status = LogStatus.FAILURE
                    error_message = "Agent returned no result"

            except asyncio.TimeoutError:
                status = LogStatus.TIMEOUT
                error_message = f"Task timed out after {task.timeout_seconds} seconds"
                logger.warning(f"Task {task.id} timed out")

        except Exception as e:
            status = LogStatus.FAILURE
            error_message = str(e)
            logger.error(f"Task {task.id} failed with error: {e}")

        finally:
            # Clean up browser
            if browser:
                try:
                    await browser.stop()
                except Exception as e:
                    logger.warning(f"Failed to stop browser: {e}")

        return status, result_summary, error_message, steps

    def _build_prompt(self, task: Task) -> str:
        """Build the prompt for the AI agent."""
        prompt = task.description

        if task.start_url:
            prompt = f"Starting from {task.start_url}: {prompt}"

        # Add hint about Telegram capability if enabled
        if task.telegram_enabled and notification_service.is_configured:
            prompt += (
                "\n\nNote: You have access to send_telegram_notification action to send "
                "custom messages to the user. Use it when appropriate based on the task."
            )

        return prompt

    def _extract_result_summary(self, result) -> str:
        """Extract a summary from the agent result."""
        if hasattr(result, "final_result") and result.final_result:
            return str(result.final_result)[:1000]
        if hasattr(result, "history") and result.history:
            # Get the last meaningful result
            for item in reversed(result.history):
                if hasattr(item, "result") and item.result:
                    return str(item.result)[:1000]
        return "Task completed"

    def _extract_steps(self, result) -> list[dict]:
        """Extract steps from the agent result."""
        steps = []
        if hasattr(result, "history"):
            for i, item in enumerate(result.history):
                step = {
                    "index": i,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                if hasattr(item, "action"):
                    step["action"] = str(item.action)
                if hasattr(item, "result"):
                    step["result"] = str(item.result)[:500]
                steps.append(step)
        return steps


# Global instance
agent_executor = AgentExecutor()
