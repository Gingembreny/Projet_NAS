#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

FICHIER_JSON = "fichier_intension.json"

# Simulation du chargement (remplacez par votre lecture de fichier)
with open(FICHIER_JSON, "r") as f:
    data = json.load(f)

def cidr_to_mask(cidr):
    """Convertit un CIDR (ex: 30) en masque décimal (ex: 255.255.255.252)"""
    cidr = int(cidr)
    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"

def process_ip_data(entry_dict, full_ip_with_mask, key_name="adresse_ip"):
    """
    Sépare l'IP et le CIDR et ajoute les clés spécifiées (par défaut 'adresse_ip') 
    et 'masque' dans le dictionnaire fourni.
    """
    ip, cidr = full_ip_with_mask.split('/')
    entry_dict[key_name] = ip
    entry_dict["masque"] = cidr_to_mask(cidr)

# --- Configuration AS 111 (Cœur de réseau) ---
num_as_core = "111"
liste_interface = data["liste_interface"]
data_as111 = data["as"]["as111"]
adresse_reseau = data_as111["adresse_reseau"]
loopback_base = data_as111["adresse_loopback"]

def get_free_interface(as_target, nom_router):
    router_obj = data["as"][as_target]["routers"].get(nom_router, {})
    used_interfaces = [v["interface"] for v in router_obj.get("voisin", {}).values() if "interface" in v]
    for intf in liste_interface:
        if intf not in used_interfaces:
            return intf
    return None  

def configure_as(data, as_id, is_core=False):
    as_key = f"as{as_id}"
    as_data = data["as"][as_key]
    
    # 1. Initialisation des routeurs
    noms_routers = list(as_data.get("topologie", {}).keys()) or list(as_data.get("routers", {}).keys())
    
    for i, nom in enumerate(noms_routers, start=1):
        if nom not in as_data["routers"]:
            as_data["routers"][nom] = {"voisin": {}}
        
        # On définit le router_id systématiquement
        as_data["routers"][nom].update({
            "nom": nom,
            "router_id": f"{as_id}.0.0.{i}"
        })

        # --- LOGIQUE D'ADRESSAGE LOOPBACK SÉCURISÉE ---
        cle_specifique = f"adresse_{nom}"
        
        if cle_specifique in as_data:
            # Cas des CE : on utilise l'IP spécifique du fichier d'intention
            ip_complete = as_data[cle_specifique]
            process_ip_data(as_data["routers"][nom], ip_complete, key_name="adresse_loopback")
        else:
            # Cas des P/PE/RR ou si l'IP n'est pas spécifiée
            # On définit loopback_base ICI pour éviter l'UnboundLocalError
            loopback_base = as_data.get("adresse_loopback", f"{as_id}.10.10.")
            process_ip_data(as_data["routers"][nom], f"{loopback_base}{i}/32", key_name="adresse_loopback")

    # 2. Liens internes (IGP) (inchangé)
    if "topologie" in as_data:
        id_ip = 0
        liens_faits = set()
        for r_name, voisins in as_data["topologie"].items():
            for v_name in voisins:
                lien = tuple(sorted([r_name, v_name]))
                if lien in liens_faits: continue
                liens_faits.add(lien)
                intf_r = get_free_interface(as_key, r_name)
                intf_v = get_free_interface(as_key, v_name)
                as_data["routers"][r_name]["voisin"][v_name] = {"interface": intf_r, "nom": v_name}
                as_data["routers"][v_name]["voisin"][r_name if 'router_nom' in locals() else r_name] = {"interface": intf_v, "nom": r_name}
                base_ip = adresse_reseau.rstrip('.')
                process_ip_data(as_data["routers"][r_name]["voisin"][v_name], f"{base_ip}.{id_ip + 1}/30")
                process_ip_data(as_data["routers"][v_name]["voisin"][r_name], f"{base_ip}.{id_ip + 2}/30")
                id_ip += 4

    # 3. Liens Externes (PE-CE) - AJOUT DU RD ICI
    if is_core and "topologie_client" in as_data:
        id_ip_pece = 0
        for client_entry in as_data["topologie_client"]:
            c_as_num = client_entry["numero_as"]
            c_as_key = f"as{c_as_num}"
            # On récupère le RD défini dans le fichier d'intention
            route_distinguisher = client_entry.get("rd")
            
            for pe_nom, ce_list in client_entry.items():
                # On ignore les clés qui ne sont pas des noms de PE
                if pe_nom in ["numero_as", "rd"]: continue 
                
                for ce_nom in ce_list:
                    if ce_nom not in data["as"][c_as_key]["routers"]:
                        idx = len(data["as"][c_as_key]["routers"]) + 1
                        data["as"][c_as_key]["routers"][ce_nom] = {
                            "nom": ce_nom,
                            "router_id": f"{c_as_num}.0.0.{idx}",
                            "voisin": {}
                        }

                    intf_pe = get_free_interface(as_key, pe_nom)
                    intf_ce = get_free_interface(c_as_key, ce_nom)
                    
                    ip_pe = f"10.255.255.{id_ip_pece + 1}"
                    ip_ce = f"10.255.255.{id_ip_pece + 2}"

                    # Ajout de la clé 'rd' dans le dictionnaire du PE
                    as_data["routers"][pe_nom]["voisin"][ce_nom] = {
                        "interface": intf_pe, 
                        "nom": ce_nom, 
                        "as_distant": c_as_num,
                        "rd": route_distinguisher  # <-- Insertion du RD
                    }
                    
                    data["as"][c_as_key]["routers"][ce_nom]["voisin"][pe_nom] = {
                        "interface": intf_ce, 
                        "nom": pe_nom, 
                        "as_distant": as_id
                    }
                    
                    process_ip_data(as_data["routers"][pe_nom]["voisin"][ce_nom], f"{ip_pe}/30")
                    process_ip_data(data["as"][c_as_key]["routers"][ce_nom]["voisin"][pe_nom], f"{ip_ce}/30")
                    id_ip_pece += 4

# 1. On configure l'AS de coeur (avec ses liens internes et PE-CE)
configure_as(data, "111", is_core=True)

# 2. On configure les AS clients (uniquement leurs structures internes)
# On boucle sur tous les AS présents sauf le coeur
for as_name in data["as"]:
    num_as = data["as"][as_name]["numero_as"]
    if num_as != "111":
        configure_as(data, num_as, is_core=False)

if "liste_interface" in data: del data["liste_interface"]
for as_name in data["as"]:
    keys_to_delete = ["topologie", "topologie_client", "adresse_reseau", "adresse_loopback"]
    for key in keys_to_delete:
        if key in data["as"][as_name]: del data["as"][as_name][key]

with open("config_final.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, sort_keys=True)

print("JSON généré avec succès avec séparation IP et Masque !")