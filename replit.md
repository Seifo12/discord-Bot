# Discord Bot - Comprehensive Server Management

## Overview
This is a comprehensive Discord bot written in Python that provides complete server management capabilities. The bot includes features for ticket support, leveling system, economy system, moderation commands, and automated server setup. The bot interface and commands are in Arabic.

## Current State
- **Language**: Python 3.11
- **Main Dependencies**: discord.py, flask
- **Status**: Configured and ready to run
- **Port**: 5000 (Flask status page)
- **Database**: Currently using in-memory dictionaries (data will reset on restart)

## Recent Changes
- 2024-11-12: Initial setup for Replit environment
  - Installed Python 3.11 and dependencies (discord.py, flask)
  - Updated Flask web server port from 8080 to 5000
  - Configured workflow to run the Discord bot
  - Created .gitignore for Python project
  - TOKEN secret configured via Replit Secrets

## Project Architecture

### Main Components
1. **Discord Bot** (`main.py`):
   - Discord.py bot with command prefix `!`
   - Requires all Discord intents (PRESENCE, SERVER MEMBERS, MESSAGE CONTENT)

2. **Flask Web Server**:
   - Runs on port 5000
   - Provides status page showing bot is online
   - Keeps bot alive on cloud platforms

3. **In-Memory Databases** (Currently):
   - `tickets_db`: Stores support ticket information
   - `warnings_db`: Stores user warnings
   - `levels_db`: Stores user XP, levels, and message counts
   - `economy_db`: Stores user coins and bank balances

### Key Features
- **Ticket System**: Create and close support tickets with button UI
- **Leveling System**: XP and levels based on message activity
- **Economy System**: Virtual currency with daily rewards and gambling
- **Moderation**: Warning, muting, and message clearing commands
- **Server Setup**: Automated server configuration with roles and channels
- **Welcome System**: Greets new members and assigns default role

### Available Commands
- `!اعداد_السيرفر` - Setup server with predefined roles and channels (Admin only)
- `!مستوى` - Show user level and XP
- `!ترتيب` - Show server leaderboard
- `!فلوس` - Show user balance
- `!يومي` - Claim daily reward
- `!قمار [amount]` - Gamble coins
- `!تحذير @user [reason]` - Warn a user (Moderator)
- `!كتم @user [minutes] [reason]` - Timeout a user (Moderator)
- `!مسح [amount]` - Clear messages (Moderator)
- `!مساعدة` - Show help menu

### Configuration
- **Token**: Stored in Replit Secrets as `TOKEN`
- **Command Prefix**: `!`
- **Host**: 0.0.0.0:5000

## Future Improvements
- Migrate from in-memory storage to PostgreSQL database for data persistence
- Add database migrations for proper schema management
- Implement backup/restore functionality for user data
- Add more economy features (shop, inventory, trading)
- Add music playback functionality
- Add custom reaction roles

## User Preferences
None documented yet.
