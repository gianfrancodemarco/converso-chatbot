import logging
import os

from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .handler import Handler

# Add stream and file handlers to logger. Use basic config
# to avoid adding duplicate handlers when reloading server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)


class ConversoTelegramBot:

    TOKEN = os.getenv("TELEGRAM_API_TOKEN")

    def __init__(self) -> None:
        self.telegram_bot = Bot(token=self.TOKEN)
        self.update_handler = Handler(bot=self.telegram_bot)

        """Start the bot."""
        logging.info("Starting the telegram bot")

        self.application = Application.builder()\
            .bot(self.telegram_bot)\
            .post_init(self.post_init)\
            .build()

        # Add command handler to application
        self.application.add_handler(CommandHandler(
            "reset", self.update_handler.reset_conversation_handler))
        self.application.add_handler(CommandHandler(
            "login_to_google", self.update_handler.login_to_google_handler))

        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.update_handler.text_handler))

        self.application.add_handler(MessageHandler(
            filters.VOICE, self.update_handler.voice_handler))

    async def post_init(
        self,
        application: Application
    ) -> None:

        await application.bot.set_my_commands([
            ("reset", "Clears the conversation history."),
            ("login_to_google", "Login to Google.")
        ])

    def start(self) -> None:
        # Run the bot until the user presses Ctrl-C
        self.application.run_polling(close_loop=False)
        logging.info("Telegram bot started")
