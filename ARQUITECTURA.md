# 🏗️ Arquitectura del Sistema IoT

## 📌 Descripción General

Este sistema implementa una solución de monitoreo de telemetría para servidores, basada en una arquitectura híbrida que combina procesamiento síncrono mediante REST y comunicación asíncrona en tiempo real mediante WebSockets.

El objetivo principal es permitir la ingesta de datos, detección de anomalías y notificación inmediata de eventos críticos.

---

## ⚙️ Componentes Principales

### 1. API REST (Django + DRF)

Permite la interacción con el sistema mediante endpoints HTTP:

* **POST /api/telemetria/ingesta/**

  * Recibe datos de sensores (CPU, RAM, temperatura).
  * Ejecuta validaciones y reglas de negocio.
  * Persiste los datos en Firebase.

* **GET /api/telemetria/estado-actual/**

  * Retorna el último estado registrado por cada servidor.

* **GET /api/telemetria/reporte-servidor/{id_servidor}/**

  * Genera métricas agregadas:

    * Promedio de CPU
    * Temperatura máxima
    * Conteo de anomalías
  * No retorna listas, solo resultados procesados.

---

### 2. Motor de Reglas

Encargado de evaluar condiciones críticas en los datos recibidos.

Reglas implementadas:

* CPU > 90% → alerta crítica
* Temperatura > 75°C → alerta crítica

Si se detecta una anomalía:

* Se marca el registro
* Se genera un evento en tiempo real

---

### 3. WebSockets (Django Channels)

Permiten comunicación en tiempo real entre servidor y cliente.

* Endpoint:

  ```
  ws://localhost:8000/ws/alertas-criticas/
  ```

* Funcionalidad:

  * Los clientes se suscriben al grupo **"alertas"**
  * Cuando ocurre una anomalía, se envía un mensaje en tiempo real

Ejemplo de mensaje:

```json
{
  "alerta": "CRÍTICA",
  "servidor": "SRV-01",
  "cpu": 95,
  "temperatura": 80,
  "motivo": "Temperatura superó 75 grados"
}
```

---

### 4. Base de Datos (Firebase Firestore)

Se utiliza Firestore como base de datos NoSQL.

Características:

* Almacenamiento flexible sin esquema fijo
* Escalabilidad
* Acceso en tiempo real

Cada registro contiene:

* id_servidor
* cpu
* ram
* temperatura
* timestamp
* anomalia
* motivo

---

## 🔐 Control de Acceso

Se implementa un sistema básico de roles mediante headers HTTP:

* **sensor**

  * Puede enviar datos (POST ingesta)

* **admin**

  * Puede consultar estado y reportes (GET)

---

## 🔄 Flujo del Sistema

1. Un sensor envía datos al endpoint REST
2. El sistema valida la información
3. Se ejecuta el motor de reglas
4. Los datos se almacenan en Firebase
5. Si hay anomalía:

   * Se envía una alerta por WebSocket
6. Los clientes reciben la alerta en tiempo real

---

## 🧠 Justificación Técnica

* **REST**: Para operaciones estructuradas y controladas
* **WebSockets**: Para notificaciones en tiempo real sin polling
* **Firebase**: Para almacenamiento escalable y flexible
* **Django Channels**: Para manejar comunicación asíncrona

---

## 📊 Beneficios del Sistema

* Monitoreo en tiempo real
* Baja latencia en alertas
* Separación clara entre ingesta y notificación
* Escalabilidad en almacenamiento
* Arquitectura modular

---

## 🏁 Conclusión

El sistema demuestra la integración efectiva de tecnologías modernas para construir soluciones IoT robustas, combinando procesamiento síncrono y asíncrono para lograr eficiencia y respuesta inmediata ante eventos críticos.
