from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen
    allow_methods=["*"],  # Permite cualquier método HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite cualquier encabezado en las solicitudes
)
load_dotenv()  # Carga las variables del archivo .env

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

class ConsultaResponse(BaseModel):
    derechohabiencia: List[str]
    foto: List[str]
    huella: List[str]

def fetch_list(query: str, params: tuple) -> List[str]:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(query, params)
    result = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return result

@app.get("/consulta/{curp}", response_model=ConsultaResponse)
def consulta_curp(curp: str):
    # DERECHOHABIENCIA
    query_derecho = """
        SELECT institucion FROM (
            SELECT 'IMSS' AS institucion FROM imss.padron WHERE curp = %s
            UNION
            SELECT 'ISSSTE' FROM issste.padron_issste WHERE curp = %s
            UNION
            SELECT 'PEMEX' FROM pemex.padron_pemex WHERE curp = %s
            UNION
            SELECT 'IMSS-BIENESTAR' FROM imss_bienestar.padron WHERE curp = %s
        ) t
    """
    derechohabiencia = fetch_list(query_derecho, (curp, curp, curp, curp))

    # FOTO
    query_foto = """
        SELECT institucion FROM (
            SELECT 'SAT' AS institucion FROM sat.sat_fotos WHERE curp = %s AND b_foto = true
            UNION
            SELECT 'CONSAR' FROM consar.consar WHERE curp = %s
            UNION
            SELECT 'IMSS-BIENESTAR' FROM imss_bienestar.fotos_bienestar WHERE curp = %s
        ) t
    """
    foto = fetch_list(query_foto, (curp, curp, curp))

    # HUELLA
    query_huella = """
        SELECT institucion FROM (
            SELECT 'SRE' AS institucion FROM sre.resultados WHERE curp = %s
            UNION
            SELECT 'SAT' AS institucion FROM sat.sat_fotos WHERE curp = %s AND b_foto = true
            -- Agrega más tablas aquí si aplica
        ) t
    """
    huella = fetch_list(query_huella, (curp, curp))

    return ConsultaResponse(
        derechohabiencia=derechohabiencia,
        foto=foto,
        huella=huella
    )
