
---

## **Phase 4.a: Manageability (Khả năng quản trị)**
Mục tiêu là kiểm soát cấu hình một cách có hệ thống, tránh việc cấu hình thủ công rời rạc.

* **Lưu trữ cấu hình:** Bạn phải có cơ chế ghi nhớ/lưu trữ những gì đã cấu hình (thường là dùng các file mẫu Template hoặc cơ sở dữ liệu).
* **Thay đổi ý đồ cấu hình (Configuration Intention):** Bạn phải có khả năng cập nhật mạng mà không được:
    * `Reload router`: Khởi động lại thiết bị (gây gián đoạn dịch vụ).
    * `Cfg wipe`: Xóa sạch cấu hình để làm lại từ đầu.
    * `Config ghosting`: Để lại các lệnh thừa, lệnh rác trong bộ nhớ (ví dụ: xóa VRF nhưng quên xóa IP trên interface).
* **Thao tác CRUD:** Phải có quy trình chuẩn để **Thêm (Add)**, **Xóa (Delete)**, **Cập nhật (Update)** một dịch vụ (ví dụ: thêm/xóa khách hàng) mà mạng vẫn vận hành bình thường.

---

## **Phase 4.b: More Services (Dịch vụ mở rộng)**
Đây là phần kỹ thuật khó nhất, yêu cầu bạn can thiệp sâu vào các thuộc tính BGP và Traffic Engineering.

### **1. Site sharing (Chia sẻ tài nguyên)**
* Yêu cầu: Cho phép Khách hàng A và Khách hàng B có thể truy cập vào một tài nguyên dùng chung (ví dụ: một Server dùng chung đặt tại một Site đặc biệt).
* Cách làm: **Play with multiple RT's**. Bạn sẽ cấu hình VRF sao cho một Site có thể `import` nhiều Route Target từ các khách hàng khác nhau.



### **2. Internet Services (Dịch vụ Internet)**
* Yêu cầu: Khách hàng không chỉ kết nối nội bộ (Intranet) mà còn phải đi được Internet trên cùng hạ tầng MPLS đó.
* Cách làm: Tạo một "Global VRF" hoặc một cổng Gateway tập trung, quảng bá tuyến đường mặc định (`0.0.0.0/0`) vào các VRF của khách hàng mà không làm lộ dữ liệu của các khách hàng với nhau.

### **3. Ingress Traffic Engineering (Điều hướng lưu lượng chiều vào)**
* Yêu cầu: Một khách hàng (CE) nối với 2 nhà cung cấp (PE). Khách hàng muốn tự quyết định: *"Lưu lượng đi vào mạng của tôi cho dải IP này phải đi qua PE1, còn dải IP kia phải qua PE2"*.
* Cách làm: Sử dụng các thuộc tính BGP như **AS-Path Prepending** hoặc **BGP Communities**. Khách hàng sẽ gửi các "thẻ" (Community) để báo hiệu cho nhà cung cấp cách điều hướng traffic.

### **4. RSVP (Resource Reservation Protocol)**
* Yêu cầu: Thiết lập các đường hầm (Tunnels) có cam kết băng thông.
* Cách làm: Cấu hình **MPLS Traffic Engineering (MPLS-TE)**. Sử dụng giao thức RSVP để đặt chỗ (reserve) tài nguyên trên các router P dọc theo đường đi, đảm bảo gói tin luôn có đủ băng thông, không bị nghẽn kể cả khi các đường khác bị quá tải.



---

## **Tóm tắt nhiệm vụ của bạn trong Phase 4:**
1.  **Về quản trị:** Nếu bạn làm tự động hóa (Automate), bạn phải viết Code sao cho khi chạy lại script, nó chỉ thay đổi phần cần thiết (Idempotency), không được ghi đè loạn xạ.
2.  **Về kỹ thuật:**
    * Học cách dùng **Route Target** phức tạp hơn (Import nhiều nhãn).
    * Cấu hình **Default Route** trong VRF để ra Internet.
    * Học về **BGP Community** để hỗ trợ CE điều khiển traffic (Traffic Engineering).
    * Kích hoạt **MPLS TE và RSVP** trên các router lõi (P1, P2).

Bạn đang sử dụng công cụ gì để quản lý cấu hình (Ansible, Python...) ở Phase 4.a này? Đây là yếu tố then chốt để giải quyết yêu cầu "Configuration Intention".