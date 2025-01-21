    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', () => {
            // Valitse kaikki password-tyyppiset input-kentät
            const inputs = document.querySelectorAll('.password-wrapper input[type="password"], .password-wrapper input[type="text"]');
            const icons = document.querySelectorAll('i.toggle-password');
            
            inputs.forEach(input => {
                if (input.type === 'password') {
                    input.type = 'text'; // Muuta tekstiksi
                } else if (input.type === 'text') {
                    input.type = 'password'; // Muuta salasanaksi
                }
            });

            // Päivitä ikonit
            //const icon = button.querySelector('i');
            icons.forEach(icon => {
                if (icon.classList.contains('fa-eye')) {
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        });
    });
