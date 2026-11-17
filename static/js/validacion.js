/* Validación en el navegador (cliente) y utilidades comunes a todas las páginas.
   Es una ayuda para el usuario: el servidor vuelve a validar todo (nunca se confía solo en el cliente). */
(() => {
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];

  /* ---------- Avisos emergentes: muestran los mensajes flash de Flask ---------- */
  const toastEl = document.getElementById('toast');
  let timer;
  const toast = (texto, tipo = 'ok') => {
    if (!toastEl) return;
    toastEl.textContent = texto;
    toastEl.dataset.tipo = tipo;
    toastEl.classList.add('is-on');
    clearTimeout(timer);
    timer = setTimeout(() => toastEl.classList.remove('is-on'), 3800);
  };
  try {
    const mensajes = JSON.parse(toastEl.dataset.mensajes || '[]');
    if (mensajes.length) toast(mensajes[0][1], mensajes[0][0]);
  } catch (e) { /* sin mensajes */ }

  /* ---------- Fecha mínima = hoy ---------- */
  const hoy = new Date(); hoy.setMinutes(hoy.getMinutes() - hoy.getTimezoneOffset());
  $$('[data-min-hoy]').forEach(i => i.min = hoy.toISOString().slice(0, 10));

  /* ---------- Reglas de validación ---------- */
  // Devuelve el mensaje de error de un campo, o '' si está bien.
  const revisar = (el) => {
    const v = el.value.trim();
    const msg = el.dataset.msg;
    if (el.required && !v) return 'Este campo es obligatorio.';
    if (!v) return '';
    if (el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return msg || 'Escribe un correo válido.';
    if (el.pattern && !new RegExp('^(?:' + el.pattern + ')$').test(v)) return msg || 'Formato inválido.';
    if (el.minLength > 0 && v.length < el.minLength) return msg || `Mínimo ${el.minLength} caracteres.`;
    if (el.dataset.minPalabras && v.split(/\s+/).length < +el.dataset.minPalabras) return msg || 'Completa el campo.';
    if (el.min && el.type === 'date' && v < el.min) return msg || 'La fecha ya pasó.';
    if (el.dataset.despuesDe) {
      const otro = el.form.elements[el.dataset.despuesDe];
      if (otro && otro.value && v <= otro.value) return msg || 'Valor inválido.';
    }
    return '';
  };

  const mostrar = (el, msg) => {
    const campo = el.closest('.field');
    if (!campo) return;
    campo.classList.toggle('is-bad', !!msg);
    const err = campo.querySelector('.err');
    if (err) err.textContent = msg;
    el.setAttribute('aria-invalid', msg ? 'true' : 'false');
  };

  $$('form[data-validar]').forEach(form => {
    const campos = () => $$('input:not([type=hidden]):not([type=checkbox]):not([type=radio]), select, textarea', form);

    // Al salir de un campo se revisa; si ya tenía error, se revisa mientras se corrige.
    form.addEventListener('focusout', e => { if (campos().includes(e.target)) mostrar(e.target, revisar(e.target)); });
    form.addEventListener('input', e => {
      if (campos().includes(e.target) && e.target.closest('.field')?.classList.contains('is-bad')) mostrar(e.target, revisar(e.target));
    });

    form.addEventListener('submit', e => {
      let primero = null;
      campos().forEach(el => {
        const msg = revisar(el);
        mostrar(el, msg);
        if (msg && !primero) primero = el;
      });
      if (primero) { e.preventDefault(); primero.focus(); toast('Revisa los campos marcados.', 'error'); return; }
      // Todo está bien: se evita el doble envío y el botón muestra que está trabajando.
      if (form.dataset.enviando) { e.preventDefault(); return; }
      form.dataset.enviando = '1';
      const boton = e.submitter || form.querySelector('button:not([type=button])');
      if (boton) boton.classList.add('is-loading');
    });
  });

  /* ---------- Confirmación antes de acciones peligrosas (eliminar, cancelar) ----------
     Se usa una ventana propia (<dialog>) con el diseño de la página, no el confirm() del navegador. */
  const dialogo = document.createElement('dialog');
  dialogo.className = 'confirmar';
  dialogo.innerHTML = `
    <h2>¿Estás seguro?</h2>
    <p id="confirmarTexto"></p>
    <div class="botones">
      <button type="button" class="btn btn--pill btn--ghost-ink" data-no>No, volver</button>
      <button type="button" class="btn btn--pill btn--peligro" data-si>Sí, continuar</button>
    </div>`;
  document.body.appendChild(dialogo);
  let formPendiente = null;

  document.addEventListener('submit', e => {
    const f = e.target.closest('form[data-confirmar]');
    if (!f) return;
    e.preventDefault();                                   // se detiene el envío hasta que la persona confirme
    formPendiente = f;
    dialogo.querySelector('#confirmarTexto').textContent = f.dataset.confirmar;
    dialogo.showModal();
    dialogo.querySelector('[data-no]').focus();
  });
  // Se cierra por el mismo camino por el que llegó (animación de salida) antes de cerrar de verdad.
  const reducir = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const cerrar = despues => {
    dialogo.classList.add('is-closing');
    setTimeout(() => { dialogo.close(); dialogo.classList.remove('is-closing'); if (despues) despues(); }, reducir ? 0 : 200);
  };
  dialogo.addEventListener('click', e => {
    if (dialogo.classList.contains('is-closing')) return;
    if (e.target.matches('[data-si]') && formPendiente) { const f = formPendiente; formPendiente = null; cerrar(() => f.submit()); }
    else if (e.target.matches('[data-no]') || e.target === dialogo) { formPendiente = null; cerrar(); }
  });
  dialogo.addEventListener('cancel', e => { e.preventDefault(); formPendiente = null; cerrar(); });   // tecla Esc

  /* ---------- Barra superior: la línea aparece solo cuando el contenido pasa por debajo ---------- */
  const barra = document.querySelector('.appbar');
  if (barra) {
    const borde = () => barra.classList.toggle('is-scrolled', scrollY > 4);
    borde(); addEventListener('scroll', borde, { passive: true });
  }

  /* ---------- Al volver con "Atrás" los botones no se quedan cargando ---------- */
  addEventListener('pageshow', () => {
    $$('.btn.is-loading').forEach(b => b.classList.remove('is-loading'));
    $$('form[data-enviando]').forEach(f => delete f.dataset.enviando);
  });
})();
