from fastapi import FastAPI, Query
from datetime import datetime
import httpx  # Cliente HTTP para consumir los microservicios externos

app = FastAPI()

# Aquí luego pondrás las IPs públicas reales cuando estén desplegadas
TEMBLOR_SERVICE_URL = "http://34.229.153.176:8001"
COMPORTAMIENTO_SERVICE_URL = "http://3.80.69.181:8002"

@app.get("/")
async def root():
    return {"message": "Microservicio de Clima conectado con Temblor y Comportamiento"}


@app.get("/clima")
async def obtener_clima(
    ciudad: str = Query(..., description="Nombre de la ciudad"),
    fecha: str = Query(..., description="Fecha en formato YYYY-MM-DD")
):
    """
    Devuelve un clima simulado y además consulta los microservicios externos
    de temblores y comportamiento.
    """
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return {"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}

    # ==== Simulación de clima ====
    condiciones = ["Soleado", "Nublado", "Lluvia", "Tormenta", "Parcialmente nublado"]
    temp_base = hash(ciudad.lower()) % 15 + 15
    temp = temp_base + (fecha_dt.day % 5)
    condicion = condiciones[(hash(ciudad + fecha) % len(condiciones))]

    clima = {
        "ciudad": ciudad,
        "fecha": fecha,
        "temperatura_celsius": temp,
        "condicion": condicion
    }

    # ==== Llamadas a otros microservicios ====
    async with httpx.AsyncClient() as client:
        temblor_data = {}
        comportamiento_data = {}

        try:
            r1 = await client.get(f"{TEMBLOR_SERVICE_URL}/proyeccion_temblor",
                                  params={"ciudad": ciudad, "fecha": fecha})
            temblor_data = r1.json()
        except Exception as e:
            temblor_data = {"error": f"No se pudo conectar con el microservicio Temblor: {str(e)}"}

        try:
            r2 = await client.get(f"{COMPORTAMIENTO_SERVICE_URL}/comportamiento",
                                  params={"ciudad": ciudad, "fecha": fecha})
            comportamiento_data = r2.json()
        except Exception as e:
            comportamiento_data = {"error": f"No se pudo conectar con el microservicio Comportamiento: {str(e)}"}

    return {
        "clima": clima,
        "temblor": temblor_data,
        "comportamiento": comportamiento_data
    }
