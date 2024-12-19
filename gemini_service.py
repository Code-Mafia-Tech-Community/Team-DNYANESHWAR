import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import requests
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro-vision')
text_model = genai.GenerativeModel('gemini-pro')

class DisasterEducation:
    DISASTER_PROMPTS = {
        'tsunami': {
            'title': '🌊 Tsunami Safety Guide',
            'description': """Generate a detailed educational guide about tsunamis including:
1. What is a tsunami and how it forms
2. Warning signs and symptoms
3. Immediate actions to take
4. Evacuation procedures
5. Post-tsunami safety measures
6. Emergency kit essentials
7. Communication plans
Include specific details about wave heights, speed, and impact zones.""",
            'image_prompt': """Create a detailed infographic showing:
1. Tsunami formation process
2. Warning signs (water recession, unusual waves)
3. Evacuation routes and safe zones
4. Emergency supplies needed
5. Safety procedures during evacuation
Make it visually clear and educational."""
        },
        'earthquake': {
            'title': '🏚️ Earthquake Preparedness Guide',
            'description': """Generate a comprehensive guide about earthquakes including:
1. Understanding earthquakes and fault lines
2. Early warning signs
3. "Drop, Cover, and Hold On" technique
4. Indoor and outdoor safety procedures
5. Post-earthquake hazards
6. Building safety assessment
7. Emergency communication
Include specific details about magnitude scales and aftershocks.""",
            'image_prompt': """Create an educational infographic showing:
1. Earthquake safety positions
2. Safe spots in different buildings
3. Hazards to avoid
4. Emergency kit contents
5. Building weak points
6. Evacuation routes
Make it clear and easy to understand."""
        },
        'flood': {
            'title': '💧 Flood Safety Guide',
            'description': """Generate a detailed flood safety guide including:
1. Types of floods and their causes
2. Warning signs and flood stages
3. Property protection measures
4. Evacuation procedures
5. Water safety guidelines
6. Post-flood recovery
7. Health hazards and prevention
Include specific details about water depths and current strengths.""",
            'image_prompt': """Create a comprehensive infographic showing:
1. Flood warning signs
2. Home protection methods
3. Safe evacuation techniques
4. Water depth dangers
5. Emergency supplies
6. Recovery steps
Make it visually informative and clear."""
        }
    }

    @staticmethod
    async def get_disaster_info(disaster_type):
        try:
            if disaster_type not in DisasterEducation.DISASTER_PROMPTS:
                return None, "Disaster type not supported"

            prompt = DisasterEducation.DISASTER_PROMPTS[disaster_type]
            
            # Get text information
            text_response = await text_model.generate_content(prompt['description'])
            
            # Get image content
            image_response = await model.generate_content([
                prompt['image_prompt'],
                "Create a clear, educational infographic about disaster safety"
            ])

            # Format the response
            formatted_response = f"""
{prompt['title']}

{text_response.text}

Key Points to Remember:
• Always follow official evacuation orders
• Keep emergency contacts handy
• Have a disaster kit ready
• Stay informed through official channels
• Help others if you can do so safely

For more information, visit: https://ndma.gov.in
"""
            return formatted_response, image_response.parts[0].image if hasattr(image_response.parts[0], 'image') else None

        except Exception as e:
            logger.error(f"Error getting disaster information: {str(e)}")
            return "Error fetching disaster information", None

    @staticmethod
    def format_message_for_telegram(text, max_length=4096):
        """Format long messages for Telegram's message length limit"""
        if len(text) <= max_length:
            return [text]
        
        parts = []
        current_part = ""
        
        for line in text.split('\n'):
            if len(current_part) + len(line) + 1 <= max_length:
                current_part += line + '\n'
            else:
                parts.append(current_part)
                current_part = line + '\n'
        
        if current_part:
            parts.append(current_part)
            
        return parts
