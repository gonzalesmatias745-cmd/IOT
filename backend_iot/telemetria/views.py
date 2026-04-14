from rest_framework.decorators import api_view
from rest_framework.response import Response
from .firebase_config import db
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime, timedelta


# 🔐 ROLES
def get_user_from_token(request):
    return {
        "uid": "demo123",
        "role": request.headers.get("Role")
    }


# 🔥 MOTOR DE REGLAS
def evaluar_anomalia(cpu, temperatura):
    if cpu > 90:
        return True, "CPU superó 90%"
    if temperatura > 75:
        return True, "Temperatura superó 75 grados"
    return False, None


# 🔧 NORMALIZAR TIMESTAMP
def parse_timestamp(ts):
    if isinstance(ts, str):
        return datetime.fromisoformat(ts.replace("Z", ""))
    else:
        return ts.replace(tzinfo=None)


# 🚀 POST INGESTA
@api_view(['POST'])
def ingesta(request):
    user = get_user_from_token(request)

    if user["role"] != "sensor":
        return Response({"error": "Solo sensores"}, status=403)

    data = request.data

    # VALIDACIÓN
    if not all(k in data for k in ["id_servidor", "cpu", "ram", "temperatura"]):
        return Response({"error": "Datos incompletos"}, status=400)

    try:
        cpu = float(data.get("cpu"))
        ram = float(data.get("ram"))
        temperatura = float(data.get("temperatura"))
    except:
        return Response({"error": "Datos inválidos"}, status=400)

    registro = {
        "id_servidor": data.get("id_servidor"),
        "cpu": cpu,
        "ram": ram,
        "temperatura": temperatura,
        "timestamp": datetime.utcnow().isoformat()
    }

    es_anomalia, motivo = evaluar_anomalia(cpu, temperatura)

    registro["anomalia"] = es_anomalia
    registro["motivo"] = motivo if es_anomalia else None

    db.collection("telemetria").add(registro)

    # 🔌 WEBSOCKET
    if es_anomalia:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "alertas",
            {
                "type": "send_alert",
                "message": {
                    "alerta": "CRÍTICA",
                    "servidor": registro["id_servidor"],
                    "cpu": cpu,
                    "temperatura": temperatura,
                    "motivo": motivo,
                    "timestamp": registro["timestamp"]
                }
            }
        )

    return Response(registro, status=201)


# 📊 ESTADO ACTUAL (🔥 CORREGIDO)
@api_view(['GET'])
def estado_actual(request):
    user = get_user_from_token(request)

    if user["role"] != "admin":
        return Response({"error": "Solo admin"}, status=403)

    docs = db.collection("telemetria").stream()

    latest = {}

    for doc in docs:
        d = doc.to_dict()
        sid = d["id_servidor"]

        fecha = parse_timestamp(d["timestamp"])

        # 🔥 CORRECCIÓN: asegurar motivo
        if d.get("anomalia") and not d.get("motivo"):
            _, motivo = evaluar_anomalia(d["cpu"], d["temperatura"])
            d["motivo"] = motivo

        if sid not in latest or fecha > parse_timestamp(latest[sid]["timestamp"]):
            latest[sid] = d

    return Response(list(latest.values()))


# 📈 REPORTE
@api_view(['GET'])
def reporte_servidor(request, id_servidor):
    user = get_user_from_token(request)

    if user["role"] != "admin":
        return Response({"error": "Solo admin"}, status=403)

    rango = request.GET.get("rango")

    docs = db.collection("telemetria") \
        .where("id_servidor", "==", id_servidor) \
        .stream()

    limite = datetime.utcnow() - timedelta(hours=24)

    cpu_total = 0
    count = 0
    temp_max = 0
    anomalias = 0

    for doc in docs:
        d = doc.to_dict()

        fecha_doc = parse_timestamp(d["timestamp"])

        if rango == "ultimas_24h" and fecha_doc < limite:
            continue

        cpu_total += d["cpu"]
        count += 1

        if d["temperatura"] > temp_max:
            temp_max = d["temperatura"]

        if d["anomalia"]:
            anomalias += 1

    return Response({
        "cpu_promedio": round(cpu_total / count, 2) if count else 0,
        "temp_maxima": temp_max,
        "contador_anomalias": anomalias
    })