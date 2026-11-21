document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const username = document.querySelector('input[name="username"]');
    const email = document.querySelector('input[name="email"]');
    const password1 = document.querySelector('input[name="password1"]');
    const password2 = document.querySelector('input[name="password2"]');
    const rolTabs = document.querySelectorAll(".rol-tab");
    const rolInput = document.getElementById("rolSeleccionado");
    const modalidadGroup = document.getElementById("modalidadGroup");
    const modalidades = modalidadGroup.querySelectorAll('input[name="modalidad"]');
    const loginCard = document.querySelector(".login-card");
    const institucionGroup = document.getElementById("institucionGroup");
    const institucionSelect = document.querySelector('select[name="institucion"]');
    const radioInstitucional = document.getElementById("institucion");
    const radioIndependiente = document.getElementById("independiente");

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function isValidPassword(password) {
        return password.length >= 8;
    }

    function actualizarInstitucion() {
        const esProfesional = rolInput.value === "profesional";
        const requiereInstitucion =
            esProfesional && radioInstitucional.checked;

        institucionGroup.hidden = !requiereInstitucion;

        institucionSelect.disabled = !requiereInstitucion;
        institucionSelect.required = requiereInstitucion;

        if (!requiereInstitucion) {
            institucionSelect.value = "";
        }
    }

    function cambiarRol(rol) {
        rolTabs.forEach(tab => {
            const seleccionado = tab.dataset.rol === rol;

            tab.classList.toggle("active", seleccionado);
            tab.setAttribute("aria-pressed", seleccionado);
        });

        rolInput.value = rol;

        loginCard.classList.toggle("patient-mode", rol === "paciente");
        loginCard.classList.toggle("professional-mode", rol === "profesional");

        const esProfesional = rol === "profesional";

        modalidadGroup.hidden = !esProfesional;

        modalidades.forEach(input => {
            input.disabled = !esProfesional;
            input.required = esProfesional;

            if (!esProfesional) {
                input.checked = false;
            }
        });
        actualizarInstitucion();
    }

    rolTabs.forEach(tab => {
        tab.addEventListener("click", function () {
            cambiarRol(tab.dataset.rol);
        });
    });

    radioInstitucional.addEventListener("change", actualizarInstitucion);
    radioIndependiente.addEventListener("change", actualizarInstitucion);

    form.addEventListener("submit", function (e) {
        let errorMessage = "";

        if (username.value.trim().length < 3) {
            errorMessage += "El usuario debe tener al menos 3 caracteres.\n";
        }

        if (!isValidEmail(email.value.trim())) {
            errorMessage += "Email no válido.\n";
        }

        if (!isValidPassword(password1.value)) {
            errorMessage += "La contraseña debe tener al menos 8 caracteres.\n";
        }

        if (password1.value !== password2.value) {
            errorMessage += "Las contraseñas no coinciden.\n";
        }

        if (rolInput.value === "profesional") {
            const modalidadSeleccionada = form.querySelector(
                'input[name="modalidad"]:checked'
            );

            if (!modalidadSeleccionada) {
                errorMessage += "Selecciona tu modalidad de trabajo.\n";
            }

            if (
                radioInstitucional.checked &&
                !institucionSelect.value
            ) {
                errorMessage += "Debes seleccionar una institución.\n";
            }
        }

        if (errorMessage !== "") {
            e.preventDefault();
            alert(errorMessage);
        }
    });
    cambiarRol("profesional");
});