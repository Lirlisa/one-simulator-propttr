configs = {
    "mapas": ["santiago", "linares", "valparaiso"],
    "rangos": {
        "santiago": {"200m": 200, "500m": 500},
        "otros": {"500m": 500, "1km": 1000},
    },
    "routers": ["LoRaPropTTRRouter", "MaxPropRouterWithTTR", "PropTTRRouter"],
    "tasa_msjs": {"masmsj": 300, "menosmsj": 600},
    "densidad_nodos": [0.2, 0.5, 1],
    "rng": [1, 2, 3],
}

mapa_paths = {
    "santiago": "data/Santiago/roads_bigger.wkt",
    "linares": "data/Linares/roads_bigger.wkt",
    "valparaiso": "data/Valparaiso/roads_bigger.wkt",
}

mapa_pois = {
    "santiago": "data/Santiago/poi.wkt",
    "linares": "data/Linares/poi.wkt",
    "valparaiso": "data/Valparaiso/poi2.wkt",
}

areas_mapas = {"santiago": 10.56, "linares": 59.78, "valparaiso": 131.72}

nombres_simples = {
    "LoRaPropTTRRouter": "lorapropttr",
    "MaxPropRouterWithTTR": "maxprop",
    "PropTTRRouter": "propttr",
}

num_groups_base = {
    "santiago": 9,
    "linares": 3,
    "valparaiso": 6,
}

path_base = "configs/"


def gen_configs():
    for mapa in configs["mapas"]:
        rangos = configs["rangos"].get(mapa, configs["rangos"]["otros"])
        for rango in rangos:
            for router in configs["routers"]:
                for tasa_msj in configs["tasa_msjs"]:
                    for rng in configs["rng"]:
                        for densidad in configs["densidad_nodos"]:
                            cant_nodos_moviles = int(areas_mapas[mapa] * densidad)
                            cant_nodos_estaticos = num_groups_base[
                                mapa
                            ]  # 1 nodo por grupo
                            yield {
                                "mapa": mapa,
                                "nombre_escenario": f"config_{nombres_simples[router]}_{mapa}_{rango}_{tasa_msj}_dens{densidad}_{rng}",
                                "num_host_groups": cant_nodos_estaticos + 3,
                                "rango_transmision": rangos[rango],
                                "router": router,
                                "path_mapa": mapa_paths[mapa],
                                "path_pois": mapa_pois[mapa],
                                "rng": rng,
                                "intervalo_mensajes": configs["tasa_msjs"][tasa_msj],
                                "rango_nodo_destinatario": f"0, {num_groups_base[mapa]+cant_nodos_moviles-1}",
                                "cant_nodos_moviles": cant_nodos_moviles,
                                "cant_nodos_estaticos": cant_nodos_estaticos,
                                "cant_grupos_estaticos": num_groups_base[mapa],
                            }


with open(path_base + "plantilla_config.txt", "r") as file:
    plantilla_config = file.read().strip()

with open(path_base + "plantillas_grupo_nodo_movil.txt", "r") as file:
    plantilla_grupo_nodo_movil = file.read().strip()

with open(path_base + "grupos_santiago.txt", "r") as file:
    grupos_santiago = file.read().strip()

with open(path_base + "grupos_valparaiso.txt", "r") as file:
    grupos_valparaiso = file.read().strip()

with open(path_base + "grupos_linares.txt", "r") as file:
    grupos_linares = file.read().strip()

ids = ["", "p", "a", "b"]

dict_configs: dict[str, str] = {}
for config in gen_configs():
    cant_nodos_por_grupos_movil = config["cant_nodos_moviles"] // 3
    extras = config["cant_nodos_moviles"] % 3
    cant_grupos_estaticos = config["cant_grupos_estaticos"]
    if config["mapa"] == "santiago":
        grupos_base = grupos_santiago
    elif config["mapa"] == "valparaiso":
        grupos_base = grupos_valparaiso
    else:
        grupos_base = grupos_linares

    lista_grupos_moviles: list[str] = []
    for i in range(1, 4):
        lista_grupos_moviles.append(
            plantilla_grupo_nodo_movil.format(
                num_grupo=cant_grupos_estaticos + i,
                id_grupo=ids[i],
                num_host=cant_nodos_por_grupos_movil + (1 if extras > 0 else 0),
            )
        )
        extras = extras - 1 if extras > 0 else 0

    if config["nombre_escenario"] in dict_configs:
        print("ERROR!!")
        break

    dict_configs[config["nombre_escenario"]] = plantilla_config.format(
        nombre_escenario=config["nombre_escenario"],
        num_host_groups=config["num_host_groups"],
        rango_transmision=config["rango_transmision"],
        router=config["router"],
        config_grupos_nodos_estaticos=grupos_base,
        config_grupos_nodos_moviles="\n".join(lista_grupos_moviles),
        path_mapa=config["path_mapa"],
        path_pois=config["path_pois"],
        rng=config["rng"],
        intervalo_mensajes=config["intervalo_mensajes"],
        rango_nodo_destinatario=config["rango_nodo_destinatario"],
    )

for escenario in dict_configs:
    with open(f"{path_base}{escenario}.txt", "w") as file:
        file.write(dict_configs[escenario])
