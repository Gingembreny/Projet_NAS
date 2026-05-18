#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import shutil


# --- Configuration des Chemins ---
# Attention au chemin
CHEMIN_PROJET = "/Users/gaillardou/Desktop/GitHub/Projet_NAS/gns_nas/project-files/dynamips/"
FICHIER_JSON = "config_final.json"

mapping_routeur = {
    "PE1":"e42c1e09-a8dd-470d-b8df-bb33d89ca8fe",
    "P1":"5ee4521d-573f-4df2-a76a-4ac9816bf28a",
    "P2":"446e007d-06ea-4736-9ac5-05ecde63e9f8", 
    "RR":"2e34189e-b85d-4293-8146-53754602fbd5",
    "PE2":"62d26b9f-6cc4-4365-91c3-e9a3a2396aa7",
    "CE1":"94419353-22e7-46fd-83f1-3f01e76451ac",
    "CE2":"0696c35b-d6f9-493f-9563-6c7f854bd95a",
    "CE3":"cc756b3a-ad03-4aec-82d9-93aca0058b57",
    "CE4":"9b840359-e6dc-4b92-ad90-361e738ce662"
}

mapping_fichiers = {
    "PE1": "i1_startup-config.cfg",
    "P1":  "i2_startup-config.cfg",
    "P2":  "i3_startup-config.cfg", 
    "RR":  "i5_startup-config.cfg", 
    "PE2": "i4_startup-config.cfg",
    "CE1": "i6_startup-config.cfg",
    "CE2": "i7_startup-config.cfg",
    "CE3": "i8_startup-config.cfg",
    "CE4": "i9_startup-config.cfg"  
}


with open(FICHIER_JSON, "r") as f:
    donnees = json.load(f)

def generer_config(nom_r):
    # Identification de l'AS du routeur
    as_du_routeur = None
    r_data = None
    for as_key, as_val in donnees["as"].items():
        if nom_r in as_val["routers"]:
            as_du_routeur = as_val
            r_data = as_val["routers"][nom_r]
            break
    
    if not r_data: return None

    as_num = as_du_routeur["numero_as"]
    if nom_r != "RR" and as_num == "111":
        config = [f"hostname {nom_r}", "ip cef", "mpls label protocol ldp"]
    else : 
        config = [f"hostname {nom_r}", "ip cef"]


    # VRF pour les PE
    vrfs = {}
    for v_nom, v_info in r_data["voisin"].items():
        if "rd" in v_info:
            vrf_name = f"CUST_{v_info['as_distant']}"
            vrfs[vrf_name] = v_info["rd"]

    for vrf_name, rd in vrfs.items():
        config += [
            f"ip vrf {vrf_name}",
            f" rd {rd}",
            f" route-target export {rd}",
            f" route-target import {rd}",
            "!"
        ]

    # Configs interfaces
    config += ["interface Loopback0", f" ip address {r_data['adresse_loopback']} {r_data['masque']}", "!"]

    for v_nom, v_info in r_data["voisin"].items():
        config += [f"interface {v_info['interface']}"]
        
        # Si c'est un PE vers un CE, on applique la VRF
        if "rd" in v_info:
            config.append(f" ip vrf forwarding CUST_{v_info['as_distant']}")
            
        config += [f" ip address {v_info['adresse_ip']} {v_info['masque']}", " negotiation auto"]
        if nom_r == "RR":
                config += [" ip ospf cost 1000"]

        # MPLS pour le backbone 
        if as_num == "111" and nom_r != "RR":
            config.append(" mpls ip")
        config += [" no shutdown", "!"]

    
    # IGP
    if as_num == "111":
        config += [f"router ospf {as_num}", f" router-id {r_data['router_id']}", " network 10.10.0.0 0.0.255.255 area 0", "!"]

    # BGP
    
    # pas de BGP pour les P
    if "P" in nom_r and "PE" not in nom_r:
        config.append("!")
    else:
        config += [f"router bgp {as_num}", f" bgp router-id {r_data['router_id']}", " bgp log-neighbor-changes"]

        if nom_r == "RR":
    # RR
            pe_list = [info for name, info in as_du_routeur["routers"].items() if "PE" in name]

            for pe in pe_list:
                config += [
                    f" neighbor {pe['adresse_loopback']} remote-as {as_num}",
                    f" neighbor {pe['adresse_loopback']} update-source Loopback0"
                ]
            
            config += [" !", " address-family vpnv4"]
            for pe in pe_list:
                config += [
                    f"  neighbor {pe['adresse_loopback']} activate",
                    f"  neighbor {pe['adresse_loopback']} send-community extended",
                    f"  neighbor {pe['adresse_loopback']} route-reflector-client"
                ]
            config.append(" exit-address-family")
    # PE
        elif "PE" in nom_r:
            rr_data = as_du_routeur["routers"].get("RR")
            if rr_data:
                config += [
                    f" neighbor {rr_data['adresse_loopback']} remote-as {as_num}",
                    f" neighbor {rr_data['adresse_loopback']} update-source Loopback0",
                    " !",
                    " address-family vpnv4",
                    f"  neighbor {rr_data['adresse_loopback']} activate",
                    f"  neighbor {rr_data['adresse_loopback']} send-community extended",
                    " exit-address-family"
                ]

    # Peering avec les CE pour les PE
            for v_nom, v_info in r_data["voisin"].items():
                if "rd" in v_info:
                    vrf_name = f"CUST_{v_info['as_distant']}"
                    ce_as = v_info["as_distant"]
                    ce_ip = donnees["as"][f"as{ce_as}"]["routers"][v_nom]["voisin"][nom_r]["adresse_ip"]
                    
                    config += [
                        f" !",
                        f" address-family ipv4 vrf {vrf_name}",
                        f"  neighbor {ce_ip} remote-as {ce_as}",
                        f"  neighbor {ce_ip} activate",
                        f"  neighbor {ce_ip} send-community both",
                        " exit-address-family"
                    ]
    # CE
        elif "CE" in nom_r:
            ip_parts = r_data["adresse_loopback"].split('.')
            network_addr = ".".join(ip_parts[:-1]) + ".0"
            mask_dec = r_data["masque"]

            for v_nom, v_info in r_data["voisin"].items():
                pe_ip = donnees["as"]["as111"]["routers"][v_nom]["voisin"][nom_r]["adresse_ip"]
                
                config += [
                    f" neighbor {pe_ip} remote-as 111",
                    " !",
                    " address-family ipv4",
                    f"  network {network_addr} mask {mask_dec}",
                    f"  neighbor {pe_ip} activate",
                    f"  neighbor {pe_ip} allowas-in",
                    " exit-address-family"
                ]

    config.append("end")
    return "\n".join(config)



if __name__ == "__main__":
    for r_nom, r_uuid in mapping_routeur.items():
            
        print(f"--- Configuration de {r_nom} ---")
        dossier_config = os.path.join(CHEMIN_PROJET, r_uuid, "configs")
        config_txt = generer_config(r_nom)
        
        if config_txt:
            nom_fichier = mapping_fichiers[r_nom]
            chemin_final = os.path.join(dossier_config, nom_fichier)
            
            with open(chemin_final, "w", encoding="utf-8") as f:
                f.write(config_txt)
                print(f"Nouveau fichier créé : {nom_fichier}")