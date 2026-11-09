function mostrarResultado(titulo, mensaje, tipo = "victoria") {
    const modal = document.getElementById("modalResultados");
    const tituloElemento = document.getElementById("modalTitulo");
    const mensajeElemento = document.getElementById("modalMensaje");
    const boton = document.getElementById("modalCerrar");

    tituloElemento.textContent = titulo;
    mensajeElemento.textContent = mensaje;

    tituloElemento.className = tipo;

    modal.classList.remove("oculto");
    boton.onclick = () => {
        modal.classList.add("oculto");
    };

}