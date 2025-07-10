import requests

API_URL = "http://localhost:8087/consulta/"

curps = [
"AAAA830719HHGLNL00",
    "AAAA981017MDFLLH08",
    "AAAD020823MVZNGRA5",
    "AAAD891207HTCVVN04",
    "AAAE880801MSPLLS06",
    "AAAG630916MTCVVD09",
    "AAAG900113HPLPGR04",
    "AAAJ860224HTCLLV04",
    "AAAK980114MZSLVR04",
    "AAAM880412MTSLCY04",
    "AAAM920111MCSLNG09",
    "AAAN830609MVZLLN03",
    "AAAR830301HGRLDB01",
    "AAAS840902MDFLCN05",
    "AAAV981106MTLXGL04",
    "AABC961119HVZLRR09",
    "AABE590131MMCYRL05",
    "AABG520413MDFLRD04",
    "AABL050320HMCBRNA3",
    "AABL220704MDFNRNA9"
]

for curp in curps:
    response = requests.get(API_URL + curp)
    print(f"CURP: {curp}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
    print("-" * 40)