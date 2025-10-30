from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(100))
    balance = Column(Float, default=0.0)
    join_date = Column(DateTime, default=datetime.utcnow)
    is_blocked = Column(Boolean, default=False)
    total_accounts_added = Column(Integer, default=0)
    
    # Relationships
    accounts = relationship("Account", back_populates="user")
    withdrawals = relationship("Withdrawal", back_populates="user")


class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    phone_number = Column(String(20), unique=True, nullable=False)
    country_iso2 = Column(String(2), ForeignKey('countries.iso2_code'))
    session_file_path = Column(String(255))
    session_string = Column(Text)
    session_json = Column(Text)
    status = Column(String(20), default='pending')  # pending/approved/rejected/spam/frozen
    confirmation_time = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_spam = Column(Boolean, default=False)
    can_receive_messages = Column(Boolean, default=True)
    has_contacts = Column(Boolean, default=True)
    two_factor_password = Column(String(255))
    api_id = Column(String(50))
    api_hash = Column(String(100))
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    country = relationship("Country", back_populates="accounts")


class Country(Base):
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    iso2_code = Column(String(2), unique=True, nullable=False)
    phone_prefix = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    capacity = Column(Integer, default=1000)
    current_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    accounts = relationship("Account", back_populates="country")


class Admin(Base):
    __tablename__ = 'admins'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    permissions = Column(String(255), default='full_access')
    added_date = Column(DateTime, default=datetime.utcnow)


class Setting(Base):
    __tablename__ = 'settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(Text)


class Withdrawal(Base):
    __tablename__ = 'withdrawals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    amount = Column(Float, nullable=False)
    method = Column(String(20), nullable=False)  # trx/ledger
    status = Column(String(20), default='pending')  # pending/approved/rejected
    wallet_address = Column(String(255))
    request_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="withdrawals")


class Message(Base):
    __tablename__ = 'messages'
    
    key = Column(String(100), primary_key=True)
    content = Column(Text, nullable=False)


class Channel(Base):
    __tablename__ = 'channels'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String(100))
    channel_username = Column(String(100))
    is_mandatory = Column(Boolean, default=True)


class LoginAttempt(Base):
    __tablename__ = 'login_attempts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    phone_number = Column(String(20), nullable=False)
    attempt_type = Column(String(20), nullable=False)  # otp_request/otp_verify/password_verify
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    attempt_time = Column(DateTime, default=datetime.utcnow)
    code_hash = Column(String(255))  # Hashed OTP code to detect reuse
    
    # Relationships
    user = relationship("User")
