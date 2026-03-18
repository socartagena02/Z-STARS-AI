document.addEventListener('DOMContentLoaded', function() { 
    const filtroJuego = document.getElementById('filtroJuego');
    const tabla = document.getElementById('tablaResultados');
    const filas = tabla.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    const btnDescargar = document.getElementById('btnDescargar'); 

    filtroJuego.addEventListener('change', function() {
        const valorFiltro = filtroJuego.value.toLowerCase();
        let registrosVisibles = 0;

        for (let i = 0; i < filas.length; i++) {
            const celdaJuego = filas[i].getElementsByTagName('td')[2];
            if (celdaJuego) {
                const textoJuego = celdaJuego.textContent || celdaJuego.innerText;
                if (valorFiltro === "" || textoJuego.toLowerCase().indexOf(valorFiltro) > -1) {
                    filas[i].style.display = "";
                    registrosVisibles++;
                } else {
                    filas[i].style.display = "none";
                }
            }
        }
        document.getElementById('infoPaginacion').textContent = `Mostrando ${registrosVisibles} registros`;
    });

    if (btnDescargar) {
        btnDescargar.addEventListener('click', function() {
            let csv = [];
            const rows = document.querySelectorAll("table tr");
            for (let i = 0; i < rows.length; i++) {
                if (rows[i].style.display !== 'none') {
                    const row = [], cols = rows[i].querySelectorAll("td, th");
                    for (let j = 0; j < cols.length; j++) 
                        row.push('"' + cols[j].innerText + '"');
                    csv.push(row.join(","));
                }
            }
            const csvFile = new Blob([csv.join("\n")], {type: "text/csv"});
            const downloadLink = document.createElement("a");
            downloadLink.download = `reporte_memoryflow_${new Date().toLocaleDateString()}.csv`;
            downloadLink.href = window.URL.createObjectURL(csvFile);
            downloadLink.style.display = "none";
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
        });
    }
});