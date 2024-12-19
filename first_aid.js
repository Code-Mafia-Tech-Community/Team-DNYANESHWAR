document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/first-aid')
        .then(response => response.json())
        .then(guide => {
            const firstAidContent = document.querySelector('.first-aid-content');
            firstAidContent.innerHTML = `<h2>${guide.title}</h2>`;
            guide.steps.forEach(step => {
                firstAidContent.innerHTML += `<p>${step}</p>`;
            });
            firstAidContent.innerHTML += '<h3>Do Not:</h3>';
            guide.dont.forEach(item => {
                firstAidContent.innerHTML += `<p>${item}</p>`;
            });
        })
        .catch(error => console.error('Error fetching first aid guide:', error));
});
