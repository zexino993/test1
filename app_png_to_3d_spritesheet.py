import streamlit as st
from PIL import Image, ImageOps, ImageFilter
import numpy as np
import io
import math
import zipfile

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Modular Sprite Studio v2.5",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. PREMIUM CSS STYLING
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #161b2e 50%, #0d111a 100%);
        color: #f1f5f9;
        font-family: 'Inter', system-ui, sans-serif;
    }
    .studio-header {
        background: linear-gradient(90deg, rgba(14, 165, 233, 0.15) 0%, rgba(236, 72, 153, 0.15) 100%);
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
        background: linear-gradient(90deg, #38bdf8, #c084fc, #ec4899);
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
        background: linear-gradient(135deg, #0ea5e9 0%, #ec4899 100%) !important;
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
    <div class="studio-title">🎛️ Modular Sprite Studio v2.5</div>
    <div class="studio-subtitle">Pilih Fitur yang Ingin Diaktifkan Secara Bebas: Pure 2D 360° Rotation, 3D Voxel Extrusion, Tilt, & FX!</div>
</div>
""", unsafe_allow_html=True)

# 4. MODULAR RENDER ENGINE
def render_modular_frame(img, current_angle_deg, scale_factor, canvas_size, 
                           use_pure_2d_rot, use_voxel_depth, voxel_thickness, 
                           use_tilt, tilt_x, tilt_z, 
                           use_bounce, use_glow):
    w, h = img.size
    new_w = max(1, int(w * scale_factor))
    new_h = max(1, int(h * scale_factor))
    base_img = img.resize((new_w, new_h), resample=Image.NEAREST)
    
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    center = canvas_size // 2
    
    # 1. FITUR PURE 2D 360° ROTATION (Murni berputar tanpa gepeng aneh)
    if use_pure_2d_rot:
        # Menggunakan rotasi PIL terpusat dengan expand=False agar ukuran konsisten di tengah
        working_img = base_img.rotate(current_angle_deg, resample=Image.NEAREST, expand=False)
    else:
        working_img = base_img

    # 2. FITUR 3D VOXEL EXTRUSION DEPTH (Menambah ketebalan ke belakang)
    if use_voxel_depth and voxel_thickness > 0:
        rad_y = math.radians(current_angle_deg)
        steps = max(1, voxel_thickness)
        
        voxel_canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        for z in range(steps, -1, -1):
            shift_x = int(z * math.sin(rad_y) * 0.8)
            shift_y = int(z * 0.2)
            
            if z > 0:
                np_layer = np.array(working_img).astype(np.float32)
                shade = max(0.35, 1.0 - (z / steps) * 0.45)
                np_layer[:, :, :3] *= shade
                layer_img = Image.fromarray(np_layer.astype(np.uint8))
            else:
                layer_img = working_img

            p_x = center - (layer_img.width // 2) + shift_x
            p_y = center - (layer_img.height // 2) - shift_y
            voxel_canvas.paste(layer_img, (p_x, p_y), layer_img)
        working_img = voxel_canvas

    # 3. FITUR PERSPECTIVE TILT (Kemiringan Sudut Pandang X & Z)
    if use_tilt and (tilt_x != 0 or tilt_z != 0):
        working_img = working_img.rotate(tilt_z, resample=Image.NEAREST, expand=True)

    # 4. FITUR SPECIAL FX (Glow & Bounce)
    if use_glow:
        glow_layer = working_img.filter(ImageFilter.GaussianBlur(radius=4))
        canvas.paste(glow_layer, (center - glow_layer.width//2, center - glow_layer.height//2), glow_layer)

    bounce_offset = 0
    if use_bounce:
        bounce_offset = int(abs(math.sin(math.radians(current_angle_deg * 2))) * 8)

    # Tempel akhir ke canvas utama
    paste_x = center - (working_img.width // 2)
    paste_y = center - (working_img.height // 2) - bounce_offset
    canvas.paste(working_img, (paste_x, paste_y), working_img)

    return canvas

def compile_spritesheet(frames, frame_size, layout_mode, grid_cols=4):
    num_frames = len(frames)
    
    if layout_mode == "Horizontal Only (1 Baris Saja)":
        cols = num_frames
        rows = 1
    elif layout_mode == "Vertical Only (1 Kolom Saja)":
        cols = 1
        rows = num_frames
    else:
        cols = grid_cols
        rows = math.ceil(num_frames / cols)
        
    sheet_w = frame_size * cols
    sheet_h = frame_size * rows
    
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        if layout_mode == "Horizontal Only (1 Baris Saja)":
            r, c = 0, idx
        elif layout_mode == "Vertical Only (1 Kolom Saja)":
            r, c = idx, 0
        else:
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
    st.sidebar.markdown("### 🎛️ 2. Panel Pilihan Fitur (Modular Toggles)")
    
    # Checkbox utama untuk mengaktifkan/menonaktifkan fitur secara spesifik
    use_pure_2d_rot = st.sidebar.checkbox("🔄 Aktifkan Pure 2D 360° Rotation", value=True)
    use_voxel_depth = st.sidebar.checkbox("🧱 Aktifkan 3D Voxel Extrusion (Ketebalan)", value=False)
    use_tilt        = st.sidebar.checkbox("📐 Aktifkan Sudut Kamera (Tilt X/Z)", value=False)
    use_bounce      = st.sidebar.checkbox("🍮 Aktifkan Efek Jelly Bounce", value=False)
    use_glow        = st.sidebar.checkbox("✨ Aktifkan Efek Glow / Pendaran", value=False)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ 3. Pengaturan Parameter Fitur")
    
    if use_pure_2d_rot:
        rotation_direction = st.sidebar.radio(
            "Arah Putaran 2D:",
            ["➡️ Searah Jarum Jam (Clockwise)", "⬅️ Berlawanan Jarum Jam (Counter-Clockwise)"]
        )
        start_angle = st.sidebar.slider("Sudut Awal (°):", 0, 360, 0, 15)
        total_sweep = st.sidebar.slider("Total Rentang Putaran (°):", 90, 360, 360, 45)
    else:
        rotation_direction = "➡️ Searah Jarum Jam (Clockwise)"
        start_angle, total_sweep = 0, 360

    total_frames = st.sidebar.slider("Jumlah Frame Animasi:", 4, 36, 12, 2)
    anim_fps = st.sidebar.slider("Preview Kecepatan (FPS):", 2, 30, 8, 1)

    if use_voxel_depth:
        voxel_thickness = st.sidebar.slider("Ketebalan Voxel (Depth Layers):", 1, 30, 8, 1)
    else:
        voxel_thickness = 0

    if use_tilt:
        tilt_x = st.sidebar.slider("Kemiringan Vertikal (X):", -90, 90, 0, 5)
        tilt_z = st.sidebar.slider("Kemiringan Rotasi (Z):", -180, 180, 0, 5)
    else:
        tilt_x, tilt_z = 0, 0

    scale_factor = st.sidebar.slider("Skala Ukuran Objek:", 0.5, 3.0, 1.2, 0.1)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📐 4. Layout Sprite Sheet")
    sheet_layout_option = st.sidebar.selectbox(
        "Pilih Orientasi Layout:",
        ["Horizontal Only (1 Baris Saja)", "Vertical Only (1 Kolom Saja)", "Grid Custom (Multi Kolom/Baris)"]
    )
    
    grid_cols = 4
    if sheet_layout_option == "Grid Custom (Multi Kolom/Baris)":
        grid_cols = st.sidebar.slider("Jumlah Kolom Grid:", 2, 8, 4, 1)

    # Preview gambar asli
    col_prev1, col_prev2 = st.columns([1, 2])
    with col_prev1:
        st.markdown("##### Gambar Asli (2D)")
        st.image(src_img, use_container_width=True)

    # Ukuran canvas aman
    canvas_res = max(128, int(max(src_img.width, src_img.height) * scale_factor * 2.2))
    canvas_res = min(512, canvas_res)

    # Kalkulasi frame render
    frames_3d = []
    dir_multiplier = 1 if "Searah" in rotation_direction else -1

    for i in range(total_frames):
        progress = i / float(max(1, total_frames - 1)) if total_frames > 1 else 0
        current_angle = start_angle + (progress * total_sweep * dir_multiplier)
        
        frame = render_modular_frame(
            src_img, current_angle, scale_factor, canvas_res,
            use_pure_2d_rot, use_voxel_depth, voxel_thickness,
            use_tilt, tilt_x, tilt_z, use_bounce, use_glow
        )
        frames_3d.append(frame)

    with col_prev2:
        st.markdown(f"##### Live Preview ({total_frames} Frames - Loop)")
        gif_io = io.BytesIO()
        frames_3d[0].save(
            gif_io, format="GIF", save_all=True, append_images=frames_3d[1:],
            duration=int(1000/anim_fps), loop=0, disposal=2
        )
        gif_bytes = gif_io.getvalue()
        st.image(gif_bytes, use_container_width=True)
        st.download_button("💾 Download GIF Preview (.gif)", data=gif_bytes, file_name="sprite_modular_animation.gif", mime="image/gif", use_container_width=True)

    st.markdown("---")
    st.markdown(f"### 🖼️ 5. Hasil Sprite Sheet ({sheet_layout_option})")
    
    sprite_sheet, f_cols, f_rows = compile_spritesheet(frames_3d, canvas_res, sheet_layout_option, grid_cols)
    st.image(sprite_sheet, caption=f"Sprite Sheet Layout ({f_cols} Kolom x {f_rows} Baris - Resolusi: {sprite_sheet.width}x{sprite_sheet.height} px)", use_container_width=False)

    sheet_io = io.BytesIO()
    sprite_sheet.save(sheet_io, format="PNG")
    sheet_bytes = sheet_io.getvalue()

    st.download_button(
        "💾 Download Sprite Sheet (.png)", 
        data=sheet_bytes, 
        file_name="sprite_sheet_modular.png", 
        mime="image/png", 
        use_container_width=True
    )

    # Paket ZIP Exporter
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sprite_sheet.png", sheet_bytes)
        zf.writestr("animation.gif", gif_bytes)
        for idx, f in enumerate(frames_3d):
            f_io = io.BytesIO()
            f.save(f_io, format="PNG")
            zf.writestr(f"frames/frame_{idx+1:02d}.png", f_io.getvalue())

    st.download_button(
        "📦 Download Full Package (.zip)", 
        data=zip_io.getvalue(), 
        file_name="Modular_SpriteSheet_Package.zip", 
        mime="application/zip", 
        use_container_width=True
    )

else:
    st.info("👈 Silakan unggah file PNG transparan di panel kiri untuk mulai memilih fitur yang ingin diaktifkan!")
