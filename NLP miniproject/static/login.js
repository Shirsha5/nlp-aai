function validateLoginForm() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    if (username === '' || password === '') {
        alert('Both fields are required.');
        return false;
    }

    // Further validation for login can be added here

    return true;
}
