#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

# --- Configuration des Chemins ---
CHEMIN_PROJET = "/Users/gaillardou/Desktop/gns/testfinal/project-files/dynamips/"
FICHIER_JSON = "config_final.json"

mapping_routeur_uuid = {
    "PE1": "/Users/gaillardou/Desktop/GitHub/Projet_NAS/NAS_gns/project-files/dynamips/3a059d65-05f2-4abd-a421-2534fa565e97",
    "P1": "/Users/gaillardou/Desktop/GitHub/Projet_NAS/NAS_gns/project-files/dynamips/81f36527-0efe-4ada-b429-77b425b5b8b1",
    "P2": "/Users/gaillardou/Desktop/GitHub/Projet_NAS/NAS_gns/project-files/dynamips/81f36527-0efe-4ada-b429-77b425b5b8b1",
    "P3": "/Users/gaillardou/Desktop/GitHub/Projet_NAS/NAS_gns/project-files/dynamips/65a3a450-a200-4ab8-bb2a-67cc36b0bed7",
    "PE2": "/Users/gaillardou/Desktop/GitHub/Projet_NAS/NAS_gns/project-files/dynamips/ad0c50d6-85f9-4965-8b7d-4f4bc5a98c2a",
    "RR": "/Users/gaillardou/Desktop/GitHub/Projet_NAS/NAS_gns/project-files/dynamips/22d9e17b-923e-47c4-a224-686e371a1472"
}

with open(FICHIER_JSON, "r") as f:
    donnees = json.load(f)

def get_router_info(nom_r):
    for as_nom, as_data in donnees["as"].items():
        if nom_r in as_data["router"]:
            return as_data, as_data["router"][nom_r]

def generer_config(nom_r):
    as_data, r_data = get_router_info(nom_r)
    as_num = as_data["numero_as"]
    igp = as_data["protocole_igp"]
    
    config = [
        "!", f"hostname {nom_r}", "!",
         "ipv6 unicast-routing", "ip bgp-community new-format","!"
    ]

    # interface physique
    ebgp_voisins = []
    ebgp_phys_ips = [] 
    
    for int_name, details in r_data["interface"].items():
        if details != {}:
            config += [
                f"interface {int_name}",
                " no ip address", " ipv6 enable",
                f" ipv6 address {details['adresse_ip']}"
            ]
            # changement métrique ospf
            if 'cost' in details:
                config.append(f" ipv6 ospf cost {details['cost']}")
            
            # active rip ou ospf
            if igp == "rip": 
                config.append(f" ipv6 rip {as_num} enable")
            elif igp == "ospf": 
                config.append(f" ipv6 ospf {as_num} area 0")
            
            # vérifie lien ebgp
            if 'relation' in details:
                ebgp_voisins.append(details)
           
            config.append(" no shutdown")
            config.append("!")

    # interface loopback
    config += [f"interface Loopback0", f" ipv6 address {r_data['loopback']}", " no ip address", " ipv6 enable"]
    if igp == "rip": 
        config.append(f" ipv6 rip {as_num} enable")
    elif igp == "ospf": 
        config.append(f" ipv6 ospf {as_num} area 0")
    
    # igp
    if igp == "rip":
        config += ["!", f"ipv6 router rip {as_num}"]
    else:
        config += ["!", f"ipv6 router ospf {as_num}", f" router-id {r_data['router_id']}"]

    config.append('!')
    
    # on verifie si on a des clients sur ce lien
    reseaux_clients_locaux = []
    for int_name, details in r_data["interface"].items():
        if details.get('relation') == 'customer':
            reseaux_clients_locaux.append(details['adresse_ip']) #on récupère l'@ ip
            
    # bgp
    config += [f"router bgp {as_num}", f" bgp router-id {r_data['router_id']}", " no bgp default ipv4-unicast"]
            
    # voisins iBGP 
    for autre_r, autre_data in as_data["router"].items():
        if autre_r != nom_r:
            v_ip = autre_data['loopback'].split("/")[0]
            config.append(f" neighbor {v_ip} remote-as {as_num}")
            config.append(f" neighbor {v_ip} update-source Loopback0")
    
    # voisins eBGP
    for i in ebgp_voisins:
        nom_voisin = i['voisin']
        relation = i.get('relation') # 'customer', 'peer', ou 'provider'
        for as_name, as_voisin_data in donnees["as"].items():
            if nom_voisin in as_voisin_data["router"]:
                voisin_router = as_voisin_data["router"][nom_voisin]
                num_as_v = as_voisin_data["numero_as"]
                for intf_data in voisin_router["interface"].values():
                    if intf_data.get("voisin") == nom_r:
                        p_ip = intf_data["adresse_ip"].split("/")[0]
                        config.append(f" neighbor {p_ip} remote-as {num_as_v}")
                        ebgp_phys_ips.append((p_ip,relation))
                        break

    # address family-ipv6
    prefixe_as = as_data["adresse_reseau"] 
    
    
    config.append(" address-family ipv6")
    config.append(f"  network {prefixe_as}:/48")

    # active voisins iBGP 
    for autre_r, autre_data in as_data["router"].items():
        if autre_r != nom_r:
            v_ip = autre_data['loopback'].split("/")[0]
            config.append(f"  neighbor {v_ip} activate") 
            config.append(f"  neighbor {v_ip} next-hop-self")
            config.append(f"  neighbor {v_ip} send-community both")

    # active voisins eBGP
    for p_ip, relation in ebgp_phys_ips:
        config.append(f"  neighbor {p_ip} activate")
        config.append(f"  neighbor {p_ip} send-community both")
        
        if relation == "customer":
            config.append(f"  neighbor {p_ip} route-map TAG_IN_CUSTOMER in") #marque comme client
            config.append(f"  neighbor {p_ip} route-map EXPORT_TO_CUSTOMER out") #envoie tout ce que l'on a 
        elif relation == "peer":
            config.append(f"  neighbor {p_ip} route-map TAG_IN_PEER in")
            config.append(f"  neighbor {p_ip} route-map EXPORT_TO_NON_CUSTOMER out")
        elif relation == "provider":
            config.append(f"  neighbor {p_ip} route-map TAG_IN_PROVIDER in")
            config.append(f"  neighbor {p_ip} route-map EXPORT_TO_NON_CUSTOMER out")

    config.append(" exit-address-family")
    config.append("!")
    config.append(f"ipv6 route {prefixe_as}:/48 null0")
    config.append("!")

    # filtrage

    prefixe_propre = as_data['adresse_reseau'].rstrip(':')






    config += [
    "!",

    "ip community-list standard L_CUSTOMER permit 0:1",
    "ip community-list standard L_PEER permit 0:2",
    "ip community-list standard L_PROVIDER permit 0:3",
    "!",

    f"ipv6 prefix-list MY_AS permit {prefixe_propre}::/48",
    "!",

    "route-map TAG_IN_CUSTOMER permit 10",
    " set community 0:1 additive",
    " set local-preference 200",
    "!",
    "route-map TAG_IN_PEER permit 10",
    " set community 0:2 additive",
    " set local-preference 150",
    "!",
    "route-map TAG_IN_PROVIDER permit 10",
    " set community 0:3 additive",
    " set local-preference 100",
    "!",

    "route-map EXPORT_TO_NON_CUSTOMER permit 10",
    " match ipv6 address prefix-list MY_AS",
    "!",
    "route-map EXPORT_TO_NON_CUSTOMER permit 20",
    " match community L_CUSTOMER",
    "!",

    "route-map EXPORT_TO_NON_CUSTOMER deny 30",
    " match community L_PEER",
    "!",
    "route-map EXPORT_TO_NON_CUSTOMER deny 40",
    " match community L_PROVIDER",
    "!",

    "route-map EXPORT_TO_CUSTOMER permit 50",
    "!"
]
    return "\n".join(config)



if __name__ == "__main__":
    for r_nom, r_uuid in mapping_routeur_uuid.items():
        config_txt = generer_config(r_nom)
        if config_txt:
            path = os.path.join(CHEMIN_PROJET, r_uuid, "configs")
            os.makedirs(path, exist_ok=True)
            num = "".join(filter(str.isdigit, r_nom))
            with open(os.path.join(path, f"i{num}_startup-config.cfg"), "w") as f:
                f.write(config_txt)
    print("Configurations générée avec succès.")