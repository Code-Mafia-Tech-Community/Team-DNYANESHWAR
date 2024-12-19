import os
from dotenv import load_dotenv
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update, ParseMode
import logging
import pymysql
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root'),
        database=os.getenv('DB_NAME', 'rakshasetu'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    message = f"""
👋 Hello {user.first_name}!

Welcome to Rakshasetu Disaster Alert System.

I can help you with:
🚨 Emergency Alerts
🔔 Alert Preferences
👤 Profile Management

Use /register to sign up for alerts
Use /help to see all commands

Stay safe! 🛡️
    """
    update.message.reply_text(message)

def help_command(update: Update, context: CallbackContext):
    help_text = """
Available commands:

/start - Start the bot
/help - Show this help message
/register - Get registration link
/profile - View your profile
/alerts - Check active alerts
/disaster_info - Get disaster preparedness information
/first_aid - Access first aid guides
/infographic - View disaster preparedness guide

Need assistance? Visit our website!
    """
    update.message.reply_text(help_text)

def register_command(update: Update, context: CallbackContext):
    message = f"""
🔔 Register for Disaster Alerts

Please visit our registration page:
http://localhost:5000/

Important:
✅ Use your Telegram username during registration
✅ Select your preferred alert types
✅ Keep your notifications enabled

Your Telegram username: @{update.effective_user.username}
    """
    update.message.reply_text(message)

def profile_command(update: Update, context: CallbackContext):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE telegram_username = %s",
                (update.effective_user.username,)
            )
            user_data = cursor.fetchone()

            if user_data:
                profile_text = f"""
👤 <b>Your Profile</b>

Name: {user_data['full_name']}
Region: {user_data['region']}

🔔 Alert Types:
{user_data['disaster_types']}

Language: {user_data['preferred_language']}

Use /update to modify your preferences
                """
                update.message.reply_text(profile_text, parse_mode=ParseMode.HTML)
            else:
                update.message.reply_text(
                    "❌ You're not registered yet!\n\nUse /register to sign up for alerts."
                )
    except Exception as e:
        logger.error(f"Database error in profile_command: {str(e)}")
        update.message.reply_text(
            "Sorry, couldn't fetch your profile. Please try again later."
        )
    finally:
        if 'connection' in locals():
            connection.close()

def alerts_command(update: Update, context: CallbackContext):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.* FROM alerts a
                JOIN users u ON FIND_IN_SET(a.type, u.disaster_types)
                WHERE u.telegram_username = %s
                AND a.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                ORDER BY a.created_at DESC
                LIMIT 5
            """, (update.effective_user.username,))
            
            alerts = cursor.fetchall()

            if alerts:
                alert_text = "<b>Recent Alerts:</b>\n\n"
                for alert in alerts:
                    alert_text += f"""
🚨 <b>{alert['type']}</b>
Region: {alert['region']}
Time: {alert['created_at'].strftime('%Y-%m-%d %H:%M')}
Message: {alert['message']}
-------------------
                    """
            else:
                alert_text = "No active alerts at this time. Stay safe! 🛡️"

            update.message.reply_text(alert_text, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Database error in alerts_command: {str(e)}")
        update.message.reply_text(
            "Sorry, couldn't fetch alerts. Please try again later."
        )
    finally:
        if 'connection' in locals():
            connection.close()

def disaster_info_command(update: Update, context: CallbackContext):
    if not context.args:
        message = """
🔍 Available Disaster Information:

1. Tsunami (/disaster_info tsunami)
2. Earthquake (/disaster_info earthquake)
3. Flood (/disaster_info flood)

Example: /disaster_info tsunami

Each guide includes:
📚 Detailed information
🎯 Warning signs
🚨 Safety procedures
🆘 Emergency contacts
🖼 Visual guide
        """
        update.message.reply_text(message)
        return

    disaster_type = context.args[0].lower()
    info, image = DisasterEducation.get_disaster_info(disaster_type)
    
    if not info:
        update.message.reply_text("Sorry, that disaster type is not supported.")
        return

    # Split long messages if needed
    messages = DisasterEducation.format_message_for_telegram(info)
    
    # Send the image first if available
    if image:
        update.message.reply_photo(
            photo=image,
            caption="Visual Guide for Disaster Safety",
            parse_mode=ParseMode.HTML
        )
    
    # Send the text information
    for msg in messages:
        update.message.reply_text(msg, parse_mode=ParseMode.HTML)

def first_aid_command(update: Update, context: CallbackContext):
    if not context.args:
        message = """
🏥 First Aid Guides Available:

1. CPR (/first_aid cpr)
2. Bleeding (/first_aid bleeding)
3. Burns (/first_aid burns)

Example: /first_aid cpr
        """
        update.message.reply_text(message)
        return

    injury_type = context.args[0].lower()
    info = "First aid info not available"  # Replace with actual implementation
    image_url = ""  # Replace with actual implementation
    
    if image_url:
        update.message.reply_photo(
            photo=image_url,
            caption=info[:1024],  # Telegram caption limit
            parse_mode=ParseMode.HTML
        )
    else:
        update.message.reply_text(info, parse_mode=ParseMode.HTML)

def infographic_command(update: Update, context: CallbackContext):
    message = """
📋 Disaster Preparedness Guide

View our comprehensive guide about:
🌊 Tsunamis
🏚️ Earthquakes
💧 Floods

The guide includes:
✅ Warning signs
✅ Safety steps
✅ Emergency contacts

View the guide here:
http://localhost:5000/infographic
    """
    update.message.reply_text(message)

def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Update {update} caused error {context.error}")
    if update:
        update.message.reply_text(
            "Sorry, something went wrong. Please try again later."
        )

def main():
    try:
        updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
        dp = updater.dispatcher

        # Add command handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("register", register_command))
        dp.add_handler(CommandHandler("profile", profile_command))
        dp.add_handler(CommandHandler("alerts", alerts_command))
        dp.add_handler(CommandHandler("disaster_info", disaster_info_command))
        dp.add_handler(CommandHandler("first_aid", first_aid_command))
        dp.add_handler(CommandHandler("infographic", infographic_command))
        
        # Add error handler
        dp.add_error_handler(error_handler)

        # Start the Bot
        updater.start_polling()
        logger.info("🤖 Telegram Bot is running!")
        
        # Run the bot until you press Ctrl-C
        updater.idle()
        
    except Exception as e:
        logger.error(f"Failed to start Telegram Bot: {str(e)}")

if __name__ == '__main__':
    main()
