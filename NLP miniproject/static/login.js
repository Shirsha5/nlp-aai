window.onload = function() {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.onsubmit = validateLoginForm;
    } else {
        console.error("Login form not found");
    }
};

function validateLoginForm() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    if (username === '' || password === '') {
        alert('Both fields are required.');
        return false;
    }

    // Further validation for login can be added here
    window.location.href = '/elderly-care-app';  // Change this to the desired redirect URL

    return true;
}
