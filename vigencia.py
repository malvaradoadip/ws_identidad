import requests

def obtener_vigencia(curp):
    vigencias = []

    # Consulta IMSS
    url_imss = f"https://verificaimss.imss.gob.mx/VigenciaIMSSREST/Consulta/{curp}"
    try:
        resp_imss = requests.get(url_imss, timeout=10)
        if resp_imss.status_code == 200 and "<codigo>4</codigo>" in resp_imss.text:
            vigencias.append("IMSS")
    except Exception as e:
        print(f"Error al consultar IMSS: {e}")

    # Consulta ISSSTE
    url_issste = f"https://consultaissste.issste.gob.mx/VigenciaISSSTERest/Consulta/{curp}"
    try:
        resp_issste = requests.get(url_issste, timeout=10)
        if resp_issste.status_code == 200 and "<codigo>4</codigo>" in resp_issste.text:
            vigencias.append("ISSSTE")
    except Exception as e:
        print(f"Error al consultar ISSSTE: {e}")

    return vigencias

# Ejemplo de uso
if __name__ == "__main__":
    curp = "GOCF850710MOCNRL03"
    resultado = obtener_vigencia(curp)
    print(resultado)
