# AI-Powered Disaster Management System

A comprehensive disaster management system that provides real-time alerts, disaster education, and emergency response guidance.

## Features

- Interactive disaster education modules
- Real-time emergency alerts
- AI-powered chatbot for assistance
- Emergency shelter locator with live updates
- First aid instructions and guidance
- Multi-language support

## Technical Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Flask (Python)
- Database: MySQL
- AI Services: Google Cloud API
- Maps Integration: Google Maps API

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   DATABASE_URL=mysql://username:password@localhost/disaster_db
   GOOGLE_CLOUD_API_KEY=your_api_key
   GOOGLE_MAPS_API_KEY=your_maps_api_key
   SECRET_KEY=your_secret_key
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Run the application:
   ```bash
   python app.py
   ```

## Project Structure

```
disaster_management_system/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
├── templates/
│   └── index.html
├── app.py
├── requirements.txt
└── README.md
```

## API Endpoints

- `/api/disasters` - Get disaster information
- `/api/shelters` - Get nearby emergency shelters
- `/api/chat` - Interact with AI chatbot

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
