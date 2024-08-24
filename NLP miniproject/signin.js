function validateSignUpForm() {
    const firstName = document.getElementById('first-name').value;
    const lastName = document.getElementById('last-name').value;
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value.toUpperCase();
    const email = document.getElementById('email').value;
    const contact = document.getElementById('contact').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (!firstName || !lastName || !age || !gender || !email || !contact || !username || !password || !confirmPassword) {
        alert('All fields are required.');
        return false;
    }

    if (isNaN(age) || age <= 0) {
        alert('Please enter a valid age.');
        return false;
    }

    if (gender !== 'M' && gender !== 'F') {
        alert('Gender must be M or F.');
        return false;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        alert('Please enter a valid email address.');
        return false;
    }

    if (!/^\d{10}$/.test(contact)) {
        alert('Please enter a valid 10-digit phone number.');
        return false;
    }

    if (password !== confirmPassword) {
        alert('Passwords do not match.');
        return false;
    }

    alert('Sign up successful!');
    return true;
}
