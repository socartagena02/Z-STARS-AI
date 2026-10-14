
document.addEventListener("DOMContentLoaded", () => {
    const layout = document.querySelector(".dashboard-layout");
    const sidebar = document.querySelector("#sidebar");
    const toggle = document.querySelector(".sidebar-toggle");

    if (!layout || !sidebar || !toggle) return;

    toggle.setAttribute("aria-controls", sidebar.id);

    const actualizarEstado = () => {
        const oculto = layout.classList.contains("sidebar-hidden");

        toggle.setAttribute("aria-expanded", String(!oculto));
        toggle.setAttribute(
            "aria-label",
            oculto ? "Mostrar menú lateral" : "Ocultar menú lateral"
        );
    };
    actualizarEstado();
    toggle.addEventListener("click", () => {
        layout.classList.toggle("sidebar-hidden");
        actualizarEstado();
    });
});
