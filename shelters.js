document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/shelters')
        .then(response => response.json())
        .then(shelters => {
            const shelterList = document.querySelector('.shelter-list');
            shelters.forEach(shelter => {
                const shelterItem = document.createElement('div');
                shelterItem.classList.add('shelter-item');
                shelterItem.innerHTML = `<h3>${shelter.name}</h3><p>Address: ${shelter.address}</p><p>Capacity: ${shelter.capacity}</p><p>Current Occupancy: ${shelter.current_occupancy}</p><p>Contact: ${shelter.contact}</p>`;
                shelterList.appendChild(shelterItem);
            });
        })
        .catch(error => console.error('Error fetching shelters:', error));
});
