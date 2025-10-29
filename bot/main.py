#!/usr/bin/env python3
"""
Telegram Session Bot - Main Entry Point
Handles user interactions for account submission and management
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
from bot.handlers.user import UserHandler
from bot.handlers.account import AccountHandler
from bot.handlers.withdrawal import WithdrawalHandler
from database.db import db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Create handler instances
account_handler = AccountHandler()


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle all text messages
    Automatically detects phone numbers and manages submission flow
    """
    # First check if we're in a withdrawal flow
    if await WithdrawalHandler.handle_withdrawal_step(update, context):
        return
    
    # Then check if we're in an account submission flow
    if await account_handler.handle_submission_step(update, context):
        return
    
    # Finally, check if message is a phone number (to start new submission)
    if await account_handler.handle_phone_number(update, context):
        return
    
    # If nothing matched, show help
    await update.message.reply_text(
        '❓ I didn\'t understand that.\n\nSend /help for available commands or send a phone number with + prefix to add an account.'
    )


def main():
    """Start the bot"""
    # Check if token is configured
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN not configured in .env file!")
        return
    
    logger.info("Starting Telegram Session Bot...")
    
    # Create application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", UserHandler.start))
    application.add_handler(CommandHandler("help", UserHandler.help_command))
    application.add_handler(CommandHandler("balance", UserHandler.balance))
    application.add_handler(CommandHandler("my_accounts", UserHandler.my_accounts))
    application.add_handler(CommandHandler("withdraw", WithdrawalHandler.withdraw))
    application.add_handler(CommandHandler("cancel", UserHandler.cancel))
    
    # Add message handler for text messages (handles phone numbers and flows)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Start the bot
    logger.info("Bot started successfully! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
