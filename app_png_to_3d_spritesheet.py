import streamlit as st
from PIL import Image, ImageOps, ImageFilter
import numpy as np
import io
import math
import zipfile
import random

# 1. PAGE CONFIG
st.set_page_config(
    page_title="PNG to 3D Sprite Sheet Extreme v2.3",
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
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.15) 0%, rgba(236, 72, 153, 0.15) 100%);
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
        background: linear-gradient(90deg, #38bdf8, #ec4899, #f59e0b);
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
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4) !important;
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
    <div class="studio-title">🧊 PNG to 3D Sprite Studio Extreme v2.3</div>
    <div class="studio-subtitle">10 Gaya Rendering 3D Gila! Hologram, Jelly Bounce, Tornado Swirl, dan Parallax Wave!</div>
</div>
""", unsafe_allow_html=True)

# 4. EXTREME MULTI-STYLE 3D ENGINE
def generate_extreme_3d_frame(img, angle_y, depth_thickness, scale_factor, canvas_size, mode, progress_ratio):
    w, h = img.size
    new_w = max(1, int(w * scale_factor))
    new_h = max(1, int(h * scale_factor))
    base_img = img.resize((new_w, new_h), resample=Image.NEAREST)
    
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    center = canvas_size // 2
    rad_y = math.radians(angle_y)
    
    if mode == "🧱 Voxel Extrusion Solid (Tebal & Berisi)":
        steps = max(1, depth_thickness)
        for z in range(steps, -1, -1):
            shift_x = int(z * math.sin(rad_y) * 0.9)
            shift_y = int(z * 0.25)
            
            if z > 0:
                np_layer = np.array(base_img).astype(np.float32)
                shade = max(0.35, 1.0 - (z / steps) * 0.45)
                np_layer[:, :, :3] *= shade
                layer_img = Image.fromarray(np_layer.astype(np.uint8))
            else:
                layer_img = base_img

            paste_x = center - (layer_img.width // 2) + shift_x
            paste_y = center - (layer_img.height // 2) - shift_y
            canvas.paste(layer_img, (paste_x, paste_y), layer_img)

    elif mode == "🔄 Smooth Billboard Spin (Putar 360° Mulus)":
        radius_orbit = depth_thickness * 1.5
        orbit_x = int(math.cos(rad_y) * radius_orbit)
        scale_w = max(0.2, abs(math.cos(rad_y)))
        scaled_w = max(4, int(base_img.width * scale_w))
        
        curr_img = base_img
        if math.sin(rad_y) < 0:
            curr_img = ImageOps.mirror(base_img)
            
        final_w_img = curr_img.resize((scaled_w, curr_img.height), resample=Image.NEAREST)
        paste_x = center - (final_w_img.width // 2) + orbit_x
        paste_y = center - (final_w_img.height // 2)
        canvas.paste(final_w_img, (paste_x, paste_y), final_w_img)

    elif mode == "🧊 Isometric Box Projection (Kotak 3D Isometrik)":
        steps = max(2, depth_thickness)
        for z in range(steps, -1, -1):
            shift_x = int(z * math.cos(rad_y) * 0.7)
            shift_y = int(z * math.sin(rad_y) * 0.7)
            
            np_layer = np.array(base_img).astype(np.float32)
            shade = max(0.3, 1.0 - (z / steps) * 0.5)
            np_layer[:, :, :3] *= shade
            layer_img = Image.fromarray(np_layer.astype(np.uint8))

            paste_x = center - (layer_img.width // 2) + shift_x
            paste_y = center - (layer_img.height // 2) + shift_y
            canvas.paste(layer_img, (paste_x, paste_y), layer_img)

    elif mode == "🌟 Curved Dome / Coin Spin (Koin / Permata Cembung)":
        steps = max(2, depth_thickness)
        for z in range(steps, -1, -1):
            expansion = math.cos((z / steps) * (math.pi / 2)) * (depth_thickness * 0.8)
            current_scale = 1.0 + (expansion / max(1, base_img.width)) * math.cos(rad_y)
            
            w_c = max(4, int(base_img.width * current_scale))
            h_c = max(4, int(base_img.height * current_scale))
            scaled_layer = base_img.resize((w_c, h_c), resample=Image.NEAREST)
            
            orbit_x = int(math.cos(rad_y) * (depth_thickness * 1.2))
            
            np_layer = np.array(scaled_layer).astype(np.float32)
            shade = max(0.4, 0.7 + 0.3 * math.cos(rad_y + (z / steps)))
            np_layer[:, :, :3] *= shade
            shaded_layer = Image.fromarray(np_layer.astype(np.uint8))

            paste_x = center - (shaded_layer.width // 2) + orbit_x
            paste_y = center - (shaded_layer.height // 2)
            canvas.paste(shaded_layer, (paste_x, paste_y), shaded_layer)

    elif mode == "🌊 Floating Wave / Parallax Depth (Melayang Berlapis)":
        steps = 5
        for z in range(steps):
            wave_offset = int(math.sin(rad_y + (z * 0.5)) * (depth_thickness * 1.5))
            
            np_layer = np.array(base_img).astype(np.float32)
            shade = max(0.5, 1.0 - (z * 0.12))
            np_layer[:, :, :3] *= shade
            layer_img = Image.fromarray(np_layer.astype(np.uint8))
            
            paste_x = center - (layer_img.width // 2) + wave_offset + (z * 2)
            paste_y = center - (layer_img.height // 2) - (z * 3)
            canvas.paste(layer_img, (paste_x, paste_y), layer_img)

    elif mode == "⚡ Hologram Glitch (Transparan & Putus-putus)":
        np_layer = np.array(base_img).astype(np.float32)
        # Warna hologram biru/cyan dengan transparansi 60%
        np_layer[:, :, 0] *= 0.2  # Kurangi Red
        np_layer[:, :, 1] *= 1.2  # Tambah Green
        np_layer[:, :, 2] *= 1.5  # Tambah Blue
        np_layer[:, :, 3] *= 0.6  # Kurangi Alpha
        
        # Bikin garis putus-putus ala Glitch TV rusak
        for y in range(0, np_layer.shape[0], 4):
            np_layer[y:y+2, :, 3] *= 0.2 
            
        # Putar sedikit
        holo_img = Image.fromarray(np.clip(np_layer, 0, 255).astype(np.uint8))
        glitch_x = int(math.sin(rad_y * 3) * 5)
        
        paste_x = center - (holo_img.width // 2) + glitch_x
        paste_y = center - (holo_img.height // 2)
        canvas.paste(holo_img, (paste_x, paste_y), holo_img)

    elif mode == "🍮 Jelly Bounce Spin (Mumbul Kenyal)":
        # Bouncing physics dengan sine wave
        bounce_h = int(abs(math.sin(rad_y * 2)) * depth_thickness)
        squish_w = 1.0 + (abs(math.cos(rad_y * 2)) * 0.3)
        squish_h = 1.0 - (abs(math.cos(rad_y * 2)) * 0.3)
        
        jelly_w = max(4, int(base_img.width * squish_w))
        jelly_h = max(4, int(base_img.height * squish_h))
        jelly_img = base_img.resize((jelly_w, jelly_h), resample=Image.NEAREST)
        
        paste_x = center - (jelly_img.width // 2)
        paste_y = center - (jelly_img.height // 2) + bounce_h - (depth_thickness // 2)
        canvas.paste(jelly_img, (paste_x, paste_y), jelly_img)

    elif mode == "🌪️ Tornado Swirl (Melintir ke Atas)":
        steps = max(2, depth_thickness)
        for z in range(steps):
            # Rotasi spiral ke atas
            spiral_x = int(math.cos(rad_y + z*0.4) * (z * 2))
            spiral_y = -int(z * 4)
            
            scale = max(0.2, 1.0 - (z * 0.05))
            sw = max(2, int(base_img.width * scale))
            sh = max(2, int(base_img.height * scale))
            
            swirl_img = base_img.resize((sw, sh), resample=Image.NEAREST)
            
            np_layer = np.array(swirl_img).astype(np.float32)
            np_layer[:, :, 3] *= max(0.1, 1.0 - (z / steps))
            swirl_img = Image.fromarray(np_layer.astype(np.uint8))
            
            paste_x = center - (swirl_img.width // 2) + spiral_x
            paste_y = center - (swirl_img.height // 2) + spiral_y + (depth_thickness * 2)
            canvas.paste(swirl_img, (paste_x, paste_y), swirl_img)

    elif mode == "🚀 Speed Dash (Motion Blur / After-Image)":
        # 3 Bayangan hantu di belakang objek utama
        for ghost in range(3, 0, -1):
            offset_x = int(math.cos(rad_y) * (ghost * depth_thickness))
            
            np_layer = np.array(base_img).astype(np.float32)
            np_layer[:, :, 3] *= (0.2 / ghost) # Sangat transparan
            ghost_img = Image.fromarray(np_layer.astype(np.uint8))
            
            paste_x = center - (ghost_img.width // 2) - offset_x
            paste_y = center - (ghost_img.height // 2)
            canvas.paste(ghost_img, (paste_x, paste_y), ghost_img)
            
        # Objek Utama
        canvas.paste(base_img, (center - base_img.width//2, center - base_img.height//2), base_img)

    elif mode == "❤️ Heartbeat Pulse (Berdetak 3D)":
        # Membesar dan mengecil seperti jantung berdetak
        pulse = 1.0 + (abs(math.sin(rad_y)) * (depth_thickness * 0.05))
        
        pulse_w = max(4, int(base_img.width * pulse))
        pulse_h = max(4, int(base_img.height * pulse))
        pulse_img = base_img.resize((pulse_w, pulse_h), resample=Image.NEAREST)
        
        # Tambahkan sedikit glow merah
        glow = pulse_img.filter(ImageFilter.GaussianBlur(radius=3))
        canvas.paste(glow, (center - glow.width//2, center - glow.height//2), glow)
        canvas.paste(pulse_img, (center - pulse_img.width//2, center - pulse_img.height//2), pulse_img)

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
    st.sidebar.markdown("### 🧊 2. Pilih Gaya 3D Ekstrem!")
    mode_3d = st.sidebar.selectbox(
        "Gaya Rendering 3D:",
        [
            "🧱 Voxel Extrusion Solid (Tebal & Berisi)",
            "🔄 Smooth Billboard Spin (Putar 360° Mulus)",
            "🧊 Isometric Box Projection (Kotak 3D Isometrik)",
            "🌟 Curved Dome / Coin Spin (Koin / Permata Cembung)",
            "🌊 Floating Wave / Parallax Depth (Melayang Berlapis)",
            "⚡ Hologram Glitch (Transparan & Putus-putus)",
            "🍮 Jelly Bounce Spin (Mumbul Kenyal)",
            "🌪️ Tornado Swirl (Melintir ke Atas)",
            "🚀 Speed Dash (Motion Blur / After-Image)",
            "❤️ Heartbeat Pulse (Berdetak 3D)"
        ]
    )
    
    depth_thickness = st.sidebar.slider("Intensitas / Ketebalan / Jarak Efek:", 1, 30, 10, 1)
    scale_factor = st.sidebar.slider("Skala Ukuran Objek:", 0.5, 3.0, 1.5, 0.1)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎬 3. Pengaturan Animasi Sprite Sheet")
    total_frames = st.sidebar.slider("Jumlah Frame Animasi (360° / Loop):", 4, 36, 12, 2)
    anim_fps = st.sidebar.slider("Preview Kecepatan (FPS):", 2, 30, 8, 1)

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

    # Hitung ukuran canvas aman
    canvas_res = max(128, int(max(src_img.width, src_img.height) * scale_factor * 2.5))
    canvas_res = min(512, canvas_res)

    # Generate semua frame
    frames_3d = []
    for i in range(total_frames):
        angle_y = (i / float(total_frames)) * 360.0
        progress_ratio = i / float(total_frames)
        frame = generate_extreme_3d_frame(src_img, angle_y, depth_thickness, scale_factor, canvas_res, mode_3d, progress_ratio)
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
        st.download_button("💾 Download GIF Preview (.gif)", data=gif_bytes, file_name="sprite_3d_extreme_animation.gif", mime="image/gif", use_container_width=True)

    st.markdown("---")
    st.markdown(f"### 🖼️ 5. Hasil Sprite Sheet ({sheet_layout_option})")
    
    sprite_sheet, f_cols, f_rows = compile_spritesheet(frames_3d, canvas_res, sheet_layout_option, grid_cols)
    st.image(sprite_sheet, caption=f"Sprite Sheet Layout ({f_cols} Kolom x {f_rows} Baris - Resolusi: {sprite_sheet.width}x{sprite_sheet.height} px)", use_container_width=False)

    sheet_io = io.BytesIO()
    sprite_sheet.save(sheet_io, format="PNG")
    sheet_bytes = sheet_io.getvalue()

    st.download_button(
        "💾 Download Sprite Sheet 3D (.png)", 
        data=sheet_bytes, 
        file_name="sprite_sheet_3d_extreme.png", 
        mime="image/png", 
        use_container_width=True
    )

    # Paket ZIP Exporter
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sprite_sheet_3d.png", sheet_bytes)
        zf.writestr("animation.gif", gif_bytes)
        for idx, f in enumerate(frames_3d):
            f_io = io.BytesIO()
            f.save(f_io, format="PNG")
            zf.writestr(f"frames/frame_{idx+1:02d}.png", f_io.getvalue())

    st.download_button(
        "📦 Download Full Package (.zip berisi Sprite Sheet + GIF + Individual Frames)", 
        data=zip_io.getvalue(), 
        file_name="3D_SpriteSheet_Extreme_Package.zip", 
        mime="application/zip", 
        use_container_width=True
    )

else:
    st.info("👈 Silakan unggah gambar PNG transparan di panel kiri untuk mulai bereksperimen dengan 10 Gaya 3D Gila!")
