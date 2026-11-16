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
      if (primero) { e.preventDefault(); primero.focus(); toast('Revisa los campos marcados.', 'error'); }
    });
  });

  /* ---------- Confirmación antes de acciones peligrosas (eliminar, cancelar) ---------- */
  document.addEventListener('submit', e => {
    const f = e.target.closest('form[data-confirmar]');
    if (f && !confirm(f.dataset.confirmar)) e.preventDefault();
  });
})();
