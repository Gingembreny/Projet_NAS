#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

# --- Configuration des Chemins ---
CHEMIN_PROJET = "/Users/tungd/GNS3/projects/PROJET/GNS_NAS/NAS_gns/project-files/dynamips/"
FICHIER_JSON = "config_final_v2.json"

mapping_routeur_uuid = {
    "PE1": "/Users/tungd/GNS3/projects/PROJET/GNS_NAS/NAS_gns/project-files/dynamips/c3c86241-71c6-4c8d-87eb-f84e39aabaa1",
    "P1": "/Users/tungd/GNS3/projects/PROJET/GNS_NAS/NAS_gns/project-files/dynamips/10fc1558-c7d4-4bdd-a317-d54aae0ff5dc",
    "P2": "/Users/tungd/GNS3/projects/PROJET/GNS_NAS/NAS_gns/project-files/dynamips/6acfe332-8b83-48b8-b1b1-b99e95fb572f",
    "PE2": "/Users/tungd/GNS3/projects/PROJET/GNS_NAS/NAS_gns/project-files/dynamips/4420ac89-323f-4b47-b73f-d809d207a496",
    "RR": "/Users/tungd/GNS3/projects/PROJET/GNS_NAS/NAS_gns/project-files/dynamips/cf17a70a-651d-4cab-9873-3718e6f4aa15",
    "CE1": "/Users/tungd/GNS3/projects/PROJET/GNS_NAS/NAS_gns/project-files/dynamips/da21e3b4-6bbe-4f49-b2b4-a5c565e72e15",
    "CE2": "/Users/tungd/GNS3/projects/PROJET/GNS_NAS/NAS_gns/project-files/dynamips/9ff78be6-28f7-41f7-900b-d8d6ae746aab",
    "CE3": "/Users/tungd/GNS3/projects/PROJET/GNS_NAS/NAS_gns/project-files/dynamips/12b5e465-0040-4d42-98e1-887fcf777bff",
    "CE4": "/Users/tungd/GNS3/projects/PROJET/GNS_NAS/NAS_gns/project-files/dynamips/49533786-867c-47c0-99c2-d99237cc1987",
}

with open(FICHIER_JSON, "r") as f:
    donnees = json.load(f)

def get_router_info(nom_r):
    """Trouver les infos du routeur dans le JSON"""
    for as_nom, as_data in donnees["as"].items():
        if nom_r in as_data["routers"]:
            return as_data, as_data["routers"][nom_r]
    return None, None


def get_ce_vrf_type(ce_nom):
    """Déterminer le type VRF d'un CE (AS222 ou AS333)"""
    for topo in donnees["as"]["as111"]["topologie_client"]:
        for pe_nom, ce_list in topo.items():
            if ce_nom in ce_list:
                return topo["numero_as"]
    return None


def get_neighbor_loopback(neighbor_name):
    """Obtenir l'adresse loopback d'un voisin"""
    for as_nom, as_data in donnees["as"].items():
        if neighbor_name in as_data["routers"]:
            return as_data["routers"][neighbor_name]["adresse_loopback"].split('/')[0]
    return None


def get_neighbor_router_id(neighbor_name):
    """Obtenir le router-id d'un voisin"""
    for as_nom, as_data in donnees["as"].items():
        if neighbor_name in as_data["routers"]:
            return as_data["routers"][neighbor_name]["router_id"]
    return None


def cidr_to_netmask(cidr_str):
    """Convertir format CIDR à format netmask"""
    ip_part, prefix = cidr_str.split('/')
    prefix = int(prefix)
    
    if prefix == 32:
        return f"{ip_part} 255.255.255.255"
    elif prefix == 30:
        return f"{ip_part} 255.255.255.252"
    elif prefix == 24:
        return f"{ip_part} 255.255.255.0"
    else:
        # Calcul générique
        mask = (0xffffffff >> (32 - prefix)) << (32 - prefix)
        octets = [(mask >> (24 - i*8)) & 0xff for i in range(4)]
        return f"{ip_part} {'.'.join(map(str, octets))}"


def vrf_config(vrf_name, rd, rt_import, rt_export):
    """Générer la config VRF"""
    config = [
        f"vrf definition {vrf_name}",
        f" rd {rd}",
        f" route-target import {rt_import}",
        f" route-target export {rt_export}",
        " address-family ipv4",
        " exit-address-family",
        "!"
    ]
    return "\n".join(config)


def generer_config(nom_r):
    """Générer la configuration complète pour un routeur"""
    as_data, r_data = get_router_info(nom_r)
    
    if as_data is None or r_data is None:
        return None
    
    as_num = as_data["numero_as"]
    config_lines = []
    
    config_lines += [
        "!",
        f"hostname {nom_r}",
        "!"
    ]
    
    if nom_r not in ["CE1", "CE2", "CE3", "CE4"]:
        config_lines.append("ip cef")
        config_lines.append("!")
    
    if nom_r in ["PE1", "PE2"]:
        config_lines.append(vrf_config("AS222", "111:222", "111:222", "111:222"))
        config_lines.append(vrf_config("AS333", "111:333", "111:333", "111:333"))
    

    config_lines += [
        "interface Loopback0",
        f" ip address {cidr_to_netmask(r_data['adresse_loopback'])}"
    ]
    
    if nom_r not in ["CE1", "CE2", "CE3", "CE4"]:
        config_lines.append(" no shutdown")
    
    config_lines.append("!")

    
    # mpls et ospf 
    if nom_r in ["P1", "P2", "PE1", "PE2", "RR"]:
        config_lines += [
            "mpls ip",
            "mpls label protocol ldp",
            "mpls ldp router-id Loopback0 force",
            "!"
        ]
        
        config_lines += [
            "router ospf 1",
            f" router-id {r_data['router_id']}"
        ]
        

        loopback_ip = r_data['adresse_loopback'].split('/')[0]
        config_lines.append(f" network {loopback_ip} 0.0.0.0 area 0")
        
        for neighbor_name, neighbor_data in r_data["voisin"].items():
            # Skip CE neighbors (pas de OSPF pour CE)
            if neighbor_name not in ["CE1", "CE2", "CE3", "CE4"]:
                network = neighbor_data['reseau'].split('/')[0]
                config_lines.append(f" network {network} 0.0.0.3 area 0")

        
        config_lines.append("!")
    

    for neighbor_name, neighbor_data in r_data["voisin"].items():
        config_lines += [
            f"interface {neighbor_data['interface']}",
            f" description Lien vers {neighbor_name}",
            f" ip address {cidr_to_netmask(neighbor_data['adresse_ip'])}"
        ]
        
        # vrf forwarding pour PE vers CE
        if nom_r in ["PE1", "PE2"] and neighbor_name in ["CE1", "CE2", "CE3", "CE4"]:
            vrf_type = get_ce_vrf_type(neighbor_name)
            config_lines.append(f" vrf forwarding AS{vrf_type}")
        
        # mpls
        if nom_r in ["P1", "P2", "PE1", "PE2", "RR"]:
            config_lines.append(" mpls ip")
        
        config_lines += [
            " no shutdown",
            "!"
        ]
    
    # bgp
    if nom_r in ["PE1", "PE2", "RR"] or nom_r in ["CE1", "CE2", "CE3", "CE4"]:
        config_lines += [
            f"router bgp {as_num}"
        ]
        
        # ibgp
        if nom_r in ["PE1", "PE2", "RR"]:
            config_lines.append(" bgp log-neighbor-changes")
            
            for neighbor_name, neighbor_data in r_data["voisin"].items():
                if neighbor_name in as_data["routers"]:
                    neighbor_loopback = get_neighbor_loopback(neighbor_name)
                    config_lines += [
                        f" neighbor {neighbor_loopback} remote-as {as_num}",
                        f" neighbor {neighbor_loopback} update-source Loopback0"
                    ]
        
            config_lines.append(" !")
        
            # Address-family pour iBGP
            config_lines.append(" address-family vpnv4")
            
            for neighbor_name, neighbor_data in r_data["voisin"].items():
                if neighbor_name in as_data["routers"]:
                    neighbor_loopback = get_neighbor_loopback(neighbor_name)
                    config_lines += [
                        f"  neighbor {neighbor_loopback} activate",
                        f"  neighbor {neighbor_loopback} send-community both"
                    ]
                    
                    # Route reflector client (seulement RR)
                    if nom_r == "RR":
                        config_lines.append(f"  neighbor {neighbor_loopback} route-reflector-client")
            
            config_lines.append(" exit-address-family")
        
            # eBGP neighbors vers CE 
            if nom_r in ["PE1", "PE2"]:
                for neighbor_name, neighbor_data in r_data["voisin"].items():
                    if neighbor_name in ["CE1", "CE2", "CE3", "CE4"]:
                        vrf_type = get_ce_vrf_type(neighbor_name)
                        neighbor_ip = neighbor_data['adresse_ip'].split("/")[0]
                        
                        config_lines += [
                            f" !",
                            f" address-family ipv4 vrf AS{vrf_type}",
                            f"  neighbor {neighbor_ip} remote-as {donnees['as'][f'as{vrf_type}']['numero_as']}",
                            f"  neighbor {neighbor_ip} activate",
                            f"  neighbor {neighbor_ip} as-override",
                            f" exit-address-family"
                        ]
        
        # bgp pour CE 
        if nom_r in ["CE1", "CE2", "CE3", "CE4"]:
            # Router ID
            config_lines.append(f" router-id {r_data['router_id']}")
            
            # eBGP neighbor (vers PE)
            for neighbor_name, neighbor_data in r_data["voisin"].items():
                neighbor_ip = neighbor_data['adresse_ip'].split("/")[0]
                config_lines.append(f" neighbor {neighbor_ip} remote-as 111")
            
            # Network statement pour loopback
            loopback_ip = r_data['adresse_loopback'].split('/')[0]
            config_lines.append(f" network {loopback_ip} mask 255.255.255.255")
        
        config_lines.append("!")


    
    config_lines += [
        "end",
        "wr"
    ]
    
    return "\n".join(config_lines)



if __name__ == "__main__":
    # Générer un fichier txt pour comparaison
    output_txt = []
    
    for r_nom in mapping_routeur_uuid.keys():
        config_txt = generer_config(r_nom)
        if config_txt:
            output_txt.append(f"\n{'='*80}\n")
            output_txt.append(f"ROUTEUR: {r_nom}\n")
            output_txt.append(f"{'='*80}\n\n")
            output_txt.append(config_txt)
            output_txt.append(f"\n\n")
    
    # Écrire dans un fichier txt pour comparaison
    with open("config_output_generated.txt", "w") as f:
        f.writelines(output_txt)

# if __name__ == "__main__":
#     for r_nom, r_uuid in mapping_routeur_uuid.items():
#         config_txt = generer_config(r_nom)
#         if config_txt:
#             path = os.path.join(CHEMIN_PROJET, r_uuid, "configs")
#             os.makedirs(path, exist_ok=True)
#             num = "".join(filter(str.isdigit, r_nom))
#             with open(os.path.join(path, f"i{num}_startup-config.cfg"), "w") as f:
#                 f.write(config_txt)
#             print(f"Config générée pour {r_nom}")