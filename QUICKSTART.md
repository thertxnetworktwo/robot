# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/thertxnetworktwo/robot.git
cd robot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file and set your configuration:

```ini
# Required: Get these from https://my.telegram.org
BOT_TOKEN=your_telegram_bot_token_from_@BotFather
BOT_API_ID=your_api_id_from_my.telegram.org
BOT_API_HASH=your_api_hash_from_my.telegram.org

# Set your admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_random_secret_key_for_flask
```

### 4. Initialize Database

The database will be automatically initialized on first run. To verify:

```bash
python test_setup.py
```

You should see all tests passing.

### 5. Start the Services

#### Start Telegram Bot

```bash
python bot/main.py
```

The bot will start and listen for messages.

#### Start Web Admin Panel

In a separate terminal:

```bash
python web_admin/app.py
```

Access the admin panel at: http://localhost:5000

**Login credentials:**
- Username: admin (or as set in .env)
- Password: admin123 (or as set in .env)

## Usage

### For Users (Telegram)

1. Start conversation with your bot
2. Send `/start` command
3. Simply send your phone number with + prefix:
   - Example: `+8801712345678`
4. Bot will automatically:
   - Detect country (Bangladesh in this case)
   - Ask for API ID
   - Ask for API Hash
   - Ask for 2FA password (if enabled)
   - Send OTP code
5. Enter the OTP code you receive
6. Wait for account approval
7. Check balance with `/balance`
8. Request withdrawal with `/withdraw`

### For Admins (Web Panel)

1. Login to http://localhost:5000
2. Navigate through the menu:
   - **Dashboard**: View statistics
   - **Users**: Manage users
   - **Accounts**: Approve/reject accounts
   - **Countries**: Configure countries and pricing
   - **Withdrawals**: Process withdrawal requests
   - **Settings**: Configure bot behavior
   - **Statistics**: View reports

## How to Get Telegram API Credentials

### For Bot Token:
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow the instructions
5. Copy the bot token

### For API ID and API Hash:
1. Go to https://my.telegram.org
2. Login with your phone number
3. Go to "API development tools"
4. Create an application
5. Copy the `api_id` and `api_hash`

## Default Countries

The system comes pre-configured with 5 countries:

- United States (US): $5.00
- United Kingdom (GB): $4.00
- Bangladesh (BD): $2.00
- India (IN): $2.50
- Canada (CA): $5.00

You can add, edit, or remove countries from the web admin panel.

## Features Overview

### Automatic Phone Detection
- No commands needed
- Just send phone number with +
- Bot automatically detects country

### Multi-Country Support
- Uses ISO2 country codes (US, GB, BD, IN, CA)
- Individual pricing per country
- Capacity limits per country

### Session Management
- Creates Telethon sessions
- Stores sessions securely by country
- Supports session export (string, JSON)

### Automated Verification
- Spam checker (via @spaminfobot)
- Contact checker
- Freeze/ban checker
- Message receive checker

### Balance System
- Country-specific pricing
- User balance tracking
- Withdrawal system (TRX, Ledger)

### Admin Features
- User management
- Account approval/rejection
- Country configuration
- Withdrawal processing
- Settings management
- Statistics and reports

## File Structure

```
robot/
├── bot/                    # Telegram bot
│   ├── handlers/          # Message handlers
│   ├── services/          # Session creator, checkers
│   ├── utils/             # Phone parser, country detector
│   └── main.py            # Bot entry point
├── web_admin/             # Web admin panel
│   ├── templates/         # HTML templates
│   └── app.py             # Web app
├── database/              # Database layer
│   ├── models.py          # Data models
│   └── db.py              # Database operations
├── sessions/              # Session files (auto-created)
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
└── README.md              # Documentation
```

## Security Notes

1. **Never commit .env file** - It's already in .gitignore
2. **Use strong passwords** for admin accounts
3. **Change SECRET_KEY** to a random string in production
4. **Use HTTPS** when deploying to production
5. **Keep session files secure** - They contain account access

## Troubleshooting

### Database Issues
```bash
# Remove and reinitialize database
rm database/bot.db
python -c "from database.db import db"
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
Edit `.env` and change `FLASK_PORT` to another port (e.g., 5001)

## Production Deployment

For production, consider:

1. Use a production WSGI server (gunicorn, uWSGI)
2. Set up HTTPS with SSL certificate
3. Use a process manager (systemd, supervisor)
4. Set up proper logging
5. Enable backups for database and sessions
6. Use environment-specific .env files

## Support

For issues, please check:
1. All dependencies are installed
2. .env is configured correctly
3. Database is initialized
4. Python version is 3.8+

## License

MIT License - See LICENSE file for details
