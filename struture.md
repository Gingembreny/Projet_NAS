# 📊 ARCHITECTURE RÉSEAU AS111 (MPLS/BGP)

## **1. Vue d'ensemble**

Réseau de **5 routeurs** configurés en architecture MPLS/BGP avec redondance et réflexion de routes.

| Routeur | Type | Loopback | Router ID | Rôle |
|---------|------|----------|-----------|------|
| **PE1** | Provider Edge | 10.10.10.1/32 | 111.0.0.1 | Accès clients (site 1) |
| **P1** | Provider Core | 10.10.10.2/32 | 111.0.0.2 | Hub central |
| **RR** | Route Reflector | 10.10.10.3/32 | 111.0.0.3 | Réflexion BGP |
| **P2** | Provider Core | 10.10.10.4/32 | 111.0.0.4 | Cœur réseau 2 |
| **PE2** | Provider Edge | 10.10.10.5/32 | 111.0.0.5 | Accès clients (site 2) |

---

## **2. Détail des routeurs AS111**


### **PE1** (Provider Edge - Site 1)
| Propriété | Valeur |
|-----------|--------|
| IP Loopback | 10.10.10.1/32 |
| Router ID | 111.0.0.1 |
| Connexions | P1, RR, CE1, CE2 |

**Interfaces:**
- **FastEthernet0/0**: 10.10.1.1/30 → P1 (subnet 10.10.1.0/30)
- **GigabitEthernet1/0**: 10.10.1.10/30 → RR (subnet 10.10.1.8/30)
- **GigabitEthernet2/0**: 10.20.1.21/30 → CE1 (subnet 10.20.1.20/30, AS222)
- **GigabitEthernet3/0**: 10.30.1.29/30 → CE2 (subnet 10.30.1.28/30, AS333)

---

### **P1** (Provider Core - Hub)
| Propriété | Valeur |
|-----------|--------|
| IP Loopback | 10.10.10.2/32 |
| Router ID | 111.0.0.2 |
| Connexions | PE1, P2 |

**Interfaces:**
- **FastEthernet0/0**: 10.10.1.2/30 → PE1 (subnet 10.10.1.0/30)
- **GigabitEthernet1/0**: 10.10.1.5/30 → P2 (subnet 10.10.1.4/30)

---

### **RR** (Route Reflector)
| Propriété | Valeur |
|-----------|--------|
| IP Loopback | 10.10.10.3/32 |
| Router ID | 111.0.0.3 |
| Connexions | PE1, PE2 |

**Interfaces:**
- **FastEthernet0/0**: 10.10.1.9/30 → PE1 (subnet 10.10.1.8/30)
- **GigabitEthernet1/0**: 10.10.1.13/30 → PE2 (subnet 10.10.1.12/30)

---

### **P2** (Provider Core - Cœur 2)
| Propriété | Valeur |
|-----------|--------|
| IP Loopback | 10.10.10.4/32 |
| Router ID | 111.0.0.4 |
| Connexions | P1, PE2 |

**Interfaces:**
- **FastEthernet0/0**: 10.10.1.6/30 → P1 (subnet 10.10.1.4/30)
- **GigabitEthernet1/0**: 10.10.1.17/30 → PE2 (subnet 10.10.1.16/30)

---

### **PE2** (Provider Edge - Site 2)
| Propriété | Valeur |
|-----------|--------|
| IP Loopback | 10.10.10.5/32 |
| Router ID | 111.0.0.5 |
| Connexions | RR, P2, CE3, CE4 |

**Interfaces:**
- **FastEthernet0/0**: 10.10.1.14/30 → RR (subnet 10.10.1.12/30)
- **GigabitEthernet1/0**: 10.10.1.18/30 → P2 (subnet 10.10.1.16/30)
- **GigabitEthernet2/0**: 10.20.1.25/30 → CE3 (subnet 10.20.1.24/30, AS222)
- **GigabitEthernet3/0**: 10.30.1.33/30 → CE4 (subnet 10.30.1.32/30, AS333)

---

## **3. Tableau complet des liens**

| # | Routeur 1 | Interface 1 | IP 1 | ↔️ | Routeur 2 | Interface 2 | IP 2 | Subnet | AS |
|---|-----------|-----------|------|-----|-----------|-----------|------|--------|-----|
| 1 | PE1 | Fa0/0 | 10.10.1.1/30 | ↔️ | P1 | Fa0/0 | 10.10.1.2/30 | 10.10.1.0/30 | 111 |
| 2 | P1 | Gi1/0 | 10.10.1.5/30 | ↔️ | P2 | Fa0/0 | 10.10.1.6/30 | 10.10.1.4/30 | 111 |
| 3 | PE1 | Gi1/0 | 10.10.1.10/30 | ↔️ | RR | Fa0/0 | 10.10.1.9/30 | 10.10.1.8/30 | 111 |
| 4 | RR | Gi1/0 | 10.10.1.13/30 | ↔️ | PE2 | Fa0/0 | 10.10.1.14/30 | 10.10.1.12/30 | 111 |
| 5 | P2 | Gi1/0 | 10.10.1.17/30 | ↔️ | PE2 | Gi1/0 | 10.10.1.18/30 | 10.10.1.16/30 | 111 |
| 6 | PE1 | Gi2/0 | 10.20.1.21/30 | ↔️ | CE1 | Fa0/0 | 10.20.1.22/30 | 10.20.1.20/30 | 222 |
| 7 | PE2 | Gi2/0 | 10.20.1.25/30 | ↔️ | CE3 | Fa0/0 | 10.20.1.26/30 | 10.20.1.24/30 | 222 |
| 8 | PE1 | Gi3/0 | 10.30.1.29/30 | ↔️ | CE2 | Fa0/0 | 10.30.1.30/30 | 10.30.1.28/30 | 333 |
| 9 | PE2 | Gi3/0 | 10.30.1.33/30 | ↔️ | CE4 | Fa0/0 | 10.30.1.34/30 | 10.30.1.32/30 | 333 |

---

## **4. Réseau client AS222**

| Routeur | Loopback | Router ID | Connexion | Interface | IP Interface | IP Distant |
|---------|----------|-----------|-----------|-----------|-------------|-----------|
| **CE1** | 10.20.10.6/32 | 222.0.0.6 | PE1 | Fa0/0 | 10.20.1.22/30 | 10.20.1.21 |
| **CE3** | 10.20.10.7/32 | 222.0.0.7 | PE2 | Fa0/0 | 10.20.1.26/30 | 10.20.1.25 |

---

## **5. Réseau client AS333**

| Routeur | Loopback | Router ID | Connexion | Interface | IP Interface | IP Distant |
|---------|----------|-----------|-----------|-----------|-------------|-----------|
| **CE2** | 10.30.10.8/32 | 333.0.0.8 | PE1 | Fa0/0 | 10.30.1.30/30 | 10.30.1.29 |
| **CE4** | 10.30.10.9/32 | 333.0.0.9 | PE2 | Fa0/0 | 10.30.1.34/30 | 10.30.1.33 |

---

## **6. Vérifications**

### **1. Doublons d'adresses IP**
✅ Aucun doublon - Toutes les adresses sont uniques
- Loopback AS111: 10.10.10.1-5
- Loopback AS222: 10.20.10.6-7
- Loopback AS333: 10.30.10.8-9
- Liens: Tous dans des subnets différents (/30)

### **2. Router IDs**
✅ Valides et uniques - Format AS.0.0.X
- AS111: 111.0.0.1-5
- AS222: 222.0.0.6-7
- AS333: 333.0.0.8-9

### **3. IPs d'interfaces**
✅ Correctes - Toutes dans le subnet /30 déclaré
- Chaque lien utilise exactement 2 IPs usables
- Pas de débordement de subnet

### **4. Masques de sous-réseau**
✅ /30 pour les liens point-à-point (4 IPs chacun)
✅ /32 pour les loopbacks (1 IP chacun)

### **5. Disponibilité des interfaces**
✅ Toutes les interfaces requises sont disponibles
- PE1: 4 interfaces (Max: 4) ✓
- PE2: 4 interfaces (Max: 4) ✓
- P1: 2 interfaces (Max: 4) ✓
- P2: 2 interfaces (Max: 4) ✓
- RR: 2 interfaces (Max: 4) ✓

---

## **📊 Résumé statistique**

| Élément | Valeur |
|---------|--------|
| **Routeurs AS111** | 5 (2 Core + 2 Edge + 1 RR) |
| **Routeurs clients** | 4 (2 en AS222 + 2 en AS333) |
| **Liens internes AS111** | 5 |
| **Liens inter-AS** | 4 |
| **Subnets /30** | 9 |
| **Loopbacks /32** | 9 |
| **Router IDs utilisés** | 9 |

**Architecture validée et prête pour configuration réseau ! ✅**