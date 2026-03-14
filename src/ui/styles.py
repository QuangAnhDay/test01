# ==========================================
# STYLESHEET TOÀN CỤC
# ==========================================
"""
Tập trung tất cả stylesheet toàn cục để dễ bảo trì.
Import từ đây thay vì định nghĩa inline trong app.py.
"""

GLOBAL_STYLESHEET = """
    /* Mau nen chinh cua toan bo ung dung */
    QMainWindow { background-color: #F5EBEC; }
    
    /* Phong chu chung cho cac nhan van ban */
    QLabel { 
        color: #D33E42; 
        font-family: 'Cooper Black', 'Arial', 'Tahoma', 'Segoe UI', sans-serif;
        font-size: 18px;
    }
    
    /* Mau tieu de chinh (VD: Ten ứng dụng) */
    QLabel#TitleLabel {
        font-size: 32px; font-weight: bold; color: #D33E42;
        font-family: 'Cooper Black', 'Arial', 'Tahoma', sans-serif;
    }
    
    /* Mau tieu de phu */
    QLabel#SubTitleLabel {
        font-size: 24px; font-weight: bold; color: #D33E42;
        font-family: 'Cooper Black', 'Arial', 'Tahoma', sans-serif;
    }
    
    /* Mau so dem nguoc (Mau trang) */
    QLabel#CountdownLabel {
        font-size: 120px; font-weight: bold; color: white;
        font-family: 'Cooper Black', 'Arial', sans-serif;
    }
    
    /* Mau chu thong tin huong dan (Mau xanh nhat) */
    QLabel#InfoLabel {
        font-size: 24px; color: #D33E42;
        font-family: 'Cooper Black', 'Arial', 'Tahoma', sans-serif;
    }
    
    /* Mau hien thi gia tien (Mau xanh la cay) */
    QLabel#PriceLabel {
        font-size: 28px; font-weight: bold; color: #D33E42;
        font-family: 'Cooper Black', 'Arial', 'Tahoma', sans-serif;
    }
    
    /* Nut nhan mac dinh (Mau do hong) */
    QPushButton {
        background-color: #e94560; color: #D33E42; border: none;
        border-radius: 15px; padding: 20px 40px; font-size: 22px;
        font-weight: bold; font-family: 'Cooper Black', 'Arial', 'Tahoma', sans-serif;
        min-height: 60px;
    }
    QPushButton:hover { background-color: #ff6b6b; }
    QPushButton:pressed { background-color: #c73e5a; }
    QPushButton:disabled { background-color: #4a4a6a; color: #D33E42; }
    
    /* Nut nhan mau xanh la (Xac nhan, Bat dau) */
    QPushButton#GreenBtn { background-color: #06d6a0; }
    QPushButton#GreenBtn:hover { background-color: #00f5d4; }
    
    /* Nut nhan mau cam */
    QPushButton#OrangeBtn { background-color: #fb8500; }
    QPushButton#OrangeBtn:hover { background-color: #ffb703; }
    
    /* Nut nhan mau xanh duong (Thong tin, Admin) */
    QPushButton#BlueBtn { background-color: #4361ee; }
    QPushButton#BlueBtn:hover { background-color: #4cc9f0; }
    
    QScrollArea { border: none; background-color: transparent; }
    
    /* Khung hien thi ảnh nhỏ */
    QWidget#PhotoCard {
        background-color: #16213e; border-radius: 10px;
        border: 2px solid #E9E1E3;
    }
    QWidget#PhotoCard:hover { border-color: #e94560; }
    
    /* Panel hien thi carousel ảnh mau */
    QWidget#GalleryPanel { background-color: #0f0f23; }
    
    /* Khung ben phai man hinh cho */
    QWidget#StartPanel {
        background-color: #1a1a2e; border-left: 2px solid #4361ee;
    }
"""
