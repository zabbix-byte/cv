(function () {
  const el = document.getElementById("stats-map");
  const dataNode = document.getElementById("stats-map-data");
  if (!el || !dataNode || typeof Globe !== "function") return;

  const points = JSON.parse(dataNode.textContent || "[]").filter(
    (p) => Number.isFinite(p.lat) && Number.isFinite(p.lon)
  );

  const globe = Globe()(el)
    .width(el.clientWidth)
    .height(el.clientHeight)
    .backgroundColor("rgba(0,0,0,0)")
    .globeImageUrl("https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-blue-marble.jpg")
    .bumpImageUrl("https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-topology.png")
    .atmosphereColor("#9ec9ff")
    .atmosphereAltitude(0.18)
    .pointsData(points)
    .pointLat("lat")
    .pointLng("lon")
    .pointAltitude((d) => 0.04 + Math.min(0.18, (d.visitors || 1) * 0.03))
    .pointRadius((d) => 0.28 + Math.min(0.7, (d.visitors || 1) * 0.1))
    .pointColor(() => "#e8f4ff")
    .pointLabel((d) => {
      const place = [d.city, d.country].filter(Boolean).join(", ") || "Unknown";
      const n = d.visitors || 1;
      return `<div class="globe-tip"><strong>${place}</strong><br>${n} visitor${n === 1 ? "" : "s"} · ${d.time}</div>`;
    })
    .ringsData(points)
    .ringLat("lat")
    .ringLng("lon")
    .ringColor(() => (t) => `rgba(186, 220, 255, ${0.7 * (1 - t)})`)
    .ringMaxRadius(3.2)
    .ringPropagationSpeed(2.2)
    .ringRepeatPeriod(1600);

  const focus = points[0] || { lat: 41.39, lon: 2.17 };
  globe.pointOfView({ lat: focus.lat, lng: focus.lon, altitude: 2.15 }, 900);

  const controls = globe.controls();
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.45;
  controls.enableDamping = true;
  el.addEventListener("pointerdown", () => {
    controls.autoRotate = false;
  });

  const resize = () => {
    globe.width(el.clientWidth);
    globe.height(el.clientHeight);
  };
  window.addEventListener("resize", resize);
})();
