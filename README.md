# 🏗️ Backend IoT - Monitoreo de Telemetría

[![Django](https://img.shields.io/badge/Django-5.2-green)](https://www.djangoproject.com/) [![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/) [![Channels](https://img.shields.io/badge/Channels-4.3-orange)](https://channels.readthedocs.io/)

## 📌 Descripción

Sistema backend para **monitoreo en tiempo real de telemetría IoT** en servidores. Recibe datos de sensores (CPU, RAM, temperatura), detecta **anomalías críticas**, almacena en **Firebase Firestore** y envía **alertas instantáneas via WebSockets**.

Arquitectura híbrida: **REST síncrono** + **WebSockets asíncronos** + **Firebase NoSQL**.

## ✨ Características

- ✅ Ingesta de datos de sensores via API REST
- ✅ Detección automática de anomalías (CPU >90%, Temp >75°C)
- ✅ Almacenamiento escalable en Firebase Firestore
- ✅ Notificaciones en tiempo real via WebSockets
- ✅ Autenticación por roles (sensor/admin)
- ✅ Reportes agregados y estado actual
- ✅ Postman collection incluida para pruebas

## 🏗️ Arquitectura

```
[Sensores IoT] --> POST /api/telemetria/ingesta/ --> [Motor Reglas] --> [Firebase Firestore]
                                                                              |
                                                                          [Anomalía?] --> [WebSockets] --> [Clientes]
```

**Componentes**:
- **Django REST Framework**: API endpoints
- **Django Channels**: WebSockets (`ws://localhost:8000/ws/alertas-criticas/`)
- **Firebase Firestore**: BD NoSQL realtime
- **Motor de reglas**: Validaciones/anomalías

Ver [ARQUITECTURA.md](ARQUITECTURA.md) para detalles completos.

## 🚀 Instalación Rápida

### 1. Clonar/Entorno
```bash
# Virtual environment
python -m venv venv
# Windows
venv\\Scripts\\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependencias (corrige encoding UTF-8 si necesario: type requeriments.txt)
pip install -r requeriments.txt
```

### 2. Configurar Firebase
- Copia `serviceAccountKey.json` a `backend_iot/telemetria/` (ver `firebase_config.py`).
- Configura credenciales en Firebase Console.

### 3. Django Setup
```bash
cd backend_iot
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

### 4. Ejecutar Servidor
```bash
# Terminal 1: Servidor principal (incluye Channels)
python manage.py runserver

# Servidor disponible en: http://127.0.0.1:8000
# WebSocket: ws://localhost:8000/ws/alertas-criticas/
```

**Producción**: Cambia `CHANNEL_LAYERS` a Redis, `DEBUG=False`, deploy (Heroku/GCP/Docker).

## 📊 API Endpoints

| Método | Endpoint | Role | Descripción | Ejemplo |
|--------|----------|------|-------------|---------|
| `POST` | `/api/telemetria/ingesta/` | `sensor` | Envía datos telemetría | `{\"id_servidor\":\"SRV-01\",\"cpu\":95,\"ram\":40,\"temperatura\":80}` |
| `GET` | `/api/telemetria/estado-actual/` | `admin` | Último estado servidores | - |
| `GET` | `/api/telemetria/reporte-servidor/SRV-01/?rango=ultimas_24h` | `admin` | Métricas agregadas | Promedios, max, anomalías |

**Headers**: `Role: sensor` o `admin`, `Content-Type: application/json`

```bash
# Ejemplo ingesta anomalía
curl -X POST http://127.0.0.1:8000/api/telemetria/ingesta/ \
  -H \"Role: sensor\" \
  -H \"Content-Type: application/json\" \
  -d '{\"id_servidor\":\"SRV-01\",\"cpu\":95,\"ram\":40,\"temperatura\":80}'
```

## 🔌 WebSockets

**URL**: `ws://localhost:8000/ws/alertas-criticas/`

**Mensaje alerta ejemplo**:
```json
{
  \"alerta\": \"CRÍTICA\" ,
  \"servidor\": \"SRV-01\",
  \"cpu\": 95,
  \"temperatura\": 80,
  \"motivo\": \"Temperatura superó 75 grados\"
}
```

**Cliente JS ejemplo**:
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/alertas-criticas/');
socket.onmessage = (e) => console.log(JSON.parse(e.data));
```

## 📁 Estructura del Proyecto

```
backend_iot/
├── manage.py
├── requeriments.txt
├── backend_iot/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── telemetria/
    ├── views.py (API)
    ├── consumers.py (WS)
    ├── firebase_config.py
    ├── models.py
    └── urls.py
├── ARQUITECTURA.md
├── postman_collection.json
├── README.md  ← ¡Tú estás aquí!
```

## 🧪 Pruebas

1. Importa `postman_collection.json` en Postman.
2. Ejecuta requests: ingesta normal → anomalía → verifica WS alerta.
3. Admin endpoints para reportes.


