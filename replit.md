# Discord Bot - Comprehensive Server Management

## Overview
This is a comprehensive Discord bot written in Python that provides complete server management capabilities. The bot includes features for advanced ticket support, leveling system, economy system, moderation commands, channel management, and automated server setup. All commands use Discord's modern Slash Commands (/) interface and the bot interface is in Arabic.

## Current State
- **Language**: Python 3.11
- **Main Dependencies**: discord.py (2.0+), flask
- **Status**: Fully operational with 15 slash commands
- **Port**: 5000 (Flask status page)
- **Database**: Currently using in-memory dictionaries (data will reset on restart)
- **Command Interface**: Slash Commands (/) - like ProBot

## Recent Changes
- 2024-11-12: Added hierarchical role system
  - ✅ Implemented role hierarchy (Owner > Co-Owner > Admin > Moderator > Helper > Booster > VIP > Member)
  - ✅ Higher roles can only assign lower roles (e.g., Admin can assign Moderator but not Co-Owner)
  - ✅ Auto-remove lower hierarchy roles when assigning higher role
  - ✅ Preserve custom/non-hierarchy roles during assignment
  - ✅ Clear feedback showing which roles were removed

- 2024-11-12: Major update - Complete rewrite with modern features
  - ✅ Converted all commands to Slash Commands using app_commands
  - ✅ Added channel lock/unlock commands
  - ✅ Added channel hide/unhide commands
  - ✅ Added role assignment command with native Discord role picker
  - ✅ Completely rebuilt ticket system with:
    - Dropdown menu to select ticket type
    - 3 ticket types: Technical Support, Server Problem, Admin Problem
    - Terms and conditions display
    - Role mentions based on ticket type
    - Modal window for renaming tickets
    - 4 management buttons: Accept, Rename, Close, Delete
    - Proper permissions for each action
    - Fixed duplicate message issues
  - ✅ Added member avatar to welcome messages
  - ✅ Improved persistent view handling
  - ✅ All existing features (levels, economy) now use slash commands
  
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

**Advanced Ticket System:**
- Dropdown menu to select ticket type (Technical Support / Server Problem / Admin Problem)
- Terms and conditions display before ticket creation
- Role mentions based on ticket type (co-owner for admin problems, admin for others)
- Accept button for staff to claim tickets
- Rename button with modal input window (admin only)
- Close button (ticket owner, assigned staff, or admins)
- Delete button (admin only)
- Persistent view handling across bot restarts
- Fixed duplicate message issues

**Channel Management:**
- Lock/unlock channels (only admin roles can speak in locked channels)
- Hide/unhide channels (hide from regular members, admins always see)
- Proper permission management

**Role Management with Hierarchical System:**
- Assign roles with native Discord role picker
- **Hierarchical role system**: Owner > Co-Owner > Admin > Moderator > Helper > Booster > VIP > Member
- **Permission validation**: Users can only assign roles lower than their highest role
  - Example: Admin can assign Moderator, Helper, Booster, VIP, Member
  - Example: Co-Owner can assign all roles except Owner
- **Auto-remove lower roles**: When assigning a higher role, all lower hierarchy roles are automatically removed
  - Example: User has "Helper" + "VIP" → receives "Moderator" → "Helper" removed, "VIP" kept (not in hierarchy)
- **Preserve custom roles**: Non-hierarchy roles (custom tags, event roles, etc.) are preserved during assignment
- **Clear feedback**: Shows which roles were removed in the response embed

**Leveling System:**
- XP and levels based on message activity
- Level-up announcements
- Leaderboard system

**Economy System:**
- Virtual currency with coins and bank
- Daily rewards (100-500 coins)
- Gambling system
- Auto-earn coins while chatting

**Moderation:**
- Warning system with auto-mute after 3 warnings
- Timeout/mute with custom duration
- Bulk message clearing
- Permission-based access control

**Server Setup:**
- Automated server configuration with predefined roles and channels
- Creates category structure
- Sets up ticket system automatically

**Welcome System:**
- Greets new members with custom embed
- Shows member avatar/profile picture
- Displays member count
- Auto-assigns default role

### Available Slash Commands (/)

**Server Management:**
- `/اعداد_السيرفر` - Setup server with predefined roles and channels (Admin only)
- `/قفل` - Lock channel (only admins can write)
- `/فتح` - Unlock channel
- `/اخفاء` - Hide channel from regular members
- `/اظهار` - Show hidden channel

**Moderation:**
- `/تحذير [member] [reason]` - Warn a user (auto-mute after 3 warnings)
- `/كتم [member] [minutes] [reason]` - Timeout a user
- `/مسح [amount]` - Clear messages
- `/اعطاء [member] [role]` - Assign role to member

**Leveling & Economy:**
- `/مستوى [member]` - Show user level and XP
- `/ترتيب` - Show server leaderboard
- `/فلوس [member]` - Show user balance
- `/يومي` - Claim daily reward
- `/قمار [amount]` - Gamble coins

**Help:**
- `/مساعدة` - Show all commands

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
