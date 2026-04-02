// --- VARIABLES DE ESTADO ---
let secuencia = [];
let secuenciaUsuario = [];
let nivelActual = 0;
let puntos = 0;
let bloqueado = true; 
let fallos = 0;
let nivelMaximo = 0;
let tiempoReaccion = [];
let ultimosClick = null;

let config = {
    botones: [],
    velocidad: 800,
    nombre: ''
};

let tiempoInicio;
var cronometroSimon = 0;

function iniciarJuego(nivel) {
    tiempoInicio = Date.now();
    const musica = document.getElementById("bgmusic");
    if (musica) musica.pause();

    document.getElementById('pantalla-menu').classList.add('hidden');
    document.getElementById('pantalla-juego').classList.remove('hidden');
    
    puntos = 0;
    nivelActual = 0;
    secuencia = [];
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
    document.getElementById('pantalla-juego').classList.add('hidden');
    document.getElementById('pantalla-menu').classList.remove('hidden');
    secuencia = [];
    bloqueado = true;
}


document.getElementById('start-game').addEventListener('click', () => {
    cronometroSimon = new Date().getTime();
    puntos = 0;
    nivelActual = 0;
    secuencia = [];
    fallos = 0;
    nivelMaximo = 0;
    tiempoReaccion = [];
    ultimosClick = null;
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
    const intervalo = setInterval(() => {
        ejecutarFlash(secuencia[i], 'sequence-active');
        i++;
        if (i >= secuencia.length) {
            clearInterval(intervalo);
            setTimeout(() => { bloqueado = false; }, 500); 
        }
    }, config.velocidad + 300);
}

function ejecutarFlash(id, clase) {
    const btn = document.getElementById(id);
    if (!btn) return;
    
    btn.classList.add(clase);
    setTimeout(() => btn.classList.remove(clase), config.velocidad);
}
document.querySelectorAll('.colorButton').forEach(boton => {
    boton.addEventListener('click', (e) => {
        if (bloqueado) 
            return; 

            const ahora = Date.now();
            if(ultimosClick !== null){
                const diff = ahora - ultimosClick;
                if (diff < 15000){
                    tiempoReaccion.push(diff);
                }
            }
            ultimosClick = ahora;

        const idElegido = e.target.id;
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
        
        setTimeout(() => {
            document.getElementById('game').classList.remove('error');
            alert(`Secuencia incorrecta. ¡Buen intento!\nPuntos: ${puntos}`);
            datos(puntos); 
        }, 600);
        return;
    }

    if (secuenciaUsuario.length === secuencia.length) {
        puntos += 150;
        document.getElementById('score').innerText = puntos;
        bloqueado = true;
        setTimeout(siguienteRonda, 1200);
    }
}

function datos(puntosActuales) {
    const ahora = new Date().getTime();
    let diferenciaMs = ahora - cronometroSimon;
    
    if (cronometroSimon === 0) diferenciaMs = 0;

    const totalSegundos = Math.floor(diferenciaMs / 1000);
    const mm = Math.floor(totalSegundos / 60).toString().padStart(2, '0');
    const ss = (totalSegundos % 60).toString().padStart(2, '0');
    const tiempoFinal = `${mm}:${ss}`;

    const promedioCalculado = tiempoReaccion.length > 0
        ? (tiempoReaccion.reduce((a, b) => a + b, 0) / tiempoReaccion.length / 1000).toFixed(2)
        : 0;

    const nickname = prompt(`¡Fin del juego! Tiempo: ${tiempoFinal}\nIngresa tu Nickname:`);
    
    if (nickname && nickname.trim() !== "") {
        fetch('/puntos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                juego: 'Simon Dice',
                puntaje: puntosActuales,
                apodo: nickname, 
                tiempo: tiempoFinal,
                fallos: fallos,
                nivel_dificultad: config.nombre,
                nivel_maximo_alcanzado: nivelMaximo,
                tiempo_reaccion_promedio: parseFloat(promedioCalculado) 
            })
        })
        .then(response => {
            if (response.ok) {
                cronometroSimon = 0;
                window.location.href = '/dashboard/';
            }
        });
    }
}