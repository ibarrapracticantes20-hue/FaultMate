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
4. Si quieres que el diagnóstico use la IA de Gemini, coloca tu clave en `faultmate/services/gemini_service.py` reemplazando `PEGA_AQUI_TU_API_KEY`.
5. Corre el servidor:
   ```
   python manage.py runserver
   ```
6. Abre `http://127.0.0.1:8000/` en tu navegador e inicia sesión con el usuario de prueba:
   - **Usuario:** `test`
   - **Contraseña:** `test123`

   También puedes crear más usuarios desde la sección "Usuarios" ya con la sesión iniciada.

## Usuarios de prueba (verificados)

> Estas credenciales son solo para desarrollo local/proyecto escolar.

| Usuario | Contraseña | Nivel |
| --- | --- | --- |
| `genadmin@example.com` | `test1234` | **Desarrollador** (admin completo) |
| `crudadmin@example.com` | `test1234` | **Desarrollador** (admin completo) |
| `visitante@example.com` | `test1234` | **Visitante** |
| `chatqa@example.com` | `test1234` | **Visitante** |
| `homeqa@example.com` | `test1234` | **Visitante** |
| `layoutqa@example.com` | `test1234` | **Visitante** |
| `dashqa@example.com` | `test1234` | **Visitante** |
| `test` | `test123` | **Visitante** |

### ¿Cuál es el usuario admin?

Actualmente los usuarios con nivel admin completo (Desarrollador) verificados son:

- `genadmin@example.com`
- `crudadmin@example.com`

## Despliegue en Azure

Se agregó una guía para desplegar con GitHub Actions, App Service Linux y PostgreSQL administrado:

- Ver `DEPLOY_AZURE.md`

