Dựa trên tệp cấu hình JSON bạn cung cấp, đây là bảng tổng hợp thông tin chi tiết của các router khách hàng (**CE - Customer Edge**) thuộc hai hệ thống mạng khác nhau (AS222 và AS333). Bạn có thể sử dụng dữ liệu này để cấu hình cho **Phase 3 (Customer Onboarding)**.

---

### **1. KHÁCH HÀNG A (Hệ thống AS 222)**
Đây là mạng của khách hàng đầu tiên, kết nối qua hai điểm đầu cuối là PE1 và PE2.

| Router CE | Thuộc AS | Kết nối với PE | Subnet kết nối (Dự kiến) | Mục đích |
| :--- | :--- | :--- | :--- | :--- |
| **CE1** | 222 | **PE1** | 10.20.1.x/30 | Điểm cuối mạng khách hàng A phía PE1 |
| **CE3** | 222 | **PE2** | 10.20.1.y/30 | Điểm cuối mạng khách hàng A phía PE2 |

---

### **2. KHÁCH HÀNG B (Hệ thống AS 333)**
Đây là mạng của khách hàng thứ hai, cũng kết nối qua PE1 và PE2 nhưng chạy trên một định tuyến ảo (VRF) riêng biệt.

| Router CE | Thuộc AS | Kết nối với PE | Subnet kết nối (Dự kiến) | Mục đích |
| :--- | :--- | :--- | :--- | :--- |
| **CE2** | 333 | **PE1** | 10.30.1.x/30 | Điểm cuối mạng khách hàng B phía PE1 |
| **CE4** | 333 | **PE2** | 10.30.1.y/30 | Điểm cuối mạng khách hàng B phía PE2 |

---

### **3. CẤU TRÚC KẾT NỐI PE-CE (DỰA TRÊN TỆP JSON)**
Theo `topologie_client`, các kết nối vật lý/logic sẽ được thiết lập như sau:

*   **Tại PE1 (10.10.10.4):**
    *   Cổng nối với **CE1** (AS222): Sẽ gán vào `vrf Customer_A`.
    *   Cổng nối với **CE2** (AS333): Sẽ gán vào `vrf Customer_B`.
*   **Tại PE2 (10.10.10.5):**
    *   Cổng nối với **CE3** (AS222): Sẽ gán vào `vrf Customer_A`.
    *   Cổng nối với **CE4** (AS333): Sẽ gán vào `vrf Customer_B`.



---

### **4. DỮ LIỆU ĐỊNH TUYẾN DÀNH CHO CE (PHASE 3.B)**
Khi bạn thực hiện cấu hình **eBGP** cho các CE này, hãy lưu ý các thông số sau:

*   **Remote-AS từ phía CE:** Tất cả các CE sẽ trỏ về `neighbor [IP_của_PE] remote-as 111`.
*   **Remote-AS từ phía PE (trong VRF):**
    *   PE1/PE2 đối với CE1/CE3: `neighbor [IP_của_CE] remote-as 222`.
    *   PE1/PE2 đối với CE2/CE4: `neighbor [IP_của_CE] remote-as 333`.
*   **Dải IP quảng bá:** Bạn nên dùng các mạng con thuộc `adresse_reseau` tương ứng (10.20.1.0 cho AS222 và 10.30.1.0 cho AS333) để làm các mạng LAN giả lập sau CE.

### **5. GỢI Ý ĐẶT IP CHI TIẾT (Để đồng bộ với AS111)**

| Link | Interface PE | IP PE (Gateway) | IP CE | Subnet |
| :--- | :--- | :--- | :--- | :--- |
| **PE1-CE1** | Gi3/0 | 10.20.1.1 | 10.20.1.2 | /30 |
| **PE1-CE2** | Gi4/0* | 10.30.1.1 | 10.30.1.2 | /30 |
| **PE2-CE3** | Gi3/0 | 10.20.1.5 | 10.20.1.6 | /30 |
| **PE2-CE4** | Gi4/0* | 10.30.1.5 | 10.30.1.6 | /30 |
