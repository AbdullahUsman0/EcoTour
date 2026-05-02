const budget = document.getElementById("budget");
const budgetValue = document.getElementById("budgetValue");
const planBtn = document.getElementById("planBtn");
const planResult = document.getElementById("planResult");
const language = document.getElementById("language");
const chatLog = document.getElementById("chatLog");

budget.addEventListener("input", () => {
  budgetValue.textContent = budget.value;
});

function addChatLine(role, text) {
  const row = document.createElement("div");
  row.textContent = `${role}: ${text}`;
  chatLog.appendChild(row);
  chatLog.scrollTop = chatLog.scrollHeight;
}

planBtn.addEventListener("click", async () => {
  const payload = {
    origin: document.getElementById("origin").value,
    destination: document.getElementById("destination").value,
    travelers: Number(document.getElementById("travelers").value),
    budget: Number(budget.value),
    language: language.value,
  };
  const res = await fetch("/api/plan-trip", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    planResult.textContent = data.detail || "Could not generate trip plan.";
    return;
  }
  planResult.textContent =
    `Route: ${data.route}\n` +
    `Distance: ${data.distance_km} km\n` +
    `Estimated cost: PKR ${Math.round(data.estimated_cost)}\n` +
    `Budget fit: ${data.budget_fit}\n` +
    `Plan:\n- ${data.plan.join("\n- ")}`;
});

document.getElementById("chatBtn").addEventListener("click", async () => {
  const chatInput = document.getElementById("chatInput");
  const message = chatInput.value.trim();
  if (!message) return;
  addChatLine("You", message);
  chatInput.value = "";
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language: language.value }),
  });
  const data = await res.json();
  addChatLine("EcoTour AI", data.response || "No response");
});

document.getElementById("voiceBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("voiceInput");
  if (!fileInput.files.length) return;
  const form = new FormData();
  form.append("file", fileInput.files[0]);
  const res = await fetch("/api/voice/transcribe", {
    method: "POST",
    body: form,
  });
  const data = await res.json();
  if (!res.ok) {
    addChatLine("System", data.detail || "Voice transcription failed");
    return;
  }
  addChatLine("Voice", data.text);
});

document.getElementById("crisisBtn").addEventListener("click", async () => {
  const message = document.getElementById("crisisInput").value.trim();
  if (!message) return;
  const res = await fetch("/api/crisis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language: language.value }),
  });
  const data = await res.json();
  document.getElementById("crisisResult").textContent =
    `Severity: ${data.severity}\nAdvice: ${data.advice}\nHelpline: ${data.helpline}`;
});

async function loadEmergency() {
  const box = document.getElementById("emergencyList");
  const res = await fetch("/api/emergency");
  const data = await res.json();
  box.innerHTML = "";
  for (const item of data.contacts || []) {
    const row = document.createElement("div");
    row.className = "emergency-item";
    row.innerHTML = `<strong>${item.title}</strong> - ${item.number}<br/><a href="tel:${item.number}">Call now</a>`;
    box.appendChild(row);
  }
}

loadEmergency();
