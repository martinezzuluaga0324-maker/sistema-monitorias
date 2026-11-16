/* Reportes de Bienestar: actualiza la tabla con fetch() mientras se escribe o se cambia un filtro,
   sin recargar la página. Si JavaScript falla, el formulario GET sigue funcionando. */
(() => {
  const form = document.getElementById('filtros');
  const tabla = document.getElementById('tablaReporte');
  const cuerpo = tabla.querySelector('tbody');
  const conteo = document.getElementById('conteo');
  let espera;

  // Evita que texto con símbolos HTML se interprete como código.
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const clases = { asignada: 'status--ok', atendida: 'status--done', cancelada: 'status--off' };
  const asistencia = a => a === null ? '—' : (a ? 'Asistió' : 'No asistió');

  const cargar = async () => {
    const params = new URLSearchParams(new FormData(form));
    try {
      const r = await fetch(tabla.dataset.api + '?' + params);
      if (!r.ok) throw new Error();
      const filas = await r.json();
      conteo.textContent = `${filas.length} resultado(s)`;
      cuerpo.innerHTML = filas.map(s => `
        <tr><td data-t="Estudiante">${esc(s.estudiante)}</td><td data-t="Materia">${esc(s.materia)}</td><td data-t="Tema">${esc(s.tema)}</td>
          <td data-t="Fecha">${esc(s.fecha)}</td><td data-t="Monitor">${esc(s.monitor)}</td>
          <td data-t="Estado"><span class="status ${clases[s.estado] || ''}">${esc(s.estado.charAt(0).toUpperCase() + s.estado.slice(1))}</span></td>
          <td data-t="Asistencia">${asistencia(s.asistio)}</td></tr>`).join('')
        || '<tr><td colspan="7">No hay resultados con esos filtros.</td></tr>';
      history.replaceState(null, '', '?' + params);   // la URL conserva el filtro
    } catch {
      conteo.textContent = 'No se pudo actualizar. Pulsa «Filtrar».';
    }
  };

  form.addEventListener('submit', e => { e.preventDefault(); cargar(); });
  form.addEventListener('change', cargar);
  form.addEventListener('input', e => { if (e.target.name === 'q') { clearTimeout(espera); espera = setTimeout(cargar, 250); } });
})();
