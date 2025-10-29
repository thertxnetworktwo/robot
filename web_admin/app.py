"""
Web Admin Panel - Main Application
Flask-based admin interface for Session Bot
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import func
import bcrypt
from functools import wraps
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from database.db import db
from database.models import User, Account, Country, Admin, Setting, Withdrawal, Message, Channel

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class AdminUser(UserMixin):
    """Admin user class for Flask-Login"""
    def __init__(self, admin_id, username):
        self.id = admin_id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    """Load admin user"""
    with db.get_session() as session:
        admin = session.query(Admin).filter_by(user_id=int(user_id)).first()
        if admin:
            return AdminUser(admin.user_id, admin.username)
    return None


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        with db.get_session() as session:
            admin = session.query(Admin).filter_by(username=username).first()
            
            if admin and bcrypt.checkpw(password.encode('utf-8'), admin.password_hash.encode('utf-8')):
                admin_user = AdminUser(admin.user_id, admin.username)
                login_user(admin_user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout admin"""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


# Dashboard
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    with db.get_session() as session:
        # Get statistics
        total_users = session.query(User).count()
        total_accounts = session.query(Account).count()
        approved_accounts = session.query(Account).filter_by(status='approved').count()
        pending_accounts = session.query(Account).filter_by(status='pending').count()
        
        # Total balance
        total_balance = session.query(func.sum(User.balance)).scalar() or 0
        
        # Recent accounts
        recent_accounts = session.query(Account).order_by(Account.created_at.desc()).limit(5).all()
        
        # Pending withdrawals
        pending_withdrawals = session.query(Withdrawal).filter_by(status='pending').order_by(Withdrawal.request_date.desc()).limit(5).all()
        
        # Account status distribution
        status_counts = {}
        for status in ['approved', 'pending', 'rejected', 'spam', 'frozen']:
            count = session.query(Account).filter_by(status=status).count()
            status_counts[status] = count
        
        # Country distribution
        country_counts = {}
        countries = session.query(Country).all()
        for country in countries:
            count = session.query(Account).filter_by(country_iso2=country.iso2_code).count()
            if count > 0:
                country_counts[country.name] = count
        
        stats = {
            'total_users': total_users,
            'total_accounts': total_accounts,
            'approved_accounts': approved_accounts,
            'pending_accounts': pending_accounts,
            'total_balance': total_balance
        }
        
        return render_template(
            'dashboard.html',
            stats=stats,
            recent_accounts=recent_accounts,
            pending_withdrawals=pending_withdrawals,
            status_labels=list(status_counts.keys()),
            status_data=list(status_counts.values()),
            country_labels=list(country_counts.keys()),
            country_data=list(country_counts.values())
        )


# Users Management
@app.route('/users')
@login_required
def users():
    """Users management page"""
    with db.get_session() as session:
        all_users = session.query(User).order_by(User.join_date.desc()).all()
        return render_template('users.html', users=all_users)


# Accounts Management
@app.route('/accounts')
@login_required
def accounts():
    """Accounts management page"""
    with db.get_session() as session:
        all_accounts = session.query(Account).order_by(Account.created_at.desc()).all()
        all_countries = session.query(Country).all()
        return render_template('accounts.html', accounts=all_accounts, countries=all_countries)


@app.route('/accounts/approve/<int:account_id>', methods=['POST'])
@login_required
def approve_account(account_id):
    """Approve an account"""
    with db.get_session() as session:
        account = session.query(Account).filter_by(id=account_id).first()
        if account:
            account.status = 'approved'
            
            # Add balance to user
            country = session.query(Country).filter_by(iso2_code=account.country_iso2).first()
            if country:
                user = session.query(User).filter_by(user_id=account.user_id).first()
                if user:
                    user.balance += country.price
                    user.total_accounts_added += 1
            
            session.commit()
            flash(f'Account {account.phone_number} approved!', 'success')
        else:
            flash('Account not found', 'danger')
    
    return redirect(url_for('accounts'))


@app.route('/accounts/reject/<int:account_id>', methods=['POST'])
@login_required
def reject_account(account_id):
    """Reject an account"""
    with db.get_session() as session:
        account = session.query(Account).filter_by(id=account_id).first()
        if account:
            account.status = 'rejected'
            session.commit()
            flash(f'Account {account.phone_number} rejected!', 'warning')
        else:
            flash('Account not found', 'danger')
    
    return redirect(url_for('accounts'))


# Countries Management
@app.route('/countries')
@login_required
def countries():
    """Countries management page"""
    with db.get_session() as session:
        all_countries = session.query(Country).order_by(Country.name).all()
        return render_template('countries.html', countries=all_countries)


# Withdrawals Management
@app.route('/withdrawals')
@login_required
def withdrawals():
    """Withdrawals management page"""
    with db.get_session() as session:
        all_withdrawals = session.query(Withdrawal).order_by(Withdrawal.request_date.desc()).all()
        return render_template('withdrawals.html', withdrawals=all_withdrawals)


@app.route('/withdrawals/approve/<int:withdrawal_id>', methods=['POST'])
@login_required
def approve_withdrawal(withdrawal_id):
    """Approve a withdrawal"""
    with db.get_session() as session:
        withdrawal = session.query(Withdrawal).filter_by(id=withdrawal_id).first()
        if withdrawal:
            # Deduct balance from user
            user = session.query(User).filter_by(user_id=withdrawal.user_id).first()
            if user and user.balance >= withdrawal.amount:
                user.balance -= withdrawal.amount
                withdrawal.status = 'approved'
                withdrawal.processed_date = datetime.utcnow()
                session.commit()
                flash(f'Withdrawal of ${withdrawal.amount:.2f} approved!', 'success')
            else:
                flash('Insufficient user balance', 'danger')
        else:
            flash('Withdrawal not found', 'danger')
    
    return redirect(url_for('withdrawals'))


@app.route('/withdrawals/reject/<int:withdrawal_id>', methods=['POST'])
@login_required
def reject_withdrawal(withdrawal_id):
    """Reject a withdrawal"""
    with db.get_session() as session:
        withdrawal = session.query(Withdrawal).filter_by(id=withdrawal_id).first()
        if withdrawal:
            withdrawal.status = 'rejected'
            withdrawal.processed_date = datetime.utcnow()
            session.commit()
            flash('Withdrawal rejected!', 'warning')
        else:
            flash('Withdrawal not found', 'danger')
    
    return redirect(url_for('withdrawals'))


# Settings Management
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Settings management page"""
    if request.method == 'POST':
        # Update settings
        with db.get_session() as session:
            for key, value in request.form.items():
                if key.startswith('setting_'):
                    setting_key = key.replace('setting_', '')
                    setting = session.query(Setting).filter_by(key=setting_key).first()
                    if setting:
                        setting.value = value
                    else:
                        session.add(Setting(key=setting_key, value=value))
            session.commit()
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))
    
    with db.get_session() as session:
        all_settings = session.query(Setting).all()
        settings_dict = {s.key: s.value for s in all_settings}
        return render_template('settings.html', settings=settings_dict)


# Statistics
@app.route('/statistics')
@login_required
def statistics():
    """Statistics and reports page"""
    with db.get_session() as session:
        # Get various statistics
        total_users = session.query(User).count()
        total_accounts = session.query(Account).count()
        total_balance = session.query(func.sum(User.balance)).scalar() or 0
        
        # Revenue by country
        country_revenue = []
        countries = session.query(Country).all()
        for country in countries:
            count = session.query(Account).filter_by(country_iso2=country.iso2_code, status='approved').count()
            revenue = count * country.price
            if revenue > 0:
                country_revenue.append({
                    'country': country.name,
                    'count': count,
                    'revenue': revenue
                })
        
        return render_template(
            'statistics.html',
            total_users=total_users,
            total_accounts=total_accounts,
            total_balance=total_balance,
            country_revenue=country_revenue
        )


if __name__ == '__main__':
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
