#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

FICHIER_INTENTION = "fichier_intension.json"
FICHIER_FINAL = "config_final.json"

with open(FICHIER_INTENTION, "r") as f:
    donnees = json.load(f)

def cidr_vers_masque(cidr):
    """Convertit un CIDR (ex: /30) en masque décimal (ex: 255.255.255.252)"""
    cidr = int(cidr)
    masque_bin = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    return f"{(masque_bin >> 24) & 0xff}.{(masque_bin >> 16) & 0xff}.{(masque_bin >> 8) & 0xff}.{masque_bin & 0xff}"

def traiter_donnees_ip(dictionnaire_entree, ip_avec_masque, nom_cle="adresse_ip"):
    """
    Sépare l'IP et le CIDR et ajoute les clés spécifiées
    et 'masque' dans le dictionnaire fourni.
    """
    ip, cidr = ip_avec_masque.split('/')
    dictionnaire_entree[nom_cle] = ip
    dictionnaire_entree["masque"] = cidr_vers_masque(cidr)

def obtenir_interface_libre(id_as, nom_routeur):
    routeur_obj = donnees["as"][id_as]["routers"].get(nom_routeur, {})
    interfaces_utilisees = [v["interface"] for v in routeur_obj.get("voisin", {}).values() if "interface" in v]
    for interface in liste_interfaces_disponibles:
        if interface not in interfaces_utilisees:
            return interface
    return None  

def configurer_as(donnees, num_as, est_coeur=False):
    cle_as = f"as{num_as}"
    donnees_as = donnees["as"][cle_as]
    
    noms_routeurs = list(donnees_as.get("topologie", {}).keys()) or list(donnees_as.get("routers", {}).keys())
    
    for i, nom in enumerate(noms_routeurs, start=1):
        if nom not in donnees_as["routers"]:
            donnees_as["routers"][nom] = {"voisin": {}}

        donnees_as["routers"][nom].update({
            "nom": nom,
            "router_id": f"{num_as}.0.0.{i}"
        })

        cle_specifique = f"adresse_{nom}"

    # CE        
        if cle_specifique in donnees_as:
            ip_complete = donnees_as[cle_specifique]
            traiter_donnees_ip(donnees_as["routers"][nom], ip_complete, nom_cle="adresse_loopback")
        
    # P/PE/RR
        else:
            base_loopback = donnees_as.get("adresse_loopback", f"{num_as}.10.10.")
            traiter_donnees_ip(donnees_as["routers"][nom], f"{base_loopback}{i}/32", nom_cle="adresse_loopback")

    # IGP
    if "topologie" in donnees_as:
        id_ip_interne = 0
        liens_termines = set()
        adresse_reseau_igp = donnees_as["adresse_reseau"]
        
        for nom_r, liste_voisins in donnees_as["topologie"].items():
            for nom_v in liste_voisins:
                identifiant_lien = tuple(sorted([nom_r, nom_v]))
                if identifiant_lien in liens_termines: continue
                
                liens_termines.add(identifiant_lien)
                intf_r = obtenir_interface_libre(cle_as, nom_r)
                intf_v = obtenir_interface_libre(cle_as, nom_v)
                
                donnees_as["routers"][nom_r]["voisin"][nom_v] = {"interface": intf_r, "nom": nom_v}
                donnees_as["routers"][nom_v]["voisin"][nom_r] = {"interface": intf_v, "nom": nom_r}
                
                base_ip = adresse_reseau_igp.rstrip('.')
                traiter_donnees_ip(donnees_as["routers"][nom_r]["voisin"][nom_v], f"{base_ip}.{id_ip_interne + 1}/30")
                traiter_donnees_ip(donnees_as["routers"][nom_v]["voisin"][nom_r], f"{base_ip}.{id_ip_interne + 2}/30")
                id_ip_interne += 4

    # PE - CE
    if est_coeur and "topologie_client" in donnees_as:
        id_ip_pece = 0
        for entree_client in donnees_as["topologie_client"]:
            as_client_num = entree_client["numero_as"]
            cle_as_client = f"as{as_client_num}"
            rd_client = entree_client.get("rd")
            
            for nom_pe, liste_ce in entree_client.items():
                if nom_pe in ["numero_as", "rd"]: continue 
                
                for nom_ce in liste_ce:
                    if nom_ce not in donnees["as"][cle_as_client]["routers"]:
                        index_ce = len(donnees["as"][cle_as_client]["routers"]) + 1
                        donnees["as"][cle_as_client]["routers"][nom_ce] = {
                            "nom": nom_ce,
                            "router_id": f"{as_client_num}.0.0.{index_ce}",
                            "voisin": {}
                        }

                    intf_pe = obtenir_interface_libre(cle_as, nom_pe)
                    intf_ce = obtenir_interface_libre(cle_as_client, nom_ce)
                    
                    ip_pe = f"10.255.255.{id_ip_pece + 1}"
                    ip_ce = f"10.255.255.{id_ip_pece + 2}"

                    # côté PE (avec RD)
                    donnees_as["routers"][nom_pe]["voisin"][nom_ce] = {
                        "interface": intf_pe, 
                        "nom": nom_ce, 
                        "as_distant": as_client_num,
                        "rd": rd_client
                    }
                    
                    # côté CE
                    donnees["as"][cle_as_client]["routers"][nom_ce]["voisin"][nom_pe] = {
                        "interface": intf_ce, 
                        "nom": nom_pe, 
                        "as_distant": num_as
                    }
                    
                    traiter_donnees_ip(donnees_as["routers"][nom_pe]["voisin"][nom_ce], f"{ip_pe}/30")
                    traiter_donnees_ip(donnees["as"][cle_as_client]["routers"][nom_ce]["voisin"][nom_pe], f"{ip_ce}/30")
                    id_ip_pece += 4


liste_interfaces_disponibles = donnees["liste_interface"]

# AS 111
configurer_as(donnees, "111", est_coeur=True)

# AS 222 et AS 333
for nom_as_cle in donnees["as"]:
    numero_as_actuel = donnees["as"][nom_as_cle]["numero_as"]
    if numero_as_actuel != "111":
        configurer_as(donnees, numero_as_actuel, est_coeur=False)

# supprime certaines clés du fichier d'intention
if "liste_interface" in donnees: 
    del donnees["liste_interface"]

cles_a_nettoyer = ["topologie", "topologie_client", "adresse_reseau", "adresse_loopback"]
for nom_as_cle in donnees["as"]:
    for cle in cles_a_nettoyer:
        if cle in donnees["as"][nom_as_cle]: 
            del donnees["as"][nom_as_cle][cle]

# Sauvegarde
with open(FICHIER_FINAL, "w", encoding="utf-8") as f:
    json.dump(donnees, f, indent=4, sort_keys=True)

print(f"Fichier {FICHIER_FINAL} généré avec succès !")