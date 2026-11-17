/* Tándem · portada. GSAP + ScrollTrigger + Lenis para el scroll animado;
   fetch() para filtrar monitores sin recargar la página. */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasGsap = !!window.gsap && !!window.ScrollTrigger;

  /* ---------- Historias de usuario (contenido fijo de la sección "Alcance") ---------- */
  const HU = [
    ['HU-1', 'Estudiante', 'Como Estudiante quiero registrarme e iniciar sesión para acceder a la plataforma.', 'Alta', 'Nombre, código, programa y correo.'],
    ['HU-2', 'Estudiante', 'Como Estudiante quiero solicitar una monitoría indicando la materia y el tema.', 'Alta', 'La solicitud queda pendiente.'],
    ['HU-3', 'Estudiante', 'Como Estudiante quiero ver la disponibilidad de los monitores y su agenda.', 'Alta', 'Monitores de la materia con días y franjas.'],
    ['HU-4', 'Estudiante', 'Como Estudiante quiero ver el estado de mis solicitudes y cancelarlas.', 'Media', 'Materia, tema, monitor y estado.'],
    ['HU-5', 'Monitor', 'Como Monitor quiero registrar mis días y horas disponibles para que los estudiantes me encuentren.', 'Alta', 'Franjas horarias por día.'],
    ['HU-6', 'Monitor', 'Como Monitor quiero registrar la asistencia y los temas vistos en cada sesión.', 'Alta', 'Asistió o no, y qué se trabajó.'],
    ['HU-7', 'Docente', 'Como Docente quiero remitir estudiantes a monitoría para apoyar a quienes lo necesitan.', 'Media', 'Solo estudiantes inscritos en su materia.'],
    ['HU-8', 'Docente', 'Como Docente quiero consultar el historial de monitorías de mis estudiantes.', 'Media', 'Únicamente los de su grupo.'],
    ['HU-9', 'Bienestar Institucional', 'Como Bienestar Institucional quiero asignar monitores a las solicitudes pendientes.', 'Alta', 'Vista de solicitudes pendientes de asignación.'],
    ['HU-10', 'Bienestar Institucional', 'Como Bienestar Institucional quiero generar reportes de monitorías por materia y monitor.', 'Media', 'Filtros por materia, monitor y periodo.'],
  ];
  const perfiles = [...new Set(HU.map(h => h[1]))];
  let perfil = perfiles[0];
  const tabs = $('#huTabs'), huList = $('#huList');
  const renderHU = () => {
    tabs.innerHTML = perfiles.map(p => `<button class="chip" role="tab" aria-selected="${p === perfil}" data-p="${p}">${p}</button>`).join('');
    huList.innerHTML = HU.filter(h => h[1] === perfil).map((h, i) => `<li style="animation-delay:${i * 70}ms"><b>${h[0]}</b><div><p>${h[2]}</p><small>${h[4]}</small></div><span class="prio ${h[3] === 'Alta' ? 'prio--alta' : ''}">${h[3]}</span></li>`).join('');
  };
  tabs.addEventListener('click', e => { const b = e.target.closest('.chip'); if (!b) return; perfil = b.dataset.p; renderHU(); });

  /* ---------- Monitores: filtro por materia y búsqueda con fetch() (HU-3) ---------- */
  const chips = $('#chips'), grid = $('#monitorGrid'), buscar = $('#buscarMonitor');
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const iniciales = n => n.split(' ').slice(0, 2).map(p => p[0]).join('');
  let materia = '', timer;

  const pintar = lista => {
    grid.innerHTML = lista.map(m => `
      <article class="mon">
        <div class="mon__top">
          <div class="mon__av" aria-hidden="true">${esc(iniciales(m.nombre))}</div>
          <div><h3>${esc(m.nombre)}</h3><div class="mon__sub">${esc(m.programa || '')}</div></div>
        </div>
        <div class="mon__tags">${m.materias.map(x => `<span class="mon__subject">${esc(x)}</span>`).join('')}</div>
        <ul class="mon__slots">${m.franjas.length ? m.franjas.map(f => `<li><span>${esc(f)}</span></li>`).join('') : '<li><span>Sin franjas publicadas</span></li>'}</ul>
      </article>`).join('') || '<p class="vacio">No hay monitores con ese filtro todavía.</p>';
    if (hasGsap && !reduce) gsap.from('.mon', { y: 30, opacity: 0, duration: .8, ease: 'expo.out', stagger: .06, clearProps: 'all' });
  };
  const cargar = async () => {
    grid.setAttribute('aria-busy', 'true');
    try {
      const r = await fetch(`/api/monitores?materia=${encodeURIComponent(materia)}&q=${encodeURIComponent(buscar.value.trim())}`);
      if (!r.ok) throw new Error();
      pintar(await r.json());
    } catch {
      grid.innerHTML = '<p class="vacio">No pudimos cargar los monitores. Inténtalo de nuevo.</p>';
    }
    grid.removeAttribute('aria-busy');
    hasGsap && ScrollTrigger.refresh();
  };
  chips.addEventListener('click', e => {
    const b = e.target.closest('.chip'); if (!b) return;
    materia = b.dataset.m;
    $$('.chip', chips).forEach(c => c.setAttribute('aria-selected', c === b));
    cargar();
  });
  buscar.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(cargar, 250); });
  renderHU();

  /* ---------- Menú móvil ---------- */
  const nav = $('#nav'), burger = $('#burger');
  burger.addEventListener('click', () => { const o = nav.classList.toggle('is-open'); burger.setAttribute('aria-expanded', o); });
  $$('.nav__links a').forEach(a => a.addEventListener('click', () => { nav.classList.remove('is-open'); burger.setAttribute('aria-expanded', false); }));


  /* ---------- Scroll suave + navegación ---------- */
  let lenis = null;
  const scrollToEl = sel => { const el = $(sel); if (!el) return; lenis ? lenis.scrollTo(el, { offset: -60, duration: 1.6 }) : el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' }); };
  $$('a[href^="#"]').forEach(a => a.addEventListener('click', e => { const h = a.getAttribute('href'); if (h.length > 1 && $(h)) { e.preventDefault(); scrollToEl(h); } }));

  /* ---------- Arranque: espera a que la pantalla de carga (carga.js) empiece a subir ---------- */
  if (!hasGsap) { $$('.w').forEach(w => w.style.opacity = 1); return; }
  gsap.registerPlugin(ScrollTrigger);
  gsap.defaults({ ease: 'expo.out' });

  if (window.Lenis && !reduce) {
    lenis = new Lenis({ lerp: .09, wheelMultiplier: 1, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(t => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  const intro = () => {
    const lines = $$('.hero__title .line > span');
    gsap.set(lines, { yPercent: 110 });
    gsap.set('.hero__lead,.hero__cta', { y: 30, opacity: 0 });
    gsap.set('.nav', { yPercent: -100 });
    gsap.to('.hero__media img', { scale: 1, duration: 2.4 });
    gsap.to(lines, { yPercent: 0, duration: 1.4, stagger: .12 });
    gsap.to('.hero__lead,.hero__cta', { y: 0, opacity: 1, duration: 1.1, stagger: .1, delay: .35 });
    gsap.to('.nav', { yPercent: 0, duration: 1, delay: .4 });
  };

  const arrancar = () => { intro(); setup(); };
  window.__tandemListo ? arrancar() : document.addEventListener('tandem:listo', arrancar, { once: true });

  /* ---------- Animaciones de scroll ---------- */
  function setup() {
    const mm = gsap.matchMedia();

    // Nav: sólida al pasar el hero, se oculta al bajar y vuelve al subir
    ScrollTrigger.create({
      start: 80, end: 'max',
      onUpdate: s => { nav.classList.toggle('is-solid', s.scroll() > 80); if (!nav.classList.contains('is-open')) nav.classList.toggle('is-hidden', s.direction === 1 && s.scroll() > 600); },
    });

    // Hero: la imagen se desplaza más despacio y el título sube
    gsap.to('.hero__media', { yPercent: 12, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
    gsap.to('.hero__content', { yPercent: -10, opacity: .2, ease: 'none', scrollTrigger: { trigger: '.hero', start: '30% top', end: 'bottom top', scrub: true } });

    // Palabra por palabra: el texto se "enciende" al leer
    $$('[data-words]').forEach(p => {
      const words = p.textContent.trim().split(/\s+/);
      p.setAttribute('aria-label', p.textContent.trim());
      p.innerHTML = words.map(w => `<span class="w" aria-hidden="true">${w} </span>`).join('');
      gsap.to($$('.w', p), { opacity: 1, ease: 'none', stagger: .12, scrollTrigger: { trigger: p, start: 'top 82%', end: 'bottom 48%', scrub: .6 } });
    });

    // Cifras
    $$('[data-count]').forEach(el => {
      const end = +el.dataset.count, suf = el.dataset.suffix || '', o = { v: 0 };
      ScrollTrigger.create({ trigger: el, start: 'top 88%', once: true, onEnter: () => gsap.to(o, { v: end, duration: 1.8, ease: 'power2.out', onUpdate: () => el.textContent = Math.round(o.v) + suf }) });
    });
    gsap.from('.fig', { y: 40, opacity: 0, duration: 1.1, stagger: .1, scrollTrigger: { trigger: '.figures__row', start: 'top 88%' } });

    mm.add('(min-width: 701px)', () => {
      // Roles: scroll horizontal anclado
      const track = $('#rolesTrack');
      const dist = () => Math.max(0, track.scrollWidth - innerWidth);
      gsap.to(track, { x: () => -dist(), ease: 'none', scrollTrigger: { trigger: '.roles', start: 'top top', end: () => '+=' + (dist() + innerHeight * .4), pin: '.roles__pin', scrub: .7, invalidateOnRefresh: true, anticipatePin: 1 } });
      gsap.from('.roles__head > *', { y: 50, opacity: 0, duration: 1.1, stagger: .12, scrollTrigger: { trigger: '.roles', start: 'top 70%' } });
    });

    // Imagen que se expande a pantalla completa
    mm.add({ wide: '(min-width: 701px)', narrow: '(max-width: 700px)' }, ctx => {
      const from = ctx.conditions.wide ? 'inset(18% 26% round 36px)' : 'inset(14% 6% round 24px)';
      const t = gsap.timeline({ scrollTrigger: { trigger: '.expand', start: 'top top', end: 'bottom bottom', scrub: .7 } });
      t.fromTo('.expand__frame', { clipPath: from }, { clipPath: 'inset(0% 0% round 0px)', ease: 'power2.inOut', duration: 1 }, 0)
       .to('.expand__frame > img', { scale: 1, ease: 'none', duration: 1.4 }, 0)
       .to('.expand__copy', { opacity: 1, y: 0, ease: 'power2.out', duration: .5 }, .7);
    });

    // Tarjetas apiladas: la anterior se aleja y se oscurece al llegar la siguiente
    const cards = $$('.card');
    cards.forEach((c, i) => {
      if (i === cards.length - 1) return;
      gsap.to(c, { scale: .93 - (cards.length - 2 - i) * 0.0, filter: 'brightness(.82)', ease: 'none', scrollTrigger: { trigger: cards[i + 1], start: 'top 85%', end: 'top 18%', scrub: true } });
    });
    $$('.card__img img').forEach(img => gsap.fromTo(img, { scale: 1.25 }, { scale: 1, ease: 'none', scrollTrigger: { trigger: img, start: 'top bottom', end: 'bottom 30%', scrub: true } }));

    // Entradas simples, una por bloque
    const reveal = (sel, trigger, extra = {}) => gsap.from(sel, { y: 60, opacity: 0, duration: 1.2, stagger: .1, scrollTrigger: { trigger, start: 'top 80%' }, ...extra });
    reveal('.stack__intro h2', '.stack__intro');
    reveal('.monitors__head > *', '.monitors__head');
    reveal('.request__lead > *', '.request__lead');
    reveal('.form', '.request__panel');
    reveal('.mine', '.mine', { delay: .1 });
    reveal('.scope__head > *', '.scope__head');
    reveal('.scope__body', '.scope__body');
    gsap.from('.cta h2', { y: 80, opacity: 0, duration: 1.4, scrollTrigger: { trigger: '.cta', start: 'top 70%' } });
    gsap.from('.cta__row > *', { y: 40, opacity: 0, duration: 1, stagger: .1, scrollTrigger: { trigger: '.cta', start: 'top 55%' } });
    gsap.from('.foot__word', { yPercent: 40, ease: 'none', scrollTrigger: { trigger: '.foot', start: 'top bottom', end: 'bottom bottom', scrub: true } });

    // Parallax suave en la foto de solicitud
    gsap.fromTo('.request__lead img', { scale: 1.15 }, { scale: 1, ease: 'none', scrollTrigger: { trigger: '.request__lead img', start: 'top bottom', end: 'bottom top', scrub: true } });

    addEventListener('load', () => ScrollTrigger.refresh());
  }
})();
