
function addToCart(productId) {
    fetch(`/api/cart/add/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        alert('Product added to cart');
    })
    .catch(error => console.error('Error:', error));
}

function removeFromCart(productId) {
    fetch(`/api/cart/remove/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        location.reload();
    })
    .catch(error => console.error('Error:', error));
}

function clearCart() {
    fetch('/api/cart/clear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        location.reload();
    })
    .catch(error => console.error('Error:', error));
}

function checkout() {
    alert('Checkout functionality coming soon!');
}