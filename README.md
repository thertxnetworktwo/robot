# Telegram Session Management Bot

A comprehensive Telegram bot for managing and creating Telegram account sessions with multi-country support, web-based admin interface, payment system, and automated verification.

## Features

### Telegram Bot
- **Automatic Phone Number Detection**: No commands needed - just send phone number with + prefix
- **Multi-Country Support**: Support for multiple countries with ISO2 codes (US, GB, BD, IN, CA, etc.)
- **Session Management**: Create and manage Telegram sessions using Telethon
- **Automated Verification**: Spam checker, contact checker, freeze checker
- **Balance & Payments**: User balance system with withdrawal requests
- **Simple Commands**: /start, /help, /balance, /my_accounts, /withdraw, /cancel

### Web Admin Panel
- **Dashboard**: Overview statistics with charts
- **User Management**: View and manage all users
- **Account Management**: Approve/reject accounts, view details
- **Country Management**: Configure countries with pricing and capacity
- **Withdrawal Management**: Approve/reject withdrawal requests
- **Settings Management**: Configure bot behavior, checkers, and limits
- **Statistics**: Revenue reports and analytics

## Installation

1. Clone the repository:
```bash
git clone https://github.com/thertxnetworktwo/robot.git
cd robot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database:
```bash
python -c "from database.db import db; db.init_db()"
```

## Configuration

Edit `.env` file with your settings:

```ini
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token
BOT_API_ID=your_telegram_api_id
BOT_API_HASH=your_telegram_api_hash

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key

# Database
DATABASE_PATH=database/bot.db

# Web Admin
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

## Running

### Start Telegram Bot
```bash
python bot/main.py
```

### Start Web Admin Panel
```bash
python web_admin/app.py
```

Then access the admin panel at: http://localhost:5000

Default login:
- Username: admin
- Password: (as set in .env)

## Usage

### For Users (Telegram Bot)

1. Start the bot: `/start`
2. Send your phone number with + prefix: `+8801712345678`
3. Bot automatically detects country and starts session creation
4. Provide 2FA password (if enabled and if you have one)
5. Enter OTP code received on Telegram
6. Wait for approval
7. Check balance: `/balance`
8. Request withdrawal: `/withdraw`

### For Admins (Web Panel)

1. Login to web panel
2. Navigate through menu:
   - **Dashboard**: View overview and statistics
   - **Users**: Manage users and balances
   - **Accounts**: Approve/reject pending accounts
   - **Countries**: Configure supported countries
   - **Withdrawals**: Process withdrawal requests
   - **Settings**: Configure bot behavior
   - **Statistics**: View revenue reports

## Project Structure

```
robot/
├── bot/                    # Telegram bot
│   ├── handlers/          # Command and message handlers
│   ├── services/          # Session creator, checkers
│   ├── utils/             # Phone parser, country detector
│   └── main.py            # Bot entry point
├── web_admin/             # Web admin panel
│   ├── routes/            # Flask routes (in app.py)
│   ├── templates/         # HTML templates
│   ├── static/            # CSS, JS, images
│   └── app.py             # Web app entry point
├── database/              # Database layer
│   ├── models.py          # SQLAlchemy models
│   └── db.py              # Database operations
├── sessions/              # Session files (organized by country)
│   └── {ISO2}/            # e.g., BD/, US/, GB/
├── config.py              # Configuration
├── requirements.txt       # Dependencies
└── .env                   # Environment variables
```

## Database Schema

- **users**: User accounts and balances
- **accounts**: Telegram account sessions
- **countries**: Supported countries with pricing
- **admins**: Admin users for web panel
- **settings**: Bot settings and configuration
- **withdrawals**: Withdrawal requests
- **messages**: Customizable bot messages
- **channels**: Mandatory channels (future)

## Security

- Admin passwords are hashed with bcrypt
- Session files stored securely
- Flask sessions with secure cookies
- Input validation on all user inputs
- SQL injection prevention with SQLAlchemy ORM

## Technologies

- **Python 3.8+**
- **python-telegram-bot**: Telegram bot framework
- **Telethon**: Session creation and management
- **Flask**: Web admin panel
- **SQLAlchemy**: Database ORM
- **SQLite**: Database (MySQL-ready)
- **Bootstrap 5**: UI framework
- **Chart.js**: Data visualization
- **DataTables**: Interactive tables

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
