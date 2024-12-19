from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
from bot_service import BotService
from shelter_service import ShelterService
from first_aid_service import FirstAidService

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
socketio = SocketIO(app)

# Initialize services
bot_service = BotService()
shelter_service = ShelterService()
first_aid_service = FirstAidService()

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/bot', methods=['POST'])
def get_bot_response():
    data = request.json
    user_message = data.get('message', '')
    response = bot_service.get_bot_response(user_message)
    return jsonify({'response': response})

@app.route('/api/shelters')
def get_shelters():
    shelters = shelter_service.get_all_shelters()
    return jsonify(shelters)

@app.route('/api/first-aid')
def get_first_aid():
    injury_type = request.args.get('type', '')
    if injury_type:
        guide = first_aid_service.get_guide_by_type(injury_type)
    else:
        guide = first_aid_service.get_all_guides()
    return jsonify(guide)

@app.route('/api/image-analysis', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    image_data = image_file.read()
    results = bot_service.analyze_image(image_data)
    return jsonify({'results': results})

if __name__ == '__main__':
    socketio.run(app, debug=True)
