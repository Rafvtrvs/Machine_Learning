# Proyecto IA - Fase 2: Chatbot con LLM Local

Este proyecto implementa un chatbot inteligente para el dominio de **Psicología y Triaje**, utilizando modelos de lenguaje de gran escala (LLM) ejecutados localmente.

## Requisitos Técnicos
1. **Ollama:** Descargar e instalar desde [ollama.com](https://ollama.com).
2. **Modelo:** Ejecutar `ollama run llama3` en la terminal.
3. **Python 3.12+** con las librerías: `fastapi`, `uvicorn`, `openai`.

## Instrucciones de Ejecución

1. **Activar Entorno Virtual:**
   ```powershell
   .\.venv\Scripts\activate
2. **Iniciar Backend**
    uvicorn backend.main:app --reload
3. **Abrir Interfaz**
    Abrir Index.html en el navegador
