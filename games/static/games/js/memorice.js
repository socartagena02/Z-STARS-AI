const imagenesBase = [
    "/static/games/assets/images/circulo_lila.png",
    "/static/games/assets/images/cruz_azul.png",
    "/static/games/assets/images/cuadrado.png",
    "/static/games/assets/images/Estrella_amarilla.png",
    "/static/games/assets/images/heart_corazon.png",
    "/static/games/assets/images/triangulo.png",
    "/static/games/assets/images/rombo_naranja.png",
    "/static/games/assets/images/media_luna_rosa.png",
    "/static/games/assets/images/Hexagono.png"
];

let estado = {
    primeraCarta: null,
    segundaCarta: null,
    bloqueado: false,
    puntaje: 0,
    nivelActual: 1,
    parejasActuales: 0,
    parejasEncontradas: 0,
    tiempo: 0,
    temporizador: null,
    fallos: 0 
};

window.cronometroMemoriceGlobal = 0;

window.iniciarJuego = function(parejasIniciales, esSiguienteNivel = false) {
    if (!esSiguienteNivel) {
        window.cronometroMemoriceGlobal = new Date().getTime(); 
        console.log("!!! Cronómetro GLOBAL iniciado para NUEVA PARTIDA !!!");
        estado.nivelActual = 1;
        estado.puntaje = 0;
        estado.fallos = 0;
        // Solo pausar música si es inicio real
        const musica = document.getElementById("bgmusic");
        if (musica) musica.pause();
    }

    estado.parejasEncontradas = 0;
    estado.parejasActuales = parejasIniciales;
    resetSeleccion(); // Limpiar cartas seleccionadas
    
    // Tiempos por nivel (ajusta según lo que tenías)
    if (estado.nivelActual === 1) estado.tiempo = 60;
    else if (estado.nivelActual === 2) estado.tiempo = 90;
    else if (estado.nivelActual === 3) estado.tiempo = 150;

    // Sonidos iniciales
    const winSound = document.getElementById("winSound");
    if (winSound) {
        winSound.play().then(() => {
            winSound.pause();
            winSound.currentTime = 0;
        }).catch(e => console.log("Audio esperando interacción"));
    }

    // UI
    document.getElementById("pantallaFinal").classList.add("hidden");
    document.getElementById("inicio").classList.add("hidden");
    document.getElementById("juego").classList.remove("hidden");

    actualizarUI();
    iniciarTemporizador();
    generarTablero();
};

function generarTablero() {
    const tablero = document.getElementById("tablero");
    tablero.innerHTML = ""; 
    estado.bloqueado = true; 

    const imagenes = imagenesBase.slice(0, estado.parejasActuales);
    const cartas = [...imagenes, ...imagenes].sort(() => Math.random() - 0.5);

    let columnas, cardSize;
    if (estado.parejasActuales === 9) { columnas = 6; cardSize = "85px"; }
    else if (estado.parejasActuales === 6) { columnas = 4; cardSize = "110px"; }
    else { columnas = 3; cardSize = "120px"; }

    tablero.style.gridTemplateColumns = `repeat(${columnas}, ${cardSize})`;
    tablero.style.width = "fit-content"; 
    tablero.style.margin = "0 auto"; 

    cartas.forEach(src => {
        const card = document.createElement("div");
        card.classList.add("card");
        card.style.width = cardSize;
        card.style.height = cardSize;

        card.innerHTML = `
            <div class="card-inner">
                <div class="card-front"><img src="${src}" style="width: 80%; height: 80%;"></div>
                <div class="card-back"></div>
            </div>
        `;
        card.addEventListener("click", () => voltearCarta(card, src));
        tablero.appendChild(card);
    });

    setTimeout(() => {
        document.querySelectorAll(".card").forEach(c => c.classList.add("flip"));
        setTimeout(() => {
            document.querySelectorAll(".card").forEach(c => c.classList.remove("flip"));
            estado.bloqueado = false;
        }, 2000);
    }, 300);
}

function voltearCarta(card, src) {
    if (estado.bloqueado || card.classList.contains("flip")) return;

    const flipSound = document.getElementById("flipSound");
    if (flipSound) { flipSound.currentTime = 0; flipSound.play(); }

    card.classList.add("flip");

    if (!estado.primeraCarta) {
        estado.primeraCarta = { card, src };
        return;
    }

    estado.segundaCarta = { card, src };
    estado.bloqueado = true;

    if (estado.primeraCarta.src === estado.segundaCarta.src) {
        estado.puntaje += 150;
        estado.parejasEncontradas++;
        aplicarBrilloPistacho();
        if (document.getElementById("matchSound")) document.getElementById("matchSound").play();

        if (estado.parejasEncontradas === estado.parejasActuales) {
            clearInterval(estado.temporizador); 
            setTimeout(siguienteNivel, 1000); 
        } else {
            resetSeleccion();
        }
    } 
    else {
        estado.fallos++;
        if (document.getElementById("errorSound")) document.getElementById("errorSound").play();

        estado.primeraCarta.card.classList.add("shake");
        estado.segundaCarta.card.classList.add("shake");

        setTimeout(() => {
            estado.primeraCarta.card.classList.remove("flip", "shake");
            estado.segundaCarta.card.classList.remove("flip", "shake");
            resetSeleccion();
            actualizarUI(); 
        }, 1000); 
    }
    actualizarUI();
}

function iniciarTemporizador() {
    clearInterval(estado.temporizador);
    estado.temporizador = setInterval(() => {
        estado.tiempo--;
        actualizarUI();
        if (estado.tiempo <= 0) finalizarJuego();
    }, 1000);
}

function actualizarUI() {
    document.getElementById("puntaje").textContent = `Puntaje: ${estado.puntaje}`;
    document.getElementById("tiempo").textContent = `Tiempo: ${estado.tiempo}`;
}

function resetSeleccion() {
    estado.primeraCarta = null;
    estado.segundaCarta = null;
    estado.bloqueado = false;
}

window.siguienteNivel = function() {
    estado.nivelActual++;
    
    if (estado.nivelActual === 2) { 
        estado.parejasActuales = 6; 
    } else if (estado.nivelActual === 3) { 
        estado.parejasActuales = 9; 
    } else { 
        finalizarJuego(); 
        return; 
    }

    iniciarJuego(estado.parejasActuales, true);
};

window.volverMenu = function() {
    clearInterval(estado.temporizador);
    window.cronometroMemoriceGlobal = 0; // Reset total
    document.getElementById("juego").classList.add("hidden");
    document.getElementById("pantallaFinal").classList.add("hidden");
    document.getElementById("inicio").classList.remove("hidden");
    estado.puntaje = 0;
    estado.nivelActual = 1;
    actualizarUI();
};

function finalizarJuego() {
    clearInterval(estado.temporizador);
    // Sonido final
    if (document.getElementById("winSound")) document.getElementById("winSound").play();
    document.getElementById("pantallaFinal").classList.remove("hidden");
    datos(estado.puntaje);
}

function datos(puntosActuales) {
    const ahora = new Date().getTime();
    let diferenciaMs = ahora - window.cronometroMemoriceGlobal;
    
    if (window.cronometroMemoriceGlobal === 0 || diferenciaMs < 0) diferenciaMs = 0;

    const totalSegundos = Math.floor(diferenciaMs / 1000);
    const mm = Math.floor(totalSegundos / 60).toString().padStart(2, '0');
    const ss = (totalSegundos % 60).toString().padStart(2, '0');
    const tiempoFinal = `${mm}:${ss}`;

    const nickname = prompt(`¡VIVA, GANASTE!, ingresa tu Nickname para guardar tu puntaje:`);
    
    if (nickname && nickname.trim() !== "") {
        fetch('/puntos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                juego: 'Memorice',
                puntaje: puntosActuales,
                apodo: nickname, 
                tiempo: tiempoFinal, 
                fallos: estado.fallos 
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.mensaje === "Éxito") {
                window.cronometroMemoriceGlobal = 0;
                window.location.href = '/dashboard/';
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function aplicarBrilloPistacho() {
    const scoreBox = document.getElementById("puntaje").parentElement;
    scoreBox.style.boxShadow = "0 0 30px #C9FF8A"; 
    scoreBox.style.backgroundColor = "rgba(188, 245, 120, 0.6)";
    setTimeout(() => {
        scoreBox.style.boxShadow = "0 8px 32px rgba(0, 0, 0, 0.3)";
        scoreBox.style.backgroundColor = "rgba(255, 255, 255, 0.2)"; 
    }, 500);
}