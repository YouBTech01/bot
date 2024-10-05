import sqlite3
from datetime import datetime

# Database connection and setup
def setup_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    # Create users table with new fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0,
            upi TEXT,
            referral_link TEXT,
            referrals INTEGER DEFAULT 0,
            last_bonus_time INTEGER DEFAULT 0,
            is_subscribed BOOLEAN DEFAULT 0,
            joining_time TEXT,
            online_status TEXT DEFAULT 'offline'
        )
    ''')
    
    # Add online_status column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN online_status TEXT DEFAULT "offline"')
    except sqlite3.OperationalError:
        # Column already exists, ignore the error
        pass

    conn.commit()
    conn.close()

# Add a user to the database
def add_user(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    joining_time = datetime.now().isoformat()  # Get current time in ISO format
    cursor.execute('INSERT OR IGNORE INTO users (user_id, joining_time) VALUES (?, ?)', (user_id, joining_time))
    
    conn.commit()
    conn.close()

# Get user data from the database
def get_user_data(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT balance, upi, referral_link, referrals, last_bonus_time, is_subscribed, joining_time, online_status 
        FROM users WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result if result else (0, None, None, 0, 0, False, None, 'offline')

# Update user's balance
def update_balance(user_id, amount):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    
    conn.commit()
    conn.close()

# Update the last bonus time
def update_last_bonus_time(user_id, timestamp):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET last_bonus_time = ? WHERE user_id = ?', (timestamp, user_id))
    
    conn.commit()
    conn.close()

# Update user's UPI
def update_upi(user_id, upi):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET upi = ? WHERE user_id = ?', (upi, user_id))
    
    conn.commit()
    conn.close()

# Update user's online status
def update_online_status(user_id, status):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET online_status = ? WHERE user_id = ?', (status, user_id))
    
    conn.commit()
    conn.close()

# Update user's subscription status
def update_user_subscription(user_id, status):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET is_subscribed = ? WHERE user_id = ?', (status, user_id))
    
    conn.commit()
    conn.close()

# Update user's referral link
def update_user_referral_link(user_id, referral_link):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET referral_link = ? WHERE user_id = ?', (referral_link, user_id))
    
    conn.commit()
    conn.close()

# Update user's referral count
def update_user_referral_count(user_id, referrals):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET referrals = ? WHERE user_id = ?', (referrals, user_id))
    
    conn.commit()
    conn.close()

# Get all users from the database
def get_all_users():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id, balance, upi, referrals, is_subscribed, joining_time, online_status FROM users')
    users = cursor.fetchall()
    
    conn.close()
    return users
