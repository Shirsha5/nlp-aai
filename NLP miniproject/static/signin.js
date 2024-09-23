function validateSignUpForm() {
    const firstName = document.getElementById('first-name').value;
    const lastName = document.getElementById('last-name').value;
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value.toUpperCase();
    const email = document.getElementById('email').value;
    const contact = document.getElementById('contact').value;
    const contact1 = document.getElementById('contact1').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Check for empty fields
    if (!firstName || !lastName || !age || !gender || !email || !contact || !contact1 || !username || !password || !confirmPassword) {
        alert('All fields are required.');
        return false; // Prevent form submission
    }

    // Validate age
    if (isNaN(age) || age <= 0) {
        alert('Please enter a valid age.');
        return false; // Prevent form submission
    }

    // Validate gender
    if (gender !== 'M' && gender !== 'F') {
        alert('Gender must be M or F.');
        return false; // Prevent form submission
    }

    // Validate email format
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        alert('Please enter a valid email address.');
        return false; // Prevent form submission
    }

    // Validate phone numbers (contact and emergency contact)
    const phonePattern = /^\d{10}$/;
    if (!phonePattern.test(contact)) {
        alert('Please enter a valid 10-digit contact number.');
        return false; // Prevent form submission
    }

    if (!phonePattern.test(contact1)) {
        alert('Please enter a valid 10-digit emergency contact number.');
        return false; // Prevent form submission
    }

    // Validate password matching
    if (password !== confirmPassword) {
        alert('Passwords do not match.');
        return false; // Prevent form submission
    }

    // If all validations pass
    alert('Sign up successful!');
    window.location.href = '/elderly-care-app';  // Change this to the desired redirect URL
    return true; // Allow form submission
}

// Attach form submit handler
document.getElementById('signup-form').onsubmit = function() {
    return validateSignUpForm();
};
