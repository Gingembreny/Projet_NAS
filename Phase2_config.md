Dès de finaliser la **Phase 2**, vous devez vous concentrer sur l'établissement du **iBGP VPNv4** entre les PE et RR pour créer un "tunnel" de transport des données client. Les routeurs intermédiaires (P1, P2) n'exécuteront pas BGP.

Dưới đây là chi tiết cấu hình cho từng loại router dựa trên sơ đồ AS111 của bạn:

---

### **1. Configuration sur Route Reflector (RR - 10.10.10.3)**
RR đóng vai trò là "điểm hội tụ" thông tin định tuyến. Thay vì PE1 và PE2 phải kết nối trực tiếp, chúng chỉ cần kết nối tới RR.



```bash
RR# configure terminal
RR(config)# router bgp 111
RR(config-router)# bgp log-neighbor-changes 
#Mặc định, BGP là một giao thức khá "im lặng". Nếu một kết nối BGP giữa PE và RR bị đứt (Down) hoặc được thiết lập lại (Up), Router có thể không hiển thị thông báo gì ra màn hình console.Khi có lệnh này: Mọi thay đổi về trạng thái của các láng giềng BGP (Neighbor) sẽ được Router ghi lại và hiển thị ngay lập tức dưới dạng các dòng thông báo hệ thống (Syslog).
! --- Établir un voisin avec PE1 ---
RR(config-router)# neighbor 10.10.10.1 remote-as 111
RR(config-router)# neighbor 10.10.10.1 update-source Loopback0
! --- Établir un voisin avec PE2 ---
RR(config-router)# neighbor 10.10.10.5 remote-as 111
RR(config-router)# neighbor 10.10.10.5 update-source Loopback0
!
RR(config-router)# address-family vpnv4
! --- Activer la réflexion (Reflection) pour PE1 ---
RR(config-router-af)# neighbor 10.10.10.1 activate
RR(config-router-af)# neighbor 10.10.10.1 send-community both
RR(config-router-af)# neighbor 10.10.10.1 route-reflector-client
! --- Activer la réflexion pour PE2 ---
RR(config-router-af)# neighbor 10.10.10.5 activate
RR(config-router-af)# neighbor 10.10.10.5 send-community both
RR(config-router-af)# neighbor 10.10.10.5 route-reflector-client
RR(config-router-af)# exit-address-family
```

---

### **2. Configuration sur les Provider Edge (PE1 et PE2)**
Les PE enverront les informations de réseau du client (plus tard en Phase 3) au RR.

*   **Sur PE1 (10.10.10.1):**
```bash
PE1(config)# router bgp 111
PE1(config-router)# neighbor 10.10.10.3 remote-as 111
PE1(config-router)# neighbor 10.10.10.3 update-source Loopback0
PE1(config-router)# address-family vpnv4
PE1(config-router-af)# neighbor 10.10.10.3 activate
PE1(config-router-af)# neighbor 10.10.10.3 send-community both
PE1(config-router-af)# exit-address-family
```

*   **Sur PE2 (10.10.10.5):**
*(Configuration similaire à PE1, pointant le voisin vers l'IP du RR 10.10.10.3)*

---

### **3. Configuration sur les routeurs Provider (P1 et P2)**
**Note extrêmement importante:** Les routeurs P n'exécutent **PAS** BGP. Leur seule tâche dans la Phase 2 est de s'assurer que LDP MPLS s'exécute sans interruption pour transporter les paquets en fonction des étiquettes.

Si vous avez déjà terminé la section Adressage, OSPF et MPLS à l'étape précédente, alors à cette Phase 2 vous n'avez **pas besoin de taper d'autres commandes** sur P1 et P2.

---

### **4. Vérification de l'état (Validation)**
Après configuration, vous devez vérifier les critères suivants:

1.  **Vérifier la session BGP (Sur RR):**
    `RR# show bgp vpnv4 unicast all summary`
    *L'état (State/PfxRcd) doit être un nombre (généralement 0 si pas de client encore), pas "Idle" ou "Active".*

2.  **Vérifier la capacité de transport d'étiquettes (Sur n'importe quel routeur):**
    `P1# show mpls forwarding-table`
    *Vous devez voir les étiquettes pour les adresses Loopback de PE1 (10.10.10.1) et PE2 (10.10.10.5).*

### **Pourquoi utiliser Loopback pour BGP?**
Parce que l'adresse Loopback est toujours "Up" tant que le routeur fonctionne. Si une ligne physique entre P1 et RR est coupée, OSPF trouvera une route alternative via P2, et la session BGP sera maintenue grâce à l'IP Loopback inchangée.

Êtes-vous prêt à passer à la **Phase 3** (configuration VRF pour les clients)?
Après avoir complété la **Phase 2**, vous devez utiliser un ensemble de commandes de vérification (verification) couche par couche pour assurer que le "tunnel" BGP VPNv4 est prêt avant de passer à la Phase 3.

Dưới đây là các lệnh quan trọng nhất phân theo mục đích:

### **1. Vérifier l'état du voisin BGP (Le plus important)**
Cette commande vous aide à savoir si les PE et RR se sont réellement connectés au niveau BGP.

*   **Commande:** `show bgp vpnv4 unicast all summary`
*   **Exécuter sur:** **RR** ou les **PE**.
*   **Signe de succès:** 
    *   La colonne **State/PfxRcd** doit être un nombre (par exemple: `0`). 
    *   Si elle affiche `Active`, `Idle` ou `Connect`, cela signifie que la session BGP n'a pas pu s'établir (généralement due à une erreur de routage OSPF qui ne passe pas Loopback ou une adresse voisin incorrecte).



---

### **2. Vérifier la configuration détaillée du voisin**
Pour voir si RR a correctement identifié les PE comme "Client" (puisque la Phase 2 nécessite un Route Reflector).

*   **Commande:** `show bgp vpnv4 unicast all neighbors [IP_Voisin]`
*   **Exemple (sur RR):** `show bgp vpnv4 unicast all neighbors 10.10.10.1`
*   **Signe de succès:** Recherchez la ligne **"Route-reflector client"** dans le résultat retourné. Cela confirme que RR réfléchira les routes pour ce PE.

---

### **3. Vérifier la capacité de transport d'étiquette MPLS (LDP)**
BGP VPNv4 a besoin d'étiquettes MPLS pour acheminer les données via les routeurs P. Si LDP ne fonctionne pas, BGP peut être Up mais les données seront rejetées (drop) aux routeurs P1, P2.

*   **Commande:** `show mpls ldp neighbor`
*   **Signe de succès:** L'état doit être **"Oper"** (Opérationnel).
*   **Commande supplémentaire:** `show mpls forwarding-table`
    *   Assurez-vous de voir une étiquette pour les adresses Loopback des routeurs opposés (par exemple, depuis PE1 vous devriez voir une étiquette pour aller à 10.10.10.5 de PE2).



---

### **4. Vérifier la table de routage VPNv4**
En Phase 2, cette table peut être vide si vous n'avez pas encore configuré de clients (Phase 3), mais vous devez toujours connaître cette commande pour vérifier dès le début de la Phase 3.

*   **Commande:** `show bgp vpnv4 unicast all`
*   **Signification:** Affiche toutes les routes VPNv4 que le routeur stocke (incluant le Route Distinguisher et VPN Label).

---

### **5. Vérifier la connectivité (End-to-End Connectivity)**
Avant de passer à la Phase 3, assurez-vous que les points finaux (Loopback des PE) peuvent communiquer les uns avec les autres avec étiquettes.

*   **Commande:** `ping 10.10.10.5 source Loopback0` (depuis PE1 ping vers PE2).
*   **Commande avancée:** `traceroute 10.10.10.5 source Loopback0`
    *   **Signe de succès:** Vous verrez des lignes avec des informations d'étiquette (par exemple: `[MPLS: Label 16 Exp 0]`). Cela prouve que le paquet est acheminé par étiquette MPLS au lieu du routage IP normal.

---

### **Résumé du processus de vérification des erreurs (Troubleshooting):**
1.  Si BGP ne monte pas (`Idle`): Vérifiez OSPF (`show ip route`) pour voir si vous pouvez voir les adresses IP Loopback les uns des autres.
2.  Si BGP est `Established` mais ping traceroute ne montre pas d'étiquette: Vérifiez LDP (`show mpls interfaces`).
3.  Si RR n'envoie pas de route aux PE: Vérifiez la commande `route-reflector-client` sur RR.
