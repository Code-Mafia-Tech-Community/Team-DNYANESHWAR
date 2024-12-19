document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registration-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Collect disaster types
            const disasterTypes = [];
            document.querySelectorAll('input[name="disasterTypes"]:checked').forEach(checkbox => {
                disasterTypes.push(checkbox.value);
            });

            // Collect special needs
            const specialNeeds = [];
            document.querySelectorAll('input[name="specialNeeds"]:checked').forEach(checkbox => {
                specialNeeds.push(checkbox.value);
            });

            // Create form data object
            const formData = {
                fullName: document.getElementById('fullName').value,
                phoneNumber: document.getElementById('phoneNumber').value,
                email: document.getElementById('email').value,
                address: document.getElementById('address').value,
                region: document.getElementById('region').value,
                disasterTypes: disasterTypes,
                preferredLanguage: document.getElementById('preferredLanguage').value,
                communicationChannel: document.getElementById('communicationChannel').value,
                telegramUsername: document.getElementById('telegramUsername').value,
                internetAccess: document.getElementById('internetAccess').value,
                specialNeeds: specialNeeds,
                firstAidTrained: document.getElementById('firstAidTrained').value,
                disasterEducation: document.getElementById('disasterEducation').value,
                emergencyContactName: document.getElementById('emergencyContactName').value,
                emergencyContactPhone: document.getElementById('emergencyContactPhone').value
            };

            // Submit form data
            fetch('/submit_form', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Registration successful! You will receive a confirmation message on Telegram if provided.');
                    form.reset();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while submitting the form. Please try again.');
            });
        });
    }
});
