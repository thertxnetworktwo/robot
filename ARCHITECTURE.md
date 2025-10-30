# Architecture Documentation

## System Overview

The Telegram Session Management Bot is a comprehensive system consisting of two main components:

1. **Telegram Bot** - User-facing interface for account submission
2. **Web Admin Panel** - Administrative interface for management

Both components share a common SQLite database and configuration.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Users                                │
│                           │                                  │
│                           ▼                                  │
│                   Telegram Bot API                           │
│                           │                                  │
│       ┌───────────────────┴───────────────────┐             │
│       ▼                                       ▼             │
│  ┌─────────────┐                      ┌──────────────┐      │
│  │             │                      │              │      │
│  │ Telegram    │                      │    Web       │      │
│  │   Bot       │◄────────────────────►│   Admin      │      │
│  │ (Python)    │    Shared Database   │  (Flask)     │      │
│  │             │                      │              │      │
│  └─────────────┘                      └──────────────┘      │
│       │                                       │             │
│       ▼                                       ▼             │
│  ┌─────────────────────────────────────────────────┐       │
│  │          SQLite Database (bot.db)               │       │
│  │  - users                                        │       │
│  │  - accounts                                     │       │
│  │  - countries                                    │       │
│  │  - admins                                       │       │
│  │  - settings                                     │       │
│  │  - withdrawals                                  │       │
│  │  - messages                                     │       │
│  │  - channels                                     │       │
│  └─────────────────────────────────────────────────┘       │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────┐       │
│  │   Session Files (organized by country)          │       │
│  │   sessions/US/14155552671.session               │       │
│  │   sessions/BD/8801712345678.session             │       │
│  │   sessions/GB/447123456789.session              │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Telegram Bot Component

**Technology Stack:**
- python-telegram-bot: Bot framework
- Telethon: Session creation and management
- phonenumbers: Phone number parsing
- pycountry: Country code validation

**Modules:**

#### Handlers (`bot/handlers/`)
- `user.py`: User commands (/start, /help, /balance, /my_accounts, /cancel)
- `account.py`: Account submission flow and phone detection
- `withdrawal.py`: Withdrawal request handling

#### Services (`bot/services/`)
- `session_creator.py`: Creates Telethon sessions
- `session_exporter.py`: Exports sessions to different formats
- `spam_checker.py`: Checks accounts via @spaminfobot
- `contact_checker.py`: Verifies contact availability
- `freeze_checker.py`: Detects frozen/banned accounts

#### Utils (`bot/utils/`)
- `phone_parser.py`: Parses phone numbers using libphonenumber
- `country_detector.py`: Detects country from phone prefix

**Flow:**

1. User sends phone number with + prefix
2. Bot automatically detects it's a phone number (regex: `^\+[1-9]\d{1,14}$`)
3. Phone is parsed and country is detected (ISO2 code)
4. Bot validates country is supported
5. Bot uses centralized API credentials (from BOT_API_ID and BOT_API_HASH in config)
6. User provides 2FA password (if enabled in settings)
7. Bot creates Telethon session and sends OTP
8. User enters OTP code
9. Session is created and stored
10. Account enters pending status
11. Background checks run after confirmation time
12. Account is approved/rejected based on checks

### 2. Web Admin Panel Component

**Technology Stack:**
- Flask: Web framework
- Flask-Login: Authentication
- SQLAlchemy: Database ORM
- Bootstrap 5: UI framework
- Chart.js: Data visualization
- DataTables: Interactive tables

**Routes (`web_admin/app.py`):**

#### Authentication
- `GET /login`: Login page
- `POST /login`: Login handler
- `GET /logout`: Logout handler

#### Dashboard
- `GET /`: Main dashboard with statistics

#### User Management
- `GET /users`: List all users

#### Account Management
- `GET /accounts`: List all accounts
- `POST /accounts/approve/<id>`: Approve account
- `POST /accounts/reject/<id>`: Reject account

#### Country Management
- `GET /countries`: List all countries

#### Withdrawal Management
- `GET /withdrawals`: List withdrawal requests
- `POST /withdrawals/approve/<id>`: Approve withdrawal
- `POST /withdrawals/reject/<id>`: Reject withdrawal

#### Settings Management
- `GET /settings`: Settings page
- `POST /settings`: Update settings

#### Statistics
- `GET /statistics`: Statistics and reports

### 3. Database Layer

**Technology:**
- SQLAlchemy ORM
- SQLite (MySQL-ready schema)

**Models (`database/models.py`):**

#### User
- Stores user information
- Tracks balance and join date
- Counts total accounts added

#### Account
- Stores account credentials
- Links to user and country
- Tracks session file path
- Stores verification results

#### Country
- Defines supported countries (ISO2)
- Sets pricing and capacity
- Tracks current count

#### Admin
- Admin user accounts
- Password hashing with bcrypt
- Permission levels

#### Setting
- Key-value configuration storage
- Bot behavior settings
- Feature toggles

#### Withdrawal
- Withdrawal requests
- Method (TRX/Ledger)
- Status tracking

#### Message
- Customizable bot messages
- Template storage

#### Channel
- Mandatory channel tracking
- Future feature

## Data Flow

### Account Submission Flow

```
User sends phone
       │
       ▼
Phone detected & parsed
       │
       ▼
Country auto-detected (ISO2)
       │
       ▼
Country validated
       │
       ▼
Use bot's API credentials
       │
       ▼
Request 2FA (if enabled)
       │
       ▼
Create Telethon session
       │
       ▼
Send OTP to phone
       │
       ▼
Verify OTP code
       │
       ▼
Save session to DB
       │
       ▼
Wait confirmation time
       │
       ▼
Run automated checks
  ├─ Spam check
  ├─ Contact check
  ├─ Freeze check
  └─ Message check
       │
       ▼
Determine final status
       │
       ├─ Approved → Add balance
       ├─ Spam → Mark as spam
       ├─ Frozen → Mark as frozen
       └─ Rejected → Mark as rejected
```

### Withdrawal Flow

```
User requests withdrawal
       │
       ▼
Select amount
       │
       ▼
Validate balance
       │
       ▼
Select method (TRX/Ledger)
       │
       ▼
Provide wallet/card info
       │
       ▼
Create withdrawal request
       │
       ▼
Admin reviews in web panel
       │
       ├─ Approve → Deduct balance
       └─ Reject → No change
```

## Security Architecture

### Authentication
- Admin passwords hashed with bcrypt (cost factor 12)
- Flask-Login for session management
- Secure session cookies with SECRET_KEY

### Data Protection
- Session files stored in organized directories
- Session strings encrypted in database
- Input validation on all user inputs
- SQL injection prevention via SQLAlchemy ORM

### Access Control
- Telegram bot: Public access for users
- Web admin: Authenticated access only
- Role-based permissions (future)

## Configuration Management

### Environment Variables (.env)
- Bot credentials (TOKEN, API_ID, API_HASH)
- Admin credentials (USERNAME, PASSWORD)
- Flask configuration (HOST, PORT, DEBUG)
- Database path
- Session directory

### Settings Database
- Feature toggles (2FA, checkers)
- Withdrawal settings
- Confirmation time
- Balance limits

### Runtime Configuration
- Settings can be changed via web admin
- No restart required for most settings
- Some settings require bot restart (token, API credentials)

## Session Management

### Session Creation
1. Telethon client connects to Telegram
2. OTP sent to phone number
3. User verifies with OTP code
4. Session saved as SQLite file
5. Session path: `sessions/{ISO2}/{phone}.session`

### Session Storage
- Files organized by country (ISO2 code)
- Example: `sessions/BD/8801712345678.session`
- Each file contains encrypted session data
- Session string stored in database for export

### Session Export Formats
- **Telethon SQLite**: Native format (.session file)
- **Session String**: Base64 encoded string
- **Session JSON**: JSON with user info and session string

## Performance Considerations

### Database
- SQLite for simplicity (supports ~100k concurrent reads)
- MySQL-ready schema for scaling
- Indexed foreign keys
- Connection pooling via SQLAlchemy

### Bot
- Async/await for non-blocking operations
- Background tasks for checks
- Session file caching
- Rate limiting (future)

### Web Admin
- DataTables for client-side pagination
- AJAX for dynamic updates (future)
- Chart caching (future)
- CDN for static assets

## Scalability

### Current Limitations
- SQLite: ~1000 concurrent writes/sec
- Single bot instance
- File-based sessions

### Future Scaling Options
1. **Database**: Migrate to PostgreSQL/MySQL
2. **Bot**: Multiple bot instances with load balancer
3. **Sessions**: Cloud storage (S3, etc.)
4. **Cache**: Redis for settings and stats
5. **Queue**: Celery for background tasks

## Monitoring and Logging

### Current Implementation
- Python logging module
- Console output for both bot and web
- Error tracking in handlers

### Future Enhancements
- Structured logging (JSON)
- Log aggregation (ELK stack)
- Metrics (Prometheus)
- Alerting (email, Telegram)
- Performance monitoring (APM)

## Deployment Architecture

### Development
```
Local Machine
├── Bot Process (python bot/main.py)
└── Web Process (python web_admin/app.py)
```

### Production (Recommended)
```
Server
├── Bot Service (systemd/supervisor)
├── Web Service (gunicorn + nginx)
├── Database (PostgreSQL)
├── Session Storage (NFS/S3)
└── Monitoring (Prometheus + Grafana)
```

## API Integration Points

### Telegram API
- Bot API for messaging
- Telethon for session management
- @spaminfobot for spam checking

### Internal APIs (Future)
- REST API for mobile app
- WebSocket for real-time updates
- Webhook for notifications

## Error Handling

### Bot Errors
- Invalid phone format → User-friendly message
- Session creation failure → Error message with restart option
- OTP timeout → Restart flow
- Invalid OTP code → Retry option

### Web Admin Errors
- Database errors → Rollback transaction
- Authentication failures → Login redirect
- Form validation → Flash messages
- Server errors → Error page with details

## Testing Strategy

### Current Tests
- `test_setup.py`: Integration tests
- Manual testing via bot and web

### Future Testing
- Unit tests for each module
- Integration tests for flows
- E2E tests with Selenium
- Load testing with Locust
- Security testing (OWASP)

## Documentation

- `README.md`: Project overview
- `QUICKSTART.md`: Getting started guide
- `ARCHITECTURE.md`: This file
- Code comments: Docstrings in modules
- API docs: (future - Swagger/OpenAPI)
