import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database import setup_db, add_user, update_balance, get_user_data, update_last_bonus_time, update_upi, update_user_subscription, update_user_referral_link, update_user_referral_count

# Set up the database
setup_db()

# Constants
TELEGRAM_CHANNEL_LINK = "https://t.me/MrfreeInternet"
BOT_NAME = "Earn_UPIMoney_Bot"

WELCOME_BONUS = 5
DAILY_BONUS = 5
WITHDRAWAL_THRESHOLD = 100

# Message with Rules and Guidelines
RULES_MESSAGE = """
📜 *Bot Rules & Guidelines* 📜

1. 🔸 *Minimum Withdrawal*: ₹100.
2. 🔸 *Daily Bonus*: ₹5 (claimable once every 24 hours).
3. 🔸 *Referral Bonus*: ₹5 for every successful referral.
4. 🔸 *Prohibited Activities*:
   - No spamming or fake referrals.
   - No multiple accounts.
   - No abusive behavior.
   
🚫 *Violation of any rules will result in a ban and forfeiture of all earnings*.

Click *Agree & Continue* to access the bot.
"""

# Generate referral link
def generate_referral_link(user_id):
    return f"https://t.me/Earn_UPIMoney_Bot?start={user_id}"

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    add_user(user_id)

    balance, _, _, referrals, _, is_subscribed, _, _ = get_user_data(user_id)

    referral_link = generate_referral_link(user_id)
    update_user_referral_link(user_id, referral_link)

    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("🔔 Subscribe to Channel", url=TELEGRAM_CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Confirm Subscription", callback_data='confirm_subscription')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('👋 Welcome! Please subscribe to the Telegram channel to start using the bot:', reply_markup=reply_markup)
    else:
        await show_rules(update, context)

# Show rules and guidelines after confirming subscription
async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
    keyboard = [[InlineKeyboardButton("✔️ Agree & Continue", callback_data='agree_rules')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user_id, text=RULES_MESSAGE, reply_markup=reply_markup, parse_mode="Markdown")

# Show main menu
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
    keyboard = [
        [InlineKeyboardButton("🏠 Home", callback_data='home')],
        [InlineKeyboardButton("💰 Balance", callback_data='show_balance')],
        [InlineKeyboardButton("🎁 Claim Daily Bonus", callback_data='claim_bonus')],
        [InlineKeyboardButton("🎁 Refer & Earn", callback_data='refer_earn')],
        [InlineKeyboardButton("🔗 Link UPI", callback_data='link_upi')],
        [InlineKeyboardButton("💵 Withdraw", callback_data='withdraw')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user_id, text="🏠 *Main Menu*:", reply_markup=reply_markup, parse_mode="Markdown")

# Show balance
async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.callback_query.from_user.id
    balance, _, _, _, _, _, _, _ = get_user_data(user_id)
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user_id, text=f"💰 Your current balance is ₹{balance}", reply_markup=reply_markup)

# Handle daily bonus claim
async def claim_daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.callback_query.from_user.id
    balance, _, _, _, last_bonus_time, _, _, _ = get_user_data(user_id)
    current_time = int(time.time())
    if current_time - last_bonus_time >= 86400:  # 24 hours in seconds
        new_balance = balance + DAILY_BONUS
        update_balance(user_id, new_balance)
        update_last_bonus_time(user_id, current_time)
        await update.callback_query.edit_message_text(f"🎉 You have claimed your daily bonus! Your new balance is ₹{new_balance}.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='back')]]))
    else:
        remaining_time = 86400 - (current_time - last_bonus_time)
        hours, remainder = divmod(remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        await update.callback_query.edit_message_text(f"🚫 You can claim your daily bonus again in {hours}h {minutes}m {seconds}s.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='back')]]))

# Show refer and earn
async def show_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.callback_query.from_user.id
    _, _, referral_link, referrals, _, _, _, _ = get_user_data(user_id)
    await context.bot.send_message(chat_id=user_id, text=f"🎁 You have {referrals} referrals. Share this link to refer friends and earn ₹5:\n{referral_link}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='back')]]))

# Link UPI method
async def link_upi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.callback_query.from_user.id
    await context.bot.send_message(chat_id=user_id, text="🔗 Please send your UPI ID to link it.")

# Withdraw functionality
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.callback_query.from_user.id
    balance, _, _, _, _, _, _, _ = get_user_data(user_id)
    
    if balance >= WITHDRAWAL_THRESHOLD:
        keyboard = [
            [InlineKeyboardButton("✅ Confirm Withdrawal", callback_data='confirm_withdrawal')],
            [InlineKeyboardButton("🔙 Cancel", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=user_id, text="💵 Are you sure you want to withdraw ₹100?", reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=user_id, text=f"🚫 You need at least ₹100 to withdraw. Your current balance is ₹{balance}.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='back')]]))

# Handle withdrawal confirmation
async def handle_withdrawal_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.callback_query.from_user.id
    balance, _, _, _, _, _, _, _ = get_user_data(user_id)

    if balance >= WITHDRAWAL_THRESHOLD:
        new_balance = balance - WITHDRAWAL_THRESHOLD
        update_balance(user_id, new_balance)
        
        # Here you would implement the actual withdrawal logic, e.g., sending money to the user.
        
        await context.bot.send_message(chat_id=user_id, text="💵 Withdrawal request sent. You will receive the funds soon.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='back')]]))
    else:
        await context.bot.send_message(chat_id=user_id, text="🚫 Your balance is insufficient for this withdrawal.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='back')]]))

# Handle button clicks
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == 'confirm_subscription':
        update_user_subscription(user_id, True)
        await query.edit_message_text("✅ Subscription confirmed! Please review and agree to the rules to continue.")
        await show_rules(update, context)

    elif query.data == 'agree_rules':
        await query.edit_message_text("✔️ You have agreed to the rules. Welcome!")
        await show_main_menu(update, context)

    elif query.data == 'home':
        await show_main_menu(update, context)

    elif query.data == 'show_balance':
        await show_balance(update, context)

    elif query.data == 'claim_bonus':
        await claim_daily_bonus(update, context)

    elif query.data == 'refer_earn':
        await show_referrals(update, context)

    elif query.data == 'link_upi':
        await link_upi(update, context)

    elif query.data == 'withdraw':
        await withdraw(update, context)

    elif query.data == 'confirm_withdrawal':
        await handle_withdrawal_confirmation(update, context)

    elif query.data == 'back':
        await show_main_menu(update, context)

# Main function to run the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token("7907085474:AAFQzJ53wXhoW37zKc7WkKPJnRsed-U_7Xo").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_upi))

    app.run_polling()
