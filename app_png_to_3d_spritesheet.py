import streamlit as st
from PIL import Image, ImageOps, ImageFilter
import numpy as np
import io
import math
import random
import zipfile

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Ultimate Sprite Studio v3.0",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. SESSION STATE DEFAULTS
default_states = {
    "use_rotation_y": True,
    "rotation_mode": "2D 360° Rotasi Datar (Flat Spin)",
    "rot_dir": "➡️ Searah Jarum Jam (Clockwise)",
    "start_angle": 0,
    "total_sweep": 360,
    "total_frames": 12,
    "anim_fps": 8,
    "use_voxel_depth": False,
    "voxel_thickness": 8,
    "use_axis_tilts": True,
    "tilt_x_deg": 0,
    "tilt_y_deg": 0,
    "tilt_z_deg": 0,
    "use_bounce": False,
    "use_glow": False,
    # Fitur Baru v3.0
    "palette_mode": "Normal (Asli)",
    "loop_mode": "Maju Normal (Forward)",
    "use_trail": False,
    "trail_color": "#00ffff",
    "trail_count": 8,
    "scale_factor": 1.2,
    "sheet_layout_option": "Horizontal Only (1 Baris Saja)",
    "grid_cols": 4
}

for key, val in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = val

def reset_rotation():
    st.session_state.use_rotation_y = default_states["use_rotation_y"]
    st.session_state.rotation_mode = default_states["rotation_mode"]
    st.session_state.rot_dir = default_states["rot_dir"]
    st.session_state.start_angle = default_states["start_angle"]
    st.session_state.total_sweep = default_states["total_sweep"]
    st.session_state.total_frames = default_states["total_frames"]
    st.session_state.anim_fps = default_states["anim_fps"]

def reset_voxel():
    st.session_state.use_voxel_depth = default_states["use_voxel_depth"]
    st.session_state.voxel_thickness = default_states["voxel_thickness"]

def reset_tilts():
    st.session_state.use_axis_tilts = default_states["use_axis_tilts"]
    st.session_state.tilt_x_deg = default_states["tilt_x_deg"]
    st.session_state.tilt_y_deg = default_states["tilt_y_deg"]
    st.session_state.tilt_z_deg = default_states["tilt_z_deg"]

def reset_v3_features():
    st.session_state.palette_mode = default_states["palette_mode"]
    st.session_state.loop_mode = default_states["loop_mode"]
    st.session_state.use_trail = default_states["use_trail"]
    st.session_state.trail_color = default_states["trail_color"]
    st.session_state.trail_count = default_states["trail_count"]

def reset_general():
    st.session_state.scale_factor = default_states["scale_factor"]
    st.session_state.sheet_layout_option = default_states["sheet_layout_option"]
    st.session_state.grid_cols = default_states["grid_cols"]

# 3. PREMIUM CSS STYLING
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #161b2e 50%, #0d111a 100%);
        color: #f1f5f9;
        font-family: 'Inter', system-ui, sans-serif;
    }
    .studio-header {
        background: linear-gradient(90deg, rgba(236, 72, 153, 0.15) 0%, rgba(14, 165, 233, 0.15) 100%);
        border: 1px solid rgba(244, 114, 182, 0.2);
        backdrop-filter: blur(12px);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .studio-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ec4899, #38bdf8, #c084fc);
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
        background: linear-gradient(135deg, #ec4899 0%, #0ea5e9 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 8px 16px !important;
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

# 4. HEADER
st.markdown("""
<div class="studio-header">
    <div class="studio-title">✨ Ultimate Sprite Studio v3.0</div>
    <div class="studio-subtitle">Dilengkapi Auto-Palette Swapper, Frame Ping-Pong Loop, & Dynamic Particle Trail Generator!</div>
</div>
""", unsafe_allow_html=True)

# 5. AUTO-PALETTE SWAPPER (RECOLOR ENGINE)
def apply_palette_swap(img, mode):
    if mode == "Normal (Asli)":
        return img
    
    img_np = np.array(img).astype(np.float32)
    rgb = img_np[:, :, :3]
    alpha = img_np[:, :, 3]

    if mode == "🔥 Fire / Lava (Merah-Oranye)":
        # Geser channel warna ke dominasi merah/oranye
        r = rgb[:, :, 0] * 1.3
        g = rgb[:, :, 1] * 0.6
        b = rgb[:, :, 2] * 0.2
        rgb[:, :, 0] = np.clip(r, 0, 255)
        rgb[:, :, 1] = np.clip(g, 0, 255)
        rgb[:, :, 2] = np.clip(b, 0, 255)

    elif mode == "❄️ Ice / Frost (Biru Es)":
        r = rgb[:, :, 0] * 0.3
        g = rgb[:, :, 1] * 0.9
        b = rgb[:, :, 2] * 1.4
        rgb[:, :, 0] = np.clip(r, 0, 255)
        rgb[:, :, 1] = np.clip(g, 0, 255)
        rgb[:, :, 2] = np.clip(b, 0, 255)

    elif mode == "🟢 Toxic / Poison (Hijau Slime)":
        r = rgb[:, :, 0] * 0.2
        g = rgb[:, :, 1] * 1.4
        b = rgb[:, :, 2] * 0.3
        rgb[:, :, 0] = np.clip(r, 0, 255)
        rgb[:, :, 1] = np.clip(g, 0, 255)
        rgb[:, :, 2] = np.clip(b, 0, 255)

    elif mode == "💀 Shadow / Dark (Ungu Gelap)":
        gray = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
        rgb[:, :, 0] = np.clip(gray * 0.8, 0, 255)
        rgb[:, :, 1] = np.clip(gray * 0.3, 0, 255)
        rgb[:, :, 2] = np.clip(gray * 1.2, 0, 255)

    elif mode == "🪙 Golden / Treasure (Emas)":
        r = rgb[:, :, 0] * 1.3
        g = rgb[:, :, 1] * 1.1
        b = rgb[:, :, 2] * 0.3
        rgb[:, :, 0] = np.clip(r, 0, 255)
        rgb[:, :, 1] = np.clip(g, 0, 255)
        rgb[:, :, 2] = np.clip(b, 0, 255)

    img_np[:, :, :3] = rgb
    return Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))

# 6. RENDER FRAME DENGAN TRAIL & EFEK
def render_frame(img, angle_deg, tilt_x_deg, tilt_y_deg, tilt_z_deg, scale_factor, canvas_size, 
                 use_rotation_y, rot_mode, use_voxel_depth, voxel_thickness, 
                 use_axis_tilts, use_bounce, use_glow, palette_mode, use_trail, trail_color_hex, trail_count):
    
    # Terapkan palette swap terlebih dahulu pada base image
    swapped_img = apply_palette_swap(img, palette_mode)

    w, h = swapped_img.size
    new_w = max(1, int(w * scale_factor))
    new_h = max(1, int(h * scale_factor))
    base_img = swapped_img.resize((new_w, new_h), resample=Image.NEAREST)
    
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    center = canvas_size // 2
    
    working_img = base_img

    if use_rotation_y:
        if "2D" in rot_mode:
            working_img = base_img.rotate(angle_deg, resample=Image.NEAREST, expand=True)
        else:
            rad_y = math.radians(angle_deg)
            scale_w = max(0.1, abs(math.cos(rad_y)))
            scaled_w = max(4, int(base_img.width * scale_w))
            
            curr_img = base_img
            if math.sin(rad_y) < 0:
                curr_img = ImageOps.mirror(base_img)
                
            working_img = curr_img.resize((scaled_w, curr_img.height), resample=Image.NEAREST)

    if use_voxel_depth and voxel_thickness > 0 and "3D" in rot_mode:
        rad_y = math.radians(angle_deg)
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

    if use_axis_tilts and (tilt_x_deg != 0 or tilt_y_deg != 0 or tilt_z_deg != 0):
        if tilt_z_deg != 0:
            working_img = working_img.rotate(tilt_z_deg, resample=Image.NEAREST, expand=True)
        if tilt_x_deg != 0:
            rad_x = math.radians(tilt_x_deg)
            new_height = max(4, int(working_img.height * max(0.1, abs(math.cos(rad_x)))))
            working_img = working_img.resize((working_img.width, new_height), resample=Image.NEAREST)
        if tilt_y_deg != 0:
            rad_y_tilt = math.radians(tilt_y_deg)
            new_width = max(4, int(working_img.width * max(0.1, abs(math.cos(rad_y_tilt)))))
            working_img = working_img.resize((new_width, working_img.height), resample=Image.NEAREST)

    # FITUR 1: PARTICLE TRAIL GENERATOR (Jejak Partikel di Sekitar Objek)
    if use_trail and trail_count > 0:
        c_hex = trail_color_hex.lstrip('#')
        tc_r, tc_g, tc_b = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
        
        random.seed(int(angle_deg * 10)) # Seed dinamis per sudut putaran
        for t in range(trail_count):
            offset_angle = math.radians(angle_deg + random.uniform(-60, 60))
            dist = random.uniform(10, working_img.width * 0.7)
            tx = center + int(dist * math.cos(offset_angle))
            ty = center + int(dist * math.sin(offset_angle))
            
            p_size = random.randint(2, 5)
            alpha_trail = random.randint(100, 220)
            
            # Gambar partikel titik/bintang kecil di layer canvas
            draw_canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            from PIL import ImageDraw
            d = ImageDraw.Draw(draw_canvas)
            d.ellipse([tx - p_size, ty - p_size, tx + p_size, ty + p_size], fill=(tc_r, tc_g, tc_b, alpha_trail))
            canvas = Image.alpha_composite(canvas, draw_canvas)

    if use_glow:
        glow_layer = working_img.filter(ImageFilter.GaussianBlur(radius=4))
        canvas.paste(glow_layer, (center - glow_layer.width//2, center - glow_layer.height//2), glow_layer)

    bounce_offset = 0
    if use_bounce:
        bounce_offset = int(abs(math.sin(math.radians(angle_deg * 2))) * 8)

    paste_x = center - (working_img.width // 2)
    paste_y = center - (working_img.height // 2) - bounce_offset
    canvas.paste(working_img, (paste_x, paste_y), working_img)

    return canvas

def compile_spritesheet(frames, layout_mode, grid_cols=4):
    num_frames = len(frames)
    if num_frames == 0:
        return Image.new("RGBA", (64, 64), (0,0,0,0)), 1, 1
        
    max_w = max(f.width for f in frames)
    max_h = max(f.height for f in frames)
    
    if layout_mode == "Horizontal Only (1 Baris Saja)":
        cols, rows = num_frames, 1
    elif layout_mode == "Vertical Only (1 Kolom Saja)":
        cols, rows = 1, num_frames
    else:
        cols = grid_cols
        rows = math.ceil(num_frames / cols)
        
    sheet = Image.new("RGBA", (max_w * cols, max_h * rows), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        if layout_mode == "Horizontal Only (1 Baris Saja)":
            r, c = 0, idx
        elif layout_mode == "Vertical Only (1 Kolom Saja)":
            r, c = idx, 0
        else:
            r, c = idx // cols, idx % cols
            
        cell_x = (c * max_w) + (max_w - frame.width) // 2
        cell_y = (r * max_h) + (max_h - frame.height) // 2
        sheet.paste(frame, (cell_x, cell_y), frame)
        
    return sheet, cols, rows

# 7. SIDEBAR CONTROLS
st.sidebar.markdown("### 📁 1. Upload Gambar PNG 2D")
uploaded_file = st.sidebar.file_uploader("Pilih file PNG transparan:", type=["png"])

if uploaded_file is not None:
    src_img = Image.open(uploaded_file).convert("RGBA")
    
    # --- FITUR BARU: AUTO-PALETTE SWAPPER ---
    st.sidebar.markdown("---")
    col_hp, col_rp = st.sidebar.columns([3, 1])
    col_hp.markdown("### 🎨 Auto-Palette Swapper")
    col_rp.button("Reset", key="btn_reset_v3", on_click=reset_v3_features)
    
    st.session_state.palette_mode = st.sidebar.selectbox(
        "Pilih Varian Warna / Elemen:",
        [
            "Normal (Asli)",
            "🔥 Fire / Lava (Merah-Oranye)",
            "❄️ Ice / Frost (Biru Es)",
            "🟢 Toxic / Poison (Hijau Slime)",
            "💀 Shadow / Dark (Ungu Gelap)",
            "🪙 Golden / Treasure (Emas)"
        ],
        key="pal_mode_val"
    )

    # --- FITUR 1: ROTASI ---
    st.sidebar.markdown("---")
    col_h1, col_r1 = st.sidebar.columns([3, 1])
    col_h1.markdown("### 🔄 Mode & Rotasi")
    col_r1.button("Reset", key="btn_reset_rot", on_click=reset_rotation)
    
    st.session_state.use_rotation_y = st.sidebar.checkbox("Aktifkan Animasi Putar", value=st.session_state.use_rotation_y)
    if st.session_state.use_rotation_y:
        st.session_state.rotation_mode = st.sidebar.radio(
            "Pilih Mode Rotasi:",
            ["2D 360° Rotasi Datar (Flat Spin)", "3D 360° Rotasi Spasial (Volume Spin)"],
            key="rot_mode_val"
        )
        st.session_state.rot_dir = st.sidebar.radio("Arah Putaran:", ["➡️ Searah Jarum Jam (Clockwise)", "⬅️ Berlawanan Jarum Jam (Counter-Clockwise)"], key="rot_dir_val")
        st.session_state.start_angle = st.sidebar.slider("Sudut Awal (°):", 0, 360, st.session_state.start_angle, 15)
        st.session_state.total_sweep = st.sidebar.slider("Total Rentang Putaran (°):", 90, 360, st.session_state.total_sweep, 45)

    st.session_state.total_frames = st.sidebar.slider("Jumlah Frame Animasi:", 4, 36, st.session_state.total_frames, 2)
    
    # --- FITUR BARU: FRAME REVERSER & PING-PONG LOOP ---
    st.session_state.loop_mode = st.sidebar.selectbox(
        "Pola Urutan Loop Frame:",
        ["Maju Normal (Forward)", "Mundur (Reverse)", "Ping-Pong (Maju lalu Memantur Mundur)"],
        key="loop_mode_val"
    )
    
    st.session_state.anim_fps = st.sidebar.slider("Preview Kecepatan (FPS):", 2, 30, st.session_state.anim_fps, 1)

    # --- FITUR 2: VOXEL DEPTH ---
    st.sidebar.markdown("---")
    col_h2, col_r2 = st.sidebar.columns([3, 1])
    col_h2.markdown("### 🧱 Voxel Depth")
    col_r2.button("Reset", key="btn_reset_voxel", on_click=reset_voxel)
    
    st.session_state.use_voxel_depth = st.sidebar.checkbox("Aktifkan Ketebalan Voxel (Hanya Mode 3D)", value=st.session_state.use_voxel_depth)
    if st.session_state.use_voxel_depth:
        st.session_state.voxel_thickness = st.sidebar.slider("Ketebalan Voxel:", 1, 30, st.session_state.voxel_thickness, 1)

    # --- FITUR 3: KEMIRINGAN SUMBU X, Y, Z ---
    st.sidebar.markdown("---")
    col_h3, col_r3 = st.sidebar.columns([3, 1])
    col_h3.markdown("### 📐 Kemiringan Sumbu X, Y, Z")
    col_r3.button("Reset", key="btn_reset_tilts", on_click=reset_tilts)
    
    st.session_state.use_axis_tilts = st.sidebar.checkbox("Aktifkan Kemiringan Sumbu X, Y, Z", value=st.session_state.use_axis_tilts)
    if st.session_state.use_axis_tilts:
        st.session_state.tilt_x_deg = st.sidebar.slider("Sudut Sumbu X (Pitch):", -90, 90, st.session_state.tilt_x_deg, 5)
        st.session_state.tilt_y_deg = st.sidebar.slider("Sudut Sumbu Y (Yaw):", -90, 90, st.session_state.tilt_y_deg, 5)
        st.session_state.tilt_z_deg = st.sidebar.slider("Sudut Sumbu Z (Roll):", -180, 180, st.session_state.tilt_z_deg, 5)

    # --- FITUR BARU: PARTICLE TRAIL GENERATOR ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ✨ Particle Trail Generator")
    st.session_state.use_trail = st.sidebar.checkbox("Aktifkan Jejak Partikel (Trail)", value=st.session_state.use_trail)
    if st.session_state.use_trail:
        st.session_state.trail_color = st.sidebar.color_picker("Warna Partikel Trail:", st.session_state.trail_color)
        st.session_state.trail_count = st.sidebar.slider("Jumlah Titik Partikel:", 2, 25, st.session_state.trail_count, 1)

    # --- FITUR 4: SPECIAL FX & LAYOUT ---
    st.sidebar.markdown("---")
    col_h5, col_r5 = st.sidebar.columns([3, 1])
    col_h5.markdown("### 🖼️ Layout & Skala")
    col_r5.button("Reset", key="btn_reset_gen", on_click=reset_general)
    
    st.session_state.use_bounce = st.sidebar.checkbox("Aktifkan Jelly Bounce", value=st.session_state.use_bounce)
    st.session_state.use_glow = st.sidebar.checkbox("Aktifkan Efek Glow", value=st.session_state.use_glow)
    st.session_state.scale_factor = st.sidebar.slider("Skala Ukuran Objek:", 0.5, 3.0, st.session_state.scale_factor, 0.1)
    st.session_state.sheet_layout_option = st.sidebar.selectbox("Layout Sprite Sheet:", ["Horizontal Only (1 Baris Saja)", "Vertical Only (1 Kolom Saja)", "Grid Custom (Multi Kolom/Baris)"], key="layout_opt")
    if st.session_state.sheet_layout_option == "Grid Custom (Multi Kolom/Baris)":
        st.session_state.grid_cols = st.sidebar.slider("Jumlah Kolom Grid:", 2, 8, st.session_state.grid_cols, 1)

    # Preview gambar asli
    col_prev1, col_prev2 = st.columns([1, 2])
    with col_prev1:
        st.markdown("##### Gambar Asli (2D)")
        st.image(src_img, use_container_width=True)

    # Canvas size
    canvas_res = max(128, int(max(src_img.width, src_img.height) * st.session_state.scale_factor * 2.5))
    canvas_res = min(512, canvas_res)

    # Render Frames Dasar
    raw_frames = []
    dir_multiplier = 1 if "Searah" in st.session_state.rot_dir else -1
    effective_frames = st.session_state.total_frames

    for i in range(effective_frames):
        progress = i / float(max(1, effective_frames - 1)) if effective_frames > 1 else 0
        current_angle = st.session_state.start_angle + (progress * st.session_state.total_sweep * dir_multiplier)
        
        frame = render_frame(
            src_img, current_angle, st.session_state.tilt_x_deg, st.session_state.tilt_y_deg, st.session_state.tilt_z_deg, 
            st.session_state.scale_factor, canvas_res,
            st.session_state.use_rotation_y, st.session_state.rotation_mode, 
            st.session_state.use_voxel_depth, st.session_state.voxel_thickness,
            st.session_state.use_axis_tilts, st.session_state.use_bounce, st.session_state.use_glow,
            st.session_state.palette_mode, st.session_state.use_trail, st.session_state.trail_color, st.session_state.trail_count
        )
        raw_frames.append(frame)

    # FITUR BARU: FRAME REVERSER & PING-PONG LOOP LOGIC
    if st.session_state.loop_mode == "Mundur (Reverse)":
        frames_3d = raw_frames[::-1]
    elif st.session_state.loop_mode == "Ping-Pong (Maju lalu Memantur Mundur)":
        # Maju ditambah mundur (tanpa duplikat frame ujung)
        frames_3d = raw_frames + raw_frames[-2:0:-1]
    else:
        frames_3d = raw_frames

    with col_prev2:
        st.markdown(f"##### Live Preview ({len(frames_3d)} Frames - Loop)")
        gif_io = io.BytesIO()
        frames_3d[0].save(
            gif_io, format="GIF", save_all=True, append_images=frames_3d[1:],
            duration=int(1000/st.session_state.anim_fps), loop=0, disposal=2
        )
        gif_bytes = gif_io.getvalue()
        st.image(gif_bytes, use_container_width=True)
        st.download_button("💾 Download GIF Preview (.gif)", data=gif_bytes, file_name="sprite_ultimate_animation.gif", mime="image/gif", use_container_width=True)

    st.markdown("---")
    st.markdown(f"### 🖼️ Hasil Sprite Sheet ({st.session_state.sheet_layout_option})")
    
    sprite_sheet, f_cols, f_rows = compile_spritesheet(frames_3d, st.session_state.sheet_layout_option, st.session_state.grid_cols)
    st.image(sprite_sheet, caption=f"Sprite Sheet Layout ({f_cols} Kolom x {f_rows} Baris - Resolusi: {sprite_sheet.width}x{sprite_sheet.height} px)", use_container_width=False)

    sheet_io = io.BytesIO()
    sprite_sheet.save(sheet_io, format="PNG")
    sheet_bytes = sheet_io.getvalue()

    st.download_button(
        "💾 Download Sprite Sheet (.png)", 
        data=sheet_bytes, 
        file_name="sprite_sheet_ultimate.png", 
        mime="image/png", 
        use_container_width=True
    )

    # ZIP Exporter
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
        file_name="Ultimate_SpriteSheet_Package.zip", 
        mime="application/zip", 
        use_container_width=True
    )

else:
    st.info("👈 Silakan unggah file PNG transparan di panel kiri untuk mulai menggunakan Ultimate Sprite Studio v3.0!")
