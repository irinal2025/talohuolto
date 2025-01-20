document.getElementById('toggle-password').addEventListener('click', function () {
    var passwordField = document.querySelector('.password-wrapper input[id="password"]');
    if (passwordField.type === 'password') {
        passwordField.type = 'text'; // Näytä salasana
        this.classList.remove('fa-eye');
        this.classList.add('fa-eye-slash');
    } else {
        passwordField.type = 'password'; // Piilota salasana
        this.classList.remove('fa-eye-slash');
        this.classList.add('fa-eye');
    }
  });