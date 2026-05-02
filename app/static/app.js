const budget = document.getElementById("budget");
const budgetValue = document.getElementById("budgetValue");
const planBtn = document.getElementById("planBtn");
const planResult = document.getElementById("planResult");
const language = document.getElementById("language");
const chatLog = document.getElementById("chatLog");
const savePlanBtn = document.getElementById("savePlanBtn");
const chatSources = document.getElementById("chatSources");
const chatInput = document.getElementById("chatInput");
let lastAssistantReply = "";
let lastPlannedTrip = null;
let activeTab = "planner";
let mediaRecorder = null;
let recordedChunks = [];

// DOM Elements - Floating Widget
const assistantFab = document.getElementById("assistantFab");
const assistantWidget = document.getElementById("assistantWidget");
const assistantClose = document.getElementById("assistantClose");
const assistantWidgetLog = document.getElementById("assistantWidgetLog");
const assistantWidgetInput = document.getElementById("assistantWidgetInput");
const assistantWidgetSend = document.getElementById("assistantWidgetSend");
const chatBtn = document.getElementById("chatBtn");
const crisisBtn = document.getElementById("crisisBtn");

// ==================== Initialize ====================
document.addEventListener("DOMContentLoaded", () => {
  loadEmergency();
  loadSavedItineraries();
  loadTripInsights();
  setupEventListeners();
});

// ==================== Event Listeners Setup ====================
function setupEventListeners() {
  // Budget slider
  budget.addEventListener("input", () => {
    budgetValue.textContent = budget.value;
  });

  // Tab navigation
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`page-${btn.dataset.tab}`).classList.add("active");
      activeTab = btn.dataset.tab;
    });
  });

  // Plan button
  planBtn.addEventListener("click", generateTripPlan);

  // Save plan button
  savePlanBtn.addEventListener("click", saveItinerary);

  // Chat page - Send message
  chatBtn.addEventListener("click", sendMainChatMessage);
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMainChatMessage();
    }
  });

  // Voice features
  document.getElementById("speakLastBtn").addEventListener("click", speakLastReply);
  document.getElementById("voiceBtn").addEventListener("click", transcribeVoice);
  document.getElementById("recordVoiceBtn").addEventListener("click", recordVoice);

  // Crisis
  crisisBtn.addEventListener("click", getCrisisAdvice);

  // Floating widget
  assistantFab.addEventListener("click", () => {
    assistantWidget.classList.toggle("hidden");
  });
  assistantClose.addEventListener("click", () => {
    assistantWidget.classList.add("hidden");
  });
  assistantWidgetSend.addEventListener("click", sendWidgetMessage);
  assistantWidgetInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendWidgetMessage();
    }
  });
}

// ==================== Chat Message Display ====================
function addChatLine(role, text, isAi = false) {
  const row = document.createElement("div");
  row.className = `msg ${isAi ? "ai" : "user"}`;
  row.innerHTML = `<strong>${role}</strong><br/>${text.replace(/\n/g, "<br/>")}`;
  chatLog.appendChild(row);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function addWidgetLine(role, text, isAi = false) {
  const row = document.createElement("div");
  row.className = `msg ${isAi ? "ai" : "user"}`;
  row.innerHTML = `<strong>${role}</strong><br/>${text.replace(/\n/g, "<br/>")}`;
  assistantWidgetLog.appendChild(row);
  assistantWidgetLog.scrollTop = assistantWidgetLog.scrollHeight;
}

// ==================== Trip Planning ====================
async function generateTripPlan() {
  planBtn.disabled = true;
  planBtn.textContent = "🔄 Generating...";
  
  try {
    const payload = {
      origin: document.getElementById("origin").value,
      destination: document.getElementById("destination").value,
      travelers: Number(document.getElementById("travelers").value),
      budget: Number(budget.value),
      language: language.value,
      hotel_tier: document.getElementById("hotelTier").value,
      transport_mode: document.getElementById("transportMode").value,
      activity_pace: document.getElementById("activityPace").value,
      food_style: document.getElementById("foodStyle").value,
    };

    const res = await fetch("/api/plan-trip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      planResult.textContent = "❌ " + (data.detail || "Could not generate trip plan.");
      return;
    }

    lastPlannedTrip = data;
    const adviceBox = document.getElementById("plannerAdvice");
    const optionsBox = document.getElementById("tripOptions");

    planResult.textContent =
      `✈️ Route: ${data.route}\n` +
      `📏 Distance: ${data.distance_km} km (${data.distance_source})\n` +
      `💰 Estimated cost: PKR ${Math.round(data.estimated_cost)}\n` +
      `✓ Budget fit: ${data.budget_fit}\n` +
      `🌤️ Weather: ${data.weather_note}\n` +
      `🚗 Fare signal: ${data.fare_note}\n` +
      `📋 Plan:\n- ${data.plan.join("\n- ")}`;

    if ((data.hotel_suggestions || []).length) {
      planResult.textContent += `\n\n🏨 Hotel ideas:\n- ${data.hotel_suggestions.join("\n- ")}`;
    }

    adviceBox.textContent =
      `✅ Do now:\n- ${(data.do_now || []).join("\n- ")}\n\n` +
      `⚠️ Avoid now:\n- ${(data.avoid_now || []).join("\n- ")}`;

    optionsBox.innerHTML = "";
    (data.options || []).forEach((option) => {
      const card = document.createElement("div");
      card.className = "summary-card";
      card.innerHTML =
        `<strong>🏷️ ${option.title}</strong><br/>` +
        `Estimated: PKR ${Math.round(option.estimated_cost || 0)}<br/>` +
        `${(option.highlights || []).map((h) => `• ${h}`).join("<br/>")}`;
      optionsBox.appendChild(card);
    });

    // Show success notification
    addWidgetLine("System", `✨ Trip plan generated for ${data.route}!`, true);
  } catch (error) {
    planResult.textContent = "❌ Error: " + error.message;
    addWidgetLine("System", "Error generating plan: " + error.message, true);
  } finally {
    planBtn.disabled = false;
    planBtn.textContent = "🚀 Generate Plan";
  }
}

// ==================== Save Itinerary ====================
async function saveItinerary() {
  if (!lastPlannedTrip) {
    alert("⚠️ Please generate a plan first!");
    return;
  }

  savePlanBtn.disabled = true;
  savePlanBtn.textContent = "💾 Saving...";

  try {
    const payload = {
      traveler_name: document.getElementById("travelerName").value || "Guest Traveler",
      route: lastPlannedTrip.route,
      estimated_cost: Number(lastPlannedTrip.estimated_cost),
      budget_fit: lastPlannedTrip.budget_fit,
      plan: lastPlannedTrip.plan,
    };

    const res = await fetch("/api/itineraries", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const data = await res.json();
      alert("❌ " + (data.detail || "Failed to save itinerary."));
      return;
    }

    planResult.textContent += "\n\n✅ Successfully saved to itinerary list!";
    addWidgetLine("System", "✅ Itinerary saved successfully!", true);
    
    // Reload saved itineraries
    await loadSavedItineraries();
    await loadTripInsights();
  } catch (error) {
    alert("❌ Error saving: " + error.message);
    addWidgetLine("System", "Error saving itinerary: " + error.message, true);
  } finally {
    savePlanBtn.disabled = false;
    savePlanBtn.textContent = "💾 Save This Plan";
  }
}

// ==================== Chat Messages ====================
async function sendMainChatMessage() {
  const message = chatInput.value.trim();
  if (!message) return;

  addChatLine("You", message, false);
  chatInput.value = "";
  chatBtn.disabled = true;
  chatBtn.textContent = "⏳ Sending...";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        language: language.value,
        screen_context: `active_tab=${activeTab}; latest_plan=${(planResult.textContent || "").slice(0, 600)}`,
      }),
    });

    const data = await res.json();
    if (!res.ok) {
      addChatLine("System", "❌ Error: " + (data.detail || "No response"), true);
      return;
    }

    lastAssistantReply = data.response || "No response";
    addChatLine("🤖 EcoTour AI", lastAssistantReply, true);

    chatSources.textContent = (data.sources || []).length
      ? `📚 Sources: ${data.sources.join(", ")}`
      : "";

    // Also add to widget
    addWidgetLine("AI", lastAssistantReply, true);
  } catch (error) {
    addChatLine("System", "❌ Error: " + error.message, true);
  } finally {
    chatBtn.disabled = false;
    chatBtn.textContent = "Send";
  }
}

async function sendWidgetMessage() {
  const message = assistantWidgetInput.value.trim();
  if (!message) return;

  addWidgetLine("You", message, false);
  assistantWidgetInput.value = "";
  assistantWidgetSend.disabled = true;
  assistantWidgetSend.textContent = "⏳";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        language: language.value,
        screen_context: `active_tab=${activeTab}; latest_plan=${(planResult.textContent || "").slice(0, 600)}`,
      }),
    });

    const data = await res.json();
    if (!res.ok) {
      addWidgetLine("System", "❌ Error: " + (data.detail || "No response"), true);
      return;
    }

    lastAssistantReply = data.response || "No response";
    addWidgetLine("🤖 AI", lastAssistantReply, true);

    // Also add to main chat if on chat page
    if (activeTab === "chat") {
      addChatLine("🤖 EcoTour AI", lastAssistantReply, true);
    }
  } catch (error) {
    addWidgetLine("System", "❌ Error: " + error.message, true);
  } finally {
    assistantWidgetSend.disabled = false;
    assistantWidgetSend.textContent = "Send";
  }
}

// ==================== Voice Features ====================
async function speakLastReply() {
  if (!lastAssistantReply) {
    alert("⚠️ No chat reply to speak yet!");
    return;
  }

  try {
    const res = await fetch("/api/voice/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: lastAssistantReply }),
    });

    const data = await res.json();
    if (!res.ok) {
      addChatLine("System", "❌ " + (data.detail || "TTS failed"), true);
      return;
    }

    const player = document.getElementById("ttsPlayer");
    player.src = `${data.audio_url}?t=${Date.now()}`;
    player.play();
  } catch (error) {
    addChatLine("System", "❌ Error: " + error.message, true);
  }
}

async function transcribeVoice() {
  const fileInput = document.getElementById("voiceInput");
  if (!fileInput.files.length) {
    alert("⚠️ Please select an audio file first!");
    return;
  }

  try {
    const form = new FormData();
    form.append("file", fileInput.files[0]);
    form.append("language", language.value || "auto");
    form.append("provider", document.getElementById("voiceProvider").value || "whisper");

    const res = await fetch("/api/voice/transcribe", {
      method: "POST",
      body: form,
    });

    const data = await res.json();
    if (!res.ok) {
      addChatLine("System", "❌ " + (data.detail || "Voice transcription failed"), true);
      return;
    }

    addChatLine("🎤 Voice", data.text, false);
    chatInput.value = data.text || "";

    const dl = document.getElementById("detectedLanguage");
    if (dl) dl.textContent = `🌐 Detected: ${data.language || "-"}`;

    // Auto-send if user has voice input
    if (chatInput.value.trim()) {
      setTimeout(sendMainChatMessage, 500);
    }
  } catch (error) {
    addChatLine("System", "❌ Error: " + error.message, true);
  }
}

async function recordVoice() {
  const btn = document.getElementById("recordVoiceBtn");
  
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    btn.textContent = "⏺️ Record Voice";
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) recordedChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      try {
        const blob = new Blob(recordedChunks, { type: "audio/webm" });
        const file = new File([blob], "recorded.webm", { type: "audio/webm" });
        const form = new FormData();
        form.append("file", file);
        form.append("language", language.value || "auto");
        form.append("provider", document.getElementById("voiceProvider").value || "whisper");

        const res = await fetch("/api/voice/transcribe", { method: "POST", body: form });
        const data = await res.json();

        if (!res.ok) {
          addChatLine("System", "❌ " + (data.detail || "Voice transcription failed"), true);
          return;
        }

        chatInput.value = data.text || "";
        const dl = document.getElementById("detectedLanguage");
        if (dl) dl.textContent = `🌐 Detected: ${data.language || "-"}`;

        if (chatInput.value.trim()) {
          sendMainChatMessage();
        }
      } catch (error) {
        addChatLine("System", "❌ Error: " + error.message, true);
      }
    };

    mediaRecorder.start();
    btn.textContent = "⏹️ Stop Recording";
    addWidgetLine("System", "🎤 Recording started...", true);
  } catch (error) {
    addChatLine("System", "❌ Microphone access denied or unavailable.", true);
  }
}

// ==================== Crisis Help ====================
async function getCrisisAdvice() {
  const message = document.getElementById("crisisInput").value.trim();
  if (!message) {
    alert("⚠️ Please describe your emergency!");
    return;
  }

  crisisBtn.disabled = true;
  crisisBtn.textContent = "🔄 Getting Help...";

  try {
    const res = await fetch("/api/crisis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, language: language.value }),
    });

    const data = await res.json();
    if (!res.ok) {
      document.getElementById("crisisResult").textContent = "❌ Error: " + (data.detail || "Failed");
      return;
    }

    document.getElementById("crisisResult").textContent =
      `🚨 Severity: ${data.severity}\n\n💡 Advice: ${data.advice}\n\n📞 Helpline: ${data.helpline}`;

    // Also show in widget
    addWidgetLine("Crisis", `Severity: ${data.severity}\nAdvice: ${data.advice}`, true);
  } catch (error) {
    document.getElementById("crisisResult").textContent = "❌ Error: " + error.message;
  } finally {
    crisisBtn.disabled = false;
    crisisBtn.textContent = "Get Crisis Advice Now";
  }
}

// ==================== Load Saved Data ====================
async function loadEmergency() {
  try {
    const box = document.getElementById("emergencyList");
    const res = await fetch("/api/emergency");
    const data = await res.json();
    box.innerHTML = "";
    for (const item of data.contacts || []) {
      const row = document.createElement("div");
      row.className = "emergency-item";
      row.innerHTML = `<strong>📞 ${item.title}</strong><br/>${item.number}<br/><a href="tel:${item.number}" style="color: var(--danger);">💬 Call now</a>`;
      box.appendChild(row);
    }
  } catch (error) {
    console.error("Error loading emergency contacts:", error);
  }
}

async function loadSavedItineraries() {
  try {
    const box = document.getElementById("savedItineraries");
    const res = await fetch("/api/itineraries");
    const items = await res.json();
    box.innerHTML = "";

    if (!Array.isArray(items) || !items.length) {
      box.innerHTML = "<div class='stack-item'>📭 No saved itineraries yet.</div>";
      return;
    }

    for (const item of items) {
      const row = document.createElement("div");
      row.className = "stack-item";
      row.innerHTML =
        `<strong>👤 ${item.traveler_name}</strong> - ✈️ ${item.route}<br/>` +
        `💰 Cost: PKR ${Math.round(item.estimated_cost)} | ${item.budget_fit}<br/>` +
        `📍 ${(item.plan || []).slice(0, 2).join(" → ")}<div class='item-actions'><button class='delete-btn' data-id='${item.id}'>🗑️ Delete</button></div>`;
      box.appendChild(row);
    }

    box.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        if (confirm("Delete this itinerary?")) {
          try {
            const res = await fetch(`/api/itineraries/${id}`, { method: "DELETE" });
            if (res.ok) {
              loadSavedItineraries();
              loadTripInsights();
              addWidgetLine("System", "✅ Itinerary deleted.", true);
            }
          } catch (error) {
            alert("Error deleting: " + error.message);
          }
        }
      });
    });
  } catch (error) {
    console.error("Error loading itineraries:", error);
  }
}

async function loadTripInsights() {
  try {
    const summaryBox = document.getElementById("summaryCards");
    const tripsBox = document.getElementById("recentTrips");

    const [summaryRes, tripsRes] = await Promise.all([
      fetch("/api/history/summary"),
      fetch("/api/history/trips"),
    ]);

    const summary = await summaryRes.json();
    const trips = await tripsRes.json();

    summaryBox.innerHTML =
      `<div class='summary-card'><strong>🎯 Total Trips</strong><br/>${summary.total_trips ?? 0}</div>` +
      `<div class='summary-card'><strong>💵 Average Cost</strong><br/>PKR ${Math.round(summary.avg_cost ?? 0)}</div>` +
      `<div class='summary-card'><strong>🏆 Top Route</strong><br/>${summary.top_route ?? "N/A"}</div>`;

    tripsBox.innerHTML = "";
    if (!Array.isArray(trips) || !trips.length) {
      tripsBox.innerHTML = "<div class='stack-item'>📭 No recent trips yet.</div>";
      return;
    }

    for (const t of trips) {
      const row = document.createElement("div");
      row.className = "stack-item";
      row.innerHTML = `<strong>✈️ ${t.origin} → ${t.destination}</strong><br/>💰 Estimated: PKR ${Math.round(t.estimated_cost)} | Budget: PKR ${Math.round(t.budget)}`;
      tripsBox.appendChild(row);
    }
  } catch (error) {
    console.error("Error loading trip insights:", error);
  }
}
