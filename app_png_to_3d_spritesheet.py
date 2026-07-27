import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import io
import math
import zipfile

# 1. PAGE CONFIG
st.set_page_config(
    page_title="PNG to 3D Sprite Sheet Studio Pro v2",
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
    <div class="studio-title">🧊 PNG to 3D Sprite Sheet Studio Pro v2</div>
    <div class="studio-subtitle">Perbaikan Algoritma 3D: Rotasi Billboard Mulus, Tanpa Efek Gepeng, & Ketebalan Voxel Solid!</div>
</div>
""", unsafe_allow_html=True)

# 4. ENGINE 3D PRO (FIXED ROTATION & EXTRUSION)
def generate_3d_pro_frame(img, angle_y, depth_thickness, scale_factor, canvas_size, mode):
    """
    Menghasilkan frame 3D dengan 2 pilihan mode berkualitas tinggi:
    1. Voxel Extrusion (Memberikan ketebalan nyata ke belakang tanpa gepeng berlebih).
    2. Isometric/Billboard Spin (Rotasi melingkar mulus ala game klasik 2.5D).
    """
    w, h = img.size
    new_w = max(1, int(w * scale_factor))
    new_h = max(1, int(h * scale_factor))
    base_img = img.resize((new_w, new_h), resample=Image.NEAREST)
    
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    center = canvas_size // 2

    rad_y = math.radians(angle_y)
    
    if mode == "🧱 Voxel Extrusion (Tebal & Berisi)":
        # Render tumpukan layer ke belakang untuk menciptakan efek ketebalan 3D
        steps = max(1, depth_thickness)
        for z in range(steps, -1, -1):
            # Pergeseran posisi berdasarkan sudut putar Y
            shift_x = int(z * math.sin(rad_y) * 0.8)
            shift_y = int(z * 0.3) # Efek sedikit miring ke bawah (isometric view)
            
            # Berikan bayangan gelap pada layer bagian dalam/belakang
            if z > 0:
                np_layer = np.array(base_img).astype(np.float32)
                shade = max(0.4, 1.0 - (z / steps) * 0.4)
                np_layer[:, :, :3] *= shade
                layer_img = Image.fromarray(np_layer.astype(np.uint8))
            else:
                layer_img = base_img

            paste_x = center - (layer_img.width // 2) + shift_x
            paste_y = center - (layer_img.height // 2) - shift_y
            canvas.paste(layer_img, (paste_x, paste_y), layer_img)

    else: # Mode "🔄 Smooth Billboard Spin (Putar 360°)"
        # Menggunakan transformasi rotasi affine / perputaran titik pusat tanpa gepeng aneh
        # Kita putar gambar asli dengan sudut Y, dan berikan sedikit efek lengkung 3D
        rotated_img = base_img.rotate(0, resample=Image.NEAREST, expand=True)
        
        # Efek pergerakan melingkar (orbiting)
        radius_orbit = depth_thickness * 1.5
        orbit_x = int(math.cos(rad_y) * radius_orbit)
        
        # Lebar menyesuaikan cosinus agar tampak berputar menjauh/mendekat secara natural
        scale_w = max(0.2, abs(math.cos(rad_y)))
        scaled_w = max(4, int(base_img.width * scale_w))
        
        # Jika menghadap samping, balik gambar (flipping) untuk efek sisi sebaliknya
        curr_img = base_img
        if math.sin(rad_y) < 0:
            curr_img = ImageOps.mirror(base_img)
            
        final_w_img = curr_img.resize((scaled_w, curr_img.height), resample=Image.NEAREST)
        
        paste_x = center - (final_w_img.width // 2) + orbit_x
        paste_y = center - (final_w_img.height // 2)
        canvas.paste(final_w_img, (paste_x, paste_y), final_w_img)

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
    st.sidebar.markdown("### 🧊 2. Pengaturan Mode 3D")
    mode_3d = st.sidebar.radio(
        "Pilih Gaya 3D:",
        ["🧱 Voxel Extrusion (Tebal & Berisi)", "🔄 Smooth Billboard Spin (Putar 360°)"]
    )
    
    depth_thickness = st.sidebar.slider("Ketebalan / Kedalaman Objek:", 1, 30, 8, 1)
    scale_factor = st.sidebar.slider("Skala Ukuran Objek:", 0.5, 3.0, 1.5, 0.1)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎬 3. Pengaturan Animasi Sprite Sheet")
    total_frames = st.sidebar.slider("Jumlah Frame Putaran (360°):", 4, 36, 12, 2)
    anim_fps = st.sidebar.slider("Preview Kecepatan (FPS):", 2, 30, 8, 1)
    grid_cols = st.sidebar.slider("Jumlah Kolom Sprite Sheet:", 2, 8, 4, 1)

    # Preview gambar asli
    col_prev1, col_prev2 = st.columns([1, 2])
    with col_prev1:
        st.markdown("##### Gambar Asli (2D)")
        st.image(src_img, use_container_width=True)

    # Hitung ukuran canvas aman agar tidak terpotong
    canvas_res = max(128, int(max(src_img.width, src_img.height) * scale_factor * 2.0))
    canvas_res = min(512, canvas_res)

    # Generate semua frame rotasi 360 derajat penuh
    frames_3d = []
    for i in range(total_frames):
        angle_y = (i / float(total_frames)) * 360.0
        frame = generate_3d_pro_frame(src_img, angle_y, depth_thickness, scale_factor, canvas_res, mode_3d)
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
        st.download_button("💾 Download GIF Preview (.gif)", data=gif_bytes, file_name="sprite_3d_pro_animation.gif", mime="image/gif", use_container_width=True)

    st.markdown("---")
    st.markdown("### 🖼️ 4. Hasil Sprite Sheet 3D Pro")
    
    sprite_sheet, f_cols, f_rows = compile_spritesheet(frames_3d, canvas_res, cols=grid_cols)
    st.image(sprite_sheet, caption=f"Sprite Sheet Grid ({f_cols} Kolom x {f_rows} Baris - Resolusi: {sprite_sheet.width}x{sprite_sheet.height} px)", use_container_width=False)

    sheet_io = io.BytesIO()
    sprite_sheet.save(sheet_io, format="PNG")
    sheet_bytes = sheet_io.getvalue()

    st.download_button(
        "💾 Download Sprite Sheet 3D (.png)", 
        data=sheet_bytes, 
        file_name="sprite_sheet_3d_pro.png", 
        mime="image/png", 
        use_container_width=True
    )

    # Paket ZIP Exporter
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sprite_sheet_3d_pro.png", sheet_bytes)
        zf.writestr("animation.gif", gif_bytes)
        for idx, f in enumerate(frames_3d):
            f_io = io.BytesIO()
            f.save(f_io, format="PNG")
            zf.writestr(f"frames/frame_{idx+1:02d}.png", f_io.getvalue())

    st.download_button(
        "📦 Download Full Package (.zip berisi Sprite Sheet + GIF + Individual Frames)", 
        data=zip_io.getvalue(), 
        file_name="3D_SpriteSheet_Pro_Package.zip", 
        mime="application/zip", 
        use_container_width=True
    )

else:
    st.info("👈 Silakan unggah gambar PNG transparan di panel kiri untuk mulai mengubahnya menjadi 3D Sprite Sheet dengan kualitas tinggi!")
