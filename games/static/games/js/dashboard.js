let pacienteInfoProcess = null;
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

    const filtrarPacientes = document.getElementById('filtrarPacientes');
    const jsonElement = document.getElementById('puntos-progreso');
    const todosLosDatos = jsonElement ? JSON.parse(jsonElement.textContent) :  [];

    if (jsonElement && document.getElementById('graficoProgreso')){
        const ctx = document.getElementById('graficoProgreso').getContext('2d');
        pacienteInfoProcess = new Chart( ctx, {
            type: "line",
           data: {
                    datasets: [{
                        label: "Puntaje por sesión",
                        data: todosLosDatos,
                        backgroundColor: "transparent",
                        fill: false,
                        borderColor: "#7F4F4F",
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointBackgroundColor: "#FAF6F0",
                        pointBorderColor: "#7F4F4F",
                        pointBorderWidth: 2,
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(c) {
                                    return `Sesión ${c.raw.x}: ${c.raw.y} pts (${c.raw.juego})`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            type: "linear",
                            title: { display: true, text: "Sesión" },
                            ticks: { stepSize: 1 },
                        },
                        y: {
                            title: { display: true, text: "Puntaje" },
                            beginAtZero: true,
                        },
                    },
                },
        })
    }

    if (filtrarPacientes) {
        filtrarPacientes.addEventListener('input', function(){
            const value = filtrarPacientes.value.toLowerCase().trim();
            filasFiltradas = todasLasFilas.filter(fila => {
                const textFila = fila.textContent.toLowerCase();
                return textFila.includes(value);
            });
            paginaActual = 1;
            mostrarPagina(paginaActual);

            if (value === "") {
                pacienteInfoProcess.data.datasets[0].data = todosLosDatos;
            }else{
                const datosFiltrados = todosLosDatos.filter(d =>
                  d.paciente && d.paciente.toLowerCase().includes(value)
                );
                const datosReajustados = datosFiltrados.map((d, index) =>({
                    ...d,
                    x: index + 1
                }));
                pacienteInfoProcess.data.datasets[0].data = datosReajustados;
            }
            pacienteInfoProcess.update();
        });
    }

    const elementoDatos = document.getElementById('datos-graficos');

    const datosPartidas = elementoDatos
        ? JSON.parse(elementoDatos.textContent)
        : [];

    const btnDescargar = document.getElementById('btnDescargar');
    if (btnDescargar) {
        btnDescargar.addEventListener('click', function() {
            let csv = [];

            const rows = document.querySelectorAll("table tr");

            for (let i = 0; i < rows.length; i++) {
                const row = [];
                const cols = rows[i].querySelectorAll("td, th");

                for (let j = 0; j < cols.length; j++) {
                    const texto = cols[j].innerText.replace(/"/g, '""');
                    row.push(`"${texto}"`);
                }

                csv.push(row.join(","));
            }

            const BOM = "\uFEFF";

            const csvFile = new Blob(
                [BOM + csv.join("\n")],
                { type: "text/csv;charset=utf-8;" }
            );

            const downloadLink = document.createElement("a");
            const url = window.URL.createObjectURL(csvFile);

            downloadLink.download =
                `reporte_${new Date().toLocaleDateString()}.csv`;

            downloadLink.href = url;
            downloadLink.style.display = "none";

            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);

            window.URL.revokeObjectURL(url);
        });
    }

    mostrarPagina(1);

    const datosOrdenados = [...datosPartidas].reverse();
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
            resultado.innerHTML = marked.parse(data.analisis);
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