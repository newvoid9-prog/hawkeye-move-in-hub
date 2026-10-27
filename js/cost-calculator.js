// Yearly dorm cost calculator for dorm-costs.html. Prices are 2026-27 rates.
(function () {
  const form = document.getElementById("cost-calc");
  if (!form) return;

  const roomSelect = document.getElementById("calc-room");
  const mealSelect = document.getElementById("calc-meal");
  const output = document.getElementById("calc-out");
  const BLOCK_50 = "1750";
  const whole = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  const cents = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: 2 });
  const money = (amount) => (Number.isInteger(amount) ? whole : cents).format(amount);

  function update() {
    const roomOption = roomSelect.options[roomSelect.selectedIndex];
    const hasKitchen = roomOption.dataset.kitchen === "yes";
    const blockedPlan = mealSelect.value === BLOCK_50 && !hasKitchen;
    const total = Number(roomSelect.value) + Number(mealSelect.value);

    const totalEl = document.createElement("span");
    totalEl.className = "calc-total";
    totalEl.textContent = money(total);

    const detailEl = document.createElement("span");
    detailEl.className = "calc-detail";
    detailEl.textContent = blockedPlan
      ? "Block 50 is only available in rooms with a university kitchen. Pick another plan for this room."
      : `${money(total / 2)} per semester. Room includes $120 in laundry dollars.`;

    output.replaceChildren(totalEl, detailEl);
  }

  form.addEventListener("change", update);
  form.addEventListener("submit", (event) => event.preventDefault());
  update();
})();
