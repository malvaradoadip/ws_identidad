import os
import requests
from dotenv import load_dotenv

# Cargar el token ISSSTE del archivo .env
load_dotenv()

def obtener_vigencias(curp):
    vigencias = []

    # 1. Consulta IMSS (sin autenticación)
    url_imss = f"https://verificaimss.imss.gob.mx/VigenciaIMSSREST/Consulta/{curp}"
    try:
        resp_imss = requests.get(url_imss, timeout=10)
        if resp_imss.status_code == 200 and "<codigo>4</codigo>" in resp_imss.text:
            vigencias.append("IMSS")
    except Exception as e:
        print(f"Error al consultar IMSS: {e}")

    # 2. Consulta ISSSTE (con autenticación Bearer)
    token = os.getenv("ISSSTE_TOKEN")
    if not token:
        print("Advertencia: No se encontró el token ISSSTE en el archivo .env. Omite consulta ISSSTE.")
    else:
        url_issste = f"https://api-dev.issste.gob.mx/api/sipe/consulta/{curp}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp_issste = requests.get(url_issste, headers=headers, timeout=10)
            if resp_issste.status_code == 200 and "tipo_derechohabiencia" in resp_issste.text:
                vigencias.append("ISSSTE")
        except Exception as e:
            print(f"Error al consultar ISSSTE: {e}")

    return vigencias

# Ejemplo de uso:
if __name__ == "__main__":
    curp = "GOMJ710104HJCMRN00"
    resultado = obtener_vigencias(curp)
    print(resultado)
