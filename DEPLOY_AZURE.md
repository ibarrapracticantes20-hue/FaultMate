# Despliegue de FaultMate en Azure (bajo costo)

Este proyecto ya queda preparado para desplegar con GitHub Actions en Azure App Service y usar una base de datos SQL relacional administrada en Azure (PostgreSQL Flexible Server).

## Arquitectura propuesta
- Hosting: Azure App Service Linux (SKU B1)
- Base de datos: Azure Database for PostgreSQL Flexible Server
- CI/CD: GitHub Actions (`.github/workflows/deploy-azure-appservice.yml`)
- URL publica: `https://<tu-webapp>.azurewebsites.net`

## 1) Crear recursos en Azure CLI

> Requiere iniciar sesion antes: `az login`

```bash
# Variables
RESOURCE_GROUP="rg-faultmate-prod"
LOCATION="eastus"
PG_SERVER="faultmate-pg-<unico>"
PG_DB="faultmate"
PG_ADMIN_USER="faultmateadmin"
PG_ADMIN_PASSWORD="<PASSWORD_SEGURA>"
APP_PLAN="faultmate-plan"
WEBAPP_NAME="faultmate-web-<unico>"

# Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# PostgreSQL Flexible Server (SQL relacional)
az postgres flexible-server create \
  --name $PG_SERVER \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --admin-user $PG_ADMIN_USER \
  --admin-password $PG_ADMIN_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 16 \
  --public-access 0.0.0.0

az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $PG_SERVER \
  --database-name $PG_DB

# Plan y WebApp Linux (Python)
az appservice plan create \
  --name $APP_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_PLAN \
  --name $WEBAPP_NAME \
  --runtime "PYTHON:3.11"

# Startup para Django en App Service
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $WEBAPP_NAME \
  --startup-file "gunicorn faultmate.wsgi:application --bind=0.0.0.0 --timeout 120"
```

## 2) Configurar variables en App Service

```bash
# Obtener cadena de conexion de PostgreSQL (revisar salida)
az postgres flexible-server show-connection-string \
  --server-name $PG_SERVER \
  --database-name $PG_DB \
  --admin-user $PG_ADMIN_USER \
  --admin-password $PG_ADMIN_PASSWORD
```

Para Django en este proyecto, define estos App Settings en la WebApp:
- `SECRET_KEY`: una clave segura de produccion
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `<tu-webapp>.azurewebsites.net`
- `CSRF_TRUSTED_ORIGINS`: `https://<tu-webapp>.azurewebsites.net`
- `DATABASE_URL`: cadena en formato PostgreSQL para Django. Ejemplo:
  - `postgresql://faultmateadmin:<PASSWORD>@<PG_SERVER>.postgres.database.azure.com:5432/faultmate?sslmode=require`

> Nota: ahora mismo `settings.py` usa `dj-database-url` con `DATABASE_URL` para entorno productivo.

## 3) Configurar secretos en GitHub

En tu repo de GitHub, crea estos secrets:
- `AZURE_WEBAPP_NAME`: nombre de tu Web App
- `AZURE_WEBAPP_PUBLISH_PROFILE`: contenido XML del publish profile

Para descargar publish profile:
```bash
az webapp deployment list-publishing-profiles \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --xml
```

## 4) Publicar

Cuando hagas push a `main`, el workflow despliega automaticamente.

## 5) Opcion Docker (local o VM)

Ya se agrego:
- `FaultMateWeb/Dockerfile`
- `FaultMateWeb/.dockerignore`

Build local:
```bash
cd FaultMateWeb
docker build -t faultmate:latest .
docker run -p 8000:8000 faultmate:latest
```

## Recomendacion de costo
- Usa B1 para App Service y PostgreSQL Burstable B1ms para iniciar.
- Monitorea consumo de creditos antes de escalar.
