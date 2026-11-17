/* Reportes de Bienestar: la tabla y la paginación se actualizan con fetch() al escribir, cambiar un
   filtro o pasar de página, sin recargar. Si JavaScript falla, el formulario GET y los enlaces
   de paginación siguen funcionando con recarga normal. */
(() => {
  const form = document.getElementById('filtros');
  const tabla = document.getElementById('tablaReporte');
  const cuerpo = tabla.querySelector('tbody');
  const conteo = document.getElementById('conteo');
  const pie = document.getElementById('paginacion');
  const POR_PAGINA = 10;
  let espera;

  // Evita que texto con símbolos HTML se interprete como código.
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const clases = { asignada: 'status--ok', atendida: 'status--done', cancelada: 'status--off' };
  const asistencia = a => a === null ? '—' : (a ? 'Asistió' : 'No asistió');
  const parametros = pagina => { const p = new URLSearchParams(new FormData(form)); p.set('pagina', pagina); return p; };

  // Dibuja los botones: Anterior, números (con "…" para los lejanos) y Siguiente.
  const dibujarPaginas = (pagina, paginas, total) => {
    const desde = total ? (pagina - 1) * POR_PAGINA + 1 : 0;
    const hasta = Math.min(pagina * POR_PAGINA, total);
    let html = `<p class="pag__info" id="pagInfo">Mostrando ${desde}–${hasta} de ${total}</p>`;
    if (paginas > 1) {
      const enlace = (n, texto, etiqueta) => `<li><a href="?${parametros(n)}" data-pagina="${n}" ${etiqueta ? `aria-label="${etiqueta}"` : ''}>${texto}</a></li>`;
      html += '<ul class="pag__lista">';
      html += pagina > 1 ? enlace(pagina - 1, 'Anterior') : '<li><span class="is-off">Anterior</span></li>';
      for (let n = 1; n <= paginas; n++) {
        if (n === 1 || n === paginas || Math.abs(n - pagina) <= 1) {
          html += n === pagina ? `<li><span class="is-on" aria-current="page">${n}</span></li>` : enlace(n, n, `Página ${n}`);
        } else if (Math.abs(n - pagina) === 2) html += '<li><span class="is-off">…</span></li>';
      }
      html += pagina < paginas ? enlace(pagina + 1, 'Siguiente') : '<li><span class="is-off">Siguiente</span></li>';
      html += '</ul>';
    }
    pie.innerHTML = html;
  };

  const cargar = async (pagina = 1) => {
    const params = parametros(pagina);
    tabla.setAttribute('aria-busy', 'true');       // la tabla se atenúa mientras llegan los datos
    try {
      const r = await fetch(tabla.dataset.api + '?' + params);
      if (!r.ok) throw new Error();
      const datos = await r.json();
      conteo.textContent = `${datos.total} resultado(s)`;
      cuerpo.innerHTML = datos.filas.map(s => `
        <tr><td data-t="Estudiante">${esc(s.estudiante)}</td><td data-t="Materia">${esc(s.materia)}</td><td data-t="Tema">${esc(s.tema)}</td>
          <td data-t="Fecha">${esc(s.fecha)}</td><td data-t="Monitor">${esc(s.monitor)}</td>
          <td data-t="Estado"><span class="status ${clases[s.estado] || ''}">${esc(s.estado.charAt(0).toUpperCase() + s.estado.slice(1))}</span></td>
          <td data-t="Asistencia">${asistencia(s.asistio)}</td></tr>`).join('')
        || '<tr><td colspan="7">No hay resultados con esos filtros.</td></tr>';
      dibujarPaginas(datos.pagina, datos.paginas, datos.total);
      history.replaceState(null, '', '?' + parametros(datos.pagina));   // la URL conserva filtros y página
    } catch {
      conteo.textContent = 'No se pudo actualizar. Pulsa «Filtrar».';
    }
    tabla.removeAttribute('aria-busy');
  };

  form.addEventListener('submit', e => { e.preventDefault(); cargar(1); });
  form.addEventListener('change', () => cargar(1));
  form.addEventListener('input', e => { if (e.target.name === 'q') { clearTimeout(espera); espera = setTimeout(() => cargar(1), 250); } });
  // Los enlaces de paginación se interceptan para pedir la página con fetch.
  pie.addEventListener('click', e => {
    const a = e.target.closest('a[data-pagina]');
    if (!a) return;
    e.preventDefault();
    cargar(+a.dataset.pagina);
  });
  // La paginación servida por Flask no trae data-pagina: se lo ponemos leyendo su dirección.
  pie.querySelectorAll('a[href]').forEach(a => { a.dataset.pagina = new URL(a.href).searchParams.get('pagina'); });
})();
