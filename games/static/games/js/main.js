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

    const popupAudioBtn = document.getElementById('popupAudioBtn');
    if (popupAudioBtn) {
        popupAudioBtn.addEventListener('click', function() {
            const description = gameDescriptions[currentGame];
            if (description) {
                const url = `/tts-eleven/?texto=${encodeURIComponent(description)}`;
                const audio = new Audio(url);
                audio.play().catch(err => console.error("Error ElevenLabs:", err));
            }
        });
    }

    function reproducirTTS(texto) {
        const url = `/tts-eleven/?texto=${encodeURIComponent(texto)}`;
        const audio = new Audio(url);
        audio.play().catch(err => console.log("Audio bloqueado por el navegador hasta interacción."));
    }

    function activarAudioInicial() {
        let textoElement = document.querySelector(".top-left-text-box");
        if (textoElement) {
            reproducirTTS(textoElement.innerText.trim());
        }
        audioHabilitado = true;
        document.removeEventListener("click", activarAudioInicial);
    }

    document.addEventListener("click", activarAudioInicial);

    const carousel = document.querySelector("#gameCarousel");
    if (carousel) {
        carousel.addEventListener("slid.bs.carousel", function () {
            if (!audioHabilitado) return;

            let activeItem = carousel.querySelector(".carousel-item.active");
            let titulo = activeItem ? activeItem.querySelector("h3") : null;

            if (titulo) {
                reproducirTTS(titulo.innerText.trim());
            }
        });
    }
});

// 1. Definimos la función de reproducción
function iniciaMusica() {
    const theme = document.getElementById("bgmusic");
    if (theme) {
        theme.volume = 0.5; 
        theme.play()
            .then(() => console.log("¡Maxwell activado con éxito!"))
            .catch(error => console.log("Error al intentar reproducir:", error));
    }
}

document.addEventListener('click', iniciaMusica, { once: true });