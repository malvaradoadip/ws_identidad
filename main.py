from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from vigencia import obtener_vigencias  # Importa la función

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Permite cualquier origen
#     allow_methods=["*"],  # Permite cualquier método HTTP (GET, POST, etc.)
#     allow_headers=["*"],  # Permite cualquier encabezado en las solicitudes
# )
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
    nombre: str = None
    apellido_paterno: str = None
    apellido_materno: str = None

def fetch_list(query: str, params: tuple) -> List[str]:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(query, params)
    result = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return result

def fetch_one_persona(query: str, params: tuple) -> dict:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {
            "nombre": row[0],
            "apellido_paterno": row[1],
            "apellido_materno": row[2]
        }
    return None

@app.get("/consulta/{curp}", response_model=ConsultaResponse)
def consulta_curp(curp: str):
    derechohabiencia_vigencia = obtener_vigencias(curp)

    query_derecho = """
        SELECT institucion FROM (
            SELECT 'PEMEX' AS institucion FROM pemex.padron_pemex WHERE curp = %s
            UNION
            SELECT 'IMSS-BIENESTAR' FROM imss_bienestar.padron WHERE curp = %s
        ) t
    """
    derechohabiencia_sql = fetch_list(query_derecho, (curp, curp))
    derechohabiencia = derechohabiencia_vigencia + derechohabiencia_sql

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

    query_huella = """
        SELECT institucion FROM (
            SELECT 'SRE' AS institucion FROM sre.resultados WHERE curp = %s
            UNION
            SELECT 'SAT' AS institucion FROM sat.sat_fotos WHERE curp = %s AND b_foto = true
        ) t
    """
    huella = fetch_list(query_huella, (curp, curp))

    # Buscar el primer registro desencriptado en orden IMSS, ISSSTE, PEMEX, IMSS-BIENESTAR
    persona = None

    # IMSS
    imss_key = os.getenv("IMSS_KEY")
    query_imss = """
        SELECT 
            pgp_sym_decrypt(nombre::bytea, %s) AS nombre,
            pgp_sym_decrypt(apellido_paterno::bytea, %s) AS apellido_paterno,
            pgp_sym_decrypt(apellido_materno::bytea, %s) AS apellido_materno
        FROM imss.padron WHERE curp = %s LIMIT 1
    """
    persona = fetch_one_persona(query_imss, (imss_key, imss_key, imss_key, curp))

    # ISSSTE
    if not persona:
        issste_key = os.getenv("ISSSTE_KEY")
        query_issste = """
            SELECT 
                pgp_sym_decrypt(nombre::bytea, %s) AS nombre,
                pgp_sym_decrypt(apellido_paterno::bytea, %s) AS apellido_paterno,
                pgp_sym_decrypt(apellido_materno::bytea, %s) AS apellido_materno
            FROM issste.padron_issste WHERE curp = %s LIMIT 1
        """
        persona = fetch_one_persona(query_issste, (issste_key, issste_key, issste_key, curp))

    # PEMEX
    if not persona:
        pemex_key = os.getenv("PEMEX_KEY")
        query_pemex = """
            SELECT 
                pgp_sym_decrypt(nombre::bytea, %s) AS nombre,
                pgp_sym_decrypt(apellido_paterno::bytea, %s) AS apellido_paterno,
                pgp_sym_decrypt(apellido_materno::bytea, %s) AS apellido_materno
            FROM pemex.padron_pemex WHERE curp = %s LIMIT 1
        """
        persona = fetch_one_persona(query_pemex, (pemex_key, pemex_key, pemex_key, curp))

    # IMSS-BIENESTAR
    if not persona:
        bienestar_key = os.getenv("BIENESTAR_KEY")
        query_bienestar = """
            SELECT 
                pgp_sym_decrypt(nombre::bytea, %s) AS nombre,
                pgp_sym_decrypt(apellido_paterno::bytea, %s) AS apellido_paterno,
                pgp_sym_decrypt(apellido_materno::bytea, %s) AS apellido_materno
            FROM imss_bienestar.padron WHERE curp = %s LIMIT 1
        """
        persona = fetch_one_persona(query_bienestar, (bienestar_key, bienestar_key, bienestar_key, curp))

    return ConsultaResponse(
        derechohabiencia=derechohabiencia,
        foto=foto,
        huella=huella,
        nombre=persona["nombre"] if persona else None,
        apellido_paterno=persona["apellido_paterno"] if persona else None,
        apellido_materno=persona["apellido_materno"] if persona else None
    )
