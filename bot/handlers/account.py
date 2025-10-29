from telegram import Update
from telegram.ext import ContextTypes
from database.db import db
from bot.utils.phone_parser import PhoneParser
from bot.utils.country_detector import CountryDetector
from bot.services.session_creator import SessionCreator
from bot.services.spam_checker import SpamChecker
from bot.services.contact_checker import ContactChecker
from bot.services.freeze_checker import FreezeChecker
import asyncio


class AccountHandler:
    """Handle account submission and management"""
    
    def __init__(self):
        self.session_creator = SessionCreator()
    
    async def handle_phone_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle when user sends a phone number
        This is automatically detected - no command needed
        """
        text = update.message.text.strip()
        
        # Check if it's a phone number
        if not PhoneParser.is_phone_number(text):
            return False  # Not a phone number, let other handlers deal with it
        
        user_id = update.effective_user.id
        
        # Check if bot is locked
        add_locked = db.get_setting('add_account_locked', 'unlocked')
        if add_locked == 'locked':
            await update.message.reply_text('🔒 Account submission is currently locked. Please try again later.')
            return True
        
        # Parse and detect country
        country_info = CountryDetector.detect_country(text)
        
        if not country_info:
            await update.message.reply_text('❌ Invalid phone number. Please send a valid phone number with + prefix.\n\nExample: +8801712345678')
            return True
        
        # Check if country is supported
        if not country_info['is_active']:
            await update.message.reply_text(f'❌ Sorry, we currently don\'t support {country_info["name"]} ({country_info["iso2_code"]}).')
            return True
        
        # Check capacity
        if country_info['current_count'] >= country_info['capacity']:
            await update.message.reply_text(f'❌ Sorry, we\'ve reached the capacity limit for {country_info["name"]}. Please try another country.')
            return True
        
        # Start account submission process
        phone_number = country_info['phone_info']['phone_number']
        
        context.user_data['account_submission'] = {
            'step': 'api_id',
            'phone_number': phone_number,
            'country_iso2': country_info['iso2_code'],
            'country_name': country_info['name'],
            'price': country_info['price']
        }
        
        msg = f'''📱 Detected {country_info["name"]} ({country_info["iso2_code"]}) phone number
        
Phone: {phone_number}
Price: ${country_info["price"]:.2f}

Please provide your Telegram API ID:'''
        
        await update.message.reply_text(msg)
        return True
    
    async def handle_submission_step(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the account submission flow"""
        if 'account_submission' not in context.user_data:
            return False
        
        submission = context.user_data['account_submission']
        step = submission.get('step')
        text = update.message.text.strip()
        
        if step == 'api_id':
            # Validate API ID
            if not text.isdigit():
                await update.message.reply_text('❌ Invalid API ID. Please send a valid numeric API ID.')
                return True
            
            submission['api_id'] = text
            submission['step'] = 'api_hash'
            
            await update.message.reply_text('Now send your API Hash:')
            return True
        
        elif step == 'api_hash':
            submission['api_hash'] = text
            
            # Check if 2FA is required
            two_fa_required = db.get_setting('two_fa_required', 'off')
            
            if two_fa_required == 'on':
                submission['step'] = 'two_fa'
                await update.message.reply_text('Please send your 2FA password (or /skip if you don\'t have one):')
            else:
                # Skip to OTP
                await self._request_otp(update, context, submission)
            
            return True
        
        elif step == 'two_fa':
            if text == '/skip':
                submission['two_factor_password'] = None
            else:
                submission['two_factor_password'] = text
            
            await self._request_otp(update, context, submission)
            return True
        
        elif step == 'otp':
            await self._verify_otp(update, context, submission, text)
            return True
        
        elif step == 'password':
            await self._verify_password(update, context, submission, text)
            return True
        
        return False
    
    async def _request_otp(self, update: Update, context: ContextTypes.DEFAULT_TYPE, submission):
        """Request OTP from Telegram"""
        await update.message.reply_text('⏳ Sending verification code to your phone number...')
        
        # Create session and request OTP
        result = await self.session_creator.create_session(
            submission['phone_number'],
            submission['api_id'],
            submission['api_hash'],
            submission['country_iso2'],
            submission.get('two_factor_password')
        )
        
        if not result['success']:
            await update.message.reply_text(f'❌ Error: {result["message"]}\n\nPlease try again with /start')
            del context.user_data['account_submission']
            return
        
        # Store client for later use
        submission['client'] = result['client']
        submission['session_path'] = result['session_path']
        submission['step'] = 'otp'
        
        await update.message.reply_text('✅ Verification code sent!\n\nPlease enter the OTP code you received:')
    
    async def _verify_otp(self, update: Update, context: ContextTypes.DEFAULT_TYPE, submission, otp_code):
        """Verify OTP code"""
        client = submission.get('client')
        
        if not client:
            await update.message.reply_text('❌ Session expired. Please start again.')
            del context.user_data['account_submission']
            return
        
        await update.message.reply_text('⏳ Verifying OTP...')
        
        result = await self.session_creator.verify_otp(
            client,
            submission['phone_number'],
            otp_code,
            submission.get('two_factor_password')
        )
        
        if not result['success']:
            if result.get('requires_password'):
                submission['client'] = result['client']
                submission['step'] = 'password'
                await update.message.reply_text('🔐 2FA is enabled on this account.\n\nPlease enter your 2FA password:')
            else:
                await update.message.reply_text(f'❌ {result["message"]}\n\nPlease try again.')
        else:
            # OTP verified successfully
            await self._complete_submission(update, context, submission, result['session_string'])
    
    async def _verify_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE, submission, password):
        """Verify 2FA password"""
        client = submission.get('client')
        
        if not client:
            await update.message.reply_text('❌ Session expired. Please start again.')
            del context.user_data['account_submission']
            return
        
        await update.message.reply_text('⏳ Verifying password...')
        
        result = await self.session_creator.verify_password(client, password)
        
        if not result['success']:
            await update.message.reply_text(f'❌ {result["message"]}\n\nPlease try again.')
        else:
            # Password verified successfully
            await self._complete_submission(update, context, submission, result['session_string'])
    
    async def _complete_submission(self, update: Update, context: ContextTypes.DEFAULT_TYPE, submission, session_string):
        """Complete the account submission"""
        user_id = update.effective_user.id
        
        # Create account in database
        account = db.create_account(
            user_id=user_id,
            phone_number=submission['phone_number'],
            country_iso2=submission['country_iso2'],
            api_id=submission['api_id'],
            api_hash=submission['api_hash'],
            two_factor_password=submission.get('two_factor_password')
        )
        
        # Update session info
        with db.get_session() as db_session:
            from database.models import Account
            db_account = db_session.query(Account).filter_by(id=account.id).first()
            if db_account:
                db_account.session_file_path = submission['session_path']
                db_account.session_string = session_string
                db_session.commit()
        
        await update.message.reply_text(f'''✅ Session created successfully!

⏳ Your account is now pending approval. 

We will verify:
- Spam status
- Contact availability
- Account status

You will be notified once your account is approved and balance is added.''')
        
        # Clear submission data
        del context.user_data['account_submission']
        
        # Run checks in background
        asyncio.create_task(self._run_checks(account.id, submission))
    
    async def _run_checks(self, account_id, submission):
        """Run automated checks on the account"""
        try:
            # Wait for confirmation time
            confirmation_time = int(db.get_setting('confirmation_time', '5'))
            await asyncio.sleep(confirmation_time * 60)  # Convert to seconds
            
            spam_enabled = db.get_setting('spam_checker', 'on') == 'on'
            contact_enabled = db.get_setting('contact_checker', 'on') == 'on'
            freeze_enabled = db.get_setting('freeze_checker', 'on') == 'on'
            
            is_spam = False
            has_contacts = True
            is_frozen = False
            can_receive = True
            
            # Run spam check
            if spam_enabled:
                spam_result = await SpamChecker.check_spam(
                    submission['phone_number'],
                    submission['session_path'],
                    submission['api_id'],
                    submission['api_hash']
                )
                is_spam = spam_result.get('is_spam', False)
            
            # Run contact check
            if contact_enabled:
                contact_result = await ContactChecker.check_contacts(
                    submission['session_path'],
                    submission['api_id'],
                    submission['api_hash']
                )
                has_contacts = contact_result.get('has_contacts', True)
            
            # Run freeze check
            if freeze_enabled:
                freeze_result = await FreezeChecker.check_freeze(
                    submission['session_path'],
                    submission['api_id'],
                    submission['api_hash']
                )
                is_frozen = freeze_result.get('is_frozen', False)
                
                receive_result = await FreezeChecker.check_can_receive_messages(
                    submission['session_path'],
                    submission['api_id'],
                    submission['api_hash']
                )
                can_receive = receive_result.get('can_receive', True)
            
            # Update account with check results
            with db.get_session() as session:
                from database.models import Account, User
                account = session.query(Account).filter_by(id=account_id).first()
                if account:
                    account.is_spam = is_spam
                    account.has_contacts = has_contacts
                    account.can_receive_messages = can_receive
                    
                    # Determine final status
                    if is_spam:
                        account.status = 'spam'
                    elif is_frozen:
                        account.status = 'frozen'
                    elif not has_contacts or not can_receive:
                        account.status = 'rejected'
                    else:
                        account.status = 'approved'
                        # Add balance to user
                        db.update_user_balance(account.user_id, submission['price'], add=True)
                        
                        # Increment user's total accounts
                        user = session.query(User).filter_by(user_id=account.user_id).first()
                        if user:
                            user.total_accounts_added += 1
                    
                    session.commit()
            
        except Exception as e:
            # Log error but don't crash
            print(f"Error running checks: {e}")
