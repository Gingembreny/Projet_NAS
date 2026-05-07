# **Guide complet de vérification MPLS L3VPN**

Ce guide permet de vérifier étape par étape qu’un réseau **MPLS L3VPN** fonctionne correctement, depuis l’infrastructure OSPF jusqu’à la connectivité client finale.

---

# **I. Vérification de l’infrastructure réseau (OSPF + MPLS)**

## **1. Vérifier les voisins OSPF**

Commande :

```bash
show ip ospf neighbor
```

### **Résultat attendu**

Tous les voisins doivent être en état :

```bash
FULL/DR
FULL/BDR
FULL/DROTHER
```

### **Interprétation**

* `FULL` = adjacency OSPF établie avec succès.

Si vous voyez :

* `INIT`
* `2WAY`
* `EXSTART`

alors OSPF présente un problème.

### **À vérifier en cas d’erreur**

* Area ID
* Hello/Dead timer
* Masque réseau
* Interface up/up

---

## **2. Vérifier les routes OSPF**

Commande :

```bash
show ip route ospf
```

### **Résultat attendu**

Les loopbacks des autres routeurs doivent apparaître :

```bash
O 10.10.10.1/32
O 10.10.10.3/32
O 10.10.10.5/32
```

### **Interprétation**

* `O` = route apprise via OSPF.

Si les loopbacks n’apparaissent pas :

* mauvais network statement
* interface passive
* loopback non annoncée

---

---

# **II. Vérification MPLS / LDP**

Objectif : vérifier que la commutation par labels fonctionne.

---

## **3. Vérifier les voisins LDP**

Commande :

```bash
show mpls ldp neighbor
```

### **Résultat attendu**

```bash
State: Operational
```

ou

```bash
Oper
```

### **Interprétation**

* Session TCP port 646 établie
* échange de labels fonctionnel

### **Si erreur**

Vérifier :

```bash
show ip interface brief
show run | section mpls
```

Erreurs fréquentes :

* oubli de `mpls ip`
* absence de router-id
* OSPF ne transporte pas les loopbacks

---

## **4. Vérifier la table MPLS (LFIB)**

Commande :

```bash
show mpls forwarding-table
```

C’est la commande la plus importante pour MPLS.

---

## **Signification des colonnes**

---

### **Local Label**

Label généré localement par le routeur.

Exemple :

```bash
16
21
25
```

---

### **Outgoing Label**

Action à effectuer ensuite.

Il existe 3 cas :

---

### **a. Swap**

Remplacement du label.

Exemple :

```bash
21
```

Signification :

* recevoir un label
* le remplacer par 21
* transmettre au routeur suivant

---

### **b. Pop Label**

Suppression du label (PHP).

Exemple :

```bash
Pop Label
```

---

### **c. Untagged**

Transmission sans MPLS.

---

### **Prefix**

Destination associée.

Exemple :

```bash
10.10.10.5/32
```

---

### **Outgoing Interface**

Interface de sortie.

Exemple :

```bash
Gi1/0
Fa0/0
```

---

### **Next Hop**

Routeur suivant.

Exemple :

```bash
10.10.1.6
```

---

## **Résultat attendu**

Des labels doivent exister pour les loopbacks PE :

```bash
10.10.10.1/32
10.10.10.5/32
```

Sinon :

* MPLS non fonctionnel

---

---

# **III. Vérification PHP (Penultimate Hop Popping)**

Objectif : vérifier que l’avant-dernier routeur retire le label.

Commande :

```bash
show mpls forwarding-table
```

---

## **Signe de succès**

Rechercher :

```bash
Pop Label
```

Exemple :

```bash
16 Pop Label 10.10.10.3/32
```

### **Interprétation**

* le routeur est penultimate hop
* il retire le label avant d’envoyer au routeur final


---

# **IV. Vérification BGP VPNv4**

Objectif : vérifier le plan de contrôle VPN.


## **5. Vérifier les sessions BGP VPNv4**

Commande :

```bash
show bgp vpnv4 unicast all summary
```

ou :

```bash
show ip bgp vpnv4 all summary
```



## **Résultat attendu**

La colonne :

```bash
State/PfxRcd
```

doit afficher un nombre :

```bash
0
2
4
```

---

## **Interprétation**

### **Nombre**

Session établie.

Exemple :

```bash
0
```

= BGP UP, mais aucune route encore reçue.

---

### **Active**

Tentative échouée.

---

### **Idle**

Session non démarrée.

---

### **Connect**

Connexion en cours.

---

## **En cas d’erreur**

Tester :

```bash
ping 10.10.10.x source loopback0
```

Si le ping échoue :

* problème OSPF ou reachability loopback.

---

## **6. Vérification détaillée d’un voisin**

Commande :

```bash
show bgp vpnv4 unicast all neighbors 10.10.10.1
```



## **Sur RR**

Rechercher :

```bash
Route-reflector client
```

### **Interprétation**

RR reconnaît le PE comme client RR.


---

# **V. Vérification des routes VPNv4**

---

## **7. Afficher toutes les routes VPNv4**

Commande :

```bash
show ip bgp vpnv4 all
```

---

## **Résultat attendu**

Exemple :

```bash
111:222:10.20.10.6/32
111:333:10.30.10.9/32
```

---

## **Interprétation**

* `111` = ASN Provider
* `222` = VRF client
* `10.20.10.6` = route client

Si absent :

* erreur RT import/export
* erreur VRF

---

---

# **VI. Vérification VRF**

Objectif : vérifier l’isolation client.

---

## **8. Vérifier les VRF**

Commande :

```bash
show ip vrf
```

---

## **Résultat attendu**

Exemple :

```bash
AS222
AS333
```

avec interfaces associées.

---

## **Interprétation**

VRF correctement créée.

---

## **9. Vérifier BGP dans une VRF**

Commande :

```bash
show ip bgp vpnv4 vrf AS222 summary
```

---

## **Résultat attendu**

Neighbor UP.

---

## **10. Vérifier la table de routage VRF**

Commande :

```bash
show ip route vrf AS222
```

---

## **Résultat attendu**

PE1 doit voir les routes CE distantes.

Exemple :

```bash
10.20.10.7/32
```

---

---

# **VII. Vérification End-to-End**

Validation finale.

---

## **11. Ping entre clients**

Sur CE1 :

```bash
ping 10.20.10.7
```

Sur CE2 :

```bash
ping 10.30.10.9
```

---

## **Résultat attendu**

```bash
!!!!!
```

---

## **Interprétation**

VPN opérationnel.

---

## **12. Traceroute MPLS**

Commande :

```bash
traceroute 10.20.10.7
```

ou :

```bash
traceroute 10.10.10.5 source loopback0
```

---

## **Résultat attendu**

Présence de labels :

```bash
MPLS Label 16
MPLS Label 21
```

---

## **Interprétation**

Le trafic utilise MPLS et non un simple routage IP.

---

---

# **VIII. Commandes de dépannage (Troubleshooting)**

| Problème            | Commande                     | Vérification     |
| ------------------- | ---------------------------- | ---------------- |
| BGP down            | `ping loopback`              | Reachability     |
| OSPF down           | `show ip ospf neighbor`      | FULL             |
| MPLS down           | `show mpls ldp neighbor`     | Operational      |
| Pas de labels       | `show mpls forwarding-table` | Labels présents  |
| VRF absente         | `show ip vrf`                | VRF existante    |
| Routes VPN absentes | `show ip bgp vpnv4 all`      | RT import/export |
| Interface down      | `show ip interface brief`    | up/up            |

---

# **IX. Ordre logique de validation**

Toujours vérifier dans cet ordre :

```text
1. Interfaces
2. OSPF
3. LDP/MPLS
4. BGP VPNv4
5. VRF
6. Ping CE-to-CE
```

Ne jamais commencer par la fin.

Exemple :

* si CE1 ne ping pas CE3, vérifier d’abord OSPF/MPLS avant BGP.

---


