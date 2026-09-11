(function () {
  const ORDER = [
    "/",
    "/experience",
    "/projects",
    "/research",
    "/press",
    "/skills",
    "/education",
  ];

  function pathOf(url) {
    try {
      const path = new URL(url, location.origin).pathname.replace(/\/+$/, "");
      return path || "/";
    } catch {
      return "/";
    }
  }

  function direction(fromUrl, toUrl) {
    const from = ORDER.indexOf(pathOf(fromUrl));
    const to = ORDER.indexOf(pathOf(toUrl));
    if (from === -1 || to === -1) return "book-forward";
    return to < from ? "book-back" : "book-forward";
  }

  function isDownload(url) {
    return pathOf(url) === "/download-cv";
  }

  window.addEventListener("pageswap", (event) => {
    if (!event.viewTransition) return;
    const to = event.activation?.entry?.url;
    const from = event.activation?.from?.url || location.href;
    if (!to || isDownload(to)) {
      event.viewTransition.skipTransition();
      return;
    }
    const type = direction(from, to);
    sessionStorage.setItem("book-turn", type);
    event.viewTransition.types.add(type);
  });

  window.addEventListener("pagereveal", (event) => {
    if (!event.viewTransition) return;
    const type = sessionStorage.getItem("book-turn") || "book-forward";
    event.viewTransition.types.add(type);
  });
})();
