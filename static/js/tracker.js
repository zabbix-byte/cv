(function () {
  const SKIP = ["/statistics", "/github", "/api/track", "/download-cv"];
  const KEY = "ztrunk-sid";

  function sid() {
    try {
      let value = sessionStorage.getItem(KEY);
      if (!value) {
        value = (crypto.randomUUID && crypto.randomUUID()) || String(Date.now()) + Math.random();
        sessionStorage.setItem(KEY, value);
      }
      return value;
    } catch {
      return "anon";
    }
  }

  function pathOf() {
    return location.pathname || "/";
  }

  function ignored(path) {
    return SKIP.some((prefix) => path.startsWith(prefix));
  }

  function utm() {
    const query = new URLSearchParams(location.search);
    return {
      utm_source: query.get("utm_source") || "",
      utm_medium: query.get("utm_medium") || "",
      utm_campaign: query.get("utm_campaign") || "",
    };
  }

  function hints() {
    const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection || {};
    let tz = "";
    try {
      tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    } catch {}
    const uaData = navigator.userAgentData;
    return {
      language: navigator.language || "",
      tz,
      screen: screen.width && screen.height ? `${screen.width}x${screen.height}` : "",
      viewport: `${window.innerWidth}x${window.innerHeight}`,
      dpr: window.devicePixelRatio || 1,
      cores: navigator.hardwareConcurrency || null,
      memory: navigator.deviceMemory || null,
      platform: (uaData && uaData.platform) || navigator.platform || "",
      color_scheme: matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
      conn: conn.effectiveType || "",
      downlink: conn.downlink || null,
      touch: navigator.maxTouchPoints > 0,
      ...utm(),
    };
  }

  function post(body) {
    const payload = JSON.stringify(body);
    if (navigator.sendBeacon && body.action === "ping") {
      const blob = new Blob([payload], { type: "application/json" });
      navigator.sendBeacon("/api/track/", blob);
      return Promise.resolve();
    }
    return fetch("/api/track/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload,
      keepalive: true,
    }).then((res) => res.json()).catch(() => ({}));
  }

  let viewId = null;
  let started = Date.now();
  let timer = 0;

  function seconds() {
    return Math.max(0, Math.round((Date.now() - started) / 1000));
  }

  function ping() {
    if (!viewId) return;
    post({ action: "ping", sid: sid(), id: viewId, seconds: seconds() });
  }

  function start() {
    const path = pathOf();
    if (ignored(path)) return;
    ping();
    started = Date.now();
    viewId = null;
    post({
      action: "start",
      sid: sid(),
      path,
      title: document.title,
      referrer: document.referrer || "",
      ...hints(),
    }).then((data) => {
      if (data && data.id) viewId = data.id;
    });
  }

  start();
  timer = window.setInterval(ping, 15000);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) ping();
  });
  window.addEventListener("pagehide", ping);
  window.addEventListener("page-turn", start);
})();
