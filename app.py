from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
from dotenv import load_dotenv
import pymysql
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import asyncio
from concurrent.futures import ThreadPoolExecutor
import groq
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Get Telegram token from environment
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    logger.error("No Telegram token found! Please set TELEGRAM_BOT_TOKEN in .env file")
    raise ValueError("Telegram token not found")

# Initialize GROQ client
groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

# Database connection
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root'),
        db=os.getenv('DB_NAME', 'rakshasetu'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# Telegram conversation states
FULLNAME, EMAIL, PHONE, LOCATION = range(4)

# First aid guides
FIRST_AID_GUIDES = {
    "burns": "1. Cool the burn under cold running water\n2. Remove jewelry/tight items\n3. Cover with sterile gauze\n4. Do not pop blisters\n5. Seek medical help if severe",
    "cuts": "1. Clean the wound with water\n2. Apply direct pressure to stop bleeding\n3. Disinfect with antiseptic\n4. Apply sterile bandage\n5. Monitor for infection",
    "fractures": "1. Do not move the injured area\n2. Apply ice pack to reduce swelling\n3. Immobilize the area\n4. Call emergency services\n5. Keep person still and comfortable",
    "choking": "1. Encourage coughing\n2. Give 5 back blows\n3. Perform Heimlich maneuver\n4. Call emergency if unsuccessful\n5. Continue until object is expelled",
    "heart_attack": "1. Call emergency services immediately\n2. Have person sit or lie down\n3. Give aspirin if available\n4. Monitor breathing\n5. Begin CPR if necessary",
    "snake_bite": "1. Keep person calm and still\n2. Remove constricting items\n3. Clean wound gently\n4. Mark swelling area and time\n5. Get immediate medical help",
    "drowning": "1. Call for help immediately\n2. Remove from water safely\n3. Check breathing\n4. Begin CPR if needed\n5. Keep person warm",
    "heatstroke": "1. Move to cool area\n2. Remove excess clothing\n3. Apply cool compresses\n4. Give fluids if conscious\n5. Seek medical attention",
    "poisoning": "1. Call poison control\n2. Do not induce vomiting\n3. Save the container/substance\n4. Note time and amount\n5. Follow medical advice",
    "seizure": "1. Clear the area\n2. Protect head\n3. Time the seizure\n4. Do not restrain\n5. Place in recovery position after"
}

# Emergency contact information
EMERGENCY_CONTACTS = {
    "police": "100",
    "ambulance": "108",
    "fire": "101",
    "disaster_management": "1070",
    "women_helpline": "1091",
    "child_helpline": "1098"
}

# Telegram command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "Welcome to Rakshasetu Disaster Management Bot! \n\n"
        "I can help you with:\n"
        "• /register - Register for disaster alerts\n"
        "• /firstaid - Get first aid instructions\n"
        "• /chat - Ask about disaster preparedness\n"
        "• /help - Show all commands\n\n"
        "Type /help to see all available commands."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_message = (
        "Here are the available commands:\n\n"
        " Registration\n"
        "/register - Register for disaster alerts\n"
        "/settings - Update your preferences\n\n"
        " First Aid\n"
        "/firstaid - Get first aid instructions\n"
        "/emergency - List emergency contacts\n\n"
        " Chat & Information\n"
        "/chat - Ask about disaster preparedness\n"
        "/info - Get disaster information\n"
        "/status - Check current alerts\n\n"
        " Help\n"
        "/help - Show this help message\n"
        "/about - About Rakshasetu"
    )
    await update.message.reply_text(help_message)

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the registration process."""
    try:
        # Check if user is already registered
        chat_id = update.message.chat_id
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE telegram_chat_id = %s", (str(chat_id),))
            if cursor.fetchone():
                await update.message.reply_text(
                    "You're already registered! \n"
                    "Use /settings to manage your preferences."
                )
                return ConversationHandler.END

        await update.message.reply_text(
            "Let's get you registered! \n\n"
            "Please enter your full name:"
        )
        return FULLNAME

    except Exception as e:
        logger.error(f"Error in register_command: {str(e)}")
        await update.message.reply_text(
            "Sorry, there was an error starting registration. Please try again later."
        )
        return ConversationHandler.END

async def handle_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle full name input."""
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text(
        "Great! Now please enter your email address:"
    )
    return EMAIL

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle email input."""
    email = update.message.text
    if '@' not in email:
        await update.message.reply_text(
            "Please enter a valid email address:"
        )
        return EMAIL
    
    context.user_data['email'] = email
    await update.message.reply_text(
        "Perfect! Now please enter your phone number:"
    )
    return PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone input."""
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "Almost done! Finally, please enter your location:"
    )
    return LOCATION

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location input and complete registration."""
    try:
        chat_id = update.message.chat_id
        username = update.message.from_user.username
        location = update.message.text
        
        # Save registration data
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO users 
                   (full_name, email, phone_number, location, telegram_chat_id, telegram_username) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    context.user_data['full_name'],
                    context.user_data['email'],
                    context.user_data['phone'],
                    location,
                    str(chat_id),
                    username
                )
            )
            connection.commit()

        await update.message.reply_text(
            " Registration successful! \n\n"
            "You're now registered for disaster alerts. Here's what you can do next:\n\n"
            "1. Use /settings to customize your alert preferences\n"
            "2. Use /info to learn about different disasters\n"
            "3. Use /firstaid to access emergency guides\n\n"
            "Stay safe! "
        )
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        await update.message.reply_text(
            "Sorry, there was an error completing your registration. Please try again later."
        )
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the registration process."""
    await update.message.reply_text(
        "Registration cancelled. You can start again anytime with /register"
    )
    return ConversationHandler.END

async def handle_first_aid_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle first aid queries using GROQ."""
    query = update.message.text.lower()
    
    try:
        # Generate first aid response using GROQ
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a first aid expert. Provide clear, step-by-step instructions for treating injuries and medical emergencies."
                },
                {
                    "role": "user",
                    "content": f"How do I treat {query}?"
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=500,
        )
        
        response = chat_completion.choices[0].message.content
        await update.message.reply_text(response)
        
        # Add emergency contact information
        contacts_message = "\n\nEmergency Contacts:\n"
        for service, number in EMERGENCY_CONTACTS.items():
            contacts_message += f"{service.replace('_', ' ').title()}: {number}\n"
        
        await update.message.reply_text(contacts_message)
        
    except Exception as e:
        logger.error(f"Error in first aid query: {str(e)}")
        await update.message.reply_text(
            "I'm sorry, I couldn't process your query. Please try again or contact emergency services:\n"
            "Ambulance: 108\nEmergency: 112"
        )

async def handle_disaster_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle disaster preparedness and response queries using GROQ."""
    query = update.message.text.lower()
    
    try:
        # Generate response using GROQ
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a disaster preparedness and response expert. Provide practical advice for disaster situations."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=500,
        )
        
        response = chat_completion.choices[0].message.content
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error in disaster chat: {str(e)}")
        await update.message.reply_text(
            "I'm sorry, I couldn't process your query. Please try again or contact our support team."
        )

async def first_aid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send first aid guide and start first aid conversation."""
    guide_message = "First Aid Guide \n\n"
    guide_message += "Here are some common emergencies I can help with:\n\n"
    
    for condition in FIRST_AID_GUIDES.keys():
        guide_message += f"• {condition.replace('_', ' ').title()}\n"
    
    guide_message += "\nJust type your emergency or condition, and I'll provide step-by-step instructions."
    
    await update.message.reply_text(guide_message)
    
    # Add emergency contacts
    contacts_message = "\nEmergency Contacts:\n"
    for service, number in EMERGENCY_CONTACTS.items():
        contacts_message += f"{service.replace('_', ' ').title()}: {number}\n"
    
    await update.message.reply_text(contacts_message)

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a disaster preparedness chat conversation."""
    await update.message.reply_text(
        "Disaster Preparedness Chat \n\n"
        "I can help you with:\n"
        "• Disaster preparation tips\n"
        "• Emergency response guidelines\n"
        "• Safety measures\n"
        "• Evacuation procedures\n"
        "• Emergency kit preparation\n\n"
        "Just ask your question, and I'll assist you!"
    )

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            full_name = request.form['name']
            email = request.form['email']
            phone_number = request.form['phone']
            location = request.form['location']
            password = request.form['password']

            # Hash the password
            hashed_password = generate_password_hash(password)

            # Insert user into database
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO users (full_name, email, phone_number, location, password) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (full_name, email, phone_number, location, hashed_password)
                )
                connection.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/bot')
def bot_page():
    return render_template('bot.html')

@app.route('/shelters')
def shelters_page():
    return render_template('shelters.html')

@app.route('/first_aid')
def first_aid_page():
    return render_template('first_aid.html')

@app.route('/infographic')
def infographic():
    return render_template('infographic.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        data = request.get_json()
        
        # Connect to MySQL database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Insert user data into database
            insert_query = """
            INSERT INTO users (
                full_name, phone_number, email, address, region,
                disaster_types, preferred_language, communication_channel,
                telegram_username, internet_access, special_needs,
                first_aid_trained, disaster_education,
                emergency_contact_name, emergency_contact_phone
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            values = (
                data['fullName'], data['phoneNumber'], data['email'],
                data['address'], data['region'], ','.join(data['disasterTypes']),
                data['preferredLanguage'], data['communicationChannel'],
                data['telegramUsername'], data['internetAccess'],
                ','.join(data['specialNeeds']), data['firstAidTrained'],
                data['disasterEducation'], data['emergencyContactName'],
                data['emergencyContactPhone']
            )
            
            cursor.execute(insert_query, values)
            connection.commit()

            # Send welcome message if Telegram username is provided
            if data['telegramUsername']:
                welcome_message = f"""
 Welcome to Rakshasetu!

Hello {data['fullName']},
Thank you for registering with our Disaster Alert System.

You will receive alerts for:
{', '.join(data['disasterTypes'])}

To get started:
1. Make sure you've started a chat with @Rakshasetubot
2. Use /help to see available commands
3. Keep your notifications enabled

Stay safe! 
                """
                send_telegram_message(data['telegramUsername'], welcome_message)

        connection.close()
        flash('Successfully submitted!', 'success')
        return redirect(url_for('home'))  # Redirect to the home page

    except Exception as e:
        logger.error(f"Error in submit_form: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/send_alert', methods=['POST'])
def send_alert():
    try:
        data = request.get_json()
        required_fields = ['type', 'message']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400

        success_count = broadcast_alert(data['type'], data['message'])
        
        return jsonify({
            'status': 'success',
            'message': f'Alert sent to {success_count} users'
        })

    except Exception as e:
        logger.error(f"Error in send_alert: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')

        # Generate response using GROQ
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are a disaster preparedness and first aid expert. 
                    Format your responses in a clear, structured way using markdown:
                    - Use **bold** for important terms
                    - Use bullet points for lists
                    - Use numbered steps for procedures
                    - Include relevant emergency numbers when appropriate
                    - Keep responses concise but informative
                    - Organize information in sections
                    - Use appropriate medical terminology while being understandable
                    """
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=500,
        )
        
        response = chat_completion.choices[0].message.content
        
        # Add emergency contacts when relevant keywords are present
        emergency_keywords = ['emergency', 'hospital', 'ambulance', 'police', 'fire', 'critical', 'immediate']
        if any(keyword in message.lower() for keyword in emergency_keywords):
            response += "\n\n**Emergency Contacts:**\n"
            response += "- Police: 100\n"
            response += "- Ambulance: 108\n"
            response += "- Fire: 101\n"
            response += "- Disaster Management: 1070"
        
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "response": "I apologize, but I encountered an error. Please try again or contact emergency services if this is urgent:\n\n"
                       "**Emergency Numbers:**\n"
                       "- Ambulance: 108\n"
                       "- Emergency: 112"
        }), 500

@app.route('/send_telegram_message', methods=['POST'])
def send_telegram_message(chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {str(e)}")
        return False

def broadcast_alert(alert_type, message):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Get all users who want this type of alert
            cursor.execute("""
                SELECT telegram_username
                FROM users
                WHERE FIND_IN_SET(%s, disaster_types)
                AND telegram_username IS NOT NULL
            """, (alert_type,))
            
            users = cursor.fetchall()
            
            # Send alert to each user
            success_count = 0
            for user in users:
                try:
                    formatted_message = f"""
 EMERGENCY ALERT 

<b>Type:</b> {alert_type}

<b>Message:</b>
{message}

Stay safe and follow official instructions.
For more information, use /help command.
                    """
                    if send_telegram_message(user['telegram_username'], formatted_message):
                        success_count += 1
                except Exception as e:
                    logger.error(f"Error sending to {user['telegram_username']}: {str(e)}")
            
            return success_count
            
    except Exception as e:
        logger.error(f"Database error in broadcast_alert: {str(e)}")
        return 0
    finally:
        if 'connection' in locals():
            connection.close()

# Initialize Telegram bot
def init_telegram_bot():
    """Initialize the Telegram bot with all handlers."""
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("firstaid", first_aid_command))
        application.add_handler(CommandHandler("chat", chat_command))

        # Add conversation handler for registration
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('register', register_command)],
            states={
                FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_fullname)],
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)],
                PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
                LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_location)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        application.add_handler(conv_handler)

        # Add message handlers for first aid and disaster chat
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_first_aid_query
        ))

        # Start the bot
        application.run_polling(poll_interval=1.0)
        logger.info("Telegram bot started successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing Telegram bot: {str(e)}")
        raise

if __name__ == '__main__':
    # Start Telegram bot in a separate thread
    telegram_thread = threading.Thread(target=init_telegram_bot)
    telegram_thread.daemon = True
    telegram_thread.start()
    
    # Start Flask app
    app.run(debug=True, use_reloader=False)
