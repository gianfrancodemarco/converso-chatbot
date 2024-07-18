import json
import logging

from telegram import Bot, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from converso_telegram_bot.clients import (
    MAIAssistantClient, get_rabbitmq_producer)
from converso_telegram_bot.constants import MessageQueues, MessageType

from openai import OpenAI
import asyncio


class Handler:
    """
    Class that handles Telegram events.
    """

    def __init__(
        self,
        bot: Bot,
    ) -> None:
        self.bot = bot
        self.converso_client = MAIAssistantClient()
        self.rabbitmq_producer = get_rabbitmq_producer()
        self.openai_client = OpenAI()

    async def reset_conversation_handler(
        self,
        update: Update,
        _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Clears the conversation history."""
        self.converso_client.reset_conversation(
            chat_id=str(update.message.chat_id)
        )
        await update.message.reply_text("Conversation history cleared.")

    async def login_to_google_handler(
        self,
        update: Update,
        _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Login to Google."""
        login_url = self.converso_client.login_to_google(
            chat_id=str(update.message.chat_id)
        )
        login_text = f"<a href='{login_url}'>Login to Google</a>"
        await update.message.reply_html(f"Please complete the login process at the following URL:\n{login_text}")

    async def voice_handler(
        self,
        update: Update,
        _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handles voice messages."""
        logging.info(f"Voice message received: {update}")

        audio_file_id = update.message.voice.file_id
        audio_telegram_file = await self.bot.get_file(audio_file_id)

        # TODO: Use download_to_memory
        await audio_telegram_file.download_to_drive("audio.ogg")

        # Call OpenAI whisper API
        text = self.openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=open("audio.ogg", "rb"),
            language="it"
        ).text

        asyncio.gather(
            self._text_handler(text, str(update.message.chat_id)),
            update.message.reply_html(
                text=f"<i>{text}</i>",
                quote=True
            )
        )

    async def text_handler(
        self,
        update: Update,
        _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handles text messages from Telegram."""

        logging.info(f"Message received: {update}")
        text = update.message.text
        chat_id = str(update.message.chat_id)
        await self._text_handler(text, chat_id)

    async def _text_handler(
        self,
        text: str,
        chat_id: str
    ) -> None:
        """Utility function to handle text messages from different inputs."""

        await self.bot.send_chat_action(
            chat_id=chat_id,
            action=ChatAction.TYPING.value
        )

        self.rabbitmq_producer.publish(
            queue=MessageQueues.converso_IN.value,
            message=json.dumps({
                "type": MessageType.TEXT.value,
                "chat_id": chat_id,
                "content": text
            })
        )
