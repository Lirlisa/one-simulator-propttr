import pandas as pd
import numpy as np
from string import Template


df = pd.read_csv("reportes.csv")

escenarios = {}

for row in df.itertuples():
    if row.mapa not in escenarios:
        escenarios[row.mapa] = {}
    if row.protocolo not in escenarios[row.mapa]:
        escenarios[row.mapa][row.protocolo] = {}
    if row.rango not in escenarios[row.mapa][row.protocolo]:
        escenarios[row.mapa][row.protocolo][row.rango] = {}
    if row.dens not in escenarios[row.mapa][row.protocolo][row.rango]:
        escenarios[row.mapa][row.protocolo][row.rango][row.dens] = {}
    string_masmsj = "masmsj" if row.masmsj else "menosmsj"
    if string_masmsj not in escenarios[row.mapa][row.protocolo][row.rango][row.dens]:
        escenarios[row.mapa][row.protocolo][row.rango][row.dens][string_masmsj] = []
    escenarios[row.mapa][row.protocolo][row.rango][row.dens][string_masmsj].append(row)


with open("plantilla_tabla.txt", "r", encoding="utf-8") as file:
    plantilla_tabla = Template(file.read().strip())

with open("plantilla_fila.txt", "r", encoding="utf-8") as file:
    plantilla_fila = file.read().strip()

tablas_masmsj: list[str] = []
tablas_menosmsj: list[str] = []
nombres_mapas = {
    "linares": "Linares",
    "santiago": "Santiago",
    "valparaiso": "Valparaíso",
}
promedios = {}
variaciones_cant_msj = {}
for mapa in escenarios:
    if mapa not in promedios:
        promedios[mapa] = {}
    if mapa not in variaciones_cant_msj:
        variaciones_cant_msj[mapa] = {}
    filas_masmsj: list[str] = []
    filas_menosmsj: list[str] = []
    for protocolo in escenarios[mapa]:
        if protocolo not in promedios[mapa]:
            promedios[mapa][protocolo] = {}
            promedios[mapa][protocolo]["delivery_prob"] = []
            promedios[mapa][protocolo]["overhead_ratio"] = []
            promedios[mapa][protocolo]["latency_avg"] = []
            promedios[mapa][protocolo]["hopcount_avg"] = []
        if protocolo not in variaciones_cant_msj[mapa]:
            variaciones_cant_msj[mapa][protocolo] = {}
        for rango in escenarios[mapa][protocolo]:
            if rango not in variaciones_cant_msj[mapa][protocolo]:
                variaciones_cant_msj[mapa][protocolo][rango] = {}
            for dens in escenarios[mapa][protocolo][rango]:
                if dens not in variaciones_cant_msj[mapa][protocolo][rango]:
                    variaciones_cant_msj[mapa][protocolo][rango][dens] = {}
                for masmsj in escenarios[mapa][protocolo][rango][dens]:
                    r1, r2, r3 = escenarios[mapa][protocolo][rango][dens][masmsj]
                    delivery_prob_vec = np.array(
                        [r1.delivery_prob, r2.delivery_prob, r3.delivery_prob]
                    )
                    overhead_ratio_vec = np.array(
                        [r1.overhead_ratio, r2.overhead_ratio, r3.overhead_ratio]
                    )
                    latency_avg_vec = np.array(
                        [r1.latency_avg, r2.latency_avg, r3.latency_avg]
                    )
                    hopcount_avg_vec = np.array(
                        [r1.hopcount_avg, r2.hopcount_avg, r3.hopcount_avg]
                    )
                    delivery_prob = delivery_prob_vec.mean()
                    delivery_prob_std = delivery_prob_vec.std()
                    overhead_ratio = overhead_ratio_vec.mean()
                    overhead_ratio_std = overhead_ratio_vec.std()
                    latency_avg = latency_avg_vec.mean()
                    latency_avg_std = latency_avg_vec.std()
                    hopcount_avg = hopcount_avg_vec.mean()
                    hopcount_avg_std = hopcount_avg_vec.std()

                    promedios[mapa][protocolo]["delivery_prob"].append(delivery_prob)
                    promedios[mapa][protocolo]["overhead_ratio"].append(overhead_ratio)
                    promedios[mapa][protocolo]["latency_avg"].append(latency_avg)
                    promedios[mapa][protocolo]["hopcount_avg"].append(hopcount_avg)

                    fila = plantilla_fila.format(
                        mapa=nombres_mapas[mapa],
                        radio=rango,
                        protocolo=protocolo,
                        densidad=dens,
                        overhead=rf"{overhead_ratio:.2f}\textpm {overhead_ratio_std:.2f}",
                        saltos=rf"{hopcount_avg:.2f}\textpm {hopcount_avg_std:.2f}",
                        latencia=rf"{latency_avg:.2f}\textpm {latency_avg_std:.2f}",
                        tasa_entrega=rf"{delivery_prob:.4f}\textpm {delivery_prob_std:.4f}",
                    )
                    if masmsj == "masmsj":
                        filas_masmsj.append(fila)
                    else:
                        filas_menosmsj.append(fila)

                    if masmsj not in variaciones_cant_msj[mapa][protocolo][rango][dens]:
                        variaciones_cant_msj[mapa][protocolo][rango][dens][masmsj] = {}

                    variaciones_cant_msj[mapa][protocolo][rango][dens][masmsj][
                        "delivery_prob"
                    ] = delivery_prob
                    variaciones_cant_msj[mapa][protocolo][rango][dens][masmsj][
                        "overhead_ratio"
                    ] = overhead_ratio
                    variaciones_cant_msj[mapa][protocolo][rango][dens][masmsj][
                        "latency_avg"
                    ] = latency_avg
                    variaciones_cant_msj[mapa][protocolo][rango][dens][masmsj][
                        "hopcount_avg"
                    ] = hopcount_avg
    tablas_masmsj.append(
        plantilla_tabla.substitute(
            mapa=mapa,
            mapa_bien_escrito=nombres_mapas[mapa],
            mensaje_cant_msj="con alta tasa de mensajes",
            filas="\n".join(filas_masmsj),
            masmsj="masmsj",
        )
    )
    tablas_menosmsj.append(
        plantilla_tabla.substitute(
            mapa=mapa,
            mapa_bien_escrito=nombres_mapas[mapa],
            mensaje_cant_msj="con baja tasa de mensajes",
            filas="\n".join(filas_menosmsj),
            masmsj="menosmsj",
        )
    )

tablas: list[str] = []
for a, b in zip(tablas_masmsj, tablas_menosmsj):
    tablas.append(a)
    tablas.append(b)


with open("tablitas.txt", "w", encoding="utf-8") as file:
    file.write("\n\n".join(tablas))


with open("plantilla_tabla_prom.txt", "r", encoding="utf-8") as file:
    plantilla_tabla_prom = Template(file.read().strip())

with open("plantilla_fila_prom.txt", "r", encoding="utf-8") as file:
    plantilla_fila_prom = file.read().strip()

lista_filas = []
for mapa in promedios:
    for protocolo in promedios[mapa]:
        overhead_ratio = np.array(promedios[mapa][protocolo]["overhead_ratio"]).mean()
        overhead_ratio_std = np.array(
            promedios[mapa][protocolo]["overhead_ratio"]
        ).std()
        hopcount_avg = np.array(promedios[mapa][protocolo]["hopcount_avg"]).mean()
        hopcount_avg_std = np.array(promedios[mapa][protocolo]["hopcount_avg"]).std()
        latency_avg = np.array(promedios[mapa][protocolo]["latency_avg"]).mean()
        latency_avg_std = np.array(promedios[mapa][protocolo]["latency_avg"]).std()
        delivery_prob = np.array(promedios[mapa][protocolo]["delivery_prob"]).mean()
        delivery_prob_std = np.array(promedios[mapa][protocolo]["delivery_prob"]).std()
        lista_filas.append(
            plantilla_fila_prom.format(
                mapa=nombres_mapas[mapa],
                protocolo=protocolo,
                overhead=rf"{overhead_ratio:.2f}\textpm {overhead_ratio_std:.2f}",
                saltos=rf"{hopcount_avg:.2f}\textpm {hopcount_avg_std:.2f}",
                latencia=rf"{latency_avg:.2f}\textpm {latency_avg_std:.2f}",
                tasa_entrega=rf"{delivery_prob:.4f}\textpm {delivery_prob_std:.4f}",
            )
        )

with open("tablita_prom.txt", "w", encoding="utf-8") as file:
    file.write(plantilla_tabla_prom.substitute(filas="\n".join(lista_filas)))

lista_variaciones_cant_msj = []
for mapa in variaciones_cant_msj:
    for protocolo in variaciones_cant_msj[mapa]:
        for rango in variaciones_cant_msj[mapa][protocolo]:
            for dens in variaciones_cant_msj[mapa][protocolo][rango]:
                overhead_ratio = (
                    variaciones_cant_msj[mapa][protocolo][rango][dens]["masmsj"][
                        "overhead_ratio"
                    ]
                    / variaciones_cant_msj[mapa][protocolo][rango][dens]["menosmsj"][
                        "overhead_ratio"
                    ]
                ) - 1
                hopcount_avg = (
                    variaciones_cant_msj[mapa][protocolo][rango][dens]["masmsj"][
                        "hopcount_avg"
                    ]
                    / variaciones_cant_msj[mapa][protocolo][rango][dens]["menosmsj"][
                        "hopcount_avg"
                    ]
                ) - 1
                latency_avg = (
                    variaciones_cant_msj[mapa][protocolo][rango][dens]["masmsj"][
                        "latency_avg"
                    ]
                    / variaciones_cant_msj[mapa][protocolo][rango][dens]["menosmsj"][
                        "latency_avg"
                    ]
                ) - 1
                delivery_prob = (
                    variaciones_cant_msj[mapa][protocolo][rango][dens]["masmsj"][
                        "delivery_prob"
                    ]
                    / variaciones_cant_msj[mapa][protocolo][rango][dens]["menosmsj"][
                        "delivery_prob"
                    ]
                ) - 1
                lista_variaciones_cant_msj.append(
                    plantilla_fila.format(
                        mapa=nombres_mapas[mapa],
                        radio=rango,
                        protocolo=protocolo,
                        densidad=dens,
                        overhead=(
                            "\cellcolor[HTML]{67FD9A}"
                            if overhead_ratio >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*overhead_ratio):.2f}",
                        saltos=(
                            "\cellcolor[HTML]{67FD9A}"
                            if hopcount_avg >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*hopcount_avg):.2f}",
                        latencia=(
                            "\cellcolor[HTML]{67FD9A}"
                            if latency_avg >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*latency_avg):.2f}",
                        tasa_entrega=(
                            "\cellcolor[HTML]{67FD9A}"
                            if delivery_prob >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*delivery_prob):.2f}",
                    )
                )

with open("plantilla_variaciones.txt", "r", encoding="utf-8") as file:
    plantilla_variaciones = Template(file.read().strip())

with open("tablita_variaciones.txt", "w", encoding="utf-8") as file:
    file.write(
        plantilla_variaciones.substitute(filas="\n".join(lista_variaciones_cant_msj))
    )

# variaciones de densidad de nodos

with open("plantilla_fila_variaciones_nodos.txt", "r", encoding="utf-8") as file:
    plantilla_fila_variaciones_nodos = file.read().strip()


lista_filas_variaciones_nodos_0 = []
lista_filas_variaciones_nodos_1 = []
for mapa in escenarios:
    for protocolo in escenarios[mapa]:
        for rango in escenarios[mapa][protocolo]:
            for masmsj in ["masmsj", "menosmsj"]:
                ######## 0.5/0.2 ###########
                delivery_prob_0 = (
                    np.array(
                        [
                            row.delivery_prob
                            for row in escenarios[mapa][protocolo][rango][0.5][masmsj]
                        ]
                    ).mean()
                    / np.array(
                        [
                            row.delivery_prob
                            for row in escenarios[mapa][protocolo][rango][0.2][masmsj]
                        ]
                    ).mean()
                ) - 1
                overhead_ratio_0 = (
                    np.array(
                        [
                            row.overhead_ratio
                            for row in escenarios[mapa][protocolo][rango][0.5][masmsj]
                        ]
                    ).mean()
                    / np.array(
                        [
                            row.overhead_ratio
                            for row in escenarios[mapa][protocolo][rango][0.2][masmsj]
                        ]
                    ).mean()
                ) - 1
                latency_avg_0 = (
                    np.array(
                        [
                            row.latency_avg
                            for row in escenarios[mapa][protocolo][rango][0.5][masmsj]
                        ]
                    ).mean()
                    / np.array(
                        [
                            row.latency_avg
                            for row in escenarios[mapa][protocolo][rango][0.2][masmsj]
                        ]
                    ).mean()
                ) - 1
                hopcount_avg_0 = (
                    np.array(
                        [
                            row.hopcount_avg
                            for row in escenarios[mapa][protocolo][rango][0.5][masmsj]
                        ]
                    ).mean()
                    / np.array(
                        [
                            row.hopcount_avg
                            for row in escenarios[mapa][protocolo][rango][0.2][masmsj]
                        ]
                    ).mean()
                ) - 1
                lista_filas_variaciones_nodos_0.append(
                    plantilla_fila_variaciones_nodos.format(
                        mapa=nombres_mapas[mapa],
                        radio=rango,
                        protocolo=protocolo,
                        overhead=(
                            "\cellcolor[HTML]{67FD9A}"
                            if overhead_ratio_0 >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*overhead_ratio_0):.2f}",
                        saltos=(
                            "\cellcolor[HTML]{67FD9A}"
                            if hopcount_avg_0 >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*hopcount_avg_0):.2f}",
                        latencia=(
                            "\cellcolor[HTML]{67FD9A}"
                            if latency_avg_0 >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*latency_avg_0):.2f}",
                        tasa_entrega=(
                            "\cellcolor[HTML]{67FD9A}"
                            if delivery_prob_0 >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*delivery_prob_0):.2f}",
                    )
                )

                ########## 1/0.5 ############
                delivery_prob_1 = (
                    np.array(
                        [
                            row.delivery_prob
                            for row in escenarios[mapa][protocolo][rango][1][masmsj]
                        ]
                    ).mean()
                    / np.array(
                        [
                            row.delivery_prob
                            for row in escenarios[mapa][protocolo][rango][0.5][masmsj]
                        ]
                    ).mean()
                ) - 1
                overhead_ratio_1 = (
                    np.array(
                        [
                            row.overhead_ratio
                            for row in escenarios[mapa][protocolo][rango][1][masmsj]
                        ]
                    ).mean()
                    / np.array(
                        [
                            row.overhead_ratio
                            for row in escenarios[mapa][protocolo][rango][0.5][masmsj]
                        ]
                    ).mean()
                ) - 1
                latency_avg_1 = (
                    np.array(
                        [
                            row.latency_avg
                            for row in escenarios[mapa][protocolo][rango][1][masmsj]
                        ]
                    ).mean()
                    / np.array(
                        [
                            row.latency_avg
                            for row in escenarios[mapa][protocolo][rango][0.5][masmsj]
                        ]
                    ).mean()
                ) - 1
                hopcount_avg_1 = (
                    np.array(
                        [
                            row.hopcount_avg
                            for row in escenarios[mapa][protocolo][rango][1][masmsj]
                        ]
                    ).mean()
                    / np.array(
                        [
                            row.hopcount_avg
                            for row in escenarios[mapa][protocolo][rango][0.5][masmsj]
                        ]
                    ).mean()
                ) - 1
                lista_filas_variaciones_nodos_1.append(
                    plantilla_fila_variaciones_nodos.format(
                        mapa=nombres_mapas[mapa],
                        radio=rango,
                        protocolo=protocolo,
                        overhead=(
                            "\cellcolor[HTML]{67FD9A}"
                            if overhead_ratio_1 >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*overhead_ratio_1):.2f}",
                        saltos=(
                            "\cellcolor[HTML]{67FD9A}"
                            if hopcount_avg_1 >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*hopcount_avg_1):.2f}",
                        latencia=(
                            "\cellcolor[HTML]{67FD9A}"
                            if latency_avg_1 >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*latency_avg_1):.2f}",
                        tasa_entrega=(
                            "\cellcolor[HTML]{67FD9A}"
                            if delivery_prob_1 >= 0
                            else "\cellcolor[HTML]{FD6864}"
                        )
                        + rf"{(100*delivery_prob_1):.2f}",
                    )
                )
with open("plantilla_variaciones_nodos.txt", "r", encoding="utf-8") as file:
    plantilla_variaciones_nodos = Template(file.read().strip())

with open("tablita_variaciones_nodos_0.txt", "w", encoding="utf-8") as file:
    file.write(
        plantilla_variaciones_nodos.substitute(
            tag="variacion_nodos_0",
            texto_variacion_densidad="desde 0,2 nodos/km^{2} a 0,5 nodos/km^{2}",
            filas="\n".join(lista_filas_variaciones_nodos_0),
        )
    )

with open("tablita_variaciones_nodos_1.txt", "w", encoding="utf-8") as file:
    file.write(
        plantilla_variaciones_nodos.substitute(
            tag="variacion_nodos_1",
            texto_variacion_densidad="desde 0,5 nodos/km^{2} a 1 nodos/km^{2}",
            filas="\n".join(lista_filas_variaciones_nodos_1),
        )
    )
