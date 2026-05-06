Để hoàn thành **Phase 2**, bạn cần tập trung vào việc thiết lập **iBGP VPNv4** giữa các PE và RR để làm "đường ống" vận chuyển dữ liệu khách hàng. Các router trung gian (P1, P2) sẽ không chạy BGP.

Dưới đây là chi tiết cấu hình cho từng loại router dựa trên sơ đồ AS111 của bạn:

---

### **1. Cấu hình trên Route Reflector (RR - 10.10.10.2)**
RR đóng vai trò là "điểm hội tụ" thông tin định tuyến. Thay vì PE1 và PE2 phải kết nối trực tiếp, chúng chỉ cần kết nối tới RR.



```bash
RR# configure terminal
RR(config)# router bgp 111wwr
RR(config-router)# bgp log-neighbor-changes 
#Mặc định, BGP là một giao thức khá "im lặng". Nếu một kết nối BGP giữa PE và RR bị đứt (Down) hoặc được thiết lập lại (Up), Router có thể không hiển thị thông báo gì ra màn hình console.Khi có lệnh này: Mọi thay đổi về trạng thái của các láng giềng BGP (Neighbor) sẽ được Router ghi lại và hiển thị ngay lập tức dưới dạng các dòng thông báo hệ thống (Syslog).
! --- Thiết lập láng giềng với PE1 ---
RR(config-router)# neighbor 10.10.10.4 remote-as 111
RR(config-router)# neighbor 10.10.10.4 update-source Loopback0
! --- Thiết lập láng giềng với PE2 ---
RR(config-router)# neighbor 10.10.10.5 remote-as 111
RR(config-router)# neighbor 10.10.10.5 update-source Loopback0
!
RR(config-router)# address-family vpnv4
! --- Kích hoạt tính năng phản xạ (Reflection) cho PE1 ---
RR(config-router-af)# neighbor 10.10.10.4 activate
RR(config-router-af)# neighbor 10.10.10.4 send-community both
RR(config-router-af)# neighbor 10.10.10.4 route-reflector-client
! --- Kích hoạt tính năng phản xạ cho PE2 ---
RR(config-router-af)# neighbor 10.10.10.5 activate
RR(config-router-af)# neighbor 10.10.10.5 send-community both
RR(config-router-af)# neighbor 10.10.10.5 route-reflector-client
RR(config-router-af)# exit-address-family
```

---

### **2. Cấu hình trên các Provider Edge (PE1 & PE2)**
Các PE sẽ gửi thông tin mạng của khách hàng (sau này ở Phase 3) lên RR.

*   **Tại PE1 (10.10.10.4):**
```bash
PE1(config)# router bgp 111
PE1(config-router)# neighbor 10.10.10.2 remote-as 111
PE1(config-router)# neighbor 10.10.10.2 update-source Loopback0
PE1(config-router)# address-family vpnv4
PE1(config-router-af)# neighbor 10.10.10.2 activate
PE1(config-router-af)# neighbor 10.10.10.2 send-community both
PE1(config-router-af)# exit-address-family
```

*   **Tại PE2 (10.10.10.5):**
*(Cấu hình tương tự PE1, trỏ neighbor về IP của RR là 10.10.10.2)*

---

### **3. Cấu hình trên các Provider Router (P1 & P2)**
**Lưu ý cực kỳ quan trọng:** Các router P **KHÔNG** chạy BGP. Nhiệm vụ của chúng trong Phase 2 chỉ là đảm bảo MPLS LDP chạy thông suốt để vận chuyển gói tin dựa trên nhãn.

Nếu bạn đã làm xong phần Addressing, OSPF và MPLS ở bước trước, thì ở Phase 2 này bạn **không cần gõ thêm lệnh gì** trên P1 và P2.

---

### **4. Kiểm tra trạng thái (Validation)**
Sau khi cấu hình xong, bạn phải kiểm tra các tiêu chí sau:

1.  **Kiểm tra phiên BGP (Trên RR):**
    `RR# show bgp vpnv4 unicast all summary`
    *Trạng thái (State/PfxRcd) phải là một con số (thường là 0 nếu chưa có khách hàng), không được là "Idle" hay "Active".*

2.  **Kiểm tra khả năng vận chuyển nhãn (Trên bất kỳ router nào):**
    `P1# show mpls forwarding-table`
    *Bạn phải thấy các nhãn cho địa chỉ Loopback của PE1 (10.10.10.4) và PE2 (10.10.10.5).*

### **Tại sao lại dùng Loopback cho BGP?**
Vì địa chỉ Loopback luôn ở trạng thái "Up" miễn là router còn chạy. Nếu một đường dây vật lý giữa P1 và RR bị đứt, OSPF sẽ tìm đường vòng qua P2, và phiên BGP vẫn được duy trì nhờ IP Loopback không đổi.

Bạn đã sẵn sàng để chuyển sang **Phase 3** (cấu hình VRF cho khách hàng) chưa?
Sau khi cấu hình xong **Phase 2**, bạn cần sử dụng một bộ lệnh kiểm tra (verification) theo từng lớp để đảm bảo "đường ống" BGP VPNv4 đã sẵn sàng trước khi sang Phase 3.

Dưới đây là các lệnh quan trọng nhất phân theo mục đích:

### **1. Kiểm tra trạng thái láng giềng BGP (Quan trọng nhất)**
Lệnh này giúp bạn biết các PE và RR đã thực sự kết nối được với nhau ở tầng BGP chưa.

*   **Lệnh:** `show bgp vpnv4 unicast all summary`
*   **Nơi thực hiện:** Trên **RR** hoặc các **PE**.
*   **Dấu hiệu thành công:** 
    *   Cột **State/PfxRcd** phải là một con số (ví dụ: `0`). 
    *   Nếu hiển thị `Active`, `Idle` hoặc `Connect`, nghĩa là phiên BGP chưa thiết lập được (thường do lỗi định tuyến OSPF không thông Loopback hoặc sai địa chỉ Neighbor).



---

### **2. Kiểm tra chi tiết cấu hình Neighbor**
Để xem RR đã nhận diện đúng các PE là "Client" chưa (vì Phase 2 yêu cầu Route Reflector).

*   **Lệnh:** `show bgp vpnv4 unicast all neighbors [IP_Neighbor]`
*   **Ví dụ (trên RR):** `show bgp vpnv4 unicast all neighbors 10.10.10.4`
*   **Dấu hiệu thành công:** Tìm dòng chữ **"Route-reflector client"** trong kết quả trả về. Điều này xác nhận RR sẽ phản xạ route cho PE này.

---

### **3. Kiểm tra khả năng vận chuyển nhãn MPLS (LDP)**
BGP VPNv4 cần nhãn MPLS để chuyển tiếp dữ liệu qua các router P. Nếu LDP không chạy, BGP có thể Up nhưng dữ liệu sẽ bị rớt (drop) ở các router P1, P2.

*   **Lệnh:** `show mpls ldp neighbor`
*   **Dấu hiệu thành công:** Trạng thái phải là **"Oper"** (Operational).
*   **Lệnh bổ trợ:** `show mpls forwarding-table`
    *   Đảm bảo bạn thấy nhãn cho các địa chỉ Loopback của các Router đối diện (ví dụ từ PE1 phải thấy nhãn để tới 10.10.10.5 của PE2).



---

### **4. Kiểm tra bảng định tuyến VPNv4**
Ở Phase 2, bảng này có thể đang trống nếu bạn chưa cấu hình khách hàng (Phase 3), nhưng bạn vẫn nên biết lệnh này để kiểm tra ngay khi bắt đầu Phase 3.

*   **Lệnh:** `show bgp vpnv4 unicast all`
*   **Ý nghĩa:** Hiển thị tất cả các tuyến đường VPNv4 mà Router đang lưu giữ (bao gồm cả Route Distinguisher và VPN Label).

---

### **5. Kiểm tra tính thông suốt (End-to-End Connectivity)**
Trước khi sang Phase 3, hãy đảm bảo các điểm cuối (Loopback của PE) có thể giao tiếp với nhau bằng nhãn.

*   **Lệnh:** `ping 10.10.10.5 source Loopback0` (từ PE1 ping sang PE2).
*   **Lệnh nâng cao:** `traceroute 10.10.10.5 source Loopback0`
    *   **Dấu hiệu thành công:** Bạn sẽ thấy các dòng có kèm thông tin nhãn (ví dụ: `[MPLS: Label 16 Exp 0]`). Điều này chứng tỏ gói tin đang được chuyển mạch bằng nhãn MPLS thay vì IP thông thường.

---

### **Tóm tắt quy trình kiểm tra lỗi (Troubleshooting):**
1.  Nếu BGP không lên (`Idle`): Kiểm tra OSPF (`show ip route`) xem có thấy IP Loopback của nhau không.
2.  Nếu BGP đã `Established` nhưng ping traceroute không thấy nhãn: Kiểm tra LDP (`show mpls interfaces`).
3.  Nếu RR không gửi route cho các PE: Kiểm tra lệnh `route-reflector-client` trên RR.

Bạn đã kiểm tra lệnh `show bgp vpnv4 unicast all summary` chưa? Kết quả cột **PfxRcd** hiện tại là bao nhiêu?