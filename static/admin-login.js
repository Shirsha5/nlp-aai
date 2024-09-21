// Show/hide password functionality
document.getElementById('show-password').addEventListener('change', function() {
  const passwordField = document.getElementById('password');
  passwordField.type = this.checked ? 'text' : 'password';
});

// Form submission handler with spinner
document.getElementById('login-form').addEventListener('submit', function(event) {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();

  if (username === '' || password === '') {
      alert('Please fill in both fields.');
      event.preventDefault(); // Prevent form submission
      return;
  }

  // Show the spinner
  document.getElementById('loading-spinner').style.display = 'block';
