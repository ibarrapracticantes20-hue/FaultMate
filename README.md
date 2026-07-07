# FaultMate
Chatbot de diagnóstico para mantenimiento industrial desarrollado en Botpress Cloud e integrado con Gemini API.

## Cómo correrlo en tu computadora (local)

1. Entra a la carpeta del proyecto Django:
   ```
   cd FaultMateWeb
   ```
2. Crea un entorno virtual e instala las dependencias:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Aplica las migraciones (esto también crea un usuario de prueba):
   ```
   python manage.py migrate
   ```
4. (Opcional) Si quieres que el diagnóstico use la IA de Gemini, agrega tu clave en el archivo `.env`:
   ```
   GEMINI_API_KEY=tu_clave_aqui
   ```
   Sin esta clave, el sistema sigue funcionando normalmente, solo que no podrá generar diagnósticos nuevos con IA.
5. Corre el servidor:
   ```
   python manage.py runserver
   ```
6. Abre `http://127.0.0.1:8000/` en tu navegador e inicia sesión con el usuario de prueba:
   - **Usuario:** `test`
   - **Contraseña:** `test123`

   También puedes crear más usuarios desde la sección "Usuarios" ya con la sesión iniciada.

