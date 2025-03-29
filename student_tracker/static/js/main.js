// Main JavaScript file for Student Tracker API

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Initialize dismissible alerts
    var alertList = document.querySelectorAll('.alert-dismissible')
    alertList.forEach(function (alert) {
        new bootstrap.Alert(alert)
    });
    
    console.log('Student Tracker API frontend initialized');
});