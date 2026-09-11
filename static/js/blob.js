(function () {
  const canvas = document.getElementById("ambient-blob");
  if (!canvas || !canvas.getContext) return;

  const ctx = canvas.getContext("2d");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const STEPS = 128;
  const GRAIN = 192;
  const blobs = [
    { x: 0.92, y: 0.1, scale: 1, phase: 0, pulse: 1.45 },
    { x: 0.08, y: 0.9, scale: 0.86, phase: 2.1, pulse: 1.18 },
    { x: 0.93, y: 0.88, scale: 0.74, phase: 4.4, pulse: 1.62 },
  ];
  const mouse = { x: 0, y: 0, has: false };

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

  function unitRadius() {
    return Math.min(width, height) * (width < 720 ? 0.16 : 0.18);
  }

  function radiusAt(theta, t, blob, variant, inside) {
    const pulse = reduced ? 1 : 1 + 0.045 * Math.sin(t * blob.pulse + blob.phase);
    const p = t + blob.phase;
    const morph =
      0.13 * Math.sin(2 * theta + p * 0.62) +
      0.09 * Math.sin(3 * theta - p * 0.41) +
      0.055 * Math.sin(4 * theta + p * 0.88) +
      0.04 * Math.sin(5 * theta + p * 0.27) +
      0.03 * Math.cos(7 * theta - p * 0.53);
    const extra = variant === "stroke" ? 0.018 * Math.sin(theta * 3 - p * 0.7) : 0;

    let bulge = 0;
    if (inside && !reduced) {
      const cx = blob.x * width;
      const cy = blob.y * height;
      const angle = Math.atan2(mouse.y - cy, mouse.x - cx);
      const facing = Math.max(0, Math.cos(theta - angle));
      bulge = 0.2 * Math.pow(facing, 2.4);
    }

    return unitRadius() * blob.scale * pulse * (1 + morph + bulge + extra);
  }

  function isInside(blob, t) {
    if (!mouse.has) return false;
    const cx = blob.x * width;
    const cy = blob.y * height;
    const dx = mouse.x - cx;
    const dy = mouse.y - cy;
    const dist = Math.hypot(dx, dy);
    const theta = Math.atan2(dy, dx);
    return dist <= radiusAt(theta, t, blob, "fill", false);
  }

  function buildPath(t, cx, cy, blob, variant, inside) {
    const path = new Path2D();
    for (let i = 0; i <= STEPS; i++) {
      const theta = (i / STEPS) * Math.PI * 2;
      const r = radiusAt(theta, t, blob, variant, inside);
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

  function drawBlob(t, blob, colors) {
    const cx = blob.x * width;
    const cy = blob.y * height;
    const r = unitRadius() * blob.scale;
    const inside = isInside(blob, t);
    const fillPath = buildPath(t, cx, cy, blob, "fill", inside);
    const strokePath = buildPath(
      t + 0.35,
      cx + r * 0.012,
      cy + r * 0.018,
      blob,
      "stroke",
      inside
    );

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
    const drift = blob.phase * 12;

    ctx.save();
    ctx.clip(fillPath);
    ctx.imageSmoothingEnabled = false;
    ctx.globalCompositeOperation = "multiply";
    ctx.globalAlpha = 0.28;
    tileGrain(grainCoarse, 4.5, t * 6 + drift, t * 4, bounds);
    ctx.globalAlpha = 0.4;
    tileGrain(grainFine, 1.15, -t * 11 + drift, t * 9, bounds);
    ctx.globalCompositeOperation = "overlay";
    ctx.globalAlpha = 0.22;
    tileGrain(grainFine, 0.7, t * 3, -t * 5 + drift, bounds);

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
  }

  function draw(now) {
    const t = (now - start) / 1000;
    const colors = palette();
    ctx.clearRect(0, 0, width, height);
    blobs.forEach((blob) => drawBlob(t, blob, colors));
    if (!reduced) raf = requestAnimationFrame(draw);
  }

  resize();
  draw(performance.now());

  window.addEventListener("pointermove", (event) => {
    mouse.x = event.clientX;
    mouse.y = event.clientY;
    mouse.has = true;
  }, { passive: true });
  window.addEventListener("pointerleave", () => {
    mouse.has = false;
  });
  window.addEventListener("resize", () => {
    resize();
    if (reduced) draw(performance.now());
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      cancelAnimationFrame(raf);
    } else if (!reduced) {
      start = performance.now() - ((performance.now() - start) % 100000);
      raf = requestAnimationFrame(draw);
    }
  });
})();
