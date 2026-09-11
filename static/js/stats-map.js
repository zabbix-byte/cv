(function () {
  const el = document.getElementById("stats-map");
  const dataNode = document.getElementById("stats-map-data");
  if (!el || !dataNode || typeof maplibregl === "undefined" || typeof maplibregl.Map !== "function") return;

  const points = JSON.parse(dataNode.textContent || "[]").filter(
    (p) => Number.isFinite(p.lat) && Number.isFinite(p.lon)
  );
  const darkQuery = window.matchMedia("(prefers-color-scheme: dark)");
  const fg = cssVar("--fg") || (darkQuery.matches ? "#e8e8e8" : "#171717");
  const bg = cssVar("--bg") || (darkQuery.matches ? "#1a1a1a" : "#ffffff");
  let autoTilt = false;

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function styleUrl() {
    return darkQuery.matches
      ? "https://tiles.openfreemap.org/styles/dark"
      : "https://tiles.openfreemap.org/styles/positron";
  }

  function enhanceStyle(nextStyle) {
    const next = {
      ...nextStyle,
      sources: { ...nextStyle.sources },
      layers: nextStyle.layers.map((layer) => ({
        ...layer,
        paint: { ...(layer.paint || {}) },
        layout: { ...(layer.layout || {}) },
      })),
    };
    next.projection = { type: "globe" };
    next.sky = { "atmosphere-blend": 0 };
    next.sources.mapterhorn = {
      type: "raster-dem",
      url: "https://tiles.mapterhorn.com/tilejson.json",
      tileSize: 512,
      encoding: "terrarium",
    };
    next.layers = next.layers.map((layer) => {
      if (layer.id === "natural_earth") layer.layout.visibility = "none";
      if (layer.id === "boundary_3") layer.minzoom = 3;
      if (layer.id === "label_state") layer.maxzoom = 12;
      if (layer.id === "background") {
        layer.paint["background-color"] = darkQuery.matches ? "#2a2a2a" : "#ebe4d6";
      }
      if (layer.id === "water") {
        layer.paint["fill-color"] = darkQuery.matches ? "#1a2a36" : "#8fb7cc";
      }
      if (layer.id === "boundary_2") {
        layer.paint["line-color"] = darkQuery.matches ? "#a3a3a3" : "#7d776f";
        layer.paint["line-width"] = [
          "interpolate",
          ["linear"],
          ["zoom"],
          0,
          0.7,
          4,
          1.15,
          8,
          1.6,
        ];
      }
      return layer;
    });
    const waterAt = next.layers.findIndex((layer) => layer.id === "water");
    const shade = {
      id: "terrain-shade",
      type: "hillshade",
      source: "mapterhorn",
      minzoom: 6,
      paint: {
        "hillshade-exaggeration": 0.42,
        "hillshade-shadow-color": darkQuery.matches ? "#0b0b0b" : "#64748b",
        "hillshade-highlight-color": "#ffffff",
        "hillshade-illumination-anchor": "viewport",
      },
    };
    if (waterAt >= 0) next.layers.splice(waterAt + 1, 0, shade);
    else next.layers.unshift(shade);
    return next;
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  const map = new maplibregl.Map({
    container: el,
    style: styleUrl(),
    center: [0, 20],
    zoom: 1.85,
    pitch: 0,
    minZoom: 0.7,
    maxZoom: 18,
    maxPitch: 80,
    attributionControl: { compact: true },
    maplibreLogo: false,
    canvasContextAttributes: { alpha: true, antialias: true },
    transformStyle: (_prev, next) => enhanceStyle(next),
  });

  map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "bottom-right");
  map.touchZoomRotate.enableRotation();

  function addBuildings() {
    const layers = map.getStyle().layers || [];
    if (layers.some((layer) => layer.type === "fill-extrusion")) return;
    if (!map.getSource("openmaptiles")) return;
    const before = layers.find(
      (layer) => layer.type === "symbol" && layer.layout && layer.layout["text-field"]
    );
    map.addLayer(
      {
        id: "stats-buildings-3d",
        source: "openmaptiles",
        "source-layer": "building",
        type: "fill-extrusion",
        minzoom: 14,
        filter: ["!=", ["get", "hide_3d"], true],
        paint: {
          "fill-extrusion-color": darkQuery.matches ? "#3a3a3a" : "#d4d4d4",
          "fill-extrusion-height": ["coalesce", ["get", "render_height"], 8],
          "fill-extrusion-base": ["coalesce", ["get", "render_min_height"], 0],
          "fill-extrusion-opacity": 0.85,
        },
      },
      before && before.id
    );
  }

  function addVisitors() {
    if (map.getSource("visitors")) {
      map.getSource("visitors").setData(visitorGeo());
      return;
    }
    map.addSource("visitors", {
      type: "geojson",
      data: visitorGeo(),
      cluster: true,
      clusterMaxZoom: 12,
      clusterRadius: 42,
    });
    map.addLayer({
      id: "visitors-heat",
      type: "circle",
      source: "visitors",
      filter: ["!", ["has", "point_count"]],
      paint: {
        "circle-radius": 18,
        "circle-color": fg,
        "circle-opacity": 0.12,
        "circle-blur": 0.85,
      },
    });
    map.addLayer({
      id: "visitors-clusters",
      type: "circle",
      source: "visitors",
      filter: ["has", "point_count"],
      paint: {
        "circle-color": fg,
        "circle-stroke-color": bg,
        "circle-stroke-width": 2,
        "circle-radius": ["step", ["get", "point_count"], 14, 4, 18, 10, 24],
      },
    });
    map.addLayer({
      id: "visitors-cluster-count",
      type: "symbol",
      source: "visitors",
      filter: ["has", "point_count"],
      layout: {
        "text-field": ["to-string", ["get", "point_count"]],
        "text-size": 12,
        "text-font": ["Noto Sans Bold"],
      },
      paint: { "text-color": bg },
    });
    map.addLayer({
      id: "visitors-point",
      type: "circle",
      source: "visitors",
      filter: ["!", ["has", "point_count"]],
      paint: {
        "circle-color": fg,
        "circle-stroke-color": bg,
        "circle-stroke-width": 2,
        "circle-radius": ["interpolate", ["linear"], ["get", "visitors"], 1, 5.5, 8, 9],
      },
    });
  }

  function visitorGeo() {
    return {
      type: "FeatureCollection",
      features: points.map((point) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [point.lon, point.lat] },
        properties: {
          city: point.city || "",
          country: point.country || "",
          visitors: point.visitors || 1,
          time: point.time || "",
        },
      })),
    };
  }

  function popupHtml(props) {
    const place = [props.city, props.country].filter(Boolean).join(", ") || "Unknown";
    const n = Number(props.visitors) || 1;
    return `<div class="stats-map-tip"><strong>${escapeHtml(place)}</strong><span>${n} visitor${n === 1 ? "" : "s"} · ${escapeHtml(props.time)}</span></div>`;
  }

  function syncCamera() {
    const zoom = map.getZoom();
    if (zoom >= 5.4) {
      if (!map.getTerrain()) {
        map.setTerrain({ source: "mapterhorn", exaggeration: 1.2 });
      }
    } else if (map.getTerrain()) {
      map.setTerrain(null);
    }
    if (zoom >= 6.8 && !autoTilt && map.getPitch() < 8) {
      autoTilt = true;
      map.setPitch(48);
    }
    if (zoom < 4.2 && map.getPitch() > 8) {
      autoTilt = false;
      map.setPitch(0);
    }
  }

  map.on("style.load", () => {
    map.setProjection({ type: "globe" });
    map.setSky({ "atmosphere-blend": 0 });
    addBuildings();
    addVisitors();
    if (map.getLayer("boundary_3")) {
      map.setPaintProperty("boundary_3", "line-color", darkQuery.matches ? "#8a8a8a" : "#9aa3ad");
      map.setPaintProperty("boundary_3", "line-width", [
        "interpolate",
        ["linear"],
        ["zoom"],
        3,
        0.4,
        8,
        1.1,
        12,
        1.8,
      ]);
    }
    syncCamera();
  });

  map.on("zoomend", syncCamera);
  map.on("pitchend", () => {
    if (map.getPitch() > 8) autoTilt = true;
  });

  map.on("mouseenter", "visitors-clusters", () => {
    map.getCanvas().style.cursor = "pointer";
  });
  map.on("mouseleave", "visitors-clusters", () => {
    map.getCanvas().style.cursor = "";
  });
  map.on("mouseenter", "visitors-point", () => {
    map.getCanvas().style.cursor = "pointer";
  });
  map.on("mouseleave", "visitors-point", () => {
    map.getCanvas().style.cursor = "";
  });

  map.on("click", "visitors-clusters", (event) => {
    const feature = event.features && event.features[0];
    if (!feature) return;
    map.getSource("visitors").getClusterExpansionZoom(feature.properties.cluster_id, (err, zoom) => {
      if (err) return;
      map.easeTo({
        center: feature.geometry.coordinates,
        zoom,
        pitch: Math.max(map.getPitch(), 40),
        duration: 700,
      });
    });
  });

  map.on("click", "visitors-point", (event) => {
    const feature = event.features && event.features[0];
    if (!feature) return;
    new maplibregl.Popup({ closeButton: false, offset: 14, className: "stats-map-popup" })
      .setLngLat(feature.geometry.coordinates)
      .setHTML(popupHtml(feature.properties))
      .addTo(map);
  });

  darkQuery.addEventListener("change", () => {
    map.setStyle(styleUrl(), { transformStyle: (_prev, next) => enhanceStyle(next) });
  });

  const resize = () => map.resize();
  window.addEventListener("resize", resize);
})();
