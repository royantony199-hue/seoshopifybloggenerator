# 🛡️ Data Protection System

**NEVER LOSE YOUR DATA AGAIN!**

This system automatically protects your API keys, products, and other important data during development.

## 🚀 Quick Start

### Option 1: Protected Server Startup (Recommended)
```bash
python3 start_with_protection.py
```
This automatically:
- Creates a backup of your data
- Initializes the database safely
- Starts the FastAPI server
- Protects against data loss

### Option 2: Manual Data Management
```bash
python3 manage_data.py
```
Interactive menu for:
- Creating backups
- Restoring data
- Checking data status
- Emergency restore

## 📁 Backup Locations
All backups are stored in: `./backups/`

Backup files are named: `backup_YYYYMMDD_HHMMSS.json`

## 🔧 Command Line Usage

```bash
# Create backup
python3 manage_data.py backup

# Restore from latest backup
python3 manage_data.py restore

# Check data status
python3 manage_data.py status

# Emergency restore
python3 manage_data.py emergency

# Safe database initialization
python3 safe_init.py
```

## 📊 What Gets Backed Up

✅ **API Keys**
- OpenAI API Key
- Serper API Key  
- Unsplash API Key
- Google Sheets credentials

✅ **Products**
- Product names and URLs
- Keywords and integration text
- Pricing and priority settings

✅ **Stores**
- Shopify store configurations
- Access tokens and settings

✅ **Metadata**
- Keyword counts
- Blog counts
- User settings

## 🚨 Emergency Recovery

If you lose data during development:

```bash
python3 manage_data.py emergency
```

This will automatically restore from the most recent backup.

## 📋 Data Status Check

To verify your data is intact:

```bash
python3 check_blog_generation.py
```

Or:

```bash
python3 manage_data.py status
```

## 🔄 Automatic Protection

The system automatically creates backups:
- When starting the server
- Before database operations
- When data changes are detected

## 💡 Best Practices

1. **Always use protected startup**: `python3 start_with_protection.py`
2. **Regular backups**: Run `python3 manage_data.py backup` before major changes
3. **Verify data**: Check `python3 manage_data.py status` after updates
4. **Keep backups**: Don't delete backup files manually

## 🛠️ Files in This System

- `backup_restore_system.py` - Core backup/restore functionality
- `start_with_protection.py` - Protected server startup
- `safe_init.py` - Safe database initialization
- `manage_data.py` - Interactive data management
- `protect_user_data.py` - Runtime data protection
- `backups/` - Directory containing all backup files

## ⚠️ Important Notes

- Backups contain sensitive API keys - keep them secure
- The system preserves existing data during database updates
- Always use the protection system during development
- Old backups are automatically managed (keeps latest 5)

---

**Your data is now protected! No more losing API keys or products during development.** 🎉