#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

FICHIER_JSON = "fichier_intension.json"

with open(FICHIER_JSON, "r") as f:
    data = json.load(f)


#as 111
num_as = "111"
liste_interface = data["liste_interface"]
data_as111 = data["as"]["as111"]
adresse_reseau = data_as111["adresse_reseau"]

def get_free_interface(nom_router):
    router_obj = data_as111["routers"][nom_router]
    used_interfaces = []
    for voisin in router_obj["voisin"].values():
        if "interface" in voisin:
            used_interfaces.append(voisin["interface"])
    for intf in liste_interface:
        if intf not in used_interfaces:
            return intf
    return None  

# {
#         "nom":"",
#         "router_id": "",
#         "adresse_ip": "",
#         "adresse_loopback": ""
#       }

id_loopback = 1
id_ip_adresse = 0

for router in data_as111["topologie"]:
    if router not in data_as111["routers"]:
        data_as111["routers"][router] = {
            "nom": router,
            "router_id": num_as + ".0.0." + str(id_loopback),
            "adresse_loopback": adresse_reseau + str(id_loopback) + "/32",
            "voisin": {
                # "nom": "",
                # "interface": "",
                # "adresse_ip": "",
                # "reseau" : ""
            }
        }
        id_loopback += 1



liens_deja_crees = set()

for router in data_as111["topologie"]:
    for voisin in data_as111["topologie"][router]:
        lien = tuple(sorted([router, voisin]))
        if lien in liens_deja_crees:
            continue
        liens_deja_crees.add(lien)
        intf_router = get_free_interface(router)
        intf_voisin = get_free_interface(voisin)
        ip_router = adresse_reseau + str(id_ip_adresse + 1) + "/30"
        ip_voisin = adresse_reseau + str(id_ip_adresse + 2) + "/30"
        reseau = adresse_reseau + str(id_ip_adresse) + "/30"
        data_as111["routers"][router]["voisin"][voisin] = {
            "interface": intf_router,
            "nom": voisin,
            "adresse_ip": ip_router,
            "reseau": reseau
        }
        data_as111["routers"][voisin]["voisin"][router] = {
            "interface": intf_voisin,
            "nom": router,
            "adresse_ip": ip_voisin,
            "reseau": reseau
        }

        id_ip_adresse += 4
            

with open("config_final_v2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, sort_keys=True)
print("JSON généré avec succès")