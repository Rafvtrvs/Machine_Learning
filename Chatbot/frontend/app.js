const chatBox = document.getElementById("chat-box");
const userInputEl = document.getElementById("user-input");
const quickRepliesEl = document.getElementById("quick-replies");
const sendBtn = document.getElementById("send-btn");
const resetBtn = document.getElementById("reset-btn");

const chatPath = `${window.location.origin}/chat`;

function getStoredContext() {
  const raw = localStorage.getItem("chatContext");
  if (!raw) return []; 
  try {
    return JSON.parse(raw);
  } catch (error) {
    console.warn("No se pudo leer el historial, reiniciando.");
    return [];
  }
}

function setStoredContext(context) {
  localStorage.setItem("chatContext", JSON.stringify(context || []));
}

function appendMessage(sender, message) {
  const p = document.createElement("p");
  const avatar = sender === "Bot" ? "🤖" : "👤";
  p.innerHTML = `<b>${avatar}</b> ${message}`;
  chatBox.appendChild(p);
  chatBox.scrollTop = chatBox.scrollHeight;
  return p;
}

function appendThinking() {
  const p = document.createElement("p");
  p.className = "thinking";
  p.innerHTML = "<b>🤖</b> Pensando… (Ollama puede tardar unos segundos)";
  chatBox.appendChild(p);
  chatBox.scrollTop = chatBox.scrollHeight;
  return p;
}

function setSending(value) {
  sendBtn.disabled = value;
  resetBtn.disabled = value;
  userInputEl.disabled = value;
}

async function sendMessage() {
  const userInput = userInputEl.value.trim();
  if (!userInput) return;
  if (sendBtn.disabled) return;

  const currentHistory = getStoredContext();


  appendMessage("Tú", userInput);
  userInputEl.value = "";

  const thinkingEl = appendThinking();
  setSending(true);

  const controller = new AbortController();
  const to = setTimeout(() => controller.abort(), 130_000);

  try {
    const response = await fetch(chatPath, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: userInput,
        context: currentHistory, 
      }),
      signal: controller.signal,
    });

    const rawBody = await response.text();

    if (!response.ok) {
      let texto = `${response.status} ${response.statusText}`;
      try {
        const err = JSON.parse(rawBody);
        if (err.detail != null) {
          texto += ` — ${
            typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail)
          }`;
        }
      } catch {
        if (rawBody) texto += ` — ${rawBody.slice(0, 400)}`;
      }
      throw new Error(texto);
    }

    const data = JSON.parse(rawBody);

    if (typeof data.reply !== "string") {
      throw new Error("El servidor no devolvió 'reply' como texto.");
    }

    thinkingEl.remove();
    appendMessage("Bot", data.reply);
    setStoredContext(data.updated_context);
  } catch (error) {
    thinkingEl.remove();
    const mensaje =
      error instanceof Error && error.message
        ? error.message
        : "⚠️ No se pudo completar la petición.";

    const isAbort =
      (error instanceof DOMException && error.name === "AbortError") ||
      (error instanceof Error && error.name === "AbortError");

    if (isAbort) {
      appendMessage(
        "Bot",
        "⚠️ La petición tardó demasiado (más de 2 min). Ollama suele tardar al primer mensaje; prueba otra vez o revisa la consola donde corre python launch.py.",
      );
    } else if (mensaje.includes("Failed to fetch")) {
      appendMessage(
        "Bot",
        "⚠️ No hay conexión con el servidor. ¿Está ejecutándose python launch.py y abriste http://127.0.0.1:8855?",
      );
    } else {
      appendMessage("Bot", `⚠️ ${mensaje}`);
    }
    console.error(error);
  } finally {
    clearTimeout(to);
    setSending(false);
  }
}


async function startConversation() {
  const history = getStoredContext();
  if (history.length === 0) {
    appendMessage("Bot", "¡Hola! Soy tu asistente inteligente. ¿En qué puedo ayudarte hoy?");
  } else {
   
    history.forEach(msg => {
      const role = msg.role === "user" ? "Tú" : "Bot";
      appendMessage(role, msg.content);
    });
  }
}

function resetConversation() {
  chatBox.innerHTML = "";
  setStoredContext([]);
  startConversation();
}


sendBtn.addEventListener("click", sendMessage);
userInputEl.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
resetBtn.addEventListener("click", resetConversation);


startConversation();
