(function () {
  const root = document.getElementById("systems-diagram");
  if (!root) return;

  const caption = root.querySelector("[data-diagram-caption]");
  const nodes = root.querySelectorAll("[data-diagram-node]");
  const defaultCaption =
    caption?.dataset.default ||
    "Hover a stage to see how the platform fits together.";

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
    node.addEventListener("mouseenter", () => setActive(node));
    node.addEventListener("focus", () => setActive(node));
    node.addEventListener("mouseleave", () => setActive(null));
    node.addEventListener("blur", () => setActive(null));
  });

  root.addEventListener("mouseleave", () => setActive(null));
})();
