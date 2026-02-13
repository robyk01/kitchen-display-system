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

let lastSignature = null;
const POLL_MS = 5000;

async function pollOrders(){
  try {
    const response = await fetch("/orders/poll", { cache: "no-store" });
    if (!response.ok) return;

    const data = await response.json();
    if (!data.signature) return;

    if (lastSignature === null){
      lastSignature = data.signature;
      return;
    }

    if (data.signature !== lastSignature){
      window.location.reload();
    }
  } catch (e) {

  }
}

pollOrders();
setInterval(pollOrders, POLL_MS);
