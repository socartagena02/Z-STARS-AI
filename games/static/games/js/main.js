document.addEventListener("DOMContentLoaded", function () {
    let audioHabilitado = false;
    let currentGame = 'simon';

    const gameDescriptions = {
        simon: "Simon Dice: Juego de memoria secuencial. Debes repetir las secuencias de colores y sonidos. Ideal para la concentración.",
        memorice: "Memorice: Encuentra las parejas de cartas iguales. Perfecto para entrenar la memoria visual.",
        camino: "Traza mi Camino: Conecta los puntos siguiendo el patrón. Disponible próximamente."
    };

    const modalElem = document.getElementById('gameInfoPopup');
    const gamePopup = modalElem ? new bootstrap.Modal(modalElem) : null;
    if (modalElem) {
        modalElem.addEventListener('hide.bs.modal', function () {
            if (document.activeElement && modalElem.contains(document.activeElement)) {
                document.activeElement.blur();
            }
        });
    }

    document.querySelectorAll('.info-btn').forEach(button => {
        button.addEventListener('click', function() {
            currentGame = this.getAttribute('data-game');
            const iconSrc = this.getAttribute('data-icon');
            const cardTitle = this.closest('.game-card').querySelector('h3').textContent;
            
            document.getElementById('popupGameTitle').textContent = cardTitle;
            document.getElementById('popupGameIcon').src = iconSrc;
            
            document.querySelectorAll('.game-info').forEach(info => info.classList.add('d-none'));
            
            const infoToShow = document.getElementById(currentGame + 'Info');
            if (infoToShow) infoToShow.classList.remove('d-none');
            
            if (gamePopup) gamePopup.show();
        });
    });

    const carousel = document.querySelector("#gameCarousel");
    if (carousel) {
        carousel.addEventListener("slid.bs.carousel", function () {
            let activeItem = carousel.querySelector(".carousel-item.active");
            let titulo = activeItem ? activeItem.querySelector("h3") : null;
        });
    }
});
