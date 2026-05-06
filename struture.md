## 📊 PHÂN TÍCH CẤU TRÚC MẠNG AS111

### **1. TỔNG QUAN CẤU TRÚC**
Mạng gồm **5 routers** trong một Autonomous System (AS 111) với kiến trúc MPLS/BGP:

| Router | Loại | Loopback IP | Router ID | Chức năng |
|--------|------|-------------|-----------|----------|
| **P1** | Provider | 10.10.10.1/32 | 111.0.0.1 | Cốt lõi, Hub trung tâm |
| **P2** | Provider | 10.10.10.3/32 | 111.0.0.3 | Cốt lõi, cân bằng tải |
| **PE1** | Provider Edge | 10.10.10.4/32 | 111.0.0.4 | Điểm kết nối khách hàng (phía 1) |
| **PE2** | Provider Edge | 10.10.10.5/32 | 111.0.0.5 | Điểm kết nối khách hàng (phía 2) |
| **RR** | Route Reflector | 10.10.10.2/32 | 111.0.0.2 | Phản xạ lộ trình BGP |

---

### **2. SƠ ĐỒ KẾT NỐI TOÀN BỘ**
```
                    ┌─────────────────────────────────┐
                    │       P1 (Hub trung tâm)        │
                    │   Loopback: 10.10.10.1/32       │
                    └──────┬────────┬────────┬─────────┘
                           │        │        │
            ┌──────────────┘        │        └──────────────┐
            │                       │                       │
    ┌───────▼──────────┐    ┌──────▼──────────┐    ┌────────▼──────────┐
    │  RR (Reflector)  │    │ PE1 (Edge phía1)│    │ P2 (Core 2)       │
    │ 10.10.10.2/32    │    │ 10.10.10.4/32   │    │ 10.10.10.3/32     │
    └─────┬────────────┘    └─────────────────┘    └────────┬──────────┘
          │                                                  │
          │                                          ┌───────▼──────────┐
          │                                          │ PE2 (Edge phía2) │
          │                                          │ 10.10.10.5/32    │
          │                                          └──────────────────┘
          └──────────────────────────────────────────┘
```

---

### **3. CHI TIẾT TỪNG KẾT NỐI (Links)**

#### **🔗 Link 1: P1 ↔ RR**
```
P1 → RR:
  - Interface P1:     FastEthernet0/0
  - Interface RR:     FastEthernet0/0
  - Subnet:           10.10.1.0/30
  - IP P1:            10.10.1.1/30
  - IP RR:            10.10.1.2/30
```

#### **🔗 Link 2: P1 ↔ P2**
```
P1 → P2:
  - Interface P1:     GigabitEthernet1/0
  - Interface P2:     FastEthernet0/0
  - Subnet:           10.10.1.4/30
  - IP P1:            10.10.1.5/30
  - IP P2:            10.10.1.6/30
```

#### **🔗 Link 3: P1 ↔ PE1**
```
P1 → PE1:
  - Interface P1:     GigabitEthernet2/0
  - Interface PE1:    FastEthernet0/0
  - Subnet:           10.10.1.8/30
  - IP P1:            10.10.1.9/30
  - IP PE1:           10.10.1.10/30
```

#### **🔗 Link 4: RR ↔ P2**
```
RR → P2:
  - Interface RR:     GigabitEthernet1/0
  - Interface P2:     GigabitEthernet1/0
  - Subnet:           10.10.1.12/30
  - IP RR:            10.10.1.13/30
  - IP P2:            10.10.1.14/30
```

#### **🔗 Link 5: P2 ↔ PE2**
```
P2 → PE2:
  - Interface P2:     GigabitEthernet2/0
  - Interface PE2:    FastEthernet0/0
  - Subnet:           10.10.1.16/30
  - IP P2:            10.10.1.17/30
  - IP PE2:           10.10.1.18/30
```

---

### **4. BẢNG TÓSTATICM TẤT CẢ INTERFACES**

| Router | Interface | Mục đích | IP Assigned | Connected To |
|--------|-----------|---------|------------|--------------|
| **P1** | FastEthernet0/0 | Link RR | 10.10.1.1/30 | RR |
| | GigabitEthernet1/0 | Link P2 | 10.10.1.5/30 | P2 |
| | GigabitEthernet2/0 | Link PE1 | 10.10.1.9/30 | PE1 |
| **P2** | FastEthernet0/0 | Link P1 | 10.10.1.6/30 | P1 |
| | GigabitEthernet1/0 | Link RR | 10.10.1.14/30 | RR |
| | GigabitEthernet2/0 | Link PE2 | 10.10.1.17/30 | PE2 |
| **RR** | FastEthernet0/0 | Link P1 | 10.10.1.2/30 | P1 |
| | GigabitEthernet1/0 | Link P2 | 10.10.1.13/30 | P2 |
| **PE1** | FastEthernet0/0 | Link P1 | 10.10.1.10/30 | P1 |
| **PE2** | FastEthernet0/0 | Link P2 | 10.10.1.18/30 | P2 |

---

### **5. PHÂN TÍCH CẤU TRÚC LÔGIC**

**Kiến trúc phân cấp:**
- **Tầng Lõi (Core)**: P1 + P2 + RR - Xử lý định tuyến
- **Tầng Biên (Edge)**: PE1 + PE2 - Kết nối khách hàng

**Đặc điểm:**
✅ **Redundancy**: 2 đường đi P1→P2 (trực tiếp + qua RR)  
✅ **High Availability**: Mỗi PE có đường kết nối riêng  
✅ **Route Reflection**: RR phản xạ lộ trình giữa P1 và P2  
✅ **Balanced Design**: Tải được chia đều qua 2 provider routers

Mạng này được thiết kế cho một mạng MPLS/BGP có khả năng phục hồi cao với khả năng mở rộng.

# 📋 TỔNG HỢP THÔNG TIN CHI TIẾT TỪNG ROUTER - AS111

---

## **1️⃣ ROUTER P1 (Provider Core - Hub Trung Tâm)**

### **Thông tin cơ bản**
| Thuộc tính | Giá trị |
|-----------|--------|
| Tên | P1 |
| Loại | Provider (Core) |
| Loopback IP | 10.10.10.1/32 |
| Router ID | 111.0.0.1 |
| Vai trò | Trung tâm Hub, kết nối với RR, P2, PE1 |

### **Danh sách các kết nối (Neighbors)**
| Neighbor | Interface | IP của P1 | Subnet | Loại Link |
|----------|-----------|-----------|--------|-----------|
| RR | FastEthernet0/0 | 10.10.1.1/30 | 10.10.1.0/30 | Core-Reflector |
| P2 | GigabitEthernet1/0 | 10.10.1.5/30 | 10.10.1.4/30 | Core-Core |
| PE1 | GigabitEthernet2/0 | 10.10.1.9/30 | 10.10.1.8/30 | Core-Edge |

### **Interface Details**
```
FastEthernet0/0
├─ IP: 10.10.1.1/30
├─ Network: 10.10.1.0/30
├─ Gateway: 10.10.1.0
├─ Broadcast: 10.10.1.3
├─ Usable IPs: .1 (P1) - .2 (RR)
└─ Connected to: RR

GigabitEthernet1/0
├─ IP: 10.10.1.5/30
├─ Network: 10.10.1.4/30
├─ Gateway: 10.10.1.4
├─ Broadcast: 10.10.1.7
├─ Usable IPs: .5 (P1) - .6 (P2)
└─ Connected to: P2

GigabitEthernet2/0
├─ IP: 10.10.1.9/30
├─ Network: 10.10.1.8/30
├─ Gateway: 10.10.1.8
├─ Broadcast: 10.10.1.11
├─ Usable IPs: .9 (P1) - .10 (PE1)
└─ Connected to: PE1
```

---

## **2️⃣ ROUTER P2 (Provider Core - Cân bằng Tải)**

### **Thông tin cơ bản**
| Thuộc tính | Giá trị |
|-----------|--------|
| Tên | P2 |
| Loại | Provider (Core) |
| Loopback IP | 10.10.10.3/32 |
| Router ID | 111.0.0.3 |
| Vai trò | Core thứ 2, kết nối P1, RR, PE2 |

### **Danh sách các kết nối (Neighbors)**
| Neighbor | Interface | IP của P2 | Subnet | Loại Link |
|----------|-----------|-----------|--------|-----------|
| P1 | FastEthernet0/0 | 10.10.1.6/30 | 10.10.1.4/30 | Core-Core |
| RR | GigabitEthernet1/0 | 10.10.1.14/30 | 10.10.1.12/30 | Core-Reflector |
| PE2 | GigabitEthernet2/0 | 10.10.1.17/30 | 10.10.1.16/30 | Core-Edge |

### **Interface Details**
```
FastEthernet0/0
├─ IP: 10.10.1.6/30
├─ Network: 10.10.1.4/30
├─ Gateway: 10.10.1.4
├─ Broadcast: 10.10.1.7
├─ Usable IPs: .5 (P1) - .6 (P2)
└─ Connected to: P1

GigabitEthernet1/0
├─ IP: 10.10.1.14/30
├─ Network: 10.10.1.12/30
├─ Gateway: 10.10.1.12
├─ Broadcast: 10.10.1.15
├─ Usable IPs: .13 (RR) - .14 (P2)
└─ Connected to: RR

GigabitEthernet2/0
├─ IP: 10.10.1.17/30
├─ Network: 10.10.1.16/30
├─ Gateway: 10.10.1.16
├─ Broadcast: 10.10.1.19
├─ Usable IPs: .17 (P2) - .18 (PE2)
└─ Connected to: PE2
```

---

## **3️⃣ ROUTER RR (Route Reflector)**

### **Thông tin cơ bản**
| Thuộc tính | Giá trị |
|-----------|--------|
| Tên | RR |
| Loại | Route Reflector |
| Loopback IP | 10.10.10.2/32 |
| Router ID | 111.0.0.2 |
| Vai trò | Phản xạ lộ trình BGP giữa P1 và P2 |

### **Danh sách các kết nối (Neighbors)**
| Neighbor | Interface | IP của RR | Subnet | Loại Link |
|----------|-----------|-----------|--------|-----------|
| P1 | FastEthernet0/0 | 10.10.1.2/30 | 10.10.1.0/30 | Reflector-Core |
| P2 | GigabitEthernet1/0 | 10.10.1.13/30 | 10.10.1.12/30 | Reflector-Core |

### **Interface Details**
```
FastEthernet0/0
├─ IP: 10.10.1.2/30
├─ Network: 10.10.1.0/30
├─ Gateway: 10.10.1.0
├─ Broadcast: 10.10.1.3
├─ Usable IPs: .1 (P1) - .2 (RR)
└─ Connected to: P1

GigabitEthernet1/0
├─ IP: 10.10.1.13/30
├─ Network: 10.10.1.12/30
├─ Gateway: 10.10.1.12
├─ Broadcast: 10.10.1.15
├─ Usable IPs: .13 (RR) - .14 (P2)
└─ Connected to: P2
```

---

## **4️⃣ ROUTER PE1 (Provider Edge - Điểm Kết nối Phía 1)**

### **Thông tin cơ bản**
| Thuộc tính | Giá trị |
|-----------|--------|
| Tên | PE1 |
| Loại | Provider Edge (Access) |
| Loopback IP | 10.10.10.4/32 |
| Router ID | 111.0.0.4 |
| Vai trò | Điểm kết nối khách hàng phía 1 |

### **Danh sách các kết nối (Neighbors)**
| Neighbor | Interface | IP của PE1 | Subnet | Loại Link |
|----------|-----------|-----------|--------|-----------|
| P1 | FastEthernet0/0 | 10.10.1.10/30 | 10.10.1.8/30 | Edge-Core |

### **Interface Details**
```
FastEthernet0/0
├─ IP: 10.10.1.10/30
├─ Network: 10.10.1.8/30
├─ Gateway: 10.10.1.8
├─ Broadcast: 10.10.1.11
├─ Usable IPs: .9 (P1) - .10 (PE1)
└─ Connected to: P1
```

---

## **5️⃣ ROUTER PE2 (Provider Edge - Điểm Kết nối Phía 2)**

### **Thông tin cơ bản**
| Thuộc tính | Giá trị |
|-----------|--------|
| Tên | PE2 |
| Loại | Provider Edge (Access) |
| Loopback IP | 10.10.10.5/32 |
| Router ID | 111.0.0.5 |
| Vai trò | Điểm kết nối khách hàng phía 2 |

### **Danh sách các kết nối (Neighbors)**
| Neighbor | Interface | IP của PE2 | Subnet | Loại Link |
|----------|-----------|-----------|--------|-----------|
| P2 | FastEthernet0/0 | 10.10.1.18/30 | 10.10.1.16/30 | Edge-Core |

### **Interface Details**
```
FastEthernet0/0
├─ IP: 10.10.1.18/30
├─ Network: 10.10.1.16/30
├─ Gateway: 10.10.1.16
├─ Broadcast: 10.10.1.19
├─ Usable IPs: .17 (P2) - .18 (PE2)
└─ Connected to: P2
```

---

## **🔗 BẢNG TÓNG HỢP TẤT CẢ LINKS**

| Link # | Router 1 | Interface 1 | IP Router 1 | ↔️ | Router 2 | Interface 2 | IP Router 2 | Subnet | Loại |
|--------|----------|-----------|-----------|-------|----------|-----------|-----------|--------|------|
| 1 | P1 | FastEthernet0/0 | 10.10.1.1/30 | ↔️ | RR | FastEthernet0/0 | 10.10.1.2/30 | 10.10.1.0/30 | P-RR |
| 2 | P1 | GigabitEthernet1/0 | 10.10.1.5/30 | ↔️ | P2 | FastEthernet0/0 | 10.10.1.6/30 | 10.10.1.4/30 | P-P |
| 3 | P1 | GigabitEthernet2/0 | 10.10.1.9/30 | ↔️ | PE1 | FastEthernet0/0 | 10.10.1.10/30 | 10.10.1.8/30 | P-PE |
| 4 | RR | GigabitEthernet1/0 | 10.10.1.13/30 | ↔️ | P2 | GigabitEthernet1/0 | 10.10.1.14/30 | 10.10.1.12/30 | RR-P |
| 5 | P2 | GigabitEthernet2/0 | 10.10.1.17/30 | ↔️ | PE2 | FastEthernet0/0 | 10.10.1.18/30 | 10.10.1.16/30 | P-PE |

---

## **📊 TÓNG HỢP THỐNG KÊ**

| Chỉ số | Giá trị |
|-------|--------|
| **Tổng Router** | 5 |
| **Tổng Links** | 5 |
| **Tổng Subnets** | 5 (range 10.10.1.0 - 10.10.1.16) |
| **Loopback Range** | 10.10.10.1 - 10.10.10.5 |
| **Router ID Range** | 111.0.0.1 - 111.0.0.5 |
| **Core Routers (P)** | 2 (P1, P2) |
| **Edge Routers (PE)** | 2 (PE1, PE2) |
| **Route Reflectors** | 1 (RR) |

---

Cấu trúc này cho phép:
✅ Định tuyến kép (Redundancy) giữa 2 core routers  
✅ Phản xạ lộ trình BGP qua RR  
✅ Kết nối tách biệt cho từng PE  
✅ High Availability cho toàn bộ mạng