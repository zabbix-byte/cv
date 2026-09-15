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
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let navigating = false;
  let currentHref = location.href;

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

  function isInternal(url) {
    return url.origin === location.origin
      && pathOf(url.href) !== "/download-cv"
      && pathOf(url.href) !== "/statistics"
      && pathOf(url.href) !== "/github"
      && !url.pathname.startsWith("/api/")
      && !url.pathname.endsWith(".pdf");
  }

  async function load(url) {
    const response = await fetch(url.href, { headers: { "X-Requested-With": "page-turn" } });
    if (!response.ok) throw new Error("fetch failed");
    const html = await response.text();
    return new DOMParser().parseFromString(html, "text/html");
  }

  function apply(doc, url) {
    const nextMain = doc.getElementById("main");
    const current = document.getElementById("main");
    if (!nextMain || !current) throw new Error("missing main");
    current.replaceWith(document.importNode(nextMain, true));
    document.title = doc.title;
    window.scrollTo(0, 0);
    if (url.hash) {
      const target = document.getElementById(decodeURIComponent(url.hash.slice(1)));
      if (target) target.scrollIntoView();
    }
    if (typeof window.initSystemsDiagrams === "function") {
      window.initSystemsDiagrams();
    }
    window.dispatchEvent(new CustomEvent("page-turn"));
  }

  function startTurn(run, dir) {
    try {
      return document.startViewTransition({ update: run, types: [dir] });
    } catch {
      return document.startViewTransition(run);
    }
  }

  async function turnTo(url, historyMode) {
    if (navigating) return;
    if (historyMode !== "none" && pathOf(url.href) === pathOf(currentHref) && url.hash === new URL(currentHref).hash) {
      return;
    }
    navigating = true;
    const dir = direction(currentHref, url.href);
    document.documentElement.classList.toggle("book-back", dir === "book-back");

    try {
      const doc = await load(url);
      const run = () => {
        apply(doc, url);
        currentHref = url.href;
        if (historyMode === "push") history.pushState({ pageTurn: true }, "", url.href);
      };

      if (reduced || typeof document.startViewTransition !== "function") {
        run();
      } else {
        const transition = startTurn(run, dir);
        await transition.finished;
      }
    } catch {
      location.href = url.href;
      return;
    } finally {
      document.documentElement.classList.remove("book-back");
      navigating = false;
    }
  }

  document.addEventListener("click", (event) => {
    if (event.defaultPrevented || event.button !== 0) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest("a[href]");
    if (!link || link.target === "_blank" || link.hasAttribute("download")) return;
    const url = new URL(link.href, location.href);
    if (!isInternal(url)) return;
    if (url.hash && pathOf(url.href) === pathOf(location.href)) return;
    event.preventDefault();
    turnTo(url, "push");
  });

  window.addEventListener("popstate", () => {
    turnTo(new URL(location.href), "none");
  });
})();
