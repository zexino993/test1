import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io
import math

st.set_page_config(
    page_title="Terraria Weapon 45° & Swing Arc Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🗡️ Terraria Weapon 45° Pivot & Swing Sheet Studio")
st.caption("Alat bantu Modder Terraria untuk rotasi $45^\circ$, penyesuaian Grip Pivot, dan pembuat Animasi Tebasan (Swing Arc) otomatis!")

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================
def rotate_nearest_neighbor(image, angle):
    """Rotasi gambar dengan metode Nearest Neighbor agar ketajaman Pixel Art terjaga."""
    # Gunakan resampling NEAREST agar piksel tidak blur
    return image.rotate(angle, resample=Image.NEAREST, expand=True)

def generate_swing_arc_frame(weapon_img, angle, pivot_x, pivot_y, canvas_size, glow_color, arc_intensity):
    """Merender satu frame ayunan senjata beserta efek pendaran sabetan (Swing Arc)."""
    frame = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    
    # 1. Rotasi Senjata
    rotated_weapon = rotate_nearest_neighbor(weapon_img, angle)
    
    # Hitung posisi paste berdasarkan Pivot Point
    # Pusat rotasi senjata asli
    orig_center_x, orig_center_y = weapon_img.width / 2.0, weapon_img.height / 2.0
    
    # Pergeseran akibat expand rotasi
    rot_w, rot_h = rotated_weapon.size
    
    # Transformasi koordinat pivot
    rad = math.radians(-angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    cx, cy = orig_center_x, orig_center_y
    px, py = pivot_x, pivot_y
    
    # Rotasi titik pivot relatif terhadap pusat gambar
    rx = (px - cx) * cos_a - (py - cy) * sin_a + (rot_w / 2.0)
    ry = (px - cx) * sin_a + (py - cy) * cos_a + (rot_h / 2.0)
    
    # Tempel senjata pada kanvas sehingga pivot berada di tengah kanvas (center_x, center_y)
    canvas_center = canvas_size // 2
    paste_x = int(canvas_center - rx)
    paste_y = int(canvas_center - ry)
    
    # 2. Gambar Efek Tebasan Arc (Energy Trail)
    if arc_intensity > 0:
        arc_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(arc_layer)
        
        # Ekstrak Warna RGB Arc
        c_hex = glow_color.lstrip('#')
        r_c = int(c_hex[0:2], 16)
        g_c = int(c_hex[2:4], 16)
        b_c = int(c_hex[4:6], 16)
        
        radius = int(max(weapon_img.width, weapon_img.height) * 0.85)
        bbox = [
            canvas_center - radius, canvas_center - radius,
            canvas_center + radius, canvas_center + radius
        ]
        
        # Gambar garis busur tebasan
        start_angle = -angle - 60
        end_angle = -angle + 10
        width_arc = int(8 * arc_intensity)
        
        draw.arc(bbox, start=start_angle, end=end_angle, fill=(r_c, g_c, b_c, int(200 * arc_intensity)), width=width_arc)
        
        # Tambahkan blur halus untuk efek pendaran sihir
        arc_glow = arc_layer.filter(ImageFilter.GaussianBlur(radius=2))
        frame = Image.alpha_composite(frame, arc_glow)
        frame = Image.alpha_composite(frame, arc_layer)

    # 3. Tempel Senjata
    frame.paste(rotated_weapon, (paste_x, paste_y), rotated_weapon)
    return frame

# ==========================================
# 2. SIDEBAR KONTROL & INPUT
# ==========================================
st.sidebar.header("📁 1. Input Gambar Senjata")
uploaded_file = st.sidebar.file_uploader("Upload PNG Senjata (Tegak Lurus/Biasa):", type=["png"])

if uploaded_file is not None:
    src_image = Image.open(uploaded_file).convert("RGBA")
    
    st.sidebar.markdown("---")
    st.sidebar.header("📐 2. Rotasi & Point Pivot Handle")
    auto_rot = st.sidebar.checkbox("Auto-Rotate ke 45° (Terraria Standard)", value=True)
    custom_rot_angle = st.sidebar.slider("Sudut Rotasi Manual (°):", -180, 180, 45 if auto_rot else 0)
    
    # Pengaturan Pivot Point (Grip Point / Pegangan Senjata)
    st.sidebar.markdown("**Grip Pivot Position (Gagang Pedang):**")
    pivot_x_pct = st.sidebar.slider("Grip Posisi X (% Lebar):", 0, 100, 20, help="20% biasanya terletak di gagang pedang dekat bagian bawah.")
    pivot_y_pct = st.sidebar.slider("Grip Posisi Y (% Tinggi):", 0, 100, 80, help="80% berada di bagian bawah gagang pedang.")

    pivot_x_px = int((pivot_x_pct / 100.0) * src_image.width)
    pivot_y_px = int((pivot_y_pct / 100.0) * src_image.height)

    st.sidebar.markdown("---")
    st.sidebar.header("💫 3. FX Slash Arc (Efek Tebasan)")
    enable_arc = st.sidebar.checkbox("Aktifkan Efek Tebasan Energi (Slash Arc)", value=True)
    arc_color = st.sidebar.color_picker("Warna Pendaran Tebasan:", "#00FFFF")
    arc_power = st.sidebar.slider("Intensitas Cahaya Arc:", 0.0, 2.0, 1.0, 0.1)

    st.sidebar.markdown("---")
    st.sidebar.header("🖼️ 4. Pengaturan Frame Sheet")
    sheet_frames_count = st.sidebar.slider("Jumlah Frame Animasi Tebasan:", 3, 6, 4)
    frame_canvas_size = st.sidebar.select_slider("Ukuran Canvas per Frame (Px):", options=[64, 80, 96, 128], value=80)
    sheet_columns = st.sidebar.slider("Jumlah Kolom Grid Sheet:", 1, 6, 4)

    # ==========================================
    # 3. PROSES & MAIN DASHBOARD
    # ==========================================
    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        st.subheader("🎯 1. Pivot Point Inspection & Hitbox")
        
        # Visualisasi Titik Pivot pada Gambar Asli
        pivot_inspect_img = src_image.copy()
        draw_insp = ImageDraw.Draw(pivot_inspect_img)
        
        # Gambar Crosshair Merah di titik Handle/Pivot
        cs = 4 # ukuran crosshair
        draw_insp.line([(pivot_x_px - cs, pivot_y_px), (pivot_x_px + cs, pivot_y_px)], fill=(255, 0, 0, 255), width=2)
        draw_insp.line([(pivot_x_px, pivot_y_px - cs), (pivot_x_px, pivot_y_px + cs)], fill=(255, 0, 0, 255), width=2)
        draw_insp.ellipse([pivot_x_px - 2, pivot_y_px - 2, pivot_x_px + 2, pivot_y_px + 2], outline=(255, 255, 0, 255))

        st.image(pivot_inspect_img, caption=f"Original Sprite ({src_image.width}x{src_image.height} px) - Silang Merah: Titik Pegangan", use_container_width=True)

        # Hitbox Data untuk Modder TModLoader
        st.info(f"""
        **📋 Data Hitbox & Pivot untuk Kodingan Mod Terraria (C#):**
        * **Item.width:** `{src_image.width}` px
        * **Item.height:** `{src_image.height}` px
        * **Pivot Offset:** X: `{pivot_x_px}` px, Y: `{pivot_y_px}` px
        """)

    with col_p2:
        st.subheader("⚔️ 2. Hasil Rotasi 45° Standar Terraria")
        
        # Rotasi Single Sprite 45 Derajat
        rotated_45_single = rotate_nearest_neighbor(src_image, custom_rot_angle)
        
        st.image(rotated_45_single, caption=f"Terraria Ready Sprite 45° ({rotated_45_single.width}x{rotated_45_single.height} px)", use_container_width=True)

        # Tombol Download Single 45 Degree PNG
        buf_single = io.BytesIO()
        rotated_45_single.save(buf_single, format="PNG")
        st.download_button(
            label="💾 Download PNG Single Weapon (45°)",
            data=buf_single.getvalue(),
            file_name="Terraria_Weapon_45deg.png",
            mime="image/png",
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("🎬 3. Generator Animated Swing Arc Sprite Sheet")

    # Generate Frame-by-Frame Ayunan Senjata
    angles_sequence = np.linspace(60, -60, sheet_frames_count)
    rendered_frames = []

    for ang in angles_sequence:
        f = generate_swing_arc_frame(
            weapon_img=src_image,
            angle=ang + (45 if auto_rot else 0),
            pivot_x=pivot_x_px,
            pivot_y=pivot_y_px,
            canvas_size=frame_canvas_size,
            glow_color=arc_color,
            arc_intensity=arc_power if enable_arc else 0.0
        )
        rendered_frames.append(f)

    # Tampilkan Preview Frame Individual
    cols_ui = st.columns(len(rendered_frames))
    for i, frm in enumerate(rendered_frames):
        with cols_ui[i]:
            st.image(frm, caption=f"Frame {i+1}")

    # Buat Sprite Sheet PNG
    rows_count = math.ceil(len(rendered_frames) / sheet_columns)
    sheet_w = frame_canvas_size * sheet_columns
    sheet_h = frame_canvas_size * rows_count
    
    sprite_sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    for idx, frame in enumerate(rendered_frames):
        r = idx // sheet_columns
        c = idx % sheet_columns
        sprite_sheet.paste(frame, (c * frame_canvas_size, r * frame_canvas_size))

    st.markdown("#### 🖼️ Hasil Sprite Sheet Grid PNG:")
    st.image(sprite_sheet, caption=f"Sprite Sheet Grid ({sheet_w}x{sheet_h} px)", use_container_width=False)

    # Download Button untuk Sprite Sheet
    buf_sheet = io.BytesIO()
    sprite_sheet.save(buf_sheet, format="PNG")
    st.download_button(
        label="💾 Download Complete Swing Sprite Sheet PNG",
        data=buf_sheet.getvalue(),
        file_name="Terraria_Weapon_Swing_Sheet.png",
        mime="image/png",
        use_container_width=True
    )

else:
    st.info("👈 Silakan upload file gambar PNG senjata milikmu di sidebar sebelah kiri untuk memulai!")
