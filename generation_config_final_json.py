#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

FICHIER_JSON = "fichier_intension.json"

with open(FICHIER_JSON, "r") as f:
    data = json.load(f)


#as 111
num_as_111 = "111"
liste_interface = data["liste_interface"]
data_as111 = data["as"]["as111"]
adresse_reseau_111 = data_as111["adresse_reseau"]
loopback_111 = data_as111["adresse_loopback"]

#as 222
num_as_222 = "222"
data_as222 = data["as"]["as222"]
adresse_reseau_222 = data_as222["adresse_reseau"]
loopback_222 = data_as222["adresse_loopback"]

#as 333
num_as_333 = "333"
data_as333 = data["as"]["as333"]
adresse_reseau_333 = data_as333["adresse_reseau"]
loopback_333 = data_as333["adresse_loopback"]

data_as_list= [data_as111, data_as222, data_as333]

def get_free_interface_in_as(as_data, nom_router):
    router_obj = as_data["routers"][nom_router]
    used_interfaces = []
    for voisin in router_obj["voisin"].values():
        if "interface" in voisin:
            used_interfaces.append(voisin["interface"])
    for intf in liste_interface:
        if intf not in used_interfaces:
            return intf
    return None  

def get_free_interface(nom_router):
    for as_data in data_as_list:
        if nom_router in as_data["routers"]:
            return get_free_interface_in_as(as_data, nom_router)
    return None
# {
#         "nom":"",
#         "router_id": "",
#         "adresse_ip": "",
#         "adresse_loopback": ""
#       }


id_loopback = 1
id_ip_adresse = 0
for as_data in data_as_list:
    for router in as_data["topologie"]:
        if router == "numero_as":  # Ignorer la clé numero_as
            continue
        if router not in as_data["routers"]:
            as_data["routers"][router] = {
                "nom": router,
                "router_id": as_data["numero_as"] + ".0.0." + str(id_loopback),
                "adresse_loopback": as_data["adresse_loopback"] + str(id_loopback) + "/32",
                "voisin": {
                    # "nom": "",
                    # "interface": "",
                    # "adresse_ip": "",
                    # "reseau" : ""
                }
            }
            id_loopback += 1



liens_deja_crees = set()   
for as_data in data_as_list: 
    for router in as_data["topologie"]:
        if router == "numero_as":  # Ignorer la clé numero_as
            continue
        for voisin in as_data["topologie"][router]:
            lien = tuple(sorted([router, voisin]))
            if lien in liens_deja_crees:
                continue
            liens_deja_crees.add(lien)
            intf_router = get_free_interface(router)
            intf_voisin = get_free_interface(voisin)
            ip_router = as_data["adresse_reseau"] + str(id_ip_adresse + 1) + "/30"
            ip_voisin = as_data["adresse_reseau"] + str(id_ip_adresse + 2) + "/30"
            reseau = as_data["adresse_reseau"] + str(id_ip_adresse) + "/30"
            as_data["routers"][router]["voisin"][voisin] = {
                "interface": intf_router,
                "nom": voisin,
                "adresse_ip": ip_router,
                "reseau": reseau
            }
            as_data["routers"][voisin]["voisin"][router] = {
                "interface": intf_voisin,
                "nom": router,
                "adresse_ip": ip_voisin,
                "reseau": reseau
            }

            id_ip_adresse += 4


if "topologie_client" in data_as111:
    for client_as_config in data_as111["topologie_client"]:
        client_as_num = client_as_config["numero_as"]
        # Trouver l'AS client
        client_as_data = None
        for as_data in data_as_list:
            if as_data["numero_as"] == client_as_num:
                client_as_data = as_data
                break
        
        if client_as_data:
            for pe_name in ["PE1", "PE2"]:
                if pe_name in client_as_config:
                    ce_list = client_as_config[pe_name]
                    for ce_name in ce_list:
                        if ce_name not in client_as_data["routers"]:
                            client_as_data["routers"][ce_name] = {
                                "nom": ce_name,
                                "router_id": client_as_data["numero_as"] + ".0.0." + str(id_loopback),
                                "adresse_loopback": client_as_data["adresse_loopback"] + str(id_loopback) + "/32",
                                "voisin": {}
                            }
                            id_loopback += 1
                        
                        lien = tuple(sorted([pe_name, ce_name]))
                        if lien not in liens_deja_crees:
                            liens_deja_crees.add(lien)
                            
                            intf_pe = get_free_interface(pe_name)
                            intf_ce = get_free_interface(ce_name)
                            
                            ip_pe = client_as_data["adresse_reseau"] + str(id_ip_adresse + 1) + "/30"
                            ip_ce = client_as_data["adresse_reseau"] + str(id_ip_adresse + 2) + "/30"
                            reseau = client_as_data["adresse_reseau"] + str(id_ip_adresse) + "/30"
                            
                            data_as111["routers"][pe_name]["voisin"][ce_name] = {
                                "interface": intf_pe,
                                "nom": ce_name,
                                "adresse_ip": ip_pe,
                                "reseau": reseau
                            }
                            
                            client_as_data["routers"][ce_name]["voisin"][pe_name] = {
                                "interface": intf_ce,
                                "nom": pe_name,
                                "adresse_ip": ip_ce,
                                "reseau": reseau
                            }
                            
                            id_ip_adresse += 4
            

with open("config_final_v2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, sort_keys=True)
print("JSON généré avec succès")