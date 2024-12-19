// Initialize Socket.IO
const socket = io();

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-message');
const sendButton = document.getElementById('send-message');

// Google Maps initialization
let map;
let markers = [];

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: -34.397, lng: 150.644 },
        zoom: 8
    });

    // Get user's location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                map.setCenter(pos);
                loadNearbyShelters(pos);
            },
            () => {
                handleLocationError(true);
            }
        );
    }
}

// Load disaster education content
function loadDisasterEducation() {
    fetch('/api/disasters')
        .then(response => response.json())
        .then(data => {
            const disasterTypes = document.querySelector('.disaster-types');
            // TODO: Populate disaster education content
        })
        .catch(error => console.error('Error loading disaster information:', error));
}

// Load nearby shelters
function loadNearbyShelters(position) {
    fetch(`/api/shelters?lat=${position.lat}&lng=${position.lng}`)
        .then(response => response.json())
        .then(shelters => {
            // Clear existing markers
            markers.forEach(marker => marker.setMap(null));
            markers = [];

            // Add new markers
            shelters.forEach(shelter => {
                const marker = new google.maps.Marker({
                    position: { lat: shelter.lat, lng: shelter.lng },
                    map: map,
                    title: shelter.name
                });
                markers.push(marker);
            });
        })
        .catch(error => console.error('Error loading shelters:', error));
}

// Chatbot functionality
function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    appendMessage('user', message);
    userInput.value = '';

    // Send message to server
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        appendMessage('bot', data.response);
    })
    .catch(error => console.error('Error:', error));
}

function appendMessage(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Event listeners
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Real-time alerts
socket.on('emergency_alert', (data) => {
    const alertsContainer = document.getElementById('current-alerts');
    const alertElement = document.createElement('div');
    alertElement.classList.add('alert');
    alertElement.textContent = data.message;
    alertsContainer.appendChild(alertElement);
});

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    loadDisasterEducation();
    initMap();
});
