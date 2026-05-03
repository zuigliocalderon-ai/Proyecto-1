# Deploy a Render

Esta guía te muestra cómo desplegar la plataforma de pronósticos deportivos en Render.

## Requisitos Previos

1. Cuenta en [render.com](https://render.com) (gratis)
2. Repositorio en GitHub (ya hecho ✅)
3. API key de Odds API (ya tienes: `9e76e9a371972c3f41c03820ba1879db`)

## Pasos para Desplegar

### 1. Conectar GitHub a Render

1. Ve a [render.com](https://render.com)
2. Haz clic en **"New +"** → **"Web Service"**
3. Selecciona **"Deploy an existing repository"**
4. Conecta tu cuenta de GitHub
5. Selecciona el repositorio `zuigliocalderon-ai/Proyecto-1`
6. Selecciona la rama `claude/setup-sports-forecasting-7fclr`

### 2. Configurar el Servicio

**Nombre del servicio:** `sports-predictions-api`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT "src.api.app:app"
```

**Environment Variables** (agregadas desde el dashboard de Render):

```
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-segura-aqui
ODDS_API_KEY=9e76e9a371972c3f41c03820ba1879db
DATABASE_URL=sqlite:///sports_predictions.db
```

### 3. Configurar Base de Datos (Opcional)

Para usar PostgreSQL en lugar de SQLite:

1. En Render, crea un nuevo **PostgreSQL Database**
2. Copia la `DATABASE_URL` completa
3. Pega en las Environment Variables del web service

### 4. Deploy Automático

Render desplegará automáticamente cuando hagas `git push` a la rama `claude/setup-sports-forecasting-7fclr`.

## Verificar el Deploy

1. Ve a tu dashboard de Render
2. Busca tu servicio `sports-predictions-api`
3. Haz clic en el URL (ej: `https://sports-predictions-api.onrender.com`)
4. Deberías ver tu dashboard en funcionamiento

## Monitoreo

- **Logs en vivo**: Render muestra logs en tiempo real
- **Status**: Verás si está corriendo, fallando, etc.
- **Redeploy**: Puedes hacer redeploy manual desde el dashboard

## Actualizaciones Futuras

Cada vez que hagas un commit a la rama `claude/setup-sports-forecasting-7fclr`, Render desplegará automáticamente.

```bash
git push origin claude/setup-sports-forecasting-7fclr
# Render detectará el cambio y hará deploy automáticamente
```

## URLs Importantes

- **Dashboard en vivo**: `https://sports-predictions-api.onrender.com`
- **API**: `https://sports-predictions-api.onrender.com/api`
- **Health check**: `https://sports-predictions-api.onrender.com/api/health`

## Solución de Problemas

**Si el deploy falla:**

1. Revisa los logs en el dashboard de Render
2. Verifica que `Procfile` esté correcto
3. Asegúrate de que todas las env vars estén configuradas
4. Prueba localmente: `python3 backend/src/api/app.py`

**Si la app va lenta:**
- Usa una base de datos PostgreSQL (SQLite es lento en web)
- Upgradate a plan pagado de Render (free tiene límites)

## Contacto y Soporte

Si tienes problemas, revisa:
- [Documentación de Render](https://render.com/docs)
- Logs del deploy en el dashboard de Render
