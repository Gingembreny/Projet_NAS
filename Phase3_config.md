Voici la configuration complète standard pour le réseau MPLS VPN basée sur votre dernier fichier JSON. Cette configuration est divisée en 3 parties: **Routeurs cœur/P**, **Route Reflector (RR)**, et les **routeurs d'accès (PE et CE)** pour compléter la Phase 3.

---

### **1. CONFIGURATION DES ROUTEURS CŒUR (CORE - P)**
Ces routeurs effectuent simplement la commutation d'étiquettes, ils n'exécutent pas BGP.

#### **Routeur P1**
```bash
conf t
hostname P1
ip cef
!
interface Loopback0
 ip address 10.10.10.2 255.255.255.255
!
mpls ip
mpls label protocol ldp
mpls ldp router-id Loopback0 force
interface FastEthernet0/0
 description Lien_vers_PE1
 ip address 10.10.1.2 255.255.255.252
 mpls ip
 no shutdown
!
interface GigabitEthernet1/0
 description Lien_vers_P2
 ip address 10.10.1.5 255.255.255.252
 mpls ip
 no shutdown
!
router ospf 1
 router-id 111.0.0.2
 network 10.10.10.2 0.0.0.0 area 0
 network 10.10.1.0 0.0.0.3 area 0
 network 10.10.1.4 0.0.0.3 area 0
end
wr
```

#### **Routeur P2**
```bash
conf t
hostname P2
ip cef
!
interface Loopback0
 ip address 10.10.10.4 255.255.255.255
!
mpls ip
mpls label protocol ldp
mpls ldp router-id Loopback0 force
interface FastEthernet0/0
 description Lien_vers_P1
 ip address 10.10.1.6 255.255.255.252
 mpls ip
 no shutdown
!
interface GigabitEthernet1/0
 description Lien_vers_PE2
 ip address 10.10.1.17 255.255.255.252
 mpls ip
 no shutdown
!
router ospf 1
 router-id 111.0.0.4
 network 10.10.10.4 0.0.0.0 area 0
 network 10.10.1.4 0.0.0.3 area 0
 network 10.10.1.16 0.0.0.3 area 0
end
wr
```

---

### **2. CONFIGURATION ROUTE REFLECTOR (RR)**
RR réachemine les routes VPNv4 pour les PE.

```bash
conf t
hostname RR
ip cef
!
interface Loopback0
 ip address 10.10.10.3 255.255.255.255
!
mpls ip
mpls label protocol ldp
mpls ldp router-id Loopback0 force
interface FastEthernet0/0
 description Lien_vers_PE1
 ip address 10.10.1.9 255.255.255.252
 mpls ip
 no shutdown
!
interface GigabitEthernet1/0
 description Lien_vers_PE2
 ip address 10.10.1.13 255.255.255.252
 mpls ip
 no shutdown
!
router ospf 1
 router-id 111.0.0.3
 network 10.10.10.3 0.0.0.0 area 0
 network 10.10.1.8 0.0.0.3 area 0
 network 10.10.1.12 0.0.0.3 area 0
!
router bgp 111
 bgp log-neighbor-changes 
 neighbor 10.10.10.1 remote-as 111
 neighbor 10.10.10.1 update-source Loopback0
 neighbor 10.10.10.5 remote-as 111
 neighbor 10.10.10.5 update-source Loopback0
 !
 address-family vpnv4
  neighbor 10.10.10.1 activate
  neighbor 10.10.10.1 route-reflector-client
  neighbor 10.10.10.1 send-community both
  neighbor 10.10.10.5 activate
  neighbor 10.10.10.5 route-reflector-client
  neighbor 10.10.10.5 send-community both
 exit-address-family
end
wr
```

---

### **3. CONFIGURATION DES ROUTEURS D'ACCÈS (PE)**
PE gèrent les VRF pour les clients AS222 et AS333.

#### **Routeur PE1**
```bash
conf t
hostname PE1
ip cef
!
vrf definition AS222
 rd 111:222
 route-target export 111:222
 route-target import 111:222
 address-family ipv4
 exit-address-family
!
vrf definition AS333
 rd 111:333
 route-target export 111:333
 route-target import 111:333
 address-family ipv4
 exit-address-family
!
interface Loopback0
 ip address 10.10.10.1 255.255.255.255
!
mpls ip
mpls label protocol ldp
mpls ldp router-id Loopback0 force
interface FastEthernet0/0
 description Lien_vers_P1
 ip address 10.10.1.1 255.255.255.252
 mpls ip
 no shutdown
!
interface GigabitEthernet1/0
 description Lien_vers_RR
 ip address 10.10.1.10 255.255.255.252
 mpls ip
 no shutdown
!
interface GigabitEthernet2/0
 description Lien_vers_CE1_AS222
 vrf forwarding AS222
 ip address 10.20.1.21 255.255.255.252
 no shutdown
!
interface GigabitEthernet3/0
 description Lien_vers_CE2_AS333
 vrf forwarding AS333
 ip address 10.30.1.29 255.255.255.252
 no shutdown
!
router ospf 1
 router-id 111.0.0.1
 network 10.10.10.1 0.0.0.0 area 0
 network 10.10.1.0 0.0.0.3 area 0
 network 10.10.1.8 0.0.0.3 area 0
!
router bgp 111
 neighbor 10.10.10.3 remote-as 111
 neighbor 10.10.10.3 update-source Loopback0
 !
 address-family vpnv4
  neighbor 10.10.10.3 activate
  neighbor 10.10.10.3 send-community both
 exit-address-family
 !
 address-family ipv4 vrf AS222
  neighbor 10.20.1.22 remote-as 222
  neighbor 10.20.1.22 activate
 exit-address-family
 !
 address-family ipv4 vrf AS333
  neighbor 10.30.1.30 remote-as 333
  neighbor 10.30.1.30 activate
 exit-address-family
end
wr
```

#### **Routeur PE2**
```bash
conf t
hostname PE2
ip cef
!
vrf definition AS222
 rd 111:222
 route-target export 111:222
 route-target import 111:222
 address-family ipv4
 exit-address-family
!
vrf definition AS333
 rd 111:333
 route-target export 111:333
 route-target import 111:333
 address-family ipv4
 exit-address-family
!
interface Loopback0
 ip address 10.10.10.5 255.255.255.255
!
mpls ip
mpls label protocol ldp
mpls ldp router-id Loopback0 force
interface FastEthernet0/0
 description Lien_vers_RR
 ip address 10.10.1.14 255.255.255.252
 mpls ip
 no shutdown
!
interface GigabitEthernet1/0
 description Lien_vers_P2
 ip address 10.10.1.18 255.255.255.252
 mpls ip
 no shutdown
!
interface GigabitEthernet2/0
 description Lien_vers_CE3_AS222
 vrf forwarding AS222
 ip address 10.20.1.25 255.255.255.252
 no shutdown
!
interface GigabitEthernet3/0
 description Lien_vers_CE4_AS333
 vrf forwarding AS333
 ip address 10.30.1.33 255.255.255.252
 no shutdown
!
router ospf 1
 router-id 111.0.0.5
 network 10.10.10.5 0.0.0.0 area 0
 network 10.10.1.12 0.0.0.3 area 0
 network 10.10.1.16 0.0.0.3 area 0
!
router bgp 111
 neighbor 10.10.10.3 remote-as 111
 neighbor 10.10.10.3 update-source Loopback0
 !
 address-family vpnv4
  neighbor 10.10.10.3 activate
  neighbor 10.10.10.3 send-community both
 exit-address-family
 !
 address-family ipv4 vrf AS222
  neighbor 10.20.1.26 remote-as 222
  neighbor 10.20.1.26 activate
 exit-address-family
 !
 address-family ipv4 vrf AS333
  neighbor 10.30.1.34 remote-as 333
  neighbor 10.30.1.34 activate
 exit-address-family
end
wr
```

---

### **4. CONFIGURATION ROUTEURS CLIENT (CE)**
CE exécutent simplement le routage standard.

#### **Routeur CE1 (AS222)**
```bash
conf t
hostname CE1
interface Loopback0
 ip address 10.20.10.6 255.255.255.255
interface FastEthernet0/0
 ip address 10.20.1.22 255.255.255.252
 no shutdown
router bgp 222
 neighbor 10.20.1.21 remote-as 111
 network 10.20.10.6 mask 255.255.255.255
end
wr
```

#### **Routeur CE2 (AS333)**
```bash
conf t
hostname CE2
interface Loopback0
 ip address 10.30.10.8 255.255.255.255
interface FastEthernet0/0
 ip address 10.30.1.30 255.255.255.252
 no shutdown
router bgp 333
 neighbor 10.30.1.29 remote-as 111
 network 10.30.10.8 mask 255.255.255.255
end
wr
```

#### **Routeur CE3 (AS222)**
```bash
conf t
hostname CE3
interface Loopback0
 ip address 10.20.10.7 255.255.255.255
interface FastEthernet0/0
 ip address 10.20.1.26 255.255.255.252
 no shutdown
router bgp 222
 neighbor 10.20.1.25 remote-as 111
 network 10.20.10.7 mask 255.255.255.255
end
wr
```

#### **Routeur CE4 (AS333)**
```bash
conf t
hostname CE4
interface Loopback0
 ip address 10.30.10.9 255.255.255.255
interface FastEthernet0/0
 ip address 10.30.1.34 255.255.255.252
 no shutdown
router bgp 333
 neighbor 10.30.1.33 remote-as 111
 network 10.30.10.9 mask 255.255.255.255
end
wr
```
