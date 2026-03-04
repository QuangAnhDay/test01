# ==========================================
# FLOW CONTROLLER - Điều khiển luồng ứng dụng
# ==========================================
"""
Quản lý state và điều khiển flow giữa các bước (steps) của photobooth.
"""


class FlowController:
    """
    Quản lý trạng thái và chuyển đổi giữa các bước.
    
    Các trạng thái (States):
        START          -> Màn hình chờ (Idle)
        PRICE_SELECT   -> Chọn gói/layout
        QR_PAYMENT     -> Thanh toán QR
        WAITING_CAPTURE-> Sẵn sàng chụp
        CAPTURING      -> Đang chụp
        PHOTO_SELECT   -> Chọn ảnh
        LAYOUT_SELECT  -> Chọn bố cục
        TEMPLATE_SELECT-> Chọn khung viền
        CONFIRM        -> Xác nhận
        PRINTING       -> Đang in
    
    Stacked Widget Indexes:
        0 - Idle/Welcome
        1 - Package/Price Select
        2 - QR Payment
        3 - LiveView/Capture
        4 - Layout Select (chỉ dùng trong chế độ có thanh toán)
        5 - Photo Select
        6 - Template Select
        7 - Confirm/Finish
    """

    # Screen index constants
    SCREEN_IDLE = 0
    SCREEN_PACKAGE = 1
    SCREEN_PAYMENT = 2
    SCREEN_LIVEVIEW = 3
    SCREEN_LAYOUT = 4
    SCREEN_PHOTO_SELECT = 5
    SCREEN_TEMPLATE = 6
    SCREEN_FINISH = 7
    SCREEN_CUSTOM_EDITOR = 8

    def __init__(self):
        self.state = "START"
        self.captured_photos = []
        self.selected_frame_count = 0
        self.selected_photo_indices = []
        self.collage_image = None
        self.merged_image = None
        self.current_frame = None
        self.countdown_val = 0
        self.selected_price_type = 0
        self.payment_confirmed = False
        self.layout_type = ""
        self.current_transaction_code = ""
        self.current_amount = 0

    def reset(self):
        """Reset toàn bộ về trạng thái ban đầu."""
        self.state = "START"
        self.captured_photos = []
        self.selected_photo_indices = []
        self.selected_frame_count = 0
        self.collage_image = None
        self.merged_image = None
        self.payment_confirmed = False
        self.selected_price_type = 0
        self.layout_type = ""
        self.current_transaction_code = ""
        self.current_amount = 0

    def can_go_to(self, target_state):
        """Kiểm tra có thể chuyển sang trạng thái mới không."""
        valid_transitions = {
            "START": ["PRICE_SELECT"],
            "PRICE_SELECT": ["START", "QR_PAYMENT", "CAPTURING", "WAITING_CAPTURE"],
            "QR_PAYMENT": ["PRICE_SELECT", "WAITING_CAPTURE"],
            "WAITING_CAPTURE": ["CAPTURING"],
            "CAPTURING": ["PHOTO_SELECT"],
            "PHOTO_SELECT": ["TEMPLATE_SELECT", "LAYOUT_SELECT"],
            "LAYOUT_SELECT": ["TEMPLATE_SELECT"],
            "TEMPLATE_SELECT": ["CONFIRM", "PRINTING"],
            "CONFIRM": ["PRINTING", "START"],
            "PRINTING": ["START"],
        }
        return target_state in valid_transitions.get(self.state, [])
