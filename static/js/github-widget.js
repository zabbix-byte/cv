(function () {
  const button = document.getElementById("embed-copy");
  const field = document.getElementById("embed-code");
  if (!button || !field) return;

  button.addEventListener("click", async () => {
    field.select();
    try {
      await navigator.clipboard.writeText(field.value);
      button.textContent = "Copied";
    } catch {
      document.execCommand("copy");
      button.textContent = "Copied";
    }
    window.setTimeout(() => {
      button.textContent = "Copy markdown";
    }, 1600);
  });
})();
