let pacienteInfoProcess = null;

document.addEventListener('DOMContentLoaded', function () {
    const filasPorPagina = 10;
    let paginaActual = 1;
    const tbody = document.getElementById('cuerpoTabla');
    const todasLasFilas = tbody
        ? Array.from(tbody.getElementsByTagName('tr'))
        : [];

    let filasFiltradas = [...todasLasFilas];

    function mostrarPagina(pagina) {
        const totalPaginas = Math.ceil(
            filasFiltradas.length / filasPorPagina
        );

        if (totalPaginas === 0) {
            todasLasFilas.forEach(f => {
                f.style.display = 'none';
            });

            const info = document.getElementById('infoPaginacion');
            if (info) {
                info.textContent = 'No hay registros para mostrar';
            }

            renderControles(0);
            return;
        }

        paginaActual = Math.max(1, Math.min(pagina, totalPaginas));

        const inicio = (paginaActual - 1) * filasPorPagina;
        const fin = inicio + filasPorPagina;

        todasLasFilas.forEach(f => {
            f.style.display = 'none';
        });

        filasFiltradas.slice(inicio, fin).forEach(f => {
            f.style.display = '';
        });

        const info = document.getElementById('infoPaginacion');

        if (info) {
            info.textContent =
                `Mostrando ${inicio + 1}-${Math.min(fin, filasFiltradas.length)} de ${filasFiltradas.length} registros`;
        }

        renderControles(paginaActual);
    }

    function renderControles(pagina) {
        const controles = document.getElementById('controlesPaginacion');

        if (!controles) return;

        controles.innerHTML = '';

        const totalPaginas = Math.ceil(
            filasFiltradas.length / filasPorPagina
        );

        if (totalPaginas === 0) return;

        const btnAnterior = document.createElement('button');
        btnAnterior.textContent = '←';
        btnAnterior.disabled = pagina <= 1;

        btnAnterior.onclick = () => {
            mostrarPagina(paginaActual - 1);
        };

        const info = document.createElement('span');
        info.textContent = `Página ${pagina} de ${totalPaginas}`;

        const btnSiguiente = document.createElement('button');
        btnSiguiente.textContent = '→';
        btnSiguiente.disabled = pagina >= totalPaginas;

        btnSiguiente.onclick = () => {
            mostrarPagina(paginaActual + 1);
        };

        controles.appendChild(btnAnterior);
        controles.appendChild(info);
        controles.appendChild(btnSiguiente);
    }

    const jsonElement = document.getElementById('puntos-progreso');

    let todosLosDatos = [];

    if (jsonElement) {
        try {
            todosLosDatos = JSON.parse(jsonElement.textContent);
        } catch (error) {
            console.error('Error leyendo los datos del gráfico:', error);
        }
    }

    const canvasGrafico = document.getElementById('graficoProgreso');

    if (canvasGrafico && typeof Chart !== 'undefined') {
        const ctx = canvasGrafico.getContext('2d');

        pacienteInfoProcess = new Chart(ctx, {
            type: 'line',

            data: {
                datasets: [{
                    label: 'Puntaje por sesión',
                    data: todosLosDatos,
                    backgroundColor: 'transparent',
                    fill: false,
                    borderColor: '#7F4F4F',
                    borderWidth: 2.5,
                    pointRadius: 4,
                    pointBackgroundColor: '#FAF6F0',
                    pointBorderColor: '#7F4F4F',
                    pointBorderWidth: 2
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function (c) {
                                const punto = c.raw;

                                return `Sesión ${punto.x}: ${punto.y} pts (${punto.juego || ''})`;
                            }
                        }
                    }
                },

                scales: {
                    x: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Sesión'
                        },
                        ticks: {
                            stepSize: 1
                        }
                    },

                    y: {
                        title: {
                            display: true,
                            text: 'Puntaje'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    const filtrarPacientes = document.getElementById('filtrarPacientes');

    if (filtrarPacientes) {
        filtrarPacientes.addEventListener('input', function () {
            const value = filtrarPacientes.value.toLowerCase().trim();

            filasFiltradas = todasLasFilas.filter(fila => {
                const textoFila = fila.textContent.toLowerCase();
                return textoFila.includes(value);
            });

            paginaActual = 1;
            mostrarPagina(paginaActual);

            if (pacienteInfoProcess) {
                if (value === '') {
                    pacienteInfoProcess.data.datasets[0].data = todosLosDatos;
                } else {
                    const datosFiltrados = todosLosDatos.filter(d =>
                        d.paciente &&
                        d.paciente.toLowerCase().includes(value)
                    );

                    const datosReajustados = datosFiltrados.map((d, index) => ({
                        ...d,
                        x: index + 1
                    }));

                    pacienteInfoProcess.data.datasets[0].data =
                        datosReajustados;
                }

                pacienteInfoProcess.update();
            }
        });
    }

    const btnDescargar = document.getElementById('btnDescargar');

    if (btnDescargar) {
        btnDescargar.addEventListener('click', function () {
            const csv = [];
            const rows = document.querySelectorAll('table tr');

            for (let i = 0; i < rows.length; i++) {
                const row = [];
                const cols = rows[i].querySelectorAll('td, th');

                for (let j = 0; j < cols.length; j++) {
                    const texto = cols[j].innerText.replace(/"/g, '""');
                    row.push(`"${texto}"`);
                }

                csv.push(row.join(','));
            }

            const BOM = '\uFEFF';

            const csvFile = new Blob(
                [BOM + csv.join('\n')],
                { type: 'text/csv;charset=utf-8;' }
            );

            const downloadLink = document.createElement('a');
            const url = window.URL.createObjectURL(csvFile);

            downloadLink.download =
                `reporte_${new Date().toLocaleDateString()}.csv`;

            downloadLink.href = url;
            downloadLink.style.display = 'none';

            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);

            setTimeout(() => {
                window.URL.revokeObjectURL(url);
            }, 1000);
        });
    }

    const elementoDatos = document.getElementById('datos-graficos');

    let datosPartidas = [];

    if (elementoDatos) {
        try {
            datosPartidas = JSON.parse(elementoDatos.textContent);
        } catch (error) {
            console.error('Error leyendo datos de partidas:', error);
        }
    }

    const datosOrdenados = [...datosPartidas].reverse();
    mostrarPagina(1);
});

function analisis() {
    const btn = document.getElementById('btnAnalizar');
    const resultado = document.getElementById('analisisResultado');
    if (!btn || !resultado) return;
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
                resultado.innerHTML = marked.parse(data.analisis);
                resultado.style.display = 'block';
            } else {
                resultado.textContent = 'Error: ' + (data.error || 'No se pudo generar el análisis');
                resultado.style.display = 'block';
            }

            btn.textContent = 'Generar análisis';
            btn.disabled = false;
        })
        .catch(error => {
            console.error('Error en análisis:', error);

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
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}