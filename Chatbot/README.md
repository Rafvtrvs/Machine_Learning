# Proyecto IA - Fase 2: Chatbot con LLM Local

Este proyecto implementa un chatbot inteligente para el dominio de **Psicología y Triaje**, utilizando modelos de lenguaje de gran escala (LLM) ejecutados localmente.

## Requisitos Técnicos
1. **Ollama:** Descargar e instalar desde [ollama.com](https://ollama.com).
2. **Modelo:** Ejecutar `ollama run llama3` en la terminal.
3. **Python 3.12+** con las librerías: `fastapi`, `uvicorn`, `openai`.

## Instrucciones de Ejecución

1. **Abrir terminal en la carpeta del proyecto** (donde están `launch.py`, `backend` y `frontend`).

2. **Crear entorno virtual (solo la primera vez):**
   ```powershell
   py -3.12 -m venv .venv
   ```

3. **Activar entorno virtual:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Arrancar servidor (usa el puerto 8855):**
   ```powershell
   python launch.py
   ```

6. **Abrir interfaz:** en el navegador entrar a `http://127.0.0.1:8855/`  
   *(No abras `index.html` desde el disco: la app se sirve por esa dirección junto al endpoint `/chat`.)*
