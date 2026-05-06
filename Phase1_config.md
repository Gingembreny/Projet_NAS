Dựa trên phân tích cấu trúc mạng AS111 từ sơ đồ và file JSON của bạn, dưới đây là hướng dẫn chi tiết các bước cấu hình **Addressing (Địa chỉ IP)** và **OSPF Routing** cho tất cả các thiết bị.

---

## **PHẦN 1: CẤU HÌNH ADDRESSING (ĐẶT ĐỊA CHỈ IP)**

Ở bước này, chúng ta sẽ cấu hình địa chỉ IP cho các cổng vật lý và cổng ảo (Loopback) dựa trên bảng phân bổ.

### **1. Cấu hình trên Router P1**
```bash
P1(config)# interface Loopback0
P1(config-if)# ip address 10.10.10.1 255.255.255.255
P1(config-if)# exit

P1(config)# interface FastEthernet0/0
P1(config-if)# ip address 10.10.1.1 255.255.255.252
P1(config-if)# no shutdown

P1(config)# interface GigabitEthernet1/0
P1(config-if)# ip address 10.10.1.5 255.255.255.252
P1(config-if)# no shutdown

P1(config)# interface GigabitEthernet2/0
P1(config-if)# ip address 10.10.1.9 255.255.255.252
P1(config-if)# no shutdown
```

### **2. Cấu hình trên Router P2**
```bash
P2(config)# interface Loopback0
P2(config-if)# ip address 10.10.10.3 255.255.255.255
P2(config-if)# exit

P2(config)# interface FastEthernet0/0
P2(config-if)# ip address 10.10.1.6 255.255.255.252
P2(config-if)# no shutdown

P2(config)# interface GigabitEthernet1/0
P2(config-if)# ip address 10.10.1.14 255.255.255.252
P2(config-if)# no shutdown

P2(config)# interface GigabitEthernet2/0
P2(config-if)# ip address 10.10.1.17 255.255.255.252
P2(config-if)# no shutdown
```

### **3. Cấu hình trên Router RR**
```bash
RR(config)# interface Loopback0
RR(config-if)# ip address 10.10.10.2 255.255.255.255
RR(config-if)# exit

RR(config)# interface FastEthernet0/0
RR(config-if)# ip address 10.10.1.2 255.255.255.252
RR(config-if)# no shutdown

RR(config)# interface GigabitEthernet1/0
RR(config-if)# ip address 10.10.1.13 255.255.255.252
RR(config-if)# no shutdown
```

### **4. Cấu hình trên Router PE1 & PE2**
*   **PE1:**
    ```bash
    PE1(config)# interface Loopback0
    PE1(config-if)# ip address 10.10.10.4 255.255.255.255
    PE1(config)# interface FastEthernet0/0
    PE1(config-if)# ip address 10.10.1.10 255.255.255.252
    PE1(config-if)# no shutdown
    ```
*   **PE2:**
    ```bash
    PE2(config)# interface Loopback0
    PE2(config-if)# ip address 10.10.10.5 255.255.255.255
    PE2(config)# interface FastEthernet0/0
    PE2(config-if)# ip address 10.10.1.18 255.255.255.252
    PE2(config-if)# no shutdown
    ```

---

## **PHẦN 2: CẤU HÌNH OSPF ROUTING**

Để toàn bộ mạng có thể nhìn thấy nhau (đặc biệt là các địa chỉ Loopback để thiết lập BGP sau này), chúng ta sẽ chạy OSPF trên tất cả các Router trong cùng **Area 0**.

### **Nguyên tắc cấu hình chung:**
- Sử dụng `Router ID` tương ứng.
- Quảng bá tất cả các mạng trực tiếp và Loopback vào OSPF.



### **1. Cấu hình cho P1 (Core Hub)**
```bash
P1(config)# router ospf 1
P1(config-router)# router-id 111.0.0.1
P1(config-router)# network 10.10.10.1 0.0.0.0 area 0
P1(config-router)# network 10.10.1.0 0.0.0.3 area 0
P1(config-router)# network 10.10.1.4 0.0.0.3 area 0
P1(config-router)# network 10.10.1.8 0.0.0.3 area 0
```

### **2. Cấu hình cho RR (Route Reflector)**
```bash
RR(config)# router ospf 1
RR(config-router)# router-id 111.0.0.2
RR(config-router)# network 10.10.10.2 0.0.0.0 area 0
RR(config-router)# network 10.10.1.0 0.0.0.3 area 0
RR(config-router)# network 10.10.1.12 0.0.0.3 area 0
```

### **3. Cấu hình cho P2 (Core 2)**
```bash
P2(config)# router ospf 1
P2(config-router)# router-id 111.0.0.3
P2(config-router)# network 10.10.10.3 0.0.0.0 area 0
P2(config-router)# network 10.10.1.4 0.0.0.3 area 0
P2(config-router)# network 10.10.1.12 0.0.0.3 area 0
P2(config-router)# network 10.10.1.16 0.0.0.3 area 0
```

### **4. Cấu hình cho PE1 & PE2 (Edge)**
*   **PE1:**
    ```bash
    PE1(config)# router ospf 1
    PE1(config-router)# router-id 111.0.0.4
    PE1(config-router)# network 10.10.10.4 0.0.0.0 area 0
    PE1(config-router)# network 10.10.1.8 0.0.0.3 area 0
    ```
*   **PE2:**
    ```bash
    PE2(config)# router ospf 1
    PE2(config-router)# router-id 111.0.0.5
    PE2(config-router)# network 10.10.10.5 0.0.0.0 area 0
    PE2(config-router)# network 10.10.1.16 0.0.0.3 area 0
    ```

---

## **PHẦN 3: KIỂM TRA (VERIFICATION)**

Sau khi cấu hình xong, bạn cần thực hiện các lệnh sau để đảm bảo mạng hoạt động thông suốt:

1.  **Kiểm tra láng giềng OSPF:**
    `show ip ospf neighbor`
    *(Tất cả phải ở trạng thái FULL)*
2.  **Kiểm tra bảng định tuyến:**
    `show ip route ospf`
    *(Bạn phải thấy các mạng Loopback của các router khác)*
3.  **Kiểm tra kết nối:**
    Từ PE1: `ping 10.10.10.5 source Loopback0` (Ping đến Loopback PE2)
    *(Kết quả phải thành công 100%)*

Để cấu hình **Phase 1.a: LDP (Label Distribution Protocol)** cho mạng AS111 của bạn, mục tiêu là thiết lập việc phân phối nhãn MPLS giữa các Router cốt lõi để tạo ra các đường truyền nhãn (LSPs).

Dưới đây là các bước cấu hình và xác thực chi tiết:

---

### **1. CẤU HÌNH BẬT MPLS LDP**

Bạn cần bật MPLS LDP trên tất cả các interface **nối giữa các Router trong AS111** (P1, P2, RR, PE1, PE2). Không bật trên interface hướng ra khách hàng (nếu có).

#### **Bước chung cho tất cả các Router:**
Sử dụng giao thức LDP và chỉ định Loopback0 làm LDP Router-ID để đảm bảo tính ổn định.

*   **Trên Router P1:**
    ```bash
    P1(config)# mpls ip
    P1(config)# mpls label protocol ldp
    P1(config)# mpls ldp router-id Loopback0 force
    P1(config)# interface FastEthernet0/0
    P1(config-if)# mpls ip
    P1(config)# interface GigabitEthernet1/0
    P1(config-if)# mpls ip
    P1(config)# interface GigabitEthernet2/0
    P1(config-if)# mpls ip
    ```

*   **Trên Router RR:**
    ```bash
    RR(config)# mpls ip
    RR(config)# mpls label protocol ldp
    RR(config)# mpls ldp router-id Loopback0 force
    RR(config)# interface FastEthernet0/0
    RR(config-if)# mpls ip
    RR(config)# interface GigabitEthernet1/0
    RR(config-if)# mpls ip
    ```

*   **Trên Router P2:**
    ```bash
    P2(config)# mpls ip
    P2(config)# mpls label protocol ldp
    P2(config)# mpls ldp router-id Loopback0 force
    P2(config)# interface FastEthernet0/0
    P2(config-if)# mpls ip
    P2(config)# interface GigabitEthernet1/0
    P2(config-if)# mpls ip
    P2(config)# interface GigabitEthernet2/0
    P2(config-if)# mpls ip
    
```

*   **Trên Router PE1 & PE2:**
    ```bash
    PE1(config)# mpls ip
    PE1(config)# interface FastEthernet0/0
    PE1(config-if)# mpls ip

    PE2(config)# mpls ip
    PE2(config)# interface FastEthernet0/0
    PE2(config-if)# mpls ip
    ```

---

### **2. XÁC THỰC (VALIDATE)**

Bạn cần thực hiện 3 bước kiểm tra theo yêu cầu của Phase 1.a:

#### **A. Kiểm tra trạng thái phiên LDP (LDP Session States)**
Lệnh này giúp bạn biết các Router đã thiết lập "quan hệ láng giềng" LDP thành công chưa.
```bash
P1# show mpls ldp neighbor
```
*   **Kết quả mong đợi:** Cột `State` phải hiển thị là **OPERATIONAL**. Điều này có nghĩa là TCP session (port 646) đã được thiết lập thành công giữa các Loopback IP.

#### **B. Kiểm tra vận chuyển MPLS (MPLS Transport in the core)**
Lệnh này kiểm tra bảng chuyển tiếp nhãn (LFIB) để xem các nhãn đã được gán cho các prefix OSPF chưa.
```bash
P1# show mpls forwarding-table
```
*   **Giải thích:** Bạn sẽ thấy danh sách các `Local Tag` và `Outgoing Tag`. Nếu bạn thấy nhãn (số nguyên) cho các địa chỉ Loopback của các router khác, nghĩa là MPLS đang vận chuyển dữ liệu tốt.

#### **C. Kiểm tra cơ chế Penultimate Hop Popping (PHP)**
PHP là cơ chế Router kề cuối sẽ gỡ bỏ nhãn MPLS trước khi gửi đến Router đích cuối cùng để giảm tải cho Router đích.
```bash
PE1# show mpls forwarding-table
```
*   **Cách kiểm tra:** Nhìn vào cột **Outgoing Label** hoặc **Action** cho prefix của Router đích ngay kế bên nó.
*   **Dấu hiệu nhận biết:** Nếu bạn thấy chữ **Pop Label** hoặc **Untagged** khi đích đến là mạng trực tiếp của router láng giềng, thì đó chính là cơ chế **PHP** đang hoạt động.

**Ví dụ:** Tại P1, khi kiểm tra đường đi tới `10.10.10.2/32` (Loopback của RR), nếu P1 thấy `Pop Label` cho chặng tới RR, nghĩa là P1 (hop kề cuối) đang thực hiện PHP cho RR.

---

### **Mẹo nhỏ:**
Nếu bạn thực hiện lệnh `ping` giữa các Loopback, hãy thử dùng lệnh `traceroute`:
```bash
PE1# traceroute 10.10.10.5 source Loopback0
```
Nếu kết quả hiển thị các giá trị nhãn (ví dụ: `MPLS label 16`), điều đó chứng tỏ gói tin đang được truyền tải bằng nhãn MPLS thay vì IP routing thuần túy.
```
Bảng `show mpls forwarding-table` (LFIB - Label Forwarding Information Base) là "trái tim" của việc chuyển mạch nhãn. Nó cho Router biết: "Nếu gói tin đến với nhãn X, tôi phải làm gì tiếp theo?".

Dưới đây là cách đọc chi tiết từng cột dựa trên kết quả của bạn tại **P1**:

---

### **1. Ý nghĩa các cột chính**
*   **Local Label**: Nhãn mà **P1 tự sinh ra** và quảng bá cho các router hàng xóm (neighbor). Khi hàng xóm gửi gói tin đến P1 với nhãn này, P1 sẽ biết nó cần xử lý cho Prefix tương ứng.
*   **Outgoing Label**: Hành động tiếp theo của P1. 
    *   **Pop Label**: Gỡ bỏ nhãn.
    *   **Số cụ thể (ví dụ: 21)**: Thay thế nhãn cũ bằng nhãn mới này (Swap).
*   **Prefix or Tunnel Id**: Đích đến của gói tin (thường là các Loopback IP hoặc các mạng kết nối giữa các router).
*   **Bytes Label Switched**: Lượng dữ liệu thực tế đã được chuyển mạch qua nhãn này.
*   **Outgoing interface & Next Hop**: Cổng vật lý và địa chỉ IP của router kế tiếp để đẩy gói tin đi.

---

### **2. Phân tích các dòng cụ thể (Case Study)**

#### **Trường hợp 1: Cơ chế PHP (Penultimate Hop Popping)**
> `16 | Pop Label | 10.10.10.2/32 | Fa0/0 | 10.10.1.2`

*   **Giải thích**: Khi P1 nhận được gói tin có nhãn **16**, nó biết đích đến là `10.10.10.2` (Router RR). 
*   **Hành động**: Vì Outgoing Label là **Pop Label**, P1 sẽ **gỡ nhãn** và đẩy gói tin IP thuần túy đến RR qua cổng `Fa0/0`.
*   **Tại sao?**: Vì P1 là "hop kề cuối" (Penultimate Hop) của RR. Nó gỡ nhãn trước để RR không phải xử lý nhãn nữa, giúp RR chạy nhanh hơn.

#### **Trường hợp 2: Cân bằng tải (Load Balancing)**
> `17 | Pop Label | 10.10.1.12/30 | Fa0/0 & Gi1/0`

*   **Giải thích**: Để đi đến mạng `10.10.1.12/30` (link giữa RR và P2), P1 có 2 đường đi qua RR (`Fa0/0`) hoặc qua P2 (`Gi1/0`). OSPF đã tính toán chi phí bằng nhau nên MPLS cũng hỗ trợ cân bằng tải tại đây.

#### **Trường hợp 3: Chuyển đổi nhãn (Label Swap)**
> `21 | 21 | 10.10.10.5/32 | Gi1/0 | 10.10.1.6`

*   **Giải thích**: Đây là dòng thú vị nhất. Đích đến là `10.10.10.5` (Router PE2).
*   **Hành động**: Khi gói tin đến P1 với nhãn **21** (Local), P1 nhìn vào bảng và thấy Router P2 (`10.10.1.6`) yêu cầu dùng nhãn **21** (Outgoing) để tới PE2.
*   **Kết quả**: P1 thực hiện hành động **Swap** (thực tế là giữ nguyên giá trị 21 nhưng về bản chất là thay nhãn của mình bằng nhãn của neighbor) và đẩy đi qua cổng `Gi1/0`.

---

### **3. Tổng kết trạng thái mạng của bạn**
*   **P1 đã học đủ nhãn**: Nó có nhãn cho tất cả các Loopback từ .1 đến .5.
*   **Lưu lượng đang chạy**: Cột `Bytes Switched` ở dòng nhãn 19, 20, 21 có số (570, 1302, 360). Điều này chứng tỏ bạn đã thực hiện `ping` hoặc `traceroute` giữa các Router PE, và dữ liệu **thực sự đang đi bằng nhãn MPLS**.
*   **Cấu trúc liên kết**: P1 đóng vai trò là "ngã tư". Nó kết nối trực tiếp với RR (qua Fa0/0), P2 (qua Gi1/0) và PE1 (qua Gi2/0).

Bạn có muốn tôi hướng dẫn cách kiểm tra xem một gói tin cụ thể (ví dụ từ PE1 sang PE2) sẽ bị thay đổi nhãn như thế nào qua từng trạm không?