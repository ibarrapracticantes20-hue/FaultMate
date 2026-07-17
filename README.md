# FaultMate

Plataforma web para diagnostico de fallas industriales con Django, historial de diagnosticos, gestion de agentes y usuarios, e integracion con Gemini.

## Contenido

- [Resumen rapido](#resumen-rapido)
- [Stack tecnologico](#stack-tecnologico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Inicio rapido (un solo comando)](#inicio-rapido-un-solo-comando)
- [Ejecucion manual (paso a paso)](#ejecucion-manual-paso-a-paso)
- [Usuarios de prueba](#usuarios-de-prueba)
- [Base de datos](#base-de-datos)
- [Variables de entorno](#variables-de-entorno)
- [Comandos utiles](#comandos-utiles)
- [Despliegue en Azure](#despliegue-en-azure)
- [Problemas comunes](#problemas-comunes)

## Resumen rapido

FaultMate corre local con Django y permite:

- Login con usuarios reales de `django.contrib.auth`
- Dashboard con filtros por fecha y rol
- Registro y consulta de diagnosticos
- Gestion de agentes y usuarios
- Exportacion de diagnosticos a Excel (`openpyxl`)

## Stack tecnologico

- Python 3.11
- Django 5.x
- WhiteNoise (estaticos)
- Gunicorn (produccion)
- dj-database-url
- PostgreSQL/MySQL (opcional por `DATABASE_URL`) o SQLite por defecto
- Google Gemini (`google-genai`)

## Estructura del proyecto

Raiz del repo:

- `start_faultmate.bat`: arranque automatico local
- `DEPLOY_AZURE.md`: guia de despliegue Azure
- `FaultMateWeb/`: proyecto Django principal

Dentro de `FaultMateWeb/`:

- `manage.py`
- `faultmate/settings.py`
- `dashboard/`
- `agentes/`
- `usuarios/`
- `static/`
- `requirements.txt`

## Requisitos

- Windows (recomendado para el script `.bat`)
- Python 3.11 instalado
- Git (opcional)
- Internet para instalar dependencias

## Inicio rapido (un solo comando)

Desde la carpeta raiz del repositorio ejecuta:

```bat
start_faultmate.bat
```

Ese comando hace automaticamente:

1. Crea `.venv` si no existe.
2. Instala dependencias de `FaultMateWeb/requirements.txt`.
3. Crea `.env` base si no existe.
4. Ejecuta migraciones.
5. Levanta el servidor en `http://127.0.0.1:8000/`.

## Ejecucion manual (paso a paso)

1. Entrar a carpeta Django:

```bat
cd FaultMateWeb
```

2. Crear y activar entorno virtual:

```bat
python -m venv ..\.venv
..\.venv\Scripts\activate
```

3. Instalar dependencias:

```bat
pip install -r requirements.txt
```

4. Aplicar migraciones:

```bat
python manage.py migrate
```

5. Levantar servidor:

```bat
python manage.py runserver 127.0.0.1:8000
```

## Usuarios de prueba

Estas credenciales son para desarrollo/pruebas.

> En login, el campo **Usuario** se llena con el username.
> Para cuentas tipo correo, el username es el correo.

| Usuario | Contrasena | Rol |
| --- | --- | --- |
| `genadmin@example.com` | `test1234` | Desarrollador (admin completo) |
| `crudadmin@example.com` | `test1234` | Desarrollador (admin completo) |
| `visitante@example.com` | `test1234` | Visitante |
| `chatqa@example.com` | `test1234` | Visitante |
| `homeqa@example.com` | `test1234` | Visitante |
| `layoutqa@example.com` | `test1234` | Visitante |
| `dashqa@example.com` | `test1234` | Visitante |
| `test` | `test123` | Visitante |

Usuarios admin completos (rol Desarrollador):

- `genadmin@example.com`
- `crudadmin@example.com`

## Base de datos

Configuracion actual en `FaultMateWeb/faultmate/settings.py`:

- Si existe `DATABASE_URL`, Django usa esa base (PostgreSQL/MySQL segun URL).
- Si no existe `DATABASE_URL`, usa SQLite local (`db.sqlite3`).

Resumen:

- Local por defecto: SQLite.
- Produccion recomendada: PostgreSQL administrado en Azure.

## Variables de entorno

El proyecto carga variables desde `FaultMateWeb/.env`.

Variables relevantes:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL` (opcional en local, recomendado en produccion)

Nota sobre Gemini:

- Actualmente la API key de Gemini esta hardcodeada en `faultmate/services/gemini_service.py` por requerimiento del proyecto.

## Comandos utiles

Desde `FaultMateWeb/`:

```bat
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

Correr pruebas:

```bat
python manage.py test
```

## Despliegue en Azure

Este repo incluye una guia de despliegue:

- Revisar `DEPLOY_AZURE.md`

Flujo recomendado:

1. Crear recursos (App Service o Container Apps + PostgreSQL).
2. Configurar `DATABASE_URL`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
3. Ejecutar migraciones en entorno de despliegue.
4. Validar login, dashboard y estaticos.

### Despliegue manual actual (Azure Container Apps)

Actualmente el despliegue que se usa en este proyecto es manual a Azure Container Apps.
El workflow de GitHub Actions de Container Apps existe, pero si faltan secretos OIDC no termina el deploy.

#### Requisitos previos

1. Azure CLI instalado (`az --version`).
2. Sesion iniciada en Azure (`az login`).
3. Permisos sobre el grupo de recursos y la Container App.
4. Repo actualizado en rama `main` con los cambios que quieres publicar.

#### Valores usados en este entorno

- Subscription: `Azure subscription 1`
- Resource Group: `rg-faultmate-dev-scus`
- Container App: `ca-faultmate-web-scus`

#### Paso a paso (comandos)

1. Ir al repo local:

```powershell
cd "c:\Users\SantiagoSegura\OneDrive - PROCETI\Documentos\Github\FaultMate"
```

2. Validar sesión y suscripción:

```powershell
az account show -o table
az account set --subscription "Azure subscription 1"
```

3. Obtener el SHA corto del commit a publicar:

```powershell
$sha = git rev-parse --short HEAD
```

4. Forzar nueva revisión de Container App:

```powershell
az containerapp update -n ca-faultmate-web-scus -g rg-faultmate-dev-scus --set-env-vars DEPLOY_SHA=$sha --output table
```

5. Verificar estado de revisión:

```powershell
az containerapp show -n ca-faultmate-web-scus -g rg-faultmate-dev-scus --query "{latestReady:properties.latestReadyRevisionName,latestRevision:properties.latestRevisionName,runningStatus:properties.runningStatus}" -o table
az containerapp revision list -n ca-faultmate-web-scus -g rg-faultmate-dev-scus --query "[].{name:name,health:properties.healthState,state:properties.runningState,active:properties.active}" -o table
```

6. Si la nueva revisión sigue en `Activating`, revisar logs:

```powershell
az containerapp logs show -n ca-faultmate-web-scus -g rg-faultmate-dev-scus --revision <NOMBRE_REVISION> --follow false --tail 120
```

7. Probar sitio publicado:

```powershell
Invoke-WebRequest -Uri "https://ca-faultmate-web-scus.happyriver-ea030381.southcentralus.azurecontainerapps.io/" -UseBasicParsing
```

#### Nota importante de operación

- Esta Container App recompone entorno en arranque (instala paquetes y clona repo), por eso algunas revisiones tardan varios minutos en pasar a `Healthy`.
- No dar por fallido el deploy hasta revisar `latestReady` y logs.

## Problemas comunes

### 1) "No se ven estilos CSS"

- Verifica que `/static/css/estilos.css` responda 200.
- Confirma WhiteNoise activo en `MIDDLEWARE`.
- En produccion, valida `DEBUG=False` y configuracion de estaticos.

### 2) "No puedo iniciar sesion"

- Confirma usuario/contrasena de la tabla.
- Recuerda: para cuentas de correo, en campo Usuario va el correo.
- Ejecuta `python manage.py migrate` para sembrar usuarios de prueba.

### 3) "No guarda datos en produccion"

- Configura `DATABASE_URL` hacia PostgreSQL.
- Revisa conectividad/firewall de la base.
- Reaplica migraciones en entorno de despliegue.

## Estado de referencia

- Rama principal: `main`
- El proyecto incluye mejoras recientes de UI en filtros de dashboard y login funcional con usuarios sembrados por migraciones.
