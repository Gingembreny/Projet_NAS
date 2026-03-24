#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# --- Topologies internes ---
voisin1 = {
          "R2": ["R3"],
          "R3": ["R4"],
          "R4": ["R5"]
        } # AS 111


FICHIER_JSON = "fichier_intension.json"

with open(FICHIER_JSON, "r") as f:
    data = json.load(f)

def get_free_interface(nom_as, nom_router):
    router_obj = data["as"][nom_as]["router"][nom_router]
    for intf in data["liste_interface"]:
        if not router_obj["interface"][intf]:
            return intf


# initialisation des routeurs et Loopbacks
for nom_as, content in data["as"].items():
    all_routers = set(content["graphe_router"]["ibgp"].keys())
    for v in content["graphe_router"]["ibgp"].values():
        all_routers.update(v)
    for r in all_routers:
        num = r.replace("R", "")
        content["router"][r] = {
            "router_id": f"{num}.{num}.{num}.{num}",
            "loopback": f"{content['adresse_reseau']}:{num}/128",
            "interface": {intf: {} for intf in data["liste_interface"]}
        }

#configuration iBGP 
for nom_as, content in data["as"].items():
    prefixe = content["adresse_reseau"]
    compteur_lien = 1
    
    for r_source, voisins in content["graphe_router"]["ibgp"].items():
        for r_dest in voisins:
            intf_s = get_free_interface(nom_as, r_source)
            intf_d = get_free_interface(nom_as, r_dest)
            if intf_s and intf_d:
                subnet = f"{prefixe}{compteur_lien}" # 2001:prefixe(ex 111):numlien(ex 1)::1ou2/64
                data["as"][nom_as]["router"][r_source]["interface"][intf_s] = {"voisin": r_dest, "adresse_ip": f"{subnet}::1/64"}
                data["as"][nom_as]["router"][r_dest]["interface"][intf_d] = {"voisin": r_source, "adresse_ip": f"{subnet}::2/64"}
                compteur_lien += 1

#configuration eBGP                 
for i in data['as']:
    for r, donnee in data['as'][i]['graphe_router']['ebgp'].items():
        for r2 in data['as'][i]['router']:
            if r == r2:
                free_interface = get_free_interface(i, r2)
                data['as'][i]['router'][r2]['interface'][free_interface] = {
                                                        "voisin": donnee["voisin"],
                                                        "relation": donnee["relation"],
                                                        "adresse_ip": donnee["adresse_ip"]
                                                        }

# coûts OSPF 
for nom_as, content in data["as"].items():
    if content.get('numero_as') == '222' and 'metrique_ospf' in content:
        for r_nom, config_metrique in content['metrique_ospf'].items():
            intf_nom = config_metrique['interface']
            if r_nom in content['router']:
                if intf_nom not in content['router'][r_nom]['interface']:
                     content['router'][r_nom]['interface'][intf_nom] = {}
                
                content['router'][r_nom]['interface'][intf_nom]['cost'] = '50'

                
with open("config_final_v2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, sort_keys=True)
print("JSON généré avec succès")