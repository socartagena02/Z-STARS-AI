document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const username = document.querySelector('input[name="username"]');
    const email = document.querySelector('input[name="email"]');
    const password1 = document.querySelector('input[name="password1"]');
    const password2 = document.querySelector('input[name="password2"]');

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function isValidPassword(password) {
        return password.length >= 8;
    }

    form.addEventListener('submit', function(e) {
        let isValid = true;
        let errorMessage = '';

        if (username.value.trim().length < 3) {
            isValid = false;
            errorMessage += 'El usuario debe tener al menos 3 caracteres.\n';
        }

        if (!isValidEmail(email.value)) {
            isValid = false;
            errorMessage += 'Email no válido.\n';
        }

        if (!isValidPassword(password1.value)) {
            isValid = false;
            errorMessage += 'La contraseña debe tener al menos 8 caracteres.\n';
        }

        if (password1.value !== password2.value) {
            isValid = false;
            errorMessage += 'Las contraseñas no coinciden.\n';
        }

        if (!isValid) {
            e.preventDefault();
            alert(errorMessage);
        }
    });
});