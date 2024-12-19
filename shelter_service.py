import requests
import json

class ShelterService:
    def __init__(self):
        self.shelters = [
            {
                "name": "Community Center Shelter",
                "address": "123 Main Street",
                "capacity": 200,
                "current_occupancy": 45,
                "contact": "+1-555-0123",
                "facilities": ["Water", "Food", "Medical Aid", "Beds"]
            },
            {
                "name": "School Emergency Shelter",
                "address": "456 Education Ave",
                "capacity": 350,
                "current_occupancy": 120,
                "contact": "+1-555-0124",
                "facilities": ["Water", "Food", "Medical Aid", "Beds", "Power Backup"]
            },
            {
                "name": "Sports Complex Shelter",
                "address": "789 Stadium Road",
                "capacity": 500,
                "current_occupancy": 200,
                "contact": "+1-555-0125",
                "facilities": ["Water", "Food", "Medical Aid", "Beds", "Power Backup", "Internet"]
            }
        ]

    def get_all_shelters(self):
        return self.shelters

    def get_shelter_by_name(self, name):
        return next((shelter for shelter in self.shelters if shelter["name"].lower() == name.lower()), None)

    def get_available_shelters(self):
        return [shelter for shelter in self.shelters if shelter["current_occupancy"] < shelter["capacity"]]
