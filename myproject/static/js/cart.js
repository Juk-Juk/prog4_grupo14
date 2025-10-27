document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Quantity update buttons
    document.querySelectorAll('.quantity-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const productId = this.dataset.productId;
            const action = this.querySelector('input[name="action"]').value;
            const cartItem = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
            
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: `action=${action}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update quantity display
                    cartItem.querySelector('.item-quantity').textContent = data.quantity;
                    
                    // Update subtotal
                    cartItem.querySelector('.item-subtotal').textContent = `$${data.subtotal}`;
                    
                    // Update cart total
                    document.getElementById('cart-total').textContent = `$${data.cart_total}`;
                    document.getElementById('cart-subtotal').textContent = `$${data.cart_total}`;
                    
                    // Update button states
                    const decreaseBtn = cartItem.querySelector('.decrease-btn');
                    const increaseBtn = cartItem.querySelector('.increase-btn');
                    
                    decreaseBtn.disabled = data.quantity <= 1;
                    increaseBtn.disabled = data.quantity >= data.stock;
                } else {
                    alert(data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});