from __future__ import annotations
from typing import Dict, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI  

app = FastAPI(title="Chatbot IA - Fase 2")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama", 
)

class ChatRequest(BaseModel):
    message: str
    context: List[Dict[str, str]] = Field(default_factory=list) 

class ChatResponse(BaseModel):
    reply: str
    updated_context: List[Dict[str, str]]


RISK_KEYWORDS = {
    # Ideación y actos suicidas
    "suicidio", "suicidarme", "matarme", "quitarme la vida", "morirme", 
    "no quiero vivir", "acabar con todo", "dejar de existir", "pastillas para morir",
    "ahorcarme", "saltar", "puente", "arma", "despedida", "carta de despedida",
    
    # Autolesiones
    "cortarme", "hacerme daño", "lastimarme", "autolesion", "quemarme",
    
    # Crisis de pánico y emergencia médica
    "emergencia", "urgencia", "ataque de panico", "no puedo respirar", 
    "presion en el pecho", "infarto", "sobredosis", "intoxicacion",
    
    # Códigos y canales específicos (Chile)
    "*4141", "4141", "fono salud", "salud responde", "samu", "131", "133", "132"
}

@app.post("/chat")
async def chat(request: ChatRequest):
    user_text = request.message.lower()
    if any(word in user_text for word in RISK_KEYWORDS):
        emergency_reply = (
            "⚠️ **HE DETECTADO UNA SITUACIÓN DE RIESGO.** \n\n"
            "Tu seguridad es lo más importante. Por favor, utiliza estos canales de ayuda inmediata:\n"
            "* **Fono Salud Responde:** 600 360 77 77 (Opción 1 para apoyo psicológico).\n"
            "* **Línea de Prevención del Suicidio (*4141):** Gratuito desde celulares.\n"
            "* **Emergencias:** 131 (SAMU) o acude al servicio de urgencias más cercano."
        )
        return ChatResponse(reply=emergency_reply, updated_context=request.context)
    
    messages = [
        {
            "role": "system", 
            "content": "Eres un experto en el dominio de [TU DOMINIO ELEGIDO, ej: Psicología Clínica]. Responde de forma breve, profesional y empática."
        }
    ]
    
    
    for msg in request.context:
        messages.append(msg)
        
    
    messages.append({"role": "user", "content": request.message})

    
    try:
        response = client.chat.completions.create(
            model="llama3", 
            messages=messages,
            temperature=0.7
        )
        bot_reply = response.choices[0].message.content
    except Exception as e:
        bot_reply = "Lo siento, tuve un problema al procesar tu solicitud. ¿Podrías repetir?"
        print(f"Error de conexión con Ollama: {e}")

    
    new_context = messages[1:] 
    new_context.append({"role": "assistant", "content": bot_reply})

    return ChatResponse(
        reply=bot_reply,
        updated_context=new_context
    )
    user_text = request.message.lower()
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)