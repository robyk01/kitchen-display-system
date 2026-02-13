document.querySelectorAll("tr.order-row-link[data-href]").forEach((row) => {
  row.addEventListener("click", (event) => {
    if (event.target.closest("a, button, input, select, textarea, label")) return;
    window.location.href = row.dataset.href;
  });
});

document.querySelectorAll(".order-card-link[data-href]").forEach((card) => {
  card.addEventListener("click", (event) => {
    if (event.target.closest("a, button, input, select, textarea, label")) return;
    window.location.href = card.dataset.href;
  });
});
