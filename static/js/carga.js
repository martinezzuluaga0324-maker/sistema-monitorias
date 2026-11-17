/* Pantalla de carga de Tándem.
   - Se muestra UNA vez por sesión del navegador (por pestaña) y dura poco más de un segundo.
   - En las demás páginas no aparece: la app responde al instante.
   - Avisa a la portada con el evento "tandem:listo" cuando la cortina empieza a subir. */
(() => {
  const html = document.documentElement;
  const loader = document.getElementById('loader');

  const avisar = () => {
    window.__tandemListo = true;
    document.dispatchEvent(new Event('tandem:listo'));
  };
  const quitar = () => {
    document.body.classList.remove('is-loading');
    if (loader) loader.remove();
  };

  // Ya se mostró en esta sesión (o no hay pantalla de carga): sin espera.
  if (!loader || html.classList.contains('sin-carga')) { quitar(); avisar(); return; }

  const reducir = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const duracion = reducir ? 300 : 1100;    // tiempo que se ve el logo
  const salida = reducir ? 200 : 750;       // tiempo que tarda en subir la cortina

  setTimeout(() => {
    loader.classList.add('is-out');
    avisar();                               // la portada anima su entrada mientras sube la cortina
    setTimeout(() => {
      quitar();
      try { sessionStorage.setItem('tandem.cargado', '1'); } catch (e) { /* sin almacenamiento: se mostrará otra vez */ }
    }, salida);
  }, duracion);
})();
