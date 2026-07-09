/* PostHog-style desktop window manager */
(function () {
  'use strict';

  const mobileMQ = window.matchMedia('(max-width: 820px)');
  const isMobile = () => mobileMQ.matches;

  let zCounter = 20;
  let focused = null;

  const windows = () => Array.from(document.querySelectorAll('.ph-window'));
  const getWin = (id) => document.getElementById('win-' + id);

  function renormalizeZ() {
    const ordered = windows()
      .filter((w) => !w.classList.contains('is-hidden'))
      .sort((a, b) => (parseInt(a.style.zIndex || '20', 10)) - (parseInt(b.style.zIndex || '20', 10)));
    zCounter = 20;
    ordered.forEach((w) => { zCounter += 1; w.style.zIndex = String(zCounter); });
  }

  function focusWin(win) {
    if (!win) return;
    if (zCounter > 800) renormalizeZ();
    zCounter += 1;
    win.style.zIndex = String(zCounter);
    focused = win;
    syncDock();
  }

  function openWin(id) {
    const win = getWin(id);
    if (!win) return;
    if (isMobile()) {
      win.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    win.classList.remove('is-hidden');
    focusWin(win);
  }

  function closeWin(win) {
    if (!win) return;
    win.classList.remove('is-max');
    win.classList.add('is-hidden');
    syncDock();
  }

  function toggleMax(win) {
    if (!win) return;
    win.classList.toggle('is-max');
    focusWin(win);
  }

  function syncDock() {
    document.querySelectorAll('.ph-task[data-dock]').forEach((item) => {
      const win = getWin(item.getAttribute('data-dock'));
      const visible = win && !win.classList.contains('is-hidden');
      item.classList.toggle('is-active', !!visible);
    });
  }

  /* ---- Open triggers (icons, start menu items) ---- */
  document.querySelectorAll('[data-open]').forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      closeStartMenu();
      openWin(el.getAttribute('data-open'));
    });
  });

  /* ---- Taskbar buttons: toggle window (minimize if active) ---- */
  document.querySelectorAll('.ph-task[data-dock]').forEach((item) => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const id = item.getAttribute('data-dock');
      const win = getWin(id);
      const visible = win && !win.classList.contains('is-hidden');
      if (visible && !isMobile()) {
        if (win === focused) closeWin(win);   // active -> minimize
        else focusWin(win);                    // open but behind -> bring to front
      } else {
        openWin(id);
      }
    });
  });

  /* ---- Start menu ---- */
  const startBtn = document.getElementById('ph-start');
  const startMenu = document.getElementById('ph-startmenu');

  function closeStartMenu() {
    if (!startMenu) return;
    startMenu.classList.add('is-hidden');
    if (startBtn) { startBtn.classList.remove('is-open'); startBtn.setAttribute('aria-expanded', 'false'); }
  }

  function toggleStartMenu() {
    if (!startMenu) return;
    const willOpen = startMenu.classList.contains('is-hidden');
    startMenu.classList.toggle('is-hidden', !willOpen);
    if (startBtn) { startBtn.classList.toggle('is-open', willOpen); startBtn.setAttribute('aria-expanded', String(willOpen)); }
  }

  if (startBtn) {
    startBtn.addEventListener('click', (e) => { e.stopPropagation(); toggleStartMenu(); });
    document.addEventListener('click', (e) => {
      if (!startMenu || startMenu.classList.contains('is-hidden')) return;
      if (e.target.closest('#ph-startmenu') || e.target.closest('#ph-start')) return;
      closeStartMenu();
    });
  }

  /* ---- Trash easter egg ---- */
  document.querySelectorAll('[data-trash]').forEach((el) => {
    el.addEventListener('click', () => {
      el.animate(
        [
          { transform: 'translateX(0) rotate(0)' },
          { transform: 'translateX(-4px) rotate(-6deg)' },
          { transform: 'translateX(4px) rotate(6deg)' },
          { transform: 'translateX(-3px) rotate(-4deg)' },
          { transform: 'translateX(0) rotate(0)' }
        ],
        { duration: 380, easing: 'ease-in-out' }
      );
    });
  });

  /* ---- Window chrome (traffic lights) + focus + drag ---- */
  windows().forEach((win) => {
    win.addEventListener('mousedown', () => focusWin(win), true);

    win.querySelectorAll('[data-action]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const action = btn.getAttribute('data-action');
        if (action === 'close' || action === 'minimize') closeWin(win);
        else if (action === 'maximize') toggleMax(win);
      });
    });

    const handle = win.querySelector('[data-drag-handle]');
    if (handle) {
      makeDraggable(win, handle);
      handle.addEventListener('dblclick', (e) => {
        if (e.target.closest('[data-action]')) return;
        toggleMax(win);
      });
    }
  });

  /* Escape closes the focused window */
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape' || isMobile()) return;
    if (focused && !focused.classList.contains('is-hidden')) closeWin(focused);
  });

  function makeDraggable(win, handle) {
    let startX = 0, startY = 0, baseLeft = 0, baseTop = 0, dragging = false;

    handle.addEventListener('pointerdown', (e) => {
      if (isMobile()) return;
      if (e.target.closest('[data-action]')) return; // ignore traffic lights
      if (win.classList.contains('is-max')) return;  // no drag while maximized
      dragging = true;
      focusWin(win);
      const rect = win.getBoundingClientRect();
      const parent = win.offsetParent ? win.offsetParent.getBoundingClientRect() : { left: 0, top: 0 };
      baseLeft = rect.left - parent.left;
      baseTop = rect.top - parent.top;
      startX = e.clientX;
      startY = e.clientY;
      handle.setPointerCapture(e.pointerId);
      e.preventDefault();
    });

    handle.addEventListener('pointermove', (e) => {
      if (!dragging) return;
      let nx = baseLeft + (e.clientX - startX);
      let ny = baseTop + (e.clientY - startY);
      nx = Math.max(4, nx);
      ny = Math.max(0, ny);
      win.style.left = nx + 'px';
      win.style.top = ny + 'px';
    });

    const end = (e) => {
      if (!dragging) return;
      dragging = false;
      try { handle.releasePointerCapture(e.pointerId); } catch (err) {}
    };
    handle.addEventListener('pointerup', end);
    handle.addEventListener('pointercancel', end);
  }

  /* ---- Boot / power-on sequence ---- */
  (function boot() {
    const boot = document.getElementById('ph-boot');
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const ready = () => document.body.classList.add('ph-ready');

    if (!boot) { ready(); return; }

    if (reduce || sessionStorage.getItem('phBooted')) {
      boot.classList.add('is-done');
      setTimeout(() => boot.remove(), 400);
      ready();
      return;
    }

    const logEl = document.getElementById('ph-boot-log');
    const barEl = document.getElementById('ph-boot-bar');
    const lines = [
      'booting ztrunkOS...',
      '<span class="ok">[ ok ]</span> mounting /home/vasile',
      '<span class="ok">[ ok ]</span> loading experience.sh',
      '<span class="ok">[ ok ]</span> indexing projects/ (6 found)',
      '<span class="ok">[ ok ]</span> compiling skills.json',
      '<span class="ok">[ ok ]</span> starting window-manager',
      '<span class="ok">[ ok ]</span> welcome, Vasile Ovidiu Ichim <span class="cur">_</span>'
    ];
    let i = 0, done = false;

    function finish() {
      if (done) return;
      done = true;
      sessionStorage.setItem('phBooted', '1');
      if (barEl) barEl.style.width = '100%';
      boot.classList.add('is-done');
      setTimeout(() => boot.remove(), 650);
      ready();
    }

    function step() {
      if (done) return;
      if (i < lines.length) {
        logEl.innerHTML += (i ? '\n' : '') + lines[i];
        i += 1;
        if (barEl) barEl.style.width = Math.round((i / lines.length) * 100) + '%';
        setTimeout(step, 220 + Math.random() * 130);
      } else {
        setTimeout(finish, 420);
      }
    }
    setTimeout(step, 260);
    boot.addEventListener('click', finish);
    document.addEventListener('keydown', function onKey(e) {
      if (!done) { finish(); }
      document.removeEventListener('keydown', onKey);
    });
  })();

  /* ---- Cursor-following glow ---- */
  (function cursorGlow() {
    const glow = document.getElementById('ph-cursor-glow');
    if (!glow || !window.matchMedia('(pointer: fine)').matches) return;
    let x = 0, y = 0, ticking = false;
    document.addEventListener('mousemove', (e) => {
      x = e.clientX; y = e.clientY;
      glow.style.opacity = '1';
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        ticking = false;
        glow.style.transform = `translate3d(${x}px, ${y}px, 0) translate(-50%, -50%)`;
      });
    }, { passive: true });
    document.addEventListener('mouseleave', () => { glow.style.opacity = '0'; });
  })();

  /* ---- Escape also closes the start menu ---- */
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeStartMenu();
  });

  /* ---- Live clock ---- */
  const clock = document.getElementById('ph-clock');
  function tick() {
    if (!clock) return;
    const now = new Date();
    clock.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  tick();
  setInterval(tick, 15000);

  syncDock();
})();
