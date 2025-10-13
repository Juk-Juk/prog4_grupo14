document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.favorite-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent page reload
            
            const formData = new FormData(this);
            const button = this.querySelector('.favorite-btn');
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Update button text and style
                if (data.is_favorited) {
                    button.innerHTML = '❤️ <span class="tooltip-text">🤍 Quitar de la lista de deseos</span>';
                    button.className = 'btn btn-outline-danger favorite-btn tooltip-btn';
                } else {
                    button.innerHTML = '🤍 <span class="tooltip-text">❤️ Agregar a la lista de deseos</span>';
                    button.className = 'btn btn-outline-light favorite-btn tooltip-btn';
                }
                
                // Show a toast message
                console.log(data.message);
            })
            .catch(error => console.error('Error:', error));
        });
    });
});