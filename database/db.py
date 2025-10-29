import sqlite3
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import bcrypt
from pathlib import Path
import config
from database.models import Base, User, Account, Country, Admin, Setting, Withdrawal, Message, Channel


class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = config.DATABASE_PATH
        
        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Create session factory
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
        # Create all tables
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(self.engine)
        self._init_default_data()
    
    def _init_default_data(self):
        """Initialize default data"""
        with self.get_session() as session:
            # Create default admin if not exists
            admin = session.query(Admin).filter_by(user_id=1).first()
            if not admin:
                password_hash = bcrypt.hashpw(
                    config.ADMIN_PASSWORD.encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                admin = Admin(
                    user_id=1,
                    username=config.ADMIN_USERNAME,
                    password_hash=password_hash,
                    permissions='full_access'
                )
                session.add(admin)
            
            # Initialize default settings
            default_settings = {
                'bot_status': 'on',
                'add_account_locked': 'unlocked',
                'two_fa_required': 'off',
                'spam_checker': 'on',
                'contact_checker': 'on',
                'freeze_checker': 'on',
                'confirmation_time': str(config.DEFAULT_CONFIRMATION_TIME),
                'proxy_system': 'off',
                'withdrawals_enabled': 'on',
                'trx_withdrawal': 'on',
                'ledger_withdrawal': 'on',
                'min_withdraw': str(config.MIN_WITHDRAW_BALANCE),
                'max_withdraw': str(config.MAX_WITHDRAW_BALANCE),
            }
            
            for key, value in default_settings.items():
                setting = session.query(Setting).filter_by(key=key).first()
                if not setting:
                    session.add(Setting(key=key, value=value))
            
            # Initialize default messages
            default_messages = {
                'welcome_message': '👋 Welcome to Session Bot!\n\nSimply send your phone number with + prefix to add an account.\n\nExample: +8801712345678',
                'help_message': '📖 Help:\n\n/start - Start bot\n/help - Show this help\n/balance - Check your balance\n/my_accounts - View your accounts\n/withdraw - Request withdrawal\n/cancel - Cancel current operation\n\nTo add an account, just send your phone number with + prefix!',
                'account_approved': '✅ Account approved! Balance added: ${amount}',
                'account_rejected': '❌ Account rejected. Reason: {reason}',
                'balance_added': '💰 Balance added: ${amount}\nNew balance: ${total}',
            }
            
            for key, content in default_messages.items():
                message = session.query(Message).filter_by(key=key).first()
                if not message:
                    session.add(Message(key=key, content=content))
            
            # Add some default countries
            default_countries = [
                {'name': 'United States', 'iso2_code': 'US', 'phone_prefix': '+1', 'price': 5.0},
                {'name': 'United Kingdom', 'iso2_code': 'GB', 'phone_prefix': '+44', 'price': 4.0},
                {'name': 'Bangladesh', 'iso2_code': 'BD', 'phone_prefix': '+880', 'price': 2.0},
                {'name': 'India', 'iso2_code': 'IN', 'phone_prefix': '+91', 'price': 2.5},
                {'name': 'Canada', 'iso2_code': 'CA', 'phone_prefix': '+1', 'price': 5.0},
            ]
            
            for country_data in default_countries:
                country = session.query(Country).filter_by(iso2_code=country_data['iso2_code']).first()
                if not country:
                    session.add(Country(**country_data))
            
            session.commit()
    
    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    # User operations
    def get_or_create_user(self, user_id, username=None):
        """Get user or create if doesn't exist"""
        with self.get_session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                user = User(user_id=user_id, username=username)
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
    
    def get_user(self, user_id):
        """Get user by ID"""
        with self.get_session() as session:
            return session.query(User).filter_by(user_id=user_id).first()
    
    def update_user_balance(self, user_id, amount, add=True):
        """Update user balance"""
        with self.get_session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                if add:
                    user.balance += amount
                else:
                    user.balance = amount
                session.commit()
                return user.balance
            return None
    
    # Account operations
    def create_account(self, user_id, phone_number, country_iso2, api_id, api_hash, two_factor_password=None):
        """Create a new account"""
        with self.get_session() as session:
            account = Account(
                user_id=user_id,
                phone_number=phone_number,
                country_iso2=country_iso2,
                api_id=api_id,
                api_hash=api_hash,
                two_factor_password=two_factor_password,
                status='pending'
            )
            session.add(account)
            session.commit()
            session.refresh(account)
            return account
    
    def get_account(self, account_id):
        """Get account by ID"""
        with self.get_session() as session:
            return session.query(Account).filter_by(id=account_id).first()
    
    def get_user_accounts(self, user_id):
        """Get all accounts for a user"""
        with self.get_session() as session:
            return session.query(Account).filter_by(user_id=user_id).all()
    
    def update_account_status(self, account_id, status):
        """Update account status"""
        with self.get_session() as session:
            account = session.query(Account).filter_by(id=account_id).first()
            if account:
                account.status = status
                session.commit()
                return True
            return False
    
    # Country operations
    def get_country_by_iso2(self, iso2_code):
        """Get country by ISO2 code"""
        with self.get_session() as session:
            return session.query(Country).filter_by(iso2_code=iso2_code).first()
    
    def get_all_countries(self, active_only=True):
        """Get all countries"""
        with self.get_session() as session:
            query = session.query(Country)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.all()
    
    # Settings operations
    def get_setting(self, key, default=None):
        """Get setting value"""
        with self.get_session() as session:
            setting = session.query(Setting).filter_by(key=key).first()
            return setting.value if setting else default
    
    def set_setting(self, key, value):
        """Set setting value"""
        with self.get_session() as session:
            setting = session.query(Setting).filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = Setting(key=key, value=value)
                session.add(setting)
            session.commit()
    
    # Message operations
    def get_message(self, key):
        """Get message by key"""
        with self.get_session() as session:
            message = session.query(Message).filter_by(key=key).first()
            return message.content if message else None


# Global database instance
db = Database()
