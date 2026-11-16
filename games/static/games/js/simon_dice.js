// --- VARIABLES DE ESTADO ---
let secuencia = [];
let secuenciaUsuario = [];
let nivelActual = 0;
let puntos = 0;
let bloqueado = true; 
let fallos = 0;
let nivelMaximo = 0;
let momentoEstimulo = null;
let esperandoRespuesta = false;
let tiempoReaccion = [];
let partidaFinalizada = false;
let partidaGuardada = false;
let timeoutSimon = new Set();
let intervaloSimon = new Set();

let config = {
    botones: [],
    velocidad: 800,
    nombre: ''
};

var cronometroSimon = 0;

function programarTimeout(callback, delay) {
    const id = setTimeout(() => {
        timeoutSimon.delete(id);
        callback();
    }, delay);
    timeoutSimon.add(id);
    return id;
}

function programarIntervalo(callback, delay){
    const id = setInterval(callback, delay);
    intervaloSimon.add(id);
    return id;
}

function detenerIntervalo(id) {
    clearInterval(id);
    intervaloSimon.delete(id);
}

function limpiarTemporizadores(){
    timeoutSimon.forEach(id => clearTimeout(id));
    intervaloSimon.forEach(id => clearInterval(id));

    timeoutSimon.clear();
    intervaloSimon.clear();

    document.querySelectorAll('.colorButton').forEach(boton => {
        boton.classList.remove('sequence-active', 'click-active');
    });
    document.getElementById('game').classList.remove('error');
}

function iniciarJuego(nivel) {
    limpiarTemporizadores();
    const musica = document.getElementById("bgmusic");
    if (musica) musica.pause();

    document.getElementById('pantalla-menu').classList.add('hidden');
    document.getElementById('pantalla-juego').classList.remove('hidden');
    
    puntos = 0;
    nivelActual = 0;
    secuencia = [];
    momentoEstimulo = null;
    esperandoRespuesta = false;
    tiempoReaccion = [];
    fallos = 0;
    nivelMaximo = 0;
    secuenciaUsuario = [];
    partidaFinalizada = false;
    partidaGuardada = false;
    
    document.getElementById('score').innerText = puntos;
    document.getElementById('level').innerText = nivelActual;
    document.getElementById('titulo-dinamico').innerText = `Simón Dice - ${nivel.toUpperCase()}`;

    const grid = document.getElementById('game');
    const todosLosBotones = document.querySelectorAll('.colorButton');
    
    todosLosBotones.forEach(b => b.classList.add('hidden'));

    if (nivel === 'basico') {
        config = { nombre: 'basico', botones: ['purple', 'blue', 'yellow', 'green'], velocidad: 800 };
        grid.style.gridTemplateColumns = "repeat(2, 1fr)";
    } else if (nivel === 'intermedio') {
        config = { nombre: 'intermedio', botones: ['purple', 'blue', 'yellow', 'green', 'orange', 'red'], velocidad: 600 };
        grid.style.gridTemplateColumns = "repeat(3, 1fr)";
    } else {
        config = { nombre: 'avanzado', botones: ['purple', 'blue', 'yellow', 'green', 'orange', 'red', 'pink', 'turquese', 'cyan'], velocidad: 400 };
        grid.style.gridTemplateColumns = "repeat(3, 1fr)";
    }

    config.botones.forEach(id => document.getElementById(id).classList.remove('hidden'));
    bloqueado = true;
}

function volverAlMenu() {
    limpiarTemporizadores();
    document.getElementById('pantalla-juego').classList.add('hidden');
    document.getElementById('pantalla-menu').classList.remove('hidden');

    secuencia = [];
    secuenciaUsuario = [];
    momentoEstimulo = null;
    esperandoRespuesta = false;
    bloqueado = true;
    cronometroSimon = 0;
    partidaFinalizada = true;
}


document.getElementById('start-game').addEventListener('click', () => {
    limpiarTemporizadores();

    bloqueado = true;
    cronometroSimon = Date.now();
    
    puntos = 0;
    nivelActual = 0;
    secuencia = [];
    fallos = 0;
    nivelMaximo = 0;
    tiempoReaccion = [];
    momentoEstimulo = null;
    esperandoRespuesta = false;
    partidaFinalizada = false;
    partidaGuardada = false;

    document.getElementById('score').innerText = puntos;
    siguienteRonda();
});

function siguienteRonda() {
    secuenciaUsuario = [];
    nivelActual++;
    nivelMaximo = nivelActual;
    document.getElementById('level').innerText = nivelActual;
    bloqueado = true; 

    const colorAzar = config.botones[Math.floor(Math.random() * config.botones.length)];
    secuencia.push(colorAzar);

    reproducirSecuencia();
}

function reproducirSecuencia() {
    let i = 0;

    const intervalo = programarIntervalo(() => {
        ejecutarFlash(secuencia[i], 'sequence-active');
        i++;

        if (i >= secuencia.length) {
            detenerIntervalo(intervalo);

            programarTimeout(() => {
                momentoEstimulo = performance.now();
                esperandoRespuesta = true;
                bloqueado = false;
            }, 500);
        }
    }, config.velocidad + 300);

}

function ejecutarFlash(id, clase) {
    const btn = document.getElementById(id);
    if (!btn) return;
    
    btn.classList.add(clase);
    programarTimeout(() =>{
        btn.classList.remove(clase);
    }, config.velocidad);
}

document.querySelectorAll('.colorButton').forEach(boton => {
    boton.addEventListener('click', (e) => {
        if (bloqueado) return;

        const ahora = performance.now();

        if (esperandoRespuesta) {
            const reaccion = (ahora - momentoEstimulo) / 1000;

            tiempoReaccion.push(reaccion);

            esperandoRespuesta = false;
            momentoEstimulo = null;
        }

        const idElegido = e.currentTarget.id;

        ejecutarFlash(idElegido, 'click-active');
        secuenciaUsuario.push(idElegido);

        verificarPaso(secuenciaUsuario.length - 1);
    });
});

function verificarPaso(indice) {
   if (secuenciaUsuario[indice] !== secuencia[indice]) {
        fallos ++;
        document.getElementById('game').classList.add('error');
        bloqueado = true;
        
        programarTimeout(() => {
            document.getElementById('game').classList.remove('error');
            
            mostrarResultado(
                "Has perdido",
                `Llegaste al nivel ${nivelMaximo}. y obtuviste ${puntos} puntos`,
                "derrota"
            );

            datos(puntos); 
        }, 600);
        return;
    }

    if (secuenciaUsuario.length === secuencia.length) {
        puntos += 150;
        document.getElementById('score').innerText = puntos;
        bloqueado = true;
        programarTimeout(siguienteRonda, 1200);
    }
}

function datos(puntosActuales) {
    if (partidaFinalizada) return;
    partidaFinalizada = true;

    const ahora = new Date().getTime();
    let diferenciaMs = ahora - cronometroSimon;
    
    if (cronometroSimon === 0) diferenciaMs = 0;

    const totalSegundos = Math.floor(diferenciaMs / 1000);
    const mm = Math.floor(totalSegundos / 60).toString().padStart(2, '0');
    const ss = (totalSegundos % 60).toString().padStart(2, '0');
    const tiempoFinal = `${mm}:${ss}`;

    const promedioCalculado = tiempoReaccion.length > 0
        ? Number((
            tiempoReaccion.reduce((a, b) => a + b, 0) /
            tiempoReaccion.length
        ).toFixed(2))
        : null;

    const nickname = prompt(`¡Fin del juego! Tiempo: ${tiempoFinal}\nIngresa tu Nickname:`);
    
    if (!nickname || nickname.trim() === "") {
        alert("Debes ingresar un nickname para registrar tu partida.");
        return;
    }
        fetch('/api/partidas/registrar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                juego: 'Simon Dice',
                puntaje: puntosActuales,
                apodo: nickname.trim(), 
                tiempo: tiempoFinal,
                fallos: fallos,
                nivel_dificultad: config.nombre,
                nivel_maximo_alcanzado: nivelMaximo,
                tiempo_reaccion_promedio: promedioCalculado
            })
        })
        .then(async response => {
            let data = {};

            try {
                data = await response.json();
            } catch {
                throw new Error("El servidor devolvió una respuesta inesperada.");
            }

            if (!response.ok) {
                throw new Error(data.error || "Nose pudo guardar la partida");
            } 

            partidaGuardada = true;
            cronometroSimon = 0;
            window.location.href = '/dashboard/';
        })
        .catch(error => {
            console.error("Error guardando partida", error);
            alert(error.message);
        })
}