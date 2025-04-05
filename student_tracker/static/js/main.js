document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize dismissible alerts
    var alertList = document.querySelectorAll('.alert-dismissible');
    alertList.forEach(function (alert) {
        new bootstrap.Alert(alert);
    });

    console.log('Student Tracker API frontend initialized');

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Handle form submission
    const form = document.getElementById("registerForm");  // Change to match your form ID
    if (form) {
        form.addEventListener("submit", function(event) {
            event.preventDefault();  // Prevent page reload

            let formData = {
                username: document.getElementById("id_username").value,
                password: document.getElementById("id_password").value
            };

            fetch("/your-endpoint/", {  // Change `/your-endpoint/` to your actual backend URL
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                console.log("Success:", data);
                alert("Registration successful!");
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("Registration failed. Please try again.");
            });
        });
    }
});
