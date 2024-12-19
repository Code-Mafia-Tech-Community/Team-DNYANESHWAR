class FirstAidService:
    def __init__(self):
        self.first_aid_guides = {
            "burns": {
                "title": "Burns Treatment",
                "steps": [
                    "Cool the burn under cool running water for at least 10 minutes",
                    "Remove any jewelry or clothing near the burnt area",
                    "Cover the burn with a sterile gauze bandage",
                    "Take an over-the-counter pain reliever if needed",
                    "Seek medical attention for severe burns"
                ],
                "dont": [
                    "Don't apply ice directly to the burn",
                    "Don't break blisters",
                    "Don't apply butter or ointments"
                ]
            },
            "cuts": {
                "title": "Cuts and Scrapes",
                "steps": [
                    "Clean your hands thoroughly",
                    "Stop the bleeding using gentle pressure",
                    "Clean the wound with water",
                    "Apply an antibiotic ointment",
                    "Cover with a sterile bandage"
                ],
                "dont": [
                    "Don't use hydrogen peroxide",
                    "Don't remove large embedded objects",
                    "Don't ignore signs of infection"
                ]
            },
            "choking": {
                "title": "Choking Response",
                "steps": [
                    "Encourage the person to cough",
                    "Perform back blows between shoulder blades",
                    "Perform abdominal thrusts (Heimlich maneuver)",
                    "Call emergency services if the person can't breathe",
                    "Continue first aid until help arrives"
                ],
                "dont": [
                    "Don't perform abdominal thrusts on pregnant women",
                    "Don't give drinks to a choking person",
                    "Don't leave the person alone"
                ]
            }
        }

    def get_all_guides(self):
        return self.first_aid_guides

    def get_guide_by_type(self, injury_type):
        return self.first_aid_guides.get(injury_type.lower(), {
            "title": "Guide Not Found",
            "steps": ["Please select a valid injury type"],
            "dont": []
        })
