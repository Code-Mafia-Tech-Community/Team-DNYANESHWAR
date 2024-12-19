import os
import pymysql
from dotenv import load_dotenv
import telegram
from telegram import ParseMode
import logging
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
TELEGRAM_CHANNEL = os.getenv('TELEGRAM_CHANNEL_ID')
bot = telegram.Bot(token=TELEGRAM_TOKEN)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root'),
        database=os.getenv('DB_NAME', 'rakshasetu'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def send_alert(alert_type, region, message, severity='high'):
    try:
        # Store alert in database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Insert alert into database
            cursor.execute("""
                INSERT INTO alerts (type, region, message, severity, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (alert_type, region, message, severity, datetime.now()))
            
            # Get affected users
            cursor.execute("""
                SELECT telegram_username, full_name, phone_number
                FROM users
                WHERE region = %s AND FIND_IN_SET(%s, disaster_types)
                AND communication_channel = 'Telegram'
            """, (region, alert_type))
            
            affected_users = cursor.fetchall()
            connection.commit()

        # Format alert message
        alert_message = f"""
🚨 <b>EMERGENCY ALERT</b> 🚨

<b>Type:</b> {alert_type}
<b>Region:</b> {region}
<b>Severity:</b> {severity.upper()}

<b>Message:</b>
{message}

Stay safe and follow official instructions.
For updates, visit our website or use /alerts command.

#Emergency #{alert_type} #{region.replace(' ', '')}
        """

        # Send to Telegram channel
        bot.send_message(
            chat_id=TELEGRAM_CHANNEL,
            text=alert_message,
            parse_mode=ParseMode.HTML
        )

        # Send to individual users
        for user in affected_users:
            try:
                if user['telegram_username']:
                    bot.send_message(
                        chat_id=user['telegram_username'],
                        text=f"⚠️ <b>Personal Alert for {user['full_name']}</b>\n\n{alert_message}",
                        parse_mode=ParseMode.HTML
                    )
            except Exception as e:
                logger.error(f"Failed to send alert to user {user['full_name']}: {str(e)}")

        return True, "Alert sent successfully"

    except Exception as e:
        logger.error(f"Error sending alert: {str(e)}")
        return False, str(e)
    finally:
        if 'connection' in locals():
            connection.close()

def trigger_test_alert():
    """Function to trigger a test alert"""
    return send_alert(
        alert_type="Test",
        region="Bengaluru",
        message="This is a test alert. Please ignore.",
        severity="low"
    )

if __name__ == "__main__":
    # Test the alert system
    success, message = trigger_test_alert()
    print(f"Test alert result: {success}, Message: {message}")
