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
    fallos: 0,
    tiempoReaccion: [],
    ultimosClick: 0,
    partidaFinalizada: false,
    timeoutNivel: null,
};

window.cronometroMemoriceGlobal = 0;

window.iniciarJuego = function(parejasIniciales, esSiguienteNivel = false) {
    estado.partidaFinalizada = false;

    if (!esSiguienteNivel) {
        window.cronometroMemoriceGlobal = new Date().getTime(); 
        estado.nivelActual = 1;
        estado.puntaje = 0;
        estado.fallos = 0;
        estado.tiempoReaccion = [];
        estado.ultimosClick = null;
        const musica = document.getElementById("bgmusic");
        if (musica) musica.pause();
    }

    estado.parejasEncontradas = 0;
    estado.parejasActuales = parejasIniciales;
    resetSeleccion(); 

    estado.tiempo = obtenerTiempoPorNivel(estado.nivelActual);

    document.getElementById("inicio").classList.add("hidden");
    document.getElementById("juego").classList.remove("hidden");

    actualizarUI();
    iniciarTemporizador();
    generarTablero();
};

window.siguienteNivel = function() {
    estado.nivelActual++;

    if (estado.nivelActual === 2) {
        iniciarJuego(6,true);
    } else if (estado.nivelActual === 3) {
        iniciarJuego(9,true);
    } else {
        finalizarJuego(true);
    }
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
    if (estado.partidaFinalizada || estado.bloqueado || card.classList.contains("flip")) return;

    const flipSound = document.getElementById("flipSound");
    if (flipSound) { flipSound.currentTime = 0; flipSound.play(); }

    card.classList.add("flip");

    if (!estado.primeraCarta) {
        estado.primeraCarta = { card, src };
        return;
    }

    estado.segundaCarta = { card, src };
    estado.bloqueado = true;

    const ahora  = Date.now();
    if (estado.ultimosClick !== null) {
        const diff = ahora - estado.ultimosClick;
        if(diff<1500){
            estado.tiempoReaccion.push(diff);
        }
    }

    if (estado.primeraCarta.src === estado.segundaCarta.src) {
        estado.puntaje += 150;
        estado.parejasEncontradas++;
        aplicarBrilloPistacho();
        if (document.getElementById("matchSound")) document.getElementById("matchSound").play();

        if (estado.parejasEncontradas === estado.parejasActuales) {
            clearInterval(estado.temporizador); 
            estado.temporizador = null;

            estado.timeoutNivel = setTimeout(() => {
                estado.timeoutNivel = null;

                if (!estado.partidaFinalizada){
                    window.siguienteNivel();
                }
            }, 1000);

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
            if (estado.partidaFinalizada) return;

            estado.primeraCarta.card.classList.remove("flip", "shake");
            estado.segundaCarta.card.classList.remove("flip", "shake");
            resetSeleccion();
            actualizarUI(); 
        }, 1000); 
    }
    estado.ultimosClick = Date.now();
    actualizarUI();
}

function iniciarTemporizador() {
    clearInterval(estado.temporizador);
    estado.temporizador = setInterval(() => {
        estado.tiempo--;
        actualizarUI();

        if (estado.tiempo <= 0) {
            clearInterval(estado.temporizador);
            estado.temporizador = null;
            finalizarJuego(false)
        }
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

window.volverMenu = function() {
    clearInterval(estado.temporizador);
    estado.temporizador = null;

    clearTimeout(estado.timeoutNivel);
    estado.timeoutNivel = null;

    window.cronometroMemoriceGlobal = 0;
    
    estado.partidaFinalizada = false;
    estado.bloqueado = true;

    estado.puntaje = 0;
    estado.nivelActual = 1;
    estado.tiempoReaccion = [];
    estado.ultimosClick = null; 
    estado.parejasEncontradas = 0;
    estado.parejasActuales = 0;
    estado.tiempo = 0;
    estado.fallos = 0;

    document.getElementById("juego").classList.add("hidden");
    document.getElementById("pantallaFinal").classList.add("hidden");
    document.getElementById("inicio").classList.remove("hidden");

    actualizarUI();
};

function finalizarJuego(gano = false) {
    if (estado.partidaFinalizada) return;
    
    estado.partidaFinalizada = true;

    clearInterval(estado.temporizador);
    estado.temporizador = null;
    estado.bloqueado = true;

    if (gano) {
        mostrarResultado(
            "Ganaste!",
            "Has completado todos los niveles.",
            "victoria"
        );
    } else {
        mostrarResultado(
            "Se te acabo el tiempo!",
            "Suerte para la proxima",
            "derrota."
        );
    }

}

function datos(puntosActuales) {
    const ahora = new Date().getTime();
    let diferenciaMs = ahora - window.cronometroMemoriceGlobal;
    
    if (window.cronometroMemoriceGlobal === 0 || diferenciaMs < 0) diferenciaMs = 0;

    const totalSegundos = Math.floor(diferenciaMs / 1000);
    const mm = Math.floor(totalSegundos / 60).toString().padStart(2, '0');
    const ss = (totalSegundos % 60).toString().padStart(2, '0');
    const tiempoFinal = `${mm}:${ss}`;

    const tiempoReaccionPromedio = estado.tiempoReaccion.length > 0
        ? (estado.tiempoReaccion.reduce((a, b) => a + b, 0) / estado.tiempoReaccion.length / 1000).toFixed(2)
        : 0;

    const nivelDificultad = estado.nivelActual >= 3 ? 'avanzado'
                          : estado.nivelActual >= 2 ? 'intermedio'
                          : 'basico';

    const nickname = prompt(`¡VIVA, GANASTE!, ingresa tu Nickname para guardar tu puntaje:`);
    
    if (nickname && nickname.trim() !== "") {
          fetch('/api/partidas/registrar/', {
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
                fallos: estado.fallos,
                nivel_dificultad: nivelDificultad,
                tiempo_reaccion_promedio: parseFloat(tiempoReaccionPromedio) 
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

function obtenerTiempoPorNivel(nivel) {
    const tiempos = {
        1: 60,
        2: 90,
        3: 150
    };
    
    return tiempos[nivel] ?? 0;
}