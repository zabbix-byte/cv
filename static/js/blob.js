(function () {
  const canvas = document.getElementById("ambient-blob");
  if (!canvas || !canvas.getContext) return;

  const ctx = canvas.getContext("2d");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const STEPS = 128;
  const GRAIN = 192;

  const mouse = { x: 0.5, y: 0.5, has: false };
  const blob = { x: 0.9, y: 0.14 };
  const rest = { x: 0.9, y: 0.14 };
  let width = 0;
  let height = 0;
  let dpr = 1;
  let raf = 0;
  let start = performance.now();
  const grainFine = makeGrain(GRAIN, 1);
  const grainCoarse = makeGrain(64, 2.2);

  function makeGrain(size, contrast) {
    const g = document.createElement("canvas");
    g.width = g.height = size;
    const gctx = g.getContext("2d");
    const img = gctx.createImageData(size, size);
    for (let i = 0; i < img.data.length; i += 4) {
      const n = Math.random();
      const speck = Math.random() > 0.9 ? Math.random() : 0;
      const v = Math.max(0, Math.min(255, (n * 180 + speck * 90) * contrast));
      img.data[i] = v;
      img.data[i + 1] = v * 0.98;
      img.data[i + 2] = v * 0.94;
      img.data[i + 3] = 40 + n * 140 + speck * 70;
    }
    gctx.putImageData(img, 0, 0);
    return g;
  }

  function cssColor(name, fallback) {
    const value = getComputedStyle(document.documentElement)
      .getPropertyValue(name)
      .trim();
    return value || fallback;
  }

  function palette() {
    return {
      core: cssColor("--blob-core", "rgba(250, 249, 246, 0.14)"),
      mid: cssColor("--blob-mid", "rgba(168, 176, 186, 0.16)"),
      rim: cssColor("--blob-rim", "rgba(122, 132, 144, 0.26)"),
      edge: cssColor("--blob-edge", "rgba(88, 96, 108, 0.32)"),
      stroke: cssColor("--blob-stroke", "rgba(62, 68, 78, 0.28)"),
      spec: cssColor("--blob-spec", "rgba(255, 255, 255, 0.18)"),
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
    return Math.min(width, height) * (width < 720 ? 0.16 : 0.18);
  }

  function radiusAt(theta, t, cx, cy, variant) {
    const pulse = reduced ? 1 : 1 + 0.045 * Math.sin(t * 1.45);
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
      const reach = baseRadius() * 2.4;
      const pull = Math.max(0, 1 - dist / reach);
      const angle = Math.atan2(dy, dx);
      const facing = Math.max(0, Math.cos(theta - angle));
      bulge = pull * 0.2 * Math.pow(facing, 2.4);
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

  function tileGrain(source, scale, ox, oy, bounds) {
    const tw = source.width * scale;
    const th = source.height * scale;
    const x0 = bounds.x - tw;
    const y0 = bounds.y - th;
    const x1 = bounds.x + bounds.w + tw;
    const y1 = bounds.y + bounds.h + th;
    for (let x = x0 + (ox % tw) - tw; x < x1; x += tw) {
      for (let y = y0 + (oy % th) - th; y < y1; y += th) {
        ctx.drawImage(source, x, y, tw, th);
      }
    }
  }

  function draw(now) {
    const t = (now - start) / 1000;
    const colors = palette();

    if (mouse.has && !reduced) {
      const lean = 0.1;
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

    const pad = r * 1.35;
    const bounds = { x: cx - pad, y: cy - pad, w: pad * 2, h: pad * 2 };

    ctx.save();
    ctx.clip(fillPath);
    ctx.imageSmoothingEnabled = false;
    ctx.globalCompositeOperation = "multiply";
    ctx.globalAlpha = 0.28;
    tileGrain(grainCoarse, 4.5, t * 6, t * 4, bounds);
    ctx.globalAlpha = 0.4;
    tileGrain(grainFine, 1.15, -t * 11, t * 9, bounds);
    ctx.globalCompositeOperation = "overlay";
    ctx.globalAlpha = 0.22;
    tileGrain(grainFine, 0.7, t * 3, -t * 5, bounds);

    ctx.globalCompositeOperation = "source-over";
    ctx.globalAlpha = 1;
    ctx.imageSmoothingEnabled = true;
    const shine = ctx.createRadialGradient(
      cx - r * 0.28,
      cy - r * 0.32,
      0,
      cx - r * 0.18,
      cy - r * 0.22,
      r * 0.5
    );
    shine.addColorStop(0, colors.spec);
    shine.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = shine;
    ctx.fillRect(cx - r, cy - r, r * 2, r * 2);
    ctx.restore();

    ctx.strokeStyle = colors.stroke;
    ctx.lineWidth = Math.max(1.1, r * 0.014);
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
