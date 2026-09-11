(function () {
  const el = document.getElementById("stats-map");
  const dataNode = document.getElementById("stats-map-data");
  if (!el || !dataNode || typeof L === "undefined") return;

  const points = JSON.parse(dataNode.textContent || "[]");
  const dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const tiles = dark
    ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
    : "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

  const map = L.map(el, {
    scrollWheelZoom: false,
    zoomControl: true,
    attributionControl: true,
  });

  L.tileLayer(tiles, {
    attribution: "&copy; OpenStreetMap &copy; CARTO",
    subdomains: "abcd",
    maxZoom: 18,
  }).addTo(map);

  const ink = dark ? "#e8e8e8" : "#171717";
  const fill = dark ? "#7dd3fc" : "#334155";

  const markers = points.map((point) => {
    const marker = L.circleMarker([point.lat, point.lon], {
      radius: Math.min(16, 6 + point.visitors * 1.6),
      color: ink,
      weight: 1,
      fillColor: fill,
      fillOpacity: 0.55,
    });
    const place = [point.city, point.country].filter(Boolean).join(", ") || "Unknown";
    marker.bindPopup(
      `<strong>${place}</strong><br>${point.visitors} visitor${point.visitors === 1 ? "" : "s"} · ${point.time}`
    );
    return marker;
  });

  if (markers.length) {
    const group = L.featureGroup(markers).addTo(map);
    map.fitBounds(group.getBounds().pad(0.35), { maxZoom: 5 });
  } else {
    map.setView([20, 0], 2);
  }
})();
