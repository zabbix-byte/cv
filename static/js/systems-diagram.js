(function () {
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  document.querySelectorAll("[data-interactive-diagram]").forEach((root) => {
    const caption = root.querySelector("[data-diagram-caption]");
    const nodes = [...root.querySelectorAll("[data-diagram-node]")];
    const defaultCaption =
      caption?.dataset.default ||
      "Select a stage to follow the path.";

    function setActive(node) {
      nodes.forEach((n) => n.classList.remove("is-active"));
      if (node) {
        node.classList.add("is-active");
        if (caption) caption.textContent = node.dataset.detail || defaultCaption;
      } else if (caption) {
        caption.textContent = defaultCaption;
      }
    }

    nodes.forEach((node) => {
      if (finePointer) {
        node.addEventListener("mouseenter", () => setActive(node));
        node.addEventListener("focus", () => setActive(node));
        node.addEventListener("mouseleave", () => setActive(null));
        node.addEventListener("blur", () => setActive(null));
      } else {
        node.addEventListener("click", (e) => {
          e.preventDefault();
          const already = node.classList.contains("is-active");
          setActive(already ? null : node);
        });
      }
    });

    if (finePointer) {
      root.addEventListener("mouseleave", () => setActive(null));
    }
  });
})();
