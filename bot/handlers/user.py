from telegram import Update
from telegram.ext import ContextTypes
from database.db import db


class UserHandler:
    """Handle user-related commands"""
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Create or get user in database
        db.get_or_create_user(user.id, user.username)
        
        # Get welcome message
        welcome_msg = db.get_message('welcome_message')
        if not welcome_msg:
            welcome_msg = '👋 Welcome to Session Bot!\n\nSimply send your phone number with + prefix to add an account.\n\nExample: +8801712345678'
        
        await update.message.reply_text(welcome_msg)
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = db.get_message('help_message')
        if not help_msg:
            help_msg = '''📖 Help:

/start - Start bot
/help - Show this help
/balance - Check your balance
/my_accounts - View your accounts
/withdraw - Request withdrawal
/cancel - Cancel current operation

To add an account, just send your phone number with + prefix!'''
        
        await update.message.reply_text(help_msg)
    
    @staticmethod
    async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        if user:
            balance_text = f'💰 Your Balance: ${user.balance:.2f}'
        else:
            balance_text = '💰 Your Balance: $0.00'
        
        await update.message.reply_text(balance_text)
    
    @staticmethod
    async def my_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /my_accounts command"""
        user_id = update.effective_user.id
        accounts = db.get_user_accounts(user_id)
        
        if not accounts:
            await update.message.reply_text('📱 You have no accounts yet.\n\nSend a phone number with + prefix to add one!')
            return
        
        # Build accounts list
        text = '📱 Your Accounts:\n\n'
        for acc in accounts:
            status_emoji = {
                'pending': '⏳',
                'approved': '✅',
                'rejected': '❌',
                'spam': '🚫',
                'frozen': '🥶'
            }.get(acc.status, '❓')
            
            text += f'{status_emoji} {acc.phone_number}\n'
            text += f'   Country: {acc.country_iso2}\n'
            text += f'   Status: {acc.status.upper()}\n\n'
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command"""
        # Clear user context
        if 'account_submission' in context.user_data:
            del context.user_data['account_submission']
        
        await update.message.reply_text('❌ Operation cancelled. Returned to main menu.')
