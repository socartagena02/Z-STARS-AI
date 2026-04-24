document.addEventListener('DOMContentLoaded', function() {
    const filasPorPagina = 10;
    let paginaActual = 1;
    const tbody = document.getElementById('cuerpoTabla');
    const todasLasFilas = Array.from(tbody.getElementsByTagName('tr'));
    let filasFiltradas = [...todasLasFilas];

    function mostrarPagina(pagina) {
        const inicio = (pagina - 1) * filasPorPagina;
        const fin = inicio + filasPorPagina;

        todasLasFilas.forEach(f => f.style.display = 'none');
        filasFiltradas.slice(inicio, fin).forEach(f => f.style.display = '');

        document.getElementById('infoPaginacion').textContent = 
            `Mostrando ${inicio + 1}-${Math.min(fin, filasFiltradas.length)} de ${filasFiltradas.length} registros`;

        renderControles(pagina);
    }

    function renderControles(pagina) {
        const totalPaginas = Math.ceil(filasFiltradas.length / filasPorPagina);
        const controles = document.getElementById('controlesPaginacion');
        controles.innerHTML = '';

        const btnAnterior = document.createElement('button');
        btnAnterior.textContent = '←';
        btnAnterior.disabled = pagina === 1;
        btnAnterior.onclick = () => { paginaActual--; mostrarPagina(paginaActual); };
        controles.appendChild(btnAnterior);

        const info = document.createElement('span');
        info.textContent = ` Página ${pagina} de ${totalPaginas} `;
        controles.appendChild(info);

        const btnSiguiente = document.createElement('button');
        btnSiguiente.textContent = '→';
        btnSiguiente.disabled = pagina === totalPaginas;
        btnSiguiente.onclick = () => { paginaActual++; mostrarPagina(paginaActual); };
        controles.appendChild(btnSiguiente);
    }

    const filtroJuego = document.getElementById('filtroJuego');
    filtroJuego.addEventListener('change', function() {
        const valorFiltro = filtroJuego.value.toLowerCase();
        filasFiltradas = todasLasFilas.filter(fila => {
            const celdaJuego = fila.getElementsByTagName('td')[2];
            if (!celdaJuego) return false;
            return valorFiltro === '' || 
                   celdaJuego.textContent.toLowerCase().includes(valorFiltro);
        });
        paginaActual = 1;
        mostrarPagina(paginaActual);
    });

    const btnDescargar = document.getElementById('btnDescargar');
    if (btnDescargar) {
        btnDescargar.addEventListener('click', function() {
            let csv = [];
            const rows = document.querySelectorAll("table tr");
            for (let i = 0; i < rows.length; i++) {
                const row = [], cols = rows[i].querySelectorAll("td, th");
                for (let j = 0; j < cols.length; j++)
                    row.push('"' + cols[j].innerText + '"');
                csv.push(row.join(","));
            }
            const csvFile = new Blob([csv.join("\n")], {type: "text/csv"});
            const downloadLink = document.createElement("a");
            downloadLink.download = `reporte_${new Date().toLocaleDateString()}.csv`;
            downloadLink.href = window.URL.createObjectURL(csvFile);
            downloadLink.style.display = "none";
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
        });
    }

    mostrarPagina(1);

    const datosOrdenados = [...datosPartidas].reverse();

    const ctxEvolucion = document.getElementById('chartEvolucion').getContext('2d');
    new Chart(ctxEvolucion, {
        type: 'line',
        data: {
            labels: datosOrdenados.map(d => d.fecha),
            datasets: [
                {
                    label: 'Memorice',
                    data: datosOrdenados.map(d => d.juego === 'Memorice' ? d.puntaje : null),
                    borderColor: '#6366f1',
                    tension: 0.3,
                    fill: false,
                    spanGaps: false
                },
                {
                    label: 'Simon Dice',
                    data: datosOrdenados.map(d => d.juego === 'Simon Dice' ? d.puntaje : null),
                    borderColor: '#10b981',
                    tension: 0.3,
                    fill: false,
                    spanGaps: false
                }
            ]
        },
        options: { 
            responsive: true, 
            plugins: { title: { display: true, text: 'Evolución del puntaje' }}
        }
    });

    const ctxFallos = document.getElementById('chartFallos').getContext('2d');
    new Chart(ctxFallos, {
        type: 'line',
        data: {
            labels: datosOrdenados.map(d => `${d['paciente__nickname']} ${d.fecha}`),
            datasets: [
                {
                    label: 'Fallos',
                    data: datosOrdenados.map(d => d.fallos),
                    borderColor: '#ef4444',
                    yAxisID: 'y',
                    tension: 0.3
                },
                {
                    label: 'Tiempo reacción (s)',
                    data: datosOrdenados.map(d => d.tiempo_reaccion_promedio),
                    borderColor: '#f59e0b',
                    yAxisID: 'y1',
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { type: 'linear', position: 'left', title: { display: true, text: 'Fallos' }},
                y1: { type: 'linear', position: 'right', title: { display: true, text: 'Reacción (s)' }}
            },
            plugins: { title: { display: true, text: 'Fallos y tiempo de reacción por sesión' }}
        }
    });

    const ctxComparacion = document.getElementById('chartComparacion').getContext('2d');
    const memorice = datosPartidas.filter(d => d.juego === 'Memorice');
    const simon = datosPartidas.filter(d => d.juego === 'Simon Dice');
    const promedioMemorice = memorice.reduce((a, b) => a + b.puntaje, 0) / (memorice.length || 1);
    const promedioSimon = simon.reduce((a, b) => a + b.puntaje, 0) / (simon.length || 1);

    new Chart(ctxComparacion, {
        type: 'bar',
        data: {
            labels: ['Memorice', 'Simon Dice'],
            datasets: [{
                label: 'Puntaje promedio',
                data: [promedioMemorice.toFixed(0), promedioSimon.toFixed(0)],
                backgroundColor: ['#6366f1', '#10b981']
            }]
        },
        options: { 
            responsive: true, 
            plugins: { title: { display: true, text: 'Comparación entre juegos' }}
        }
    });

    const ctxDificultad = document.getElementById('chartDificultad').getContext('2d');
    const basico = datosPartidas.filter(d => d.nivel_dificultad === 'basico').length;
    const intermedio = datosPartidas.filter(d => d.nivel_dificultad === 'intermedio').length;
    const avanzado = datosPartidas.filter(d => d.nivel_dificultad === 'avanzado').length;

    new Chart(ctxDificultad, {
        type: 'doughnut',
        data: {
            labels: ['Básico', 'Intermedio', 'Avanzado'],
            datasets: [{
                data: [basico, intermedio, avanzado],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
            }]
        },
        options: { 
            responsive: true, 
            maintainAspectRatio: false,
            plugins: { title: { display: true, text: 'Distribución por dificultad' }}
        }
    });

}); 

function analisis() {
    const btn = document.getElementById('btnAnalizar');
    const resultado = document.getElementById('analisisResultado');
    
    btn.textContent = 'Analizando...';
    btn.disabled = true;
    resultado.style.display = 'none';
    
    fetch('/api/analizar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.analisis) {
            resultado.innerHTML = data.analisis
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
            resultado.style.display = 'block';
        } else {
            resultado.textContent = 'Error: ' + data.error;
            resultado.style.display = 'block';
        }
        btn.textContent = 'Generar análisis';
        btn.disabled = false;
    })
    .catch(error => {
        resultado.textContent = 'Error al conectar con la IA';
        resultado.style.display = 'block';
        btn.textContent = 'Generar análisis';
        btn.disabled = false;
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}