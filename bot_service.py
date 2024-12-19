import requests
import json
from google.cloud import vision
import os

class BotService:
    def __init__(self):
        self.groq_api_key = "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"
        self.gemini_api_key = "AIzaSyCJDngtBiXYLX7c8DMyXOBkonMPC6kDCps"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.messages = [
            {
                "role": "system",
                "content": "You are a Rag Based Health awareness Bot and dont assume and hallicunating anything on your own if you dont know give output as Sorry we still under development"
            }
        ]

    def get_bot_response(self, user_message):
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        data = {
            "messages": self.messages,
            "model": "llama3-8b-8192",
            "temperature": 0
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.groq_api_key}"
        }

        try:
            response = requests.post(
                self.groq_url,
                data=json.dumps(data),
                headers=headers
            )
            response_data = response.json()
            bot_response = response_data["choices"][0]["message"]["content"]
            
            self.messages.append({
                "role": "assistant",
                "content": bot_response
            })
            
            return bot_response
        except Exception as e:
            return f"Sorry, there was an error: {str(e)}"

    def analyze_image(self, image_data):
        # Initialize Google Vision client
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_data)

        try:
            # Perform label detection
            response = client.label_detection(image=image)
            labels = response.label_annotations

            # Format the response
            results = [label.description for label in labels]
            return results
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
