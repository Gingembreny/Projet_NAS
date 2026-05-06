Sur la base de l'analyse de la structure du réseau AS111 à partir du schéma et de votre fichier JSON, voici un guide détaillé des étapes de configuration de l'**Adressage (Adresses IP)** et du **Routage OSPF** pour tous les appareils.

---

## **PARTIE 1: CONFIGURATION D'ADRESSAGE (ATTRIBUTION D'ADRESSES IP)**

À cette étape, nous configurerons les adresses IP pour les ports physiques et les ports virtuels (Loopback) en fonction du tableau d'allocation.

### **1. Configuration du routeur P1**
```bash
P1(config)# interface Loopback0
P1(config-if)# ip address 10.10.10.2 255.255.255.255
P1(config-if)# exit

P1(config)# interface FastEthernet0/0
P1(config-if)# ip address 10.10.1.2 255.255.255.252
P1(config-if)# no shutdown

P1(config)# interface GigabitEthernet1/0
P1(config-if)# ip address 10.10.1.5 255.255.255.252
P1(config-if)# no shutdown
```

### **2. Configuration du routeur P2**
```bash
P2(config)# interface Loopback0
P2(config-if)# ip address 10.10.10.4 255.255.255.255
P2(config-if)# exit

P2(config)# interface FastEthernet0/0
P2(config-if)# ip address 10.10.1.6 255.255.255.252
P2(config-if)# no shutdown

P2(config)# interface GigabitEthernet1/0
P2(config-if)# ip address 10.10.1.17 255.255.255.252
P2(config-if)# no shutdown
```

### **3. Configuration du routeur RR**
```bash
RR(config)# interface Loopback0
RR(config-if)# ip address 10.10.10.3 255.255.255.255
RR(config-if)# exit

RR(config)# interface FastEthernet0/0
RR(config-if)# ip address 10.10.1.9 255.255.255.252
RR(config-if)# no shutdown

RR(config)# interface GigabitEthernet1/0
RR(config-if)# ip address 10.10.1.13 255.255.255.252
RR(config-if)# no shutdown
```

### **4. Configuration des routeurs PE1 et PE2**
*   **PE1:**
    ```bash
    PE1(config)# interface Loopback0
    PE1(config-if)# ip address 10.10.10.1 255.255.255.255
    PE1(config)# interface FastEthernet0/0
    PE1(config-if)# ip address 10.10.1.1 255.255.255.252
    PE1(config-if)# no shutdown
    
    PE1(config)# interface GigabitEthernet1/0
    PE1(config-if)# ip address 10.10.1.10 255.255.255.252
    PE1(config-if)# no shutdown
    ```
*   **PE2:**
    ```bash
    PE2(config)# interface Loopback0
    PE2(config-if)# ip address 10.10.10.5 255.255.255.255
    PE2(config)# interface FastEthernet0/0
    PE2(config-if)# ip address 10.10.1.14 255.255.255.252
    PE2(config-if)# no shutdown
    
    PE2(config)# interface GigabitEthernet1/0
    PE2(config-if)# ip address 10.10.1.18 255.255.255.252
    PE2(config-if)# no shutdown
    ```

---

## **PARTIE 2: CONFIGURATION OSPF ROUTING**

Pour que tout le réseau puisse se voir (en particulier les adresses Loopback pour établir BGP par la suite), nous exécuterons OSPF sur tous les routeurs de la même **Zone 0**.

### **Principes généraux de configuration:**
- Utiliser le `Router ID` correspondant.
- Annoncer tous les réseaux directs et Loopback dans OSPF.



### **1. Configuration pour P1 (Hub central)**
```bash
P1(config)# router ospf 1
P1(config-router)# router-id 111.0.0.2
P1(config-router)# network 10.10.10.2 0.0.0.0 area 0
P1(config-router)# network 10.10.1.0 0.0.0.3 area 0
P1(config-router)# network 10.10.1.4 0.0.0.3 area 0
```

### **2. Configuration pour RR (Route Reflector)**
```bash
RR(config)# router ospf 1
RR(config-router)# router-id 111.0.0.3
RR(config-router)# network 10.10.10.3 0.0.0.0 area 0
RR(config-router)# network 10.10.1.8 0.0.0.3 area 0
RR(config-router)# network 10.10.1.12 0.0.0.3 area 0
```

### **3. Configuration pour P2 (Cœur 2)**
```bash
P2(config)# router ospf 1
P2(config-router)# router-id 111.0.0.4
P2(config-router)# network 10.10.10.4 0.0.0.0 area 0
P2(config-router)# network 10.10.1.4 0.0.0.3 area 0
P2(config-router)# network 10.10.1.16 0.0.0.3 area 0
```

### **4. Configuration pour PE1 et PE2 (Accès)**
*   **PE1:**
    ```bash
    PE1(config)# router ospf 1
    PE1(config-router)# router-id 111.0.0.1
    PE1(config-router)# network 10.10.10.1 0.0.0.0 area 0
    PE1(config-router)# network 10.10.1.0 0.0.0.3 area 0
    PE1(config-router)# network 10.10.1.8 0.0.0.3 area 0
    ```
*   **PE2:**
    ```bash
    PE2(config)# router ospf 1
    PE2(config-router)# router-id 111.0.0.5
    PE2(config-router)# network 10.10.10.5 0.0.0.0 area 0
    PE2(config-router)# network 10.10.1.12 0.0.0.3 area 0
    PE2(config-router)# network 10.10.1.16 0.0.0.3 area 0
    ```

---

## **PARTIE 3: VÉRIFICATION (VERIFICATION)**

Après la configuration, vous devez exécuter les commandes suivantes pour assurer le fonctionnement correct du réseau:

1.  **Vérifier les voisins OSPF:**
    `show ip ospf neighbor`
    *(Tous doivent être à l'état FULL)*
2.  **Vérifier la table de routage:**
    `show ip route ospf`
    *(Vous devez voir les réseaux Loopback des autres routeurs)*
3.  **Vérifier la connectivité:**
    Depuis PE1: `ping 10.10.10.5 source Loopback0` (Ping vers Loopback PE2)
    *(Le résultat doit être 100% de succès)*

Pour configurer la **Phase 1.a: LDP (Label Distribution Protocol)** pour votre réseau AS111, l'objectif est d'établir la distribution des étiquettes MPLS entre les routeurs cœur pour créer des chemins d'étiquettes (LSPs).

Voici les étapes détaillées de configuration et de vérification:

---

### **1. CONFIGURATION ACTIVATION MPLS LDP**

Vous devez activer MPLS LDP sur toutes les interfaces **reliant les routeurs dans AS111** (P1, P2, RR, PE1, PE2). N'activez pas sur les interfaces vers les clients (le cas échéant).

#### **Étape commune pour tous les routeurs:**
Utilisez le protocole LDP et désignez Loopback0 comme LDP Router-ID pour assurer la stabilité.

*   **Sur le routeur P1:**
    ```bash
    P1(config)# mpls ip
    P1(config)# mpls label protocol ldp
    P1(config)# mpls ldp router-id Loopback0 force
    P1(config)# interface FastEthernet0/0
    P1(config-if)# mpls ip
    P1(config)# interface GigabitEthernet1/0
    P1(config-if)# mpls ip
    ```

*   **Sur le routeur RR:**
    ```bash
    RR(config)# mpls ip
    RR(config)# mpls label protocol ldp
    RR(config)# mpls ldp router-id Loopback0 force
    RR(config)# interface FastEthernet0/0
    RR(config-if)# mpls ip
    RR(config)# interface GigabitEthernet1/0
    RR(config-if)# mpls ip
    ```

*   **Sur le routeur P2:**
    ```bash
    P2(config)# mpls ip
    P2(config)# mpls label protocol ldp
    P2(config)# mpls ldp router-id Loopback0 force
    P2(config)# interface FastEthernet0/0
    P2(config-if)# mpls ip
    P2(config)# interface GigabitEthernet1/0
    P2(config-if)# mpls ip
    ```

*   **Sur les routeurs PE1 et PE2:**
    ```bash
    PE1(config)# mpls ip
    PE1(config)# interface FastEthernet0/0
    PE1(config-if)# mpls ip
    PE1(config)# interface GigabitEthernet1/0
    PE1(config-if)# mpls ip

    PE2(config)# mpls ip
    PE2(config)# interface FastEthernet0/0
    PE2(config-if)# mpls ip
    PE2(config)# interface GigabitEthernet1/0
    PE2(config-if)# mpls ip
    ```

---

### **2. VÉRIFICATION (VALIDATE)**

Vous devez effectuer 3 étapes de vérification selon les exigences de la Phase 1.a:

#### **A. Vérifier l'état des sessions LDP (LDP Session States)**
Cette commande vous aide à savoir si les routeurs ont établi avec succès les "relations voisins" LDP.
```bash
P1# show mpls ldp neighbor
```
*   **Résultat attendu:** La colonne `State` doit afficher **OPERATIONAL**. Cela signifie que la session TCP (port 646) a été établie avec succès entre les adresses IP Loopback.

#### **B. Vérifier le transport MPLS (MPLS Transport dans le cœur)**
Cette commande vérifie la table de commutation d'étiquettes (LFIB) pour voir si les étiquettes ont été attribuées aux préfixes OSPF.
```bash
P1# show mpls forwarding-table
```
*   **Explication:** Vous verrez une liste d'`étiquettes locales` et d'`étiquettes sortantes`. Si vous voyez une étiquette (nombre entier) pour les adresses Loopback des autres routeurs, cela signifie que MPLS transporte correctement les données.

#### **C. Vérifier le mécanisme Penultimate Hop Popping (PHP)**
PHP est le mécanisme par lequel le routeur avant-dernier supprime l'étiquette MPLS avant d'envoyer au routeur de destination final pour alléger le routeur de destination.
```bash
PE1# show mpls forwarding-table
```
*   **Méthode de vérification:** Regardez la colonne **Outgoing Label** ou **Action** pour le préfixe du routeur de destination adjacent.
*   **Signe de reconnaissance:** Si vous voyez **Pop Label** ou **Untagged** lorsque la destination est un réseau direct d'un routeur voisin, alors le mécanisme **PHP** fonctionne.

**Exemple:** À P1, lors de la vérification du chemin vers `10.10.10.3/32` (Loopback du RR), si P1 voit `Pop Label` pour le saut vers RR, cela signifie que P1 (avant-dernier saut) effectue PHP pour RR.

---

### **Astuce:**
Si vous exécutez la commande `ping` entre les Loopback, essayez la commande `traceroute`:
```bash
PE1# traceroute 10.10.10.5 source Loopback0
```
Si le résultat affiche des valeurs d'étiquette (par exemple: `MPLS label 16`), cela prouve que le paquet est transporté par étiquette MPLS plutôt que par routage IP pur.

---

### **Compréhension de la table `show mpls forwarding-table` (LFIB)**

La table `show mpls forwarding-table` (LFIB - Label Forwarding Information Base) est le "cœur" de la commutation d'étiquettes. Elle indique au routeur: "Si un paquet arrive avec l'étiquette X, que dois-je faire ensuite?"

Voici comment lire en détail chaque colonne en fonction de vos résultats à **P1**:

---

### **1. Signification des colonnes principales**
*   **Local Label**: L'étiquette que **P1 génère lui-même** et annonce aux routeurs voisins (neighbor). Lorsqu'un voisin envoie un paquet à P1 avec cette étiquette, P1 sait qu'il doit la traiter pour le Préfixe correspondant.
*   **Outgoing Label**: L'action suivante de P1. 
    *   **Pop Label**: Suppression de l'étiquette.
    *   **Nombre spécifique (par exemple: 21)**: Remplacer l'étiquette ancienne par cette nouvelle étiquette (Swap).
*   **Prefix or Tunnel Id**: La destination du paquet (généralement des adresses IP Loopback ou des réseaux reliant les routeurs).
*   **Bytes Label Switched**: La quantité réelle de données commutées via cette étiquette.
*   **Outgoing interface & Next Hop**: Le port physique et l'adresse IP du routeur suivant pour envoyer le paquet.

---

### **2. Analyse de cas spécifiques (Case Study)**

#### **Cas 1: Mécanisme PHP (Penultimate Hop Popping)**
> `16 | Pop Label | 10.10.10.3/32 | Fa0/0 | 10.10.1.9`

*   **Explication**: Quand P1 reçoit un paquet avec l'étiquette **16**, il sait que la destination est `10.10.10.3` (Routeur RR). 
*   **Action**: Parce que Outgoing Label est **Pop Label**, P1 va **supprimer l'étiquette** et envoyer le paquet IP pur au RR via le port `Fa0/0`.
*   **Pourquoi?**: Parce que P1 est le "saut avant-dernier" (Penultimate Hop) du RR. Il supprime l'étiquette d'abord pour que RR n'ait pas à la traiter, ce qui aide RR à fonctionner plus vite.

#### **Cas 2: Équilibrage de charge (Load Balancing)**
> `17 | Pop Label | 10.10.1.12/30 | Fa0/0 & Gi1/0`

*   **Explication**: Pour atteindre le réseau `10.10.1.12/30` (lien entre RR et P2), P1 a 2 routes via RR (`Fa0/0`) ou via P2 (`Gi1/0`). OSPF a calculé le coût identique donc MPLS supporte aussi l'équilibrage de charge ici.

#### **Cas 3: Remplacement d'étiquette (Label Swap)**
> `21 | 21 | 10.10.10.5/32 | Gi1/0 | 10.10.1.6`

*   **Explication**: C'est la ligne la plus intéressante. La destination est `10.10.10.5` (Routeur PE2).
*   **Action**: Quand un paquet arrive à P1 avec l'étiquette **21** (Local), P1 regarde dans la table et voit que le Routeur P2 (`10.10.1.6`) demande d'utiliser l'étiquette **21** (Outgoing) pour aller à PE2.
*   **Résultat**: P1 effectue l'action **Swap** (garder effectivement la valeur 21 mais essentiellement remplacer sa propre étiquette par celle du voisin) et envoie via le port `Gi1/0`.

---

### **3. Résumé de l'état de votre réseau**
*   **P1 a appris toutes les étiquettes**: Il a les étiquettes pour tous les Loopback de .1 à .5.
*   **Le trafic fonctionne**: La colonne `Bytes Switched` aux lignes 19, 20, 21 a des chiffres (570, 1302, 360). Cela prouve que vous avez exécuté `ping` ou `traceroute` entre les Routeurs PE, et les données **vont réellement via étiquette MPLS**.
*   **Structure de connexion**: P1 joue le rôle de "carrefour". Il se connecte directement au RR (via Fa0/0), P2 (via Gi1/0) et PE1 (via Gi2/0).
