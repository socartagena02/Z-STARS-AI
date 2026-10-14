
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".profile-card form");
    const preview = document.getElementById("profile-preview");
    const edit = document.getElementById("profile-edit");
    const editButton = document.getElementById("edit-profile");
    const cancelButton = document.getElementById("cancel-edit");

    const nickname = document.getElementById("nickname");
    const email = document.getElementById("email");

    if (
        !form || !preview || !edit || !editButton ||
        !cancelButton || !nickname || !email
    ) {
        console.error("No se encontraron los elementos del perfil.");
        return;
    }

    editButton.addEventListener("click", () => {
        preview.hidden = true;
        edit.hidden = false;
    });

    cancelButton.addEventListener("click", () => {
        nickname.value = form.dataset.username || "";
        email.value = form.dataset.email || "";
        edit.hidden = true;
        preview.hidden = false;
    });
});
