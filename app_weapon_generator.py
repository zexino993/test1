import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_procedural_slash_effect(width=200, height=200, color="#00FFFF", intensity=1.5, arc_angle=120):
    # 1. Buat kanvas transparan
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    center_x, center_y = width // 2, height // 2
    radius = int(min(width, height) * 0.4)
    bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
    
    # Extract RGB
    c_hex = color.lstrip('#')
    r, g, b = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
    
    # 2. Gambar beberapa layer busur bergradasi (Outer Glow)
    start_deg = -arc_angle / 2
    end_deg = arc_angle / 2
    
    for i in range(4):
        thick = int((8 + i * 4) * intensity)
        alpha = int((120 - i * 25) * min(1.0, intensity))
        draw.arc(bbox, start=start_deg, end=end_deg, fill=(r, g, b, alpha), width=max(1, thick))
        
    # 3. Core hotspot line (Inti tebasan putih terang)
    draw.arc(bbox, start=start_deg, end=end_deg, fill=(255, 255, 255, 230), width=max(2, int(3 * intensity)))
    
    # 4. Beri efek Blur agar terlihat seperti energi bercahaya
    glow_layer = canvas.filter(ImageFilter.GaussianBlur(radius=4))
    final_slash = Image.alpha_composite(glow_layer, canvas)
    
    return final_slash

# Jalankan & Simpan Gambar
slash_img = create_procedural_slash_effect(width=256, height=256, color="#00FFCC", intensity=1.2)
slash_img.save("slash_effect.png")
print("✅ Efek tebasan sintetis berhasil dibuat!")
