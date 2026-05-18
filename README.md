# Projet_NAS

Projet d'automatisation de configuration d'un réseau MPLS L3VPN sous GNS3.

## Objectif

Le projet génère automatiquement les configurations de routeurs Cisco à partir d'un fichier d'intention décrivant la topologie du réseau. Le scénario étudié contient un coeur opérateur avec des routeurs PE, P et RR, ainsi que deux clients raccordés via des routeurs CE.

## Fichier d'entrée

L'exemple de fichier d'entrée est clairement identifié ici :

```text
fichier_intension.json
```

Ce fichier décrit :

- les AS du projet ;
- les interfaces disponibles ;
- la topologie du coeur MPLS ;
- les relations PE-CE ;
- les clients, leurs CE et leurs RD.

Exemple de données présentes dans le fichier :

```json
{
  "as111": {
    "numero_as": "111",
    "topologie": {
      "PE1": ["P1"],
      "P1": ["P2"],
      "RR": ["PE1", "PE2"],
      "P2": ["PE2"]
    }
  }
}
```

## Fonctionnalités

- Génération d'un fichier `config_final.json` enrichi à partir du fichier d'intention.
- Attribution automatique des routeurs, interfaces, loopbacks, router-id et adresses de liens.
- Génération des configurations Cisco pour PE, P, RR et CE.
- Configuration automatique du coeur MPLS : OSPF, LDP et MP-BGP VPNv4.
- Configuration des services VPN client : VRF, RD, route-target et eBGP PE-CE.
- Écriture des fichiers `startup-config.cfg` dans le projet GNS3.

## Fichiers principaux

- `fichier_intension.json` : fichier d'entrée décrivant l'intention réseau.
- `generation_config_final_json.py` : transforme le fichier d'intention en `config_final.json`.
- `config_final.json` : fichier intermédiaire contenant toutes les informations nécessaires à la génération.
- `generation_config_routers.py` : génère les configurations Cisco et les place dans les dossiers GNS3.
- `configuration_manuelle/` : configurations écrites manuellement, utilisées comme référence.

## Utilisation

Les scripts doivent être exécutés dans cet ordre :

Générer le JSON final :

```bash
python3 generation_config_final_json.py
```

Générer les configurations des routeurs :

```bash
python3 generation_config_routers.py
```

Avant d'exécuter `generation_config_routers.py`, vérifier le chemin du projet GNS3 dans la variable `CHEMIN_PROJET`.

## Tests et vérifications

Après génération, vérifier que les fichiers `i*_startup-config.cfg` sont bien présents dans les dossiers `configs` du projet GNS3.

Dans GNS3, démarrer les routeurs puis vérifier :

```cisco
show running-config
show ip ospf neighbor
show mpls ldp neighbor
show bgp vpnv4 unicast all summary
show ip route vrf <VRF>
```

Exemples de tests de connectivité :

```cisco
CE1# ping 10.20.2.1
CE2# ping 10.30.2.1
PE1# ping vrf CUST_222 10.20.2.1
PE1# ping vrf CUST_333 10.30.2.1
```

## Topologie logique

- AS 111 : coeur opérateur MPLS avec PE1, PE2, P1, P2 et RR.
- AS 222 : client 1, avec CE1 et CE3.
- AS 333 : client 2, avec CE2 et CE4.

Le RR sert uniquement à la réflexion des routes VPNv4 entre les PE. Les routeurs P transportent le trafic MPLS sans connaître les routes clientes.
Les deux CE d'un même client appartiennent au même VPN et doivent pouvoir communiquer entre eux.

## Contraintes et points d'attention

- Le chemin `CHEMIN_PROJET` dans `generation_config_routers.py` doit correspondre au chemin local du projet GNS3.
- Les UUID des routeurs dans `generation_config_routers.py` doivent correspondre aux routeurs GNS3.
- Le RR est utilisé pour le contrôle BGP VPNv4, pas pour transporter le trafic client.
- Les routeurs CE ne participent pas au MPLS du coeur opérateur.
- Les configurations manuelles dans `configuration_manuelle/` servent de référence pour comparer les configurations générées.