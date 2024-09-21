function redirectTo(role) {
  if (role === 'admin') {
      window.location.href = '/admin-login'; // Redirect to admin login
  } else if (role === 'user') {
      window.location.href = '/user-login';  // Redirect to user login
  }
}
