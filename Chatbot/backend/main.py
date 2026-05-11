from pathlib import Path
import asyncio
from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field
from openai import OpenAI

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

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
    timeout=120.0,
)

@app.get("/malvekee-identidad", include_in_schema=True)
async def malvekee_identidad() -> dict[str, str]:
    """Responde solo si cargaste ESTE proyecto (útil si ves Not Found usando otro `backend`)."""
    return {"proyecto": "chatbot-malvekee-fase2", "frontend_dir": str(FRONTEND_DIR)}


class ChatRequest(BaseModel):
    message: str
    context: List[Dict[str, str]] = Field(default_factory=list) 

class ChatResponse(BaseModel):
    reply: str
    updated_context: List[Dict[str, str]]


RISK_KEYWORDS = {
    "suicidio", "matarme", "autolesion", "quitarme la vida", "emergencia"
}

@app.post("/chat")
async def chat(request: ChatRequest):
    user_text = request.message.lower()

    
    if any(word in user_text for word in RISK_KEYWORDS):
        emergency_reply = "Si te encuentras en una situación de emergencia, por favor acude al centro de urgencias más cercano o llama a los servicios de salud."
        return ChatResponse(reply=emergency_reply, updated_context=request.context)

    
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un asistente conversacional orientado al bienestar y al apoyo inicial; "
                "no eres médico ni psicólogo, ni debes afirmarlo. No digas que eres experto en psicología. "
                "Responde siempre en español, salvo que el usuario pida explícitamente otro idioma. "
                "Sé claro, breve y cordial; no des diagnósticos ni tratamientos; ante situaciones graves, "
                "indica buscar ayuda profesional presencial."
            ),
        }
    ]
    
    
    for msg in request.context:
        messages.append(msg)
        
    
    messages.append({"role": "user", "content": request.message})

    
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="llama3",
            messages=messages,
            temperature=0.7,
        )
        raw = response.choices[0].message.content if response.choices else ""
        bot_reply = (raw or "").strip()
        if not bot_reply:
            bot_reply = (
                "El modelo devolvió texto vacío. Revisa en Ollama el nombre del modelo "
                "(debe coincidir con 'llama3' en el código) con: ollama list"
            )
    except Exception as e:
        bot_reply = (
            "No pude obtener respuesta de Ollama. Comprueba que Ollama está abierto, "
            "que el modelo existe (ollama pull llama3) y el error en la consola del servidor."
        )
        print(f"Error de conexión con Ollama: {e}")

    
    new_context = messages[1:] 
    new_context.append({"role": "assistant", "content": bot_reply})

    return ChatResponse(
        reply=bot_reply,
        updated_context=new_context
    )


@app.get("/health", include_in_schema=False)
async def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/debug/frontend", include_in_schema=False)
async def debug_frontend() -> dict[str, bool | str]:
    idx = FRONTEND_DIR / "index.html"
    return {
        "frontend_dir": str(FRONTEND_DIR),
        "dir_exists": FRONTEND_DIR.is_dir(),
        "index_html": idx.is_file(),
    }


@app.get("/", include_in_schema=False)
async def serve_index():
    index = FRONTEND_DIR / "index.html"
    if not index.is_file():
        return HTMLResponse(
            content=(
                f"<meta charset=utf-8>"
                f"<p>No encuentro <code>index.html</code>.</p>"
                f"<p>Ruta calculada: <code>{index}</code></p>"
                f"<p>Abre <a href=/debug/frontend>/debug/frontend</a> para revisar rutas.</p>"
            ),
            status_code=503,
            media_type="text/html",
        )
    return FileResponse(index, media_type="text/html")


@app.get("/styles.css", include_in_schema=False)
async def serve_styles():
    path = FRONTEND_DIR / "styles.css"
    if not path.is_file():
        return HTMLResponse(content="Missing styles.css", status_code=404)
    return FileResponse(path, media_type="text/css")


@app.get("/app.js", include_in_schema=False)
async def serve_app_js():
    path = FRONTEND_DIR / "app.js"
    if not path.is_file():
        return HTMLResponse(content="Missing app.js", status_code=404)
    return FileResponse(path, media_type="application/javascript")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)