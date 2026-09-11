(function () {
  const canvas = document.getElementById("ambient-blob");
  if (!canvas || !canvas.getContext) return;

  const ctx = canvas.getContext("2d");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const STEPS = 128;

  const mouse = { x: 0.5, y: 0.5, has: false };
  const blob = { x: 0.72, y: 0.38 };
  const rest = { x: 0.72, y: 0.38 };
  let width = 0;
  let height = 0;
  let dpr = 1;
  let raf = 0;
  let start = performance.now();

  function cssColor(name, fallback) {
    const value = getComputedStyle(document.documentElement)
      .getPropertyValue(name)
      .trim();
    return value || fallback;
  }

  function palette() {
    return {
      core: cssColor("--blob-core", "rgba(232, 246, 255, 0.18)"),
      mid: cssColor("--blob-mid", "rgba(86, 178, 255, 0.42)"),
      rim: cssColor("--blob-rim", "rgba(38, 142, 245, 0.72)"),
      edge: cssColor("--blob-edge", "rgba(18, 96, 210, 0.88)"),
      stroke: cssColor("--blob-stroke", "rgba(16, 32, 64, 0.55)"),
      spec: cssColor("--blob-spec", "rgba(255, 255, 255, 0.55)"),
    };
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function baseRadius() {
    return Math.min(width, height) * (width < 720 ? 0.42 : 0.48);
  }

  function radiusAt(theta, t, cx, cy, variant) {
    const pulse = reduced ? 1 : 1 + 0.055 * Math.sin(t * 1.45);
    const morph =
      0.13 * Math.sin(2 * theta + t * 0.62) +
      0.09 * Math.sin(3 * theta - t * 0.41) +
      0.055 * Math.sin(4 * theta + t * 0.88) +
      0.04 * Math.sin(5 * theta + t * 0.27) +
      0.03 * Math.cos(7 * theta - t * 0.53);

    let bulge = 0;
    if (mouse.has && !reduced) {
      const dx = mouse.x * width - cx;
      const dy = mouse.y * height - cy;
      const dist = Math.hypot(dx, dy) || 1;
      const reach = baseRadius() * 2.2;
      const pull = Math.max(0, 1 - dist / reach);
      const angle = Math.atan2(dy, dx);
      const facing = Math.max(0, Math.cos(theta - angle));
      bulge = pull * 0.22 * Math.pow(facing, 2.4);
    }

    const extra = variant === "stroke" ? 0.018 * Math.sin(theta * 3 - t * 0.7) : 0;
    return baseRadius() * pulse * (1 + morph + bulge + extra);
  }

  function buildPath(t, cx, cy, variant) {
    const path = new Path2D();
    for (let i = 0; i <= STEPS; i++) {
      const theta = (i / STEPS) * Math.PI * 2;
      const r = radiusAt(theta, t, cx, cy, variant);
      const x = cx + Math.cos(theta) * r;
      const y = cy + Math.sin(theta) * r;
      if (i === 0) path.moveTo(x, y);
      else path.lineTo(x, y);
    }
    path.closePath();
    return path;
  }

  function draw(now) {
    const t = (now - start) / 1000;
    const colors = palette();

    if (mouse.has && !reduced) {
      const lean = 0.16;
      blob.x += (rest.x + (mouse.x - rest.x) * lean - blob.x) * 0.055;
      blob.y += (rest.y + (mouse.y - rest.y) * lean - blob.y) * 0.055;
    } else {
      blob.x += (rest.x - blob.x) * 0.04;
      blob.y += (rest.y - blob.y) * 0.04;
    }

    const cx = blob.x * width;
    const cy = blob.y * height;
    const r = baseRadius();

    ctx.clearRect(0, 0, width, height);

    const fillPath = buildPath(t, cx, cy, "fill");
    const strokePath = buildPath(t + 0.35, cx + r * 0.012, cy + r * 0.018, "stroke");

    const gx = cx - r * 0.18;
    const gy = cy - r * 0.22;
    const grad = ctx.createRadialGradient(gx, gy, r * 0.05, cx, cy, r * 1.08);
    grad.addColorStop(0, colors.core);
    grad.addColorStop(0.38, colors.mid);
    grad.addColorStop(0.78, colors.rim);
    grad.addColorStop(1, colors.edge);

    ctx.fillStyle = grad;
    ctx.fill(fillPath);

    ctx.save();
    ctx.clip(fillPath);
    const shine = ctx.createRadialGradient(
      cx - r * 0.28,
      cy - r * 0.32,
      0,
      cx - r * 0.18,
      cy - r * 0.22,
      r * 0.55
    );
    shine.addColorStop(0, colors.spec);
    shine.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = shine;
    ctx.fillRect(cx - r, cy - r, r * 2, r * 2);
    ctx.restore();

    ctx.strokeStyle = colors.stroke;
    ctx.lineWidth = Math.max(1.4, r * 0.012);
    ctx.lineJoin = "round";
    ctx.stroke(strokePath);

    if (!reduced) raf = requestAnimationFrame(draw);
  }

  function onPointer(event) {
    mouse.x = event.clientX / width;
    mouse.y = event.clientY / height;
    mouse.has = true;
  }

  function onLeave() {
    mouse.has = false;
  }

  resize();
  draw(performance.now());

  window.addEventListener("resize", () => {
    resize();
    if (reduced) draw(performance.now());
  });
  window.addEventListener("pointermove", onPointer, { passive: true });
  window.addEventListener("pointerleave", onLeave);
  window.addEventListener("blur", onLeave);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      cancelAnimationFrame(raf);
    } else if (!reduced) {
      start = performance.now() - ((performance.now() - start) % 100000);
      raf = requestAnimationFrame(draw);
    }
  });
})();
