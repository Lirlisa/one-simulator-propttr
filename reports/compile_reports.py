import pandas as pd
import glob

filas = []


for filename in glob.glob("./config_*.txt"):
    _, protocolo, mapa, rango, masmsj, dens, rng, _ = filename.split("_")
    dens = dens[4:]
    with open(filename, "r") as file:
        lineas = file.readlines()
        filas.append(
            [
                protocolo,
                mapa,
                rango,
                masmsj == "masmsj",
                dens,
                rng,
                float(lineas[9].split(":")[1].strip()),
                float(lineas[11].split(":")[1].strip()),
                float(lineas[12].split(":")[1].strip()),
                float(lineas[14].split(":")[1].strip()),
            ]
        )

df = pd.DataFrame(
    data=filas,
    columns=[
        "protocolo",
        "mapa",
        "rango",
        "masmsj",
        "dens",
        "rng",
        "delivery_prob",
        "overhead_ratio",
        "latency_avg",
        "hopcount_avg",
    ],
)
df.to_csv("reportes.csv")
