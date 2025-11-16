/* ==========================================================
   NexaPilot UI v5 — chat.js (Final)
   - Theme persistence
   - Mic support (SpeechRecognition)
   - Mobile toggles
   - Chat, Tasks & Weather integration
   ========================================================== */

(() => {
  // Elements
  const chatArea = document.getElementById("chat-area");
  const typingElem = document.getElementById("typing");
  const inputEl = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const micBtn = document.getElementById("mic-btn");
  const themeBtn = document.getElementById("theme-toggle");
  const suggestionsBox = document.getElementById("suggestions");

  const sidebar = document.querySelector(".sidebar");
  const panel = document.querySelector(".panel");
  const menuToggleBtn = document.getElementById("menu-toggle-btn");
  const taskToggleBtn = document.getElementById("task-toggle-btn");

  let recognition = null;
  let micOn = false;

  // Safe helpers
  const safeFetch = async (url, options) => {
    try { const r = await fetch(url, options); return await r.json(); }
    catch(e){ console.warn("fetch error", url, e); return null; }
  };

  function escapeHtml(s){
    if(!s) return "";
    return s.replace(/[&<>"']/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"})[m]);
  }

  // THEME: persist + apply
  function applyTheme(theme){
    document.body.classList.remove("theme-dark", "theme-light");
    document.body.classList.add("theme-" + theme);
    document.body.dataset.theme = theme;
    localStorage.setItem("nexa-theme", theme);
    if(themeBtn) themeBtn.textContent = theme === "dark" ? "🌗" : "🌞";
  }
  function initTheme(){
    const saved = localStorage.getItem("nexa-theme") || "dark";
    applyTheme(saved);
    if(themeBtn) themeBtn.addEventListener("click", ()=> applyTheme(document.body.dataset.theme === "dark" ? "light" : "dark"));
  }

  // MESSAGES
  function appendMessage(text, who="bot"){
    const wrapper = document.createElement("div");
    wrapper.className = "msg " + (who === "you" ? "user" : "bot");
    wrapper.innerHTML = `<div class="avatar" aria-hidden="true"></div><div class="bubble">${escapeHtml(text)}</div>`;
    wrapper.draggable = true;
    wrapper.addEventListener("dragstart", e => e.dataTransfer.setData("text/plain", text));
    chatArea.appendChild(wrapper);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function setTyping(show){
    if(!typingElem) return;
    typingElem.classList.toggle("hidden", !show);
  }

  // SEND
  async function sendMessage(){
    const text = inputEl.value.trim();
    if(!text) return;
    appendMessage(text, "you");
    inputEl.value = "";
    setTyping(true);

    const res = await safeFetch("/api", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ q: text })
    });

    setTyping(false);
    if(res && res.response) appendMessage(res.response, "bot");
    else appendMessage("⚠ Server error or invalid response", "bot");
    refreshTasks();
  }

  if(sendBtn) sendBtn.addEventListener("click", sendMessage);
  if(inputEl) inputEl.addEventListener("keydown", e => { if(e.key === "Enter") sendMessage(); });

  // TASKS
  async function refreshTasks(){
    const j = await safeFetch("/tasks?user=web");
    const list = document.getElementById("task-list");
    if(!list) return;
    list.innerHTML = "";
    if(!j || !Array.isArray(j.tasks)) { list.innerHTML = "<div class='task-item'>No tasks</div>"; return; }
    j.tasks.forEach(t => {
      const el = document.createElement("div");
      el.className = "task-item";
      el.innerHTML = `<div>${escapeHtml(t.title)}</div><div><button onclick="(function(){ window.__nexa_markDone && window.__nexa_markDone('${escapeHtml(t.title)}') })()">✓</button></div>`;
      list.appendChild(el);
    });
  }

  // Expose markDone globally for inline buttons (simple stub)
  window.__nexa_markDone = function(title){
    appendMessage(`Marked "${title}" complete.`, "bot");
    refreshTasks();
  };

  async function addTaskFromInput(){
    const v = document.getElementById("new-task").value.trim();
    if(!v) return;
    await safeFetch("/tasks?user=web", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ text: v }) });
    document.getElementById("new-task").value = "";
    refreshTasks();
  }
  window.addTaskFromInput = addTaskFromInput; // keep callable from HTML

  // QUICK HELPERS
  function clearChat(){ chatArea.innerHTML = ""; }
  function quickAdd(){
    const t = prompt("Task title?");
    if(t) safeFetch("/tasks?user=web", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ text: t }) }).then(refreshTasks);
  }
  function planDay(){ inputEl.value = "Plan my day"; sendMessage(); }

  // WEATHER
  async function loadWeather(){
    const j = await safeFetch("/weather");
    const el = document.querySelector("#weather-card .weather-body");
    if(el) el.innerText = (j && j.advice) ? j.advice : "No data";
  }

  // MIC (SpeechRecognition) — graceful fallback if not supported
  function initMic(){
    if(!("SpeechRecognition" in window || "webkitSpeechRecognition" in window)){
      if(micBtn) micBtn.title = "Voice input not supported.";
      return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SR();
    recognition.lang = "en-US";
    recognition.interimResults = false;

    recognition.onresult = (e) => {
      const text = e.results[0][0].transcript;
      inputEl.value = text;
      sendMessage();
    };
    recognition.onerror = () => {
      if(micBtn) micBtn.classList.remove("recording");
      micOn = false;
    };
    recognition.onend = () => {
      if(micBtn) micBtn.classList.remove("recording");
      micOn = false;
    };
  }

  function toggleMic(){
    if(!recognition) initMic();
    if(!recognition) return alert("Speech recognition not supported in this browser.");
    if(!micOn){
      recognition.start(); micOn = true; micBtn && micBtn.classList.add("recording");
    } else {
      recognition.stop(); micOn = false; micBtn && micBtn.classList.remove("recording");
    }
  }
  if(micBtn) micBtn.addEventListener("click", toggleMic);

  // MOBILE PANELS
  if(menuToggleBtn) menuToggleBtn.addEventListener("click", () => { sidebar && sidebar.classList.toggle("open"); panel && panel.classList.remove("open"); });
  if(taskToggleBtn) taskToggleBtn.addEventListener("click", () => { panel && panel.classList.toggle("open"); sidebar && sidebar.classList.remove("open"); });

  document.addEventListener("click", (e) => {
    if(window.innerWidth > 1200) return; // <-- CHANGED FROM 980
    if(sidebar && !sidebar.contains(e.target) && e.target !== menuToggleBtn) sidebar.classList.remove("open");
    if(panel && !panel.contains(e.target) && e.target !== taskToggleBtn) panel.classList.remove("open");
  });

  // RESPONSIVE helper
  function handleResize(){
    if(window.innerWidth > 1200){ // <-- CHANGED FROM 980
      sidebar && sidebar.classList.remove("open");
      panel && panel.classList.remove("open");
    }
  }
  window.addEventListener("resize", handleResize);

  // SUGGESTIONS (small set)
  function loadSuggestions(){
    const suggestions = ["Plan my day", "Add a task", "What's the weather?", "Summarize tasks"];
    suggestionsBox && suggestions.forEach(s => {
      const b = document.createElement("button");
      b.className = "suggestion-chip";
      b.textContent = s;
      b.onclick = () => { inputEl.value = s; sendMessage(); };
      suggestionsBox.appendChild(b);
    });
  }

  // INIT
  initTheme();
  loadSuggestions();
  loadWeather();
  refreshTasks();
  initMic();

  // expose functions used inline in HTML
  window.quickAdd = quickAdd;
  window.clearChat = clearChat;
  window.planDay = planDay;
  window.refreshTasks = refreshTasks;
  window.addTaskFromInput = addTaskFromInput;
  window.sendMessage = sendMessage;
  window.toggleMic = toggleMic;
})();