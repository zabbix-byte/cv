/* PostHog-style desktop window manager */
(function () {
  'use strict';

  const mobileMQ = window.matchMedia('(max-width: 820px)');
  const isMobile = () => mobileMQ.matches;

  let zCounter = 20;

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
    document.querySelectorAll('.ph-dock-item[data-dock]').forEach((item) => {
      const win = getWin(item.getAttribute('data-dock'));
      const visible = win && !win.classList.contains('is-hidden');
      item.classList.toggle('is-active', !!visible);
    });
  }

  /* ---- Open triggers (icons, menu items, dock) ---- */
  document.querySelectorAll('[data-open]').forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      openWin(el.getAttribute('data-open'));
    });
  });

  document.querySelectorAll('.ph-dock-item[data-dock]').forEach((item) => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const id = item.getAttribute('data-dock');
      const win = getWin(id);
      if (win && !win.classList.contains('is-hidden') && !isMobile()) {
        // already open -> just bring to front
        focusWin(win);
      } else {
        openWin(id);
      }
    });
  });

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
    if (handle) makeDraggable(win, handle);
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
