# ==========================================
# STYLESHEET TOÀN CỤC
# ==========================================
"""
Tập trung tất cả stylesheet toàn cục để dễ bảo trì.
Import từ đây thay vì định nghĩa inline trong app.py.
"""

GLOBAL_STYLESHEET = """
    QMainWindow { background-color: #F5EBEC; }
    QLabel { 
        color: white; 
        font-family: 'Cooper Black', 'Arial', 'Tahoma', 'Segoe UI', sans-serif;
        font-size: 18px;
    }
    QLabel#TitleLabel {
        font-size: 32px; font-weight: bold; color: #eaf0f6;
        font-family: 'Cooper Black', 'Arial', 'Tahoma', sans-serif;
    }
    QLabel#SubTitleLabel {
        font-size: 24px; font-weight: bold; color: #ffd700;
        font-family: 'Cooper Black', 'Arial', 'Tahoma', sans-serif;
    }
    QLabel#CountdownLabel {
        font-size: 120px; font-weight: bold; color: #ffd700;
        font-family: 'Cooper Black', 'Arial', sans-serif;
    }
    QLabel#InfoLabel {
        font-size: 24px; color: #a8dadc;
        font-family: 'Cooper Black', 'Arial', 'Tahoma', sans-serif;
    }
    QLabel#PriceLabel {
        font-size: 28px; font-weight: bold; color: #06d6a0;
        font-family: 'Cooper Black', 'Arial', 'Tahoma', sans-serif;
    }
    QPushButton {
        background-color: #e94560; color: white; border: none;
        border-radius: 15px; padding: 20px 40px; font-size: 22px;
        font-weight: bold; font-family: 'Cooper Black', 'Arial', 'Tahoma', sans-serif;
        min-height: 60px;
    }
    QPushButton:hover { background-color: #ff6b6b; }
    QPushButton:pressed { background-color: #c73e5a; }
    QPushButton:disabled { background-color: #4a4a6a; color: #8a8a9a; }
    QPushButton#GreenBtn { background-color: #06d6a0; }
    QPushButton#GreenBtn:hover { background-color: #00f5d4; }
    QPushButton#OrangeBtn { background-color: #fb8500; }
    QPushButton#OrangeBtn:hover { background-color: #ffb703; }
    QPushButton#BlueBtn { background-color: #4361ee; }
    QPushButton#BlueBtn:hover { background-color: #4cc9f0; }
    QScrollArea { border: none; background-color: transparent; }
    QWidget#PhotoCard {
        background-color: #16213e; border-radius: 10px;
        border: 2px solid #E9E1E3;
    }
    QWidget#PhotoCard:hover { border-color: #e94560; }
    QWidget#GalleryPanel { background-color: #0f0f23; }
    QWidget#StartPanel {
        background-color: #1a1a2e; border-left: 2px solid #4361ee;
    }
"""
