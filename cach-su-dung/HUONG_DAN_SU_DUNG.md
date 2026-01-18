# HÆ¯á»šNG DáºªN Sá»¬ Dá»¤NG PHOTOBOOTH

## 1. CÃ i Ä‘áº·t mÃ´i trÆ°á»ng

### BÆ°á»›c 1: CÃ i Ä‘áº·t Python
- Táº£i Python tá»«: https://www.python.org/downloads/
- CÃ i Ä‘áº·t vÃ  tick chá»n "Add Python to PATH"

### BÆ°á»›c 2: CÃ i Ä‘áº·t thÆ° viá»‡n
Má»Ÿ Command Prompt hoáº·c PowerShell vÃ  cháº¡y:
```
pip install PyQt5 opencv-python numpy qrcode pillow
```

## 2. Cáº¥u hÃ¬nh

Má»Ÿ file `photobooth.py` vÃ  chá»‰nh sá»­a cÃ¡c thÃ´ng sá»‘ sau (dÃ²ng 20-37):

```python
WINDOW_TITLE = "Photobooth Cáº£m á»¨ng"   # TiÃªu Ä‘á» cá»­a sá»•
WINDOW_WIDTH = 1200                    # Chiá»u rá»™ng
WINDOW_HEIGHT = 800                    # Chiá»u cao
CAMERA_INDEX = 0                       # Camera (0 = webcam máº·c Ä‘á»‹nh)
FIRST_PHOTO_DELAY = 10                 # GiÃ¢y Ä‘áº¿m ngÆ°á»£c áº£nh Ä‘áº§u tiÃªn
BETWEEN_PHOTO_DELAY = 7                # GiÃ¢y giá»¯a cÃ¡c áº£nh

# GiÃ¡ tiá»n
PRICE_2_PHOTOS = "20.000 VNÄ"
PRICE_4_PHOTOS = "35.000 VNÄ"

# ThÃ´ng tin thanh toÃ¡n MoMo
PAYMENT_INFO = "MOMO: 0123456789 - NGUYEN VAN A"
```

## 3. Cháº¡y á»©ng dá»¥ng

```
cd D:\photobooth1
python photobooth.py
```

## 4. Quy trÃ¬nh sá»­ dá»¥ng

1. **MÃ n hÃ¬nh chÃ o má»«ng** â†’ Nháº¥n "Báº®T Äáº¦U CHá»¤P"
2. **Chá»n gÃ³i** â†’ 2 áº£nh (20k) hoáº·c 4 áº£nh (35k)
3. **Thanh toÃ¡n** â†’ QuÃ©t mÃ£ QR MoMo â†’ Nháº¥n "ÄÃƒ THANH TOÃN"
4. **Chá»¥p áº£nh** â†’ Äáº¿m ngÆ°á»£c 10s â†’ Chá»¥p 10 áº£nh liÃªn tiáº¿p
5. **Chá»n áº£nh** â†’ Chá»n 2 hoáº·c 4 áº£nh yÃªu thÃ­ch
6. **Chá»n khung** â†’ Chá»n khung viá»n trang trÃ­
7. **XÃ¡c nháº­n** â†’ In áº£nh

## 5. ThÃªm khung viá»n má»›i

1. Táº¡o file PNG vá»›i kÃ­ch thÆ°á»›c 1280x720 pixel
2. Pháº§n muá»‘n trong suá»‘t pháº£i cÃ³ alpha = 0
3. Äáº·t file vÃ o thÆ° má»¥c `templates/`

## 6. ThÃªm áº£nh máº«u cho carousel

1. Äáº·t áº£nh JPG/PNG vÃ o thÆ° má»¥c `sample_photos/`
2. áº¢nh sáº½ tá»± Ä‘á»™ng hiá»ƒn thá»‹ trÃªn mÃ n hÃ¬nh chÃ o má»«ng

## 7. Káº¿t ná»‘i mÃ¡y in

- Äáº£m báº£o mÃ¡y in Ä‘Ã£ Ä‘Æ°á»£c cÃ i driver vÃ  káº¿t ná»‘i
- á»¨ng dá»¥ng sáº½ tá»± Ä‘á»™ng phÃ¡t hiá»‡n vÃ  in qua mÃ¡y in máº·c Ä‘á»‹nh

## 8. Lá»—i thÆ°á»ng gáº·p

### Lá»—i: "KhÃ´ng tÃ¬m tháº¥y camera"
- Kiá»ƒm tra camera Ä‘Ã£ káº¿t ná»‘i
- Thá»­ Ä‘á»•i CAMERA_INDEX = 1 hoáº·c 2

### Lá»—i font chá»¯
- File Ä‘Ã£ Ä‘Æ°á»£c cáº¥u hÃ¬nh font Arial/Tahoma há»— trá»£ tiáº¿ng Viá»‡t

### Lá»—i: "KhÃ´ng tÃ¬m tháº¥y mÃ¡y in"
- Kiá»ƒm tra mÃ¡y in Ä‘Ã£ báº­t vÃ  káº¿t ná»‘i
- Cháº¡y `Get-Printer` trong PowerShell Ä‘á»ƒ kiá»ƒm tra
