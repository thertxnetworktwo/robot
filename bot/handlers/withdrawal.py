from telegram import Update
from telegram.ext import ContextTypes
from database.db import db


class WithdrawalHandler:
    """Handle withdrawal requests"""
    
    @staticmethod
    async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /withdraw command"""
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        if not user:
            await update.message.reply_text(
                '❌ Please use /start first.',
                reply_to_message_id=update.message.message_id
            )
            return
        
        # Check if withdrawals are enabled
        withdrawals_enabled = db.get_setting('withdrawals_enabled', 'on')
        if withdrawals_enabled != 'on':
            await update.message.reply_text(
                '❌ Withdrawals are currently disabled. Please try again later.',
                reply_to_message_id=update.message.message_id
            )
            return
        
        # Check minimum balance
        min_withdraw = float(db.get_setting('min_withdraw', '10'))
        
        if user.balance < min_withdraw:
            await update.message.reply_text(
                f'❌ Minimum withdrawal amount is ${min_withdraw:.2f}\n\nYour balance: ${user.balance:.2f}',
                reply_to_message_id=update.message.message_id
            )
            return
        
        # Show withdrawal options
        trx_enabled = db.get_setting('trx_withdrawal', 'on') == 'on'
        ledger_enabled = db.get_setting('ledger_withdrawal', 'on') == 'on'
        
        if not trx_enabled and not ledger_enabled:
            await update.message.reply_text(
                '❌ No withdrawal methods are currently available.',
                reply_to_message_id=update.message.message_id
            )
            return
        
        # Start withdrawal flow
        msg = f'''💰 Withdrawal Request

Your Balance: ${user.balance:.2f}

Available Methods:
'''
        
        if trx_enabled:
            msg += '- TRX (Cryptocurrency)\n'
        if ledger_enabled:
            msg += '- Ledger Card\n'
        
        msg += '\nPlease send the amount you want to withdraw (e.g., 50):'
        
        context.user_data['withdrawal'] = {
            'step': 'amount'
        }
        
        await update.message.reply_text(msg, reply_to_message_id=update.message.message_id)
    
    @staticmethod
    async def handle_withdrawal_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle withdrawal flow steps"""
        if 'withdrawal' not in context.user_data:
            return False
        
        withdrawal = context.user_data['withdrawal']
        step = withdrawal.get('step')
        text = update.message.text.strip()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        if step == 'amount':
            # Validate amount
            try:
                amount = float(text)
            except ValueError:
                await update.message.reply_text(
                    '❌ Invalid amount. Please send a valid number.',
                    reply_to_message_id=update.message.message_id
                )
                return True
            
            min_withdraw = float(db.get_setting('min_withdraw', '10'))
            max_withdraw = float(db.get_setting('max_withdraw', '10000'))
            
            if amount < min_withdraw:
                await update.message.reply_text(
                    f'❌ Minimum withdrawal amount is ${min_withdraw:.2f}',
                    reply_to_message_id=update.message.message_id
                )
                return True
            
            if amount > max_withdraw:
                await update.message.reply_text(
                    f'❌ Maximum withdrawal amount is ${max_withdraw:.2f}',
                    reply_to_message_id=update.message.message_id
                )
                return True
            
            if amount > user.balance:
                await update.message.reply_text(
                    f'❌ Insufficient balance. Your balance: ${user.balance:.2f}',
                    reply_to_message_id=update.message.message_id
                )
                return True
            
            withdrawal['amount'] = amount
            withdrawal['step'] = 'method'
            
            # Ask for method
            trx_enabled = db.get_setting('trx_withdrawal', 'on') == 'on'
            ledger_enabled = db.get_setting('ledger_withdrawal', 'on') == 'on'
            
            msg = 'Select withdrawal method:\n\n'
            if trx_enabled:
                msg += 'Send "TRX" for cryptocurrency withdrawal\n'
            if ledger_enabled:
                msg += 'Send "LEDGER" for ledger card withdrawal\n'
            
            await update.message.reply_text(msg, reply_to_message_id=update.message.message_id)
            return True
        
        elif step == 'method':
            method = text.upper()
            
            if method == 'TRX':
                trx_enabled = db.get_setting('trx_withdrawal', 'on') == 'on'
                if not trx_enabled:
                    await update.message.reply_text(
                        '❌ TRX withdrawals are currently disabled.',
                        reply_to_message_id=update.message.message_id
                    )
                    return True
                
                withdrawal['method'] = 'trx'
                withdrawal['step'] = 'wallet'
                await update.message.reply_text(
                    'Please send your TRX wallet address:',
                    reply_to_message_id=update.message.message_id
                )
                
            elif method == 'LEDGER':
                ledger_enabled = db.get_setting('ledger_withdrawal', 'on') == 'on'
                if not ledger_enabled:
                    await update.message.reply_text(
                        '❌ Ledger card withdrawals are currently disabled.',
                        reply_to_message_id=update.message.message_id
                    )
                    return True
                
                withdrawal['method'] = 'ledger'
                withdrawal['step'] = 'wallet'
                await update.message.reply_text(
                    'Please send your Ledger card details:',
                    reply_to_message_id=update.message.message_id
                )
            else:
                await update.message.reply_text(
                    '❌ Invalid method. Please send TRX or LEDGER.',
                    reply_to_message_id=update.message.message_id
                )
            
            return True
        
        elif step == 'wallet':
            withdrawal['wallet_address'] = text
            
            # Create withdrawal request
            with db.get_session() as session:
                from database.models import Withdrawal
                
                new_withdrawal = Withdrawal(
                    user_id=user_id,
                    amount=withdrawal['amount'],
                    method=withdrawal['method'],
                    wallet_address=withdrawal['wallet_address'],
                    status='pending'
                )
                session.add(new_withdrawal)
                session.commit()
            
            msg = f'''✅ Withdrawal request submitted!

Amount: ${withdrawal["amount"]:.2f}
Method: {withdrawal["method"].upper()}
Status: Pending

Your request will be reviewed by an admin.'''
            
            await update.message.reply_text(msg, reply_to_message_id=update.message.message_id)
            
            # Clear withdrawal data
            del context.user_data['withdrawal']
            return True
        
        return False
