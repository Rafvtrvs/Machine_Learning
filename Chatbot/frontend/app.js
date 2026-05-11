const chatBox = document.getElementById("chat-box");
const userInputEl = document.getElementById("user-input");
const quickRepliesEl = document.getElementById("quick-replies");
const sendBtn = document.getElementById("send-btn");
const resetBtn = document.getElementById("reset-btn");

const API_URL = "http://localhost:8000/chat";

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
  let formattedMessage = message
      .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
      .replace(/\n/g, '<br>');
  p.innerHTML = `<b>${avatar} ${sender}:</b> ${formattedMessage}`;
  chatBox.appendChild(p);
  chatBox.scrollTop = chatBox.scrollHeight;

}

async function sendMessage() {
  const userInput = userInputEl.value.trim();
  if (!userInput) return;

  const currentHistory = getStoredContext();


  appendMessage("Tú", userInput);
  userInputEl.value = "";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: userInput,
        context: currentHistory, 
      }),
    });

    if (!response.ok) {
      throw new Error(`Error en el servidor: ${response.status}`);
    }

    const data = await response.json();
    
   
    appendMessage("Bot", data.reply);
    
    
    setStoredContext(data.updated_context);

  } catch (error) {
    appendMessage(
      "Bot",
      "⚠️ Error de conexión. Asegúrate de que el backend y Ollama estén corriendo."
    );
    console.error(error);
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