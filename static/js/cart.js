// static/js/cart.js

// This function will run once the entire HTML document is loaded and parsed.
document.addEventListener('DOMContentLoaded', function() {

    // Get all elements with the class 'update-cart'
    const updateBtns = document.getElementsByClassName('update-cart');

    // Loop through all the buttons we found
    for (let i = 0; i < updateBtns.length; i++) {
        updateBtns[i].addEventListener('click', function() {
            // When a button is clicked, get its 'data-product' and 'data-action' attributes
            const productId = this.dataset.product;
            const action = this.dataset.action;
            
            console.log('Button Clicked: Product ID -', productId, ', Action -', action);
            
            // The 'user' variable is defined in a script tag in base.html
            // This is how we check if the user is logged in or a guest.
            if (user === 'AnonymousUser') {
                // If the user is a guest, redirect them to the login page.
                // We add the 'next' parameter to send them back here after they log in.
                const currentPath = window.location.pathname + window.location.search;
                window.location.href = `/login/?next=${encodeURIComponent(currentPath)}`;
            } else {
                // If the user is logged in, call the function to update the cart on the server.
                updateUserOrder(productId, action);
            }
        });
    }
});


/**
 * This function sends a request to our Django backend to update the cart.
 * @param {string} productId - The ID of the product to update.
 * @param {string} action - The action to perform ('add', 'remove', or 'delete').
 */
function updateUserOrder(productId, action) {
    console.log('User is logged in. Sending data to the server...');

    // The URL of our Django view that handles cart updates.
    const url = '/update_item/';

    // Use the Fetch API to send a POST request.
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // The 'csrftoken' is crucial for Django's security. It's also in base.html.
            'X-CSRFToken': csrftoken,
        },
        // The data we are sending to the server, converted to a JSON string.
        body: JSON.stringify({
            'productId': productId,
            'action': action
        })
    })
    .then((response) => {
        // After the server responds, parse the JSON response.
        return response.json();
    })
    .then((data) => {
        // The request was successful. Log the data and reload the page.
        console.log('Server response:', data);
        // Reloading the page is the simplest way to show the updated cart state.
        location.reload();
    })
    .catch((error) => {
        // If there was an error with the network request, log it.
        console.error('Error:', error);
        alert('An error occurred while updating the cart.');
    });
}