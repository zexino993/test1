import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import io
import math
import zipfile

# 1. PAGE CONFIG
st.set_page_config(
    page_title="PNG to 3D Sprite Sheet Generator",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. PREMIUM CSS STYLING
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #1a1f35 50%, #0d111a 100%);
        color: #f1f5f9;
        font-family: 'Inter', system-ui, sans-serif;
    }
    .studio-header {
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
        border: 1px solid rgba(125, 211, 252, 0.2);
        backdrop-filter: blur(12px);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .studio-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .studio-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 6px;
    }
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4) !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        filter: brightness(1.15) !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. HEADER
st.markdown("""
<div class="studio-header">
    <div class="studio-title">🧊 PNG to 3D Sprite Sheet Studio</div>
    <div class="studio-subtitle">Ubah gambar PNG 2D datar Anda menjadi model 3D berputar (Extrusion / Voxel / Billboard) & Export jadi Sprite Sheet!</div>
</div>
""", unsafe_allow_html=True)

# 4. ENGINE 3D PSEUDO-EXTRUSION & ROTATION
def generate_3d_frame(img, angle_y, angle_x, depth_layers, scale_factor, canvas_size):
    """
    Mensimulasikan objek 3D dengan teknik Voxel/Layer Extrusion 
    berdasarkan ketebalan (depth_layers) dan rotasi sumbu Y & X.
    """
    # Resize gambar awal sesuai skala
    w, h = img.size
    new_w, new_h = max(1, int(w * scale_factor)), max(1, int(img.height * scale_factor))
    base_img = img.resize((new_w, new_h), resample=Image.NEAREST)
    
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    center = canvas_size // 2

    rad_y = math.radians(angle_y)
    rad_x = math.radians(angle_x)

    # Efek 3D Extrusion: Menumpuk layer gambar ke belakang dengan pergeseran sudut
    cos_y = math.cos(rad_y)
    sin_y = math.sin(rad_y)

    # Render dari belakang ke depan (painter's algorithm sederhana)
    step = max(1, depth_layers // 10) if depth_layers > 10 else 1
    
    for z in range(-depth_layers // 2, depth_layers // 2 + 1, step):
        # Hitung pergeseran posisi berdasarkan rotasi Y
        offset_x = z * sin_y * 1.5
        offset_y = z * math.sin(rad_x) * 1.5
        
        # Efek bayangan atau penggelapan pada layer belakang untuk kesan 3D mendalam
        if z != 0:
            layer_img = base_img.copy()
            # Buat sedikit lebih gelap untuk layer dalam
            np_layer = np.array(layer_img).astype(np.float32)
            shade = 1.0 - (abs(z) / (depth_layers / 2 + 1)) * 0.35
            np_layer[:, :, :3] *= shade
            layer_img = Image.fromarray(np_layer.astype(np.uint8))
        else:
            layer_img = base_img

        # Kompres lebar horizontal berdasarkan cosinus rotasi Y (efek memutar 3D)
        current_w = max(1, int(layer_img.width * abs(cos_y)))
        if current_w < 1: 
            continue
        
        scaled_layer = layer_img.resize((current_w, layer_img.height), resample=Image.NEAREST)
        
        # Posisi tempel
        paste_x = int(center - (scaled_layer.width // 2) + offset_x)
        paste_y = int(center - (scaled_layer.height // 2) + offset_y)
        
        # Tempel ke canvas utama
        canvas.paste(scaled_layer, (paste_x, paste_y), scaled_layer)

    return canvas

def compile_spritesheet(frames, frame_size, cols=4):
    num_frames = len(frames)
    rows = math.ceil(num_frames / cols)
    sheet_w = frame_size * cols
    sheet_h = frame_size * rows
    
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        r = idx // cols
        c = idx % cols
        sheet.paste(frame, (c * frame_size, r * frame_size))
        
    return sheet, cols, rows

# 5. SIDEBAR CONTROLS
st.sidebar.markdown("### 📁 1. Upload Gambar PNG 2D")
uploaded_file = st.sidebar.file_uploader("Pilih file PNG transparan:", type=["png"])

if uploaded_file is not None:
    src_img = Image.open(uploaded_file).convert("RGBA")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧊 2. Pengaturan 3D Extrusion")
    depth_layers = st.sidebar.slider("Ketebalan Objek 3D (Depth Layers):", 1, 40, 15, 1)
    scale_factor = st.sidebar.slider("Skala Ukuran Objek:", 0.2, 2.0, 1.0, 0.1)
    tilt_x = st.sidebar.slider("Kemiringan Sumbu X (°):", -45, 45, 0, 5)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎬 3. Pengaturan Animasi Putar (Sprite Sheet)")
    total_frames = st.sidebar.slider("Jumlah Frame Putaran (360°):", 4, 36, 12, 2)
    anim_fps = st.sidebar.slider("Preview Kecepatan (FPS):", 2, 30, 8, 1)
    grid_cols = st.sidebar.slider("Jumlah Kolom Sprite Sheet:", 2, 8, 4, 1)

    # Preview gambar asli
    col_prev1, col_prev2 = st.columns([1, 2])
    with col_prev1:
        st.markdown("##### Gambar Asli (2D)")
        st.image(src_img, use_container_width=True)

    # Hitung ukuran canvas aman
    canvas_res = max(128, int(max(src_img.width, src_img.height) * scale_factor * 1.5))
    canvas_res = min(512, canvas_res)

    # Generate semua frame rotasi 360 derajat penuh
    frames_3d = []
    for i in range(total_frames):
        angle_y = (i / float(total_frames)) * 360.0
        frame = generate_3d_frame(src_img, angle_y, tilt_x, depth_layers, scale_factor, canvas_res)
        frames_3d.append(frame)

    with col_prev2:
        st.markdown(f"##### Live 3D Preview (GIF - {total_frames} Frames)")
        gif_io = io.BytesIO()
        frames_3d[0].save(
            gif_io, format="GIF", save_all=True, append_images=frames_3d[1:],
            duration=int(1000/anim_fps), loop=0, disposal=2
        )
        gif_bytes = gif_io.getvalue()
        st.image(gif_bytes, use_container_width=True)
        st.download_button("💾 Download GIF Preview (.gif)", data=gif_bytes, file_name="sprite_3d_animation.gif", mime="image/gif", use_container_width=True)

    st.markdown("---")
    st.markdown("### 🖼️ 4. Hasil Sprite Sheet 3D")
    
    sprite_sheet, f_cols, f_rows = compile_spritesheet(frames_3d, canvas_res, cols=grid_cols)
    st.image(sprite_sheet, caption=f"Sprite Sheet Grid ({f_cols} Kolom x {f_rows} Baris - Resolusi: {sprite_sheet.width}x{sprite_sheet.height} px)", use_container_width=False)

    sheet_io = io.BytesIO()
    sprite_sheet.save(sheet_io, format="PNG")
    sheet_bytes = sheet_io.getvalue()

    st.download_button(
        "💾 Download Sprite Sheet 3D (.png)", 
        data=sheet_bytes, 
        file_name="sprite_sheet_3d.png", 
        mime="image/png", 
        use_container_width=True
    )

    # Paket ZIP Exporter
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sprite_sheet_3d.png", sheet_bytes)
        zf.writestr("animation.gif", gif_bytes)
        # Simpan frame satuan jika dibutuhkan developer game
        for idx, f in enumerate(frames_3d):
            f_io = io.BytesIO()
            f.save(f_io, format="PNG")
            zf.writestr(f"frames/frame_{idx+1:02d}.png", f_io.getvalue())

    st.download_button(
        "📦 Download Full Package (.zip berisi Sprite Sheet + GIF + Individual Frames)", 
        data=zip_io.getvalue(), 
        file_name="3D_SpriteSheet_Package.zip", 
        mime="application/zip", 
        use_container_width=True
    )

else:
    st.info("👈 Silakan unggah gambar PNG transparan (seperti koin, karakter, item, atau pohon pixel art) di panel kiri untuk mulai mengubahnya menjadi 3D Sprite Sheet!")
