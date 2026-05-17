#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import shutil

# --- Configuration des Chemins ---
# Adapte ce chemin à ton dossier projet GNS3 réel
CHEMIN_PROJET = "/Users/gaillardou/Desktop/GitHub/Projet_NAS/gns_nas/project-files/dynamips/"
FICHIER_JSON = "config_final.json"

# Mapping des UUID GNS3 (Vérifie bien tes UUID dans GNS3 !)
mapping_routeur_uuid = {
    "PE1":"e42c1e09-a8dd-470d-b8df-bb33d89ca8fe",
    "P1":"5ee4521d-573f-4df2-a76a-4ac9816bf28a",
    "P2":"446e007d-06ea-4736-9ac5-05ecde63e9f8", # Note: P1 et P2 semblent avoir le même UUID dans ton exemple, vérifie bien !
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
    "P2":  "i3_startup-config.cfg", # À vérifier selon tes dossiers
    "RR":  "i5_startup-config.cfg", # Correspond à ton dossier 2e34189e... dans l'image
    "PE2": "i4_startup-config.cfg",
    "CE1": "i6_startup-config.cfg",
    "CE2": "i7_startup-config.cfg",
    "CE3": "i8_startup-config.cfg",
    "CE4": "i9_startup-config.cfg"  # Correspond à ton dossier 9b840359... dans l'image
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

    # --- 1. Gestion des VRF (Uniquement pour les PE) ---
    # On regarde si le routeur a un voisin avec un 'rd' (Route Distinguisher)
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

    # --- 2. Configuration des Interfaces ---
    config += ["interface Loopback0", f" ip address {r_data['adresse_loopback']} {r_data['masque']}", "!"]

    for v_nom, v_info in r_data["voisin"].items():
        config += [f"interface {v_info['interface']}"]
        
        # Si c'est un PE vers un CE, on applique la VRF
        if "rd" in v_info:
            config.append(f" ip vrf forwarding CUST_{v_info['as_distant']}")
            
        config += [f" ip address {v_info['adresse_ip']} {v_info['masque']}", " negotiation auto"]
        if nom_r == "RR":
                config += [" ip ospf cost 1000"]
        # MPLS uniquement dans le backbone (AS 111)
        if as_num == "111" and v_nom in as_du_routeur["routers"] and nom_r != "RR" and v_nom != "RR":
            config.append(" mpls ip")
        config += [" no shutdown", "!"]

    
    # --- 3. Routage IGP (OSPF) ---
    if as_num == "111":
        config += [f"router ospf {as_num}", f" router-id {r_data['router_id']}", " network 10.10.0.0 0.0.255.255 area 0", "!"]

    # --- 4. Configuration BGP ---  ############ A MODIFIER  POUR LES P. ##########
    
    if "P" in nom_r and "PE" not in nom_r:
        # C'est un routeur P (ex: P1, P2) -> On ne met pas de BGP.
        config.append("!")
    else:
        # On commence le bloc BGP pour les RR, PE et CE
        config += [f"router bgp {as_num}", f" bgp router-id {r_data['router_id']}", " bgp log-neighbor-changes"]

        if nom_r == "RR":
            # --- LOGIQUE ROUTE REFLECTOR ---
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

        elif "PE" in nom_r:
            # --- LOGIQUE PE (Vers RR + vers Clients) ---
            # 1. Peering vers le Route Reflector (iBGP VPNv4)
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

            # 2. Peering vers les Clients (eBGP IPv4 VRF)
            for v_nom, v_info in r_data["voisin"].items():
                if "rd" in v_info:
                    vrf_name = f"CUST_{v_info['as_distant']}"
                    ce_as = v_info["as_distant"]
                    # Récupération de l'IP du CE (l'autre côté du lien)
                    ce_ip = donnees["as"][f"as{ce_as}"]["routers"][v_nom]["voisin"][nom_r]["adresse_ip"]
                    
                    config += [
                        f" !",
                        f" address-family ipv4 vrf {vrf_name}",
                        f"  neighbor {ce_ip} remote-as {ce_as}",
                        f"  neighbor {ce_ip} activate",
                        f"  neighbor {ce_ip} send-community both",
                        " exit-address-family"
                    ]

        elif "CE" in nom_r:
            # 1. On récupère les infos du réseau client depuis le JSON
            # On calcule le réseau (ex: 10.20.1.1 -> 10.20.1.0)
            ip_parts = r_data["adresse_loopback"].split('.')
            network_addr = ".".join(ip_parts[:-1]) + ".0"
            mask_dec = r_data["masque"]

            # --- LOGIQUE CE (Vers PE) ---
            for v_nom, v_info in r_data["voisin"].items():
                # On récupère l'IP du PE distant
                pe_ip = donnees["as"]["as111"]["routers"][v_nom]["voisin"][nom_r]["adresse_ip"]
                
                config += [
                    f" neighbor {pe_ip} remote-as 111",
                    " !",
                    " address-family ipv4",
                    # On utilise le réseau et le masque dynamiques
                    f"  network {network_addr} mask {mask_dec}",
                    f"  neighbor {pe_ip} activate",
                    f"  neighbor {pe_ip} allowas-in",
                    " exit-address-family"
                ]

    config.append("end")
    return "\n".join(config)

import glob # À ajouter au début de ton script

if __name__ == "__main__":
    for r_nom, r_uuid in mapping_routeur_uuid.items():
        if r_nom not in mapping_fichiers:
            print(f"⚠️ Aucun fichier de config défini pour {r_nom}, saut...")
            continue
            
        print(f"--- Configuration de {r_nom} ---")
        dossier_config = os.path.join(CHEMIN_PROJET, r_uuid, "configs")

        # --- ÉTAPE DE NETTOYAGE : Supprime TOUS les anciens .cfg ---
        # Cela évite d'avoir i1_startup.cfg ET i5_startup.cfg en même temps
        anciens_fichiers = glob.glob(os.path.join(dossier_config, "*.cfg"))
        for f in anciens_fichiers:
            try:
                os.remove(f)
                print(f"🧹 Suppression de l'ancien fichier : {os.path.basename(f)}")
            except Exception as e:
                print(f"⚠️ Erreur lors de la suppression de {f}: {e}")

        config_txt = generer_config(r_nom)
        
        if config_txt:
            nom_fichier = mapping_fichiers[r_nom]
            chemin_final = os.path.join(dossier_config, nom_fichier)
            
            # Écriture du nouveau fichier (propre et unique)
            with open(chemin_final, "w", encoding="utf-8") as f:
                f.write(config_txt)
                print(f"💾 Nouveau fichier unique créé : {nom_fichier}")