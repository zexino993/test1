import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io
import math
import random
import zipfile

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Terraria Weapon Master Studio v9.2",
    page_icon="🗡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CUSTOM PREMIUM CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0d0b18 0%, #161224 50%, #0a0813 100%);
        color: #e2e8f0;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .studio-header {
        background: linear-gradient(90deg, rgba(138, 43, 226, 0.15) 0%, rgba(0, 255, 255, 0.15) 100%);
        border: 1px solid rgba(212, 165, 255, 0.2);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .studio-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a5b4fc, #c084fc, #38bdf8);
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
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3) !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(168, 85, 247, 0.6) !important;
        filter: brightness(1.1) !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #090712 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 28px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. HEADER
st.markdown("""
<div class="studio-header">
    <div class="studio-title">🗡️ Terraria Weapon Master Studio Pro v9.2</div>
    <div class="studio-subtitle">Studio Modding Terraria Pro: Smooth Fade-In/Out Engine, Sync Controls, 25+ Model Dust Particles, Clean GIF Player, & Mod Exporter.</div>
</div>
""", unsafe_allow_html=True)

# 4. HELPER SYNC FUNCTION
def sync_control(key_name, default_val, min_val, max_val, step_val, label_text):
    if key_name not in st.session_state:
        st.session_state[key_name] = default_val

    col_a, col_b = st.sidebar.columns([2, 1])
    
    val_num = col_b.number_input(
        f"{label_text} (#)", min_value=min_val, max_value=max_val, 
        value=st.session_state[key_name], step=step_val, key=f"{key_name}_num"
    )
    st.session_state[key_name] = val_num
    
    val_slide = col_a.slider(
        label_text, min_value=min_val, max_value=max_val, 
        value=st.session_state[key_name], step=step_val, key=f"{key_name}_slide"
    )
    st.session_state[key_name] = val_slide
    return st.session_state[key_name]

# 5. FADE IN & FADE OUT ALPHA CALCULATOR
def calculate_fade_multiplier(frame_idx, total_frames, fade_in_pct, fade_out_pct):
    """Menghitung pengali transparansi (0.0 hingga 1.0) berdasarkan kurva Fade In & Fade Out."""
    progress = frame_idx / float(max(1, total_frames - 1))
    
    fade_in_threshold = fade_in_pct / 100.0
    fade_out_threshold = 1.0 - (fade_out_pct / 100.0)
    
    alpha_mult = 1.0
    
    # Process Fade In
    if fade_in_threshold > 0 and progress < fade_in_threshold:
        alpha_mult *= (progress / fade_in_threshold)
        
    # Process Fade Out
    if fade_out_threshold < 1.0 and progress > fade_out_threshold:
        fade_out_progress = (1.0 - progress) / (1.0 - fade_out_threshold)
        alpha_mult *= max(0.0, fade_out_progress)
        
    return min(1.0, max(0.0, alpha_mult))

# ==========================================
# 6. CORE ENGINE FUNCTIONS
# ==========================================
def rotate_nearest_neighbor(image, angle):
    return image.rotate(angle, resample=Image.NEAREST, expand=True)

def generate_glowmask(image, threshold=200):
    img_np = np.array(image).copy()
    rgb = img_np[:, :, :3].astype(np.float32)
    luminance = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    mask = luminance < threshold
    img_np[mask, 3] = 0
    return Image.fromarray(img_np)

def render_advanced_dust_particles(canvas_size, base_rot_angle, swing_arc_range, p_style, p_count, p_color, p_seed, frame_idx, total_frames, fade_mult):
    layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    center = canvas_size // 2
    
    c_hex = p_color.lstrip('#')
    r_c, g_c, b_c = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
    
    base_radius = canvas_size * 0.42
    swing_progress = frame_idx / float(max(1, total_frames - 1))
    half_range = swing_arc_range / 2.0

    random.seed(p_seed)
    
    for i in range(p_count):
        birth_progress = random.uniform(0.0, 1.0)
        if swing_progress >= birth_progress:
            age = (swing_progress - birth_progress)
            angle_at_birth = (half_range - birth_progress * swing_arc_range) + base_rot_angle
            spawn_rad = math.radians(-angle_at_birth)
            
            r_scatter = random.uniform(-6, 6)
            spawn_x = center + (base_radius + r_scatter) * math.cos(spawn_rad)
            spawn_y = center + (base_radius + r_scatter) * math.sin(spawn_rad)
            drift_x = random.uniform(-4, 4) * age * 10
            
            base_alpha = max(0, (1.0 - age) * 255)
            alpha = int(base_alpha * fade_mult) # Terapkan Smooth Fade
            
            p_r = max(1, int((1.0 - age * 0.5) * random.uniform(2, 4)))
            px, py = spawn_x + drift_x, spawn_y + (-random.uniform(2, 8) * age * 10)

            if p_style == "🔥 Fire Embers":
                draw.ellipse([px - p_r, py - p_r, px + p_r, py + p_r], fill=(255, int(max(0, 200 - age * 200)), 0, alpha))
            elif p_style == "✨ Magic Sparkles":
                draw.line([(px - p_r * 2, py), (px + p_r * 2, py)], fill=(r_c, g_c, b_c, alpha), width=1)
                draw.line([(px, py - p_r * 2), (px, py + p_r * 2)], fill=(r_c, g_c, b_c, alpha), width=1)
                draw.rectangle([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255, alpha))
            elif p_style == "❄️ Ice Crystals":
                draw.polygon([(px, py - p_r), (px + p_r, py), (px, py + p_r), (px - p_r, py)], fill=(200, 240, 255, alpha))
            elif p_style == "⚡ Electric Sparks":
                dx1, dy1 = random.randint(-4, 4), random.randint(-4, 4)
                draw.line([(px, py), (px + dx1, py + dy1)], fill=(r_c, g_c, 255, alpha), width=1)
            elif p_style == "🟢 Toxic Slime Bubbles":
                draw.ellipse([px - p_r, py - p_r, px + p_r, py + p_r], outline=(50, 255, 100, alpha), width=1)
            elif p_style == "🌸 Cherry Blossoms":
                draw.ellipse([px - p_r, py - p_r, px + p_r, py + p_r], fill=(255, 182, 193, alpha))
            elif p_style == "🌌 Cosmic Nebulae":
                draw.ellipse([px - p_r*2, py - p_r*2, px + p_r*2, py + p_r*2], fill=(138, 43, 226, int(alpha*0.5)))
            elif p_style == "🌋 Lava Sparks":
                draw.rectangle([px - 1, py - 1, px + 1, py + 1], fill=(255, 68, 0, alpha))
            elif p_style == "💥 Explosion Cinders":
                draw.polygon([(px, py - p_r), (px + p_r, py), (px, py + p_r)], fill=(255, 140, 0, alpha))
            elif p_style == "☀️ Solar Flares":
                draw.ellipse([px - p_r*1.5, py - p_r*1.5, px + p_r*1.5, py + p_r*1.5], fill=(255, 215, 0, alpha))
            elif p_style == "🍃 Forest Leaves":
                draw.polygon([(px - p_r, py), (px, py - p_r*2), (px + p_r, py), (px, py + p_r)], fill=(34, 139, 34, alpha))
            elif p_style == "💧 Water Drops":
                draw.ellipse([px - 1, py - p_r*1.5, px + 1, py + p_r*1.5], fill=(30, 144, 255, alpha))
            elif p_style == "🌟 Starlight Rays":
                draw.line([(px - p_r*3, py), (px + p_r*3, py)], fill=(255, 255, 255, alpha), width=1)
            elif p_style == "🔮 Rune Symbols":
                draw.rectangle([px - p_r, py - p_r, px + p_r, py + p_r], outline=(147, 112, 219, alpha), width=1)
            elif p_style == "🩸 Blood Spatters":
                draw.ellipse([px - p_r, py - p_r, px + p_r, py + p_r], fill=(178, 34, 34, alpha))
            elif p_style == "👾 Cyber Glitch Pixels":
                draw.rectangle([px - 2, py - 1, px + 2, py + 1], fill=(0, 255, 255, alpha))
            elif p_style == "💀 Shadow Smoke":
                draw.ellipse([px - p_r*2, py - p_r*2, px + p_r*2, py + p_r*2], fill=(40, 40, 50, int(alpha*0.4)))
            elif p_style == "🪙 Golden Shimmers":
                draw.polygon([(px, py - p_r), (px + p_r, py), (px, py + p_r), (px - p_r, py)], fill=(255, 223, 0, alpha))
            elif p_style == "🕷️ Venom Drips":
                draw.line([(px, py), (px, py + p_r*2)], fill=(128, 0, 128, alpha), width=2)
            elif p_style == "💨 Wind Gusts":
                draw.arc([px - 5, py - 5, px + 5, py + 5], start=0, end=180, fill=(240, 248, 255, alpha), width=1)
            elif p_style == "⚛️ Quantum Plasma":
                draw.ellipse([px - p_r, py - p_r, px + p_r, py + p_r], fill=(0, 255, 200, alpha))
            elif p_style == "⚡ Void Lightning":
                draw.line([(px, py), (px + 3, py + 3), (px - 2, py + 6)], fill=(138, 43, 226, alpha), width=1)
            elif p_style == "🌧️ Snow Flakes":
                draw.rectangle([px - p_r, py - p_r, px + p_r, py + p_r], fill=(255, 255, 255, alpha))
            elif p_style == "💥 Arcane Orbs":
                draw.ellipse([px - p_r, py - p_r, px + p_r, py + p_r], fill=(218, 112, 214, alpha))
            else: # 💖 Heart Particles
                draw.polygon([(px - 2, py), (px, py - 2), (px + 2, py), (px, py + 3)], fill=(255, 105, 180, alpha))

    glow = layer.filter(ImageFilter.GaussianBlur(radius=2))
    return Image.alpha_composite(glow, layer)

def overlay_custom_effect_image(effect_img, angle, eff_extra_rot, flip_h, flip_v, distance_offset, scale_val, opacity_val, canvas_size, fade_mult):
    canvas_center = canvas_size // 2
    proc_eff = effect_img.copy()
    if flip_h: proc_eff = proc_eff.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_v: proc_eff = proc_eff.transpose(Image.FLIP_TOP_BOTTOM)
    
    new_w = max(1, int(proc_eff.width * scale_val))
    new_h = max(1, int(proc_eff.height * scale_val))
    resized_effect = proc_eff.resize((new_w, new_h), resample=Image.NEAREST)
    
    # Smooth Fade Mult
    final_opacity = max(0.0, min(1.0, opacity_val * fade_mult))
    
    eff_np = np.array(resized_effect).copy()
    eff_np[:, :, 3] = (eff_np[:, :, 3] * final_opacity).astype(np.uint8)
    resized_effect = Image.fromarray(eff_np)
        
    total_angle = angle + eff_extra_rot
    rotated_eff = rotate_nearest_neighbor(resized_effect, total_angle)
    
    rad = math.radians(-angle)
    off_x = int(distance_offset * math.cos(rad))
    off_y = int(distance_offset * math.sin(rad))
    
    paste_x = canvas_center - (rotated_eff.width // 2) + off_x
    paste_y = canvas_center - (rotated_eff.height // 2) + off_y
    
    layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    layer.paste(rotated_eff, (paste_x, paste_y), rotated_eff)
    return layer

def generate_weapon_frame(weapon_img, w_type, frame_idx, total_frames, base_rot_angle, swing_arc_range, pivot_x, pivot_y, canvas_size, 
                            p_style, p_count, p_color, enable_dust,
                            custom_effect_img, eff_extra_rot, eff_flip_h, eff_flip_v, eff_offset, eff_scale, eff_opacity,
                            fade_in_pct, fade_out_pct):
    frame = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    canvas_center = canvas_size // 2

    fade_mult = calculate_fade_multiplier(frame_idx, total_frames, fade_in_pct, fade_out_pct)

    half_range = swing_arc_range / 2.0
    if w_type == "⚔️ Broadsword / Sword":
        angle = np.linspace(half_range, -half_range, total_frames)[frame_idx] + base_rot_angle
    elif w_type == "🌙 Scythe / Axe (360° Spin)":
        angle = (frame_idx / float(total_frames)) * 360 + base_rot_angle
    elif w_type == "🪀 Yoyo Spin":
        angle = (frame_idx / float(total_frames)) * 180 + base_rot_angle
    else:
        angle = base_rot_angle

    if custom_effect_img is not None:
        eff_layer = overlay_custom_effect_image(
            custom_effect_img, angle, eff_extra_rot, eff_flip_h, eff_flip_v, 
            eff_offset, eff_scale, eff_opacity, canvas_size, fade_mult
        )
        frame = Image.alpha_composite(frame, eff_layer)

    if enable_dust and w_type != "🔱 Spear / Polearm":
        dust_layer = render_advanced_dust_particles(
            canvas_size, base_rot_angle, swing_arc_range, p_style, p_count, p_color, 
            p_seed=42, frame_idx=frame_idx, total_frames=total_frames, fade_mult=fade_mult
        )
        frame = Image.alpha_composite(frame, dust_layer)

    if w_type == "🔱 Spear / Polearm":
        thrust_dist = np.sin((frame_idx / float(max(1, total_frames - 1))) * math.pi) * (canvas_size * 0.25)
        rotated = rotate_nearest_neighbor(weapon_img, base_rot_angle)
        offset_x = int(thrust_dist * math.cos(math.radians(base_rot_angle)))
        offset_y = int(-thrust_dist * math.sin(math.radians(base_rot_angle)))
        paste_x = canvas_center - (rotated.width // 2) + offset_x
        paste_y = canvas_center - (rotated.height // 2) + offset_y
        frame.paste(rotated, (paste_x, paste_y), rotated)
    else:
        rotated = rotate_nearest_neighbor(weapon_img, angle)
        orig_cx, orig_cy = weapon_img.width / 2.0, weapon_img.height / 2.0
        rad = math.radians(-angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rx = (pivot_x - orig_cx) * cos_a - (pivot_y - orig_cy) * sin_a + (rotated.width / 2.0)
        ry = (pivot_x - orig_cx) * sin_a + (pivot_y - orig_cy) * cos_a + (rotated.height / 2.0)
        
        paste_x, paste_y = int(canvas_center - rx), int(canvas_center - ry)
        
        if w_type == "🪀 Yoyo Spin":
            draw = ImageDraw.Draw(frame)
            draw.line([(0, canvas_size), (canvas_center, canvas_center)], fill=(220, 220, 220, 200), width=1)
            
        frame.paste(rotated, (paste_x, paste_y), rotated)

    return frame

def compile_custom_spritesheet(frames, frame_size, orientation, grid_value, padding_px):
    num_frames = len(frames)
    
    if orientation == "Horizontal Grid (Kiri ke Kanan)":
        cols = grid_value
        rows = math.ceil(num_frames / cols)
    elif orientation == "Vertical Grid (Atas ke Bawah)":
        rows = grid_value
        cols = math.ceil(num_frames / rows)
    elif orientation == "Horizontal Strip (1 Baris Horizontal)":
        cols = num_frames
        rows = 1
    else:
        cols = 1
        rows = num_frames

    total_w = (frame_size + padding_px) * cols + padding_px
    total_h = (frame_size + padding_px) * rows + padding_px
    
    sheet = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))

    for idx, frame in enumerate(frames):
        if orientation == "Horizontal Grid (Kiri ke Kanan)":
            r = idx // cols
            c = idx % cols
        elif orientation == "Vertical Grid (Atas ke Bawah)":
            c = idx // rows
            r = idx % rows
        elif orientation == "Horizontal Strip (1 Baris Horizontal)":
            r = 0
            c = idx
        else:
            r = idx
            c = 0
            
        pos_x = padding_px + c * (frame_size + padding_px)
        pos_y = padding_px + r * (frame_size + padding_px)
        sheet.paste(frame, (pos_x, pos_y))

    return sheet, cols, rows

# ==========================================
# 7. SIDEBAR CONTROLS
# ==========================================
st.sidebar.markdown("### 📁 1. Sprite Input")
uploaded_file = st.sidebar.file_uploader("Upload File Senjata PNG:", type=["png"])

st.sidebar.markdown("---")
st.sidebar.markdown("### ✨ 2. Custom Image FX (Opsional)")
uploaded_effect = st.sidebar.file_uploader("Upload Efek External PNG:", type=["png"])

if uploaded_effect is not None:
    custom_eff_img = Image.open(uploaded_effect).convert("RGBA")
    st.sidebar.markdown("**Transformasi Efek Custom:**")
    eff_rot_extra = sync_control("eff_rot_extra", 0, -180, 180, 1, "Rotasi Ekstra Efek")
    col_f1, col_f2 = st.sidebar.columns(2)
    eff_flip_h = col_f1.checkbox("Flip H", value=False)
    eff_flip_v = col_f2.checkbox("Flip V", value=False)
    eff_scale_val = st.sidebar.slider("Skala Efek:", 0.2, 3.0, 1.0, 0.1)
    eff_dist_offset = sync_control("eff_dist_offset", 15, -50, 80, 1, "Offset Jarak Efek")
    eff_opacity_val = st.sidebar.slider("Transparansi:", 0.1, 1.0, 0.9, 0.05)
else:
    custom_eff_img = None
    eff_rot_extra = 0
    eff_flip_h = False
    eff_flip_v = False
    eff_scale_val = 1.0
    eff_dist_offset = 0
    eff_opacity_val = 1.0

if uploaded_file is not None:
    src_image = Image.open(uploaded_file).convert("RGBA")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ 3. Tipe & Rotasi Senjata")
    weapon_type = st.sidebar.selectbox("Kategori Senjata:", ["⚔️ Broadsword / Sword", "🔱 Spear / Polearm", "🌙 Scythe / Axe (360° Spin)", "🪀 Yoyo Spin"])
    
    base_angle_val = sync_control("base_angle", 45, -180, 180, 1, "Sudut Rotasi Base (°)")
    swing_arc_range_val = sync_control("swing_arc_range", 130, 30, 240, 5, "Rentang Sudut Tebasan (°)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 4. Smooth Fade In & Fade Out Engine")
    fade_in_pct_val = sync_control("fade_in_pct", 20, 0, 50, 5, "Fade In Ratio (%)")
    fade_out_pct_val = sync_control("fade_out_pct", 25, 0, 50, 5, "Fade Out Ratio (%)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 5. Grip Pivot Position")
    preset_choice = st.sidebar.radio("Preset Pegangan Cepat:", ["Custom", "🗡️ Shortsword (15,85)", "⚔️ Broadsword (25,75)", "🔱 Spear (40,60)"])
    if preset_choice == "🗡️ Shortsword (15,85)": def_x, def_y = 15, 85
    elif preset_choice == "⚔️ Broadsword (25,75)": def_x, def_y = 25, 75
    elif preset_choice == "🔱 Spear (40,60)": def_x, def_y = 40, 60
    else: def_x, def_y = st.session_state.get("pivot_x", 25), st.session_state.get("pivot_y", 75)

    pivot_x_pct = sync_control("pivot_x", def_x, 0, 100, 1, "Grip Posisi X (%)")
    pivot_y_pct = sync_control("pivot_y", def_y, 0, 100, 1, "Grip Posisi Y (%)")
    pivot_x_px = int((pivot_x_pct / 100.0) * src_image.width)
    pivot_y_px = int((pivot_y_pct / 100.0) * src_image.height)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ✨ 6. Pro Particle Dust Engine (25 Variations)")
    enable_dust = st.sidebar.checkbox("Aktifkan Dust FX", value=True)
    
    particle_options = [
        "✨ Magic Sparkles", "🔥 Fire Embers", "❄️ Ice Crystals", "⚡ Electric Sparks", "🟢 Toxic Slime Bubbles",
        "🌸 Cherry Blossoms", "🌌 Cosmic Nebulae", "🌋 Lava Sparks", "💥 Explosion Cinders", "☀️ Solar Flares",
        "🍃 Forest Leaves", "💧 Water Drops", "🌟 Starlight Rays", "🔮 Rune Symbols", "🩸 Blood Spatters",
        "👾 Cyber Glitch Pixels", "💀 Shadow Smoke", "🪙 Golden Shimmers", "🕷️ Venom Drips", "💨 Wind Gusts",
        "⚛️ Quantum Plasma", "⚡ Void Lightning", "🌧️ Snow Flakes", "💥 Arcane Orbs", "💖 Heart Particles"
    ]
    particle_style = st.sidebar.selectbox("Model Dust Partikel:", particle_options)
    particle_count = sync_control("particle_count", 25, 5, 80, 1, "Kepadatan Partikel")
    particle_color = st.sidebar.color_picker("Warna Partikel:", "#00FFFF")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🖼️ 7. Sprite Sheet Layout")
    sheet_orientation = st.sidebar.selectbox("Arah Layout Grid:", ["Horizontal Grid (Kiri ke Kanan)", "Vertical Grid (Atas ke Bawah)", "Horizontal Strip (1 Baris Horizontal)", "Vertical Strip (1 Kolom Vertikal)"])
    grid_limit = sync_control("grid_limit", 4, 2, 8, 1, "Jumlah Kolom/Baris Grid") if "Grid" in sheet_orientation else 1
    padding_between_frames = sync_control("padding_frames", 0, 0, 16, 1, "Padding Antar Frame (Px)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🪄 8. Glowmask Generator")
    enable_glowmask = st.sidebar.checkbox("Generate Glowmask", value=False)
    glow_threshold = sync_control("glow_thresh", 180, 50, 255, 5, "Threshold Glow")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎬 9. Export & Preview Settings")
    sheet_frames_count = sync_control("sheet_frames", 6, 3, 16, 1, "Jumlah Frame Animasi")
    frame_canvas_size = st.sidebar.select_slider("Resolusi Canvas (Px):", options=[64, 80, 96, 128], value=80)
    anim_fps = sync_control("anim_fps", 10, 5, 30, 1, "Frame Rate Preview (FPS)")

    # ==========================================
    # 8. MAIN STUDIO DASHBOARD VIEW
    # ==========================================
    col_v1, col_v2, col_v3 = st.columns([1, 1, 1])

    with col_v1:
        st.markdown("##### 🎯 1. Pivot Crosshair Inspector")
        pivot_inspect_img = src_image.copy()
        draw_insp = ImageDraw.Draw(pivot_inspect_img)
        cs = 4
        draw_insp.line([(pivot_x_px - cs, pivot_y_px), (pivot_x_px + cs, pivot_y_px)], fill=(255, 0, 0, 255), width=2)
        draw_insp.line([(pivot_x_px, pivot_y_px - cs), (pivot_x_px, pivot_y_px + cs)], fill=(255, 0, 0, 255), width=2)
        st.image(pivot_inspect_img, caption=f"Original ({src_image.width}x{src_image.height} px)", use_container_width=True)

    with col_v2:
        st.subheader(f"⚔️ 2. Rotasi ({base_angle_val}°)")
        rotated_base = rotate_nearest_neighbor(src_image, base_angle_val)
        st.image(rotated_base, caption=f"Ready Sprite ({rotated_base.width}x{rotated_base.height} px)", use_container_width=True)
        
        buf_rot = io.BytesIO()
        rotated_base.save(buf_rot, format="PNG")
        st.download_button(f"💾 Download PNG ({base_angle_val}°)", data=buf_rot.getvalue(), file_name=f"Terraria_Item_{base_angle_val}deg.png", mime="image/png", use_container_width=True)

    # RENDER ANIMATION FRAMES (WITH SMOOTH FADE)
    rendered_frames = [
        generate_weapon_frame(
            src_image, weapon_type, idx, sheet_frames_count, 
            base_angle_val, swing_arc_range_val, pivot_x_px, pivot_y_px, frame_canvas_size, 
            particle_style, particle_count, particle_color, enable_dust,
            custom_eff_img, eff_rot_extra, eff_flip_h, eff_flip_v, eff_dist_offset, eff_scale_val, eff_opacity_val,
            fade_in_pct_val, fade_out_pct_val
        )
        for idx in range(sheet_frames_count)
    ]

    with col_v3:
        st.subheader("🎬 3. Live GIF Preview")
        gif_bytes_io = io.BytesIO()
        frame_delay = int(1000 / anim_fps)
        rendered_frames[0].save(
            gif_bytes_io, 
            format="GIF", 
            save_all=True, 
            append_images=rendered_frames[1:], 
            duration=frame_delay, 
            loop=0, 
            disposal=2
        )
        gif_bytes = gif_bytes_io.getvalue()
        
        st.image(gif_bytes, caption=f"Smooth Loop Preview ({anim_fps} FPS)", use_container_width=True)
        st.download_button("💾 Download GIF Preview (.gif)", data=gif_bytes, file_name="Terraria_Weapon_Swing_Animation.gif", mime="image/gif", use_container_width=True)

    # C# CODE SNIPPET SECTION
    st.markdown("---")
    st.markdown("### 💻 4. TModLoader C# Code Generator")
    item_style = "ItemUseStyleID.Swing" if "Sword" in weapon_type or "Scythe" in weapon_type else ("ItemUseStyleID.Thrust" if "Spear" in weapon_type else "ItemUseStyleID.Shoot")
    dust_id_map = {
        "✨ Magic Sparkles": "DustID.Electric", "🔥 Fire Embers": "DustID.Torch", "❄️ Ice Crystals": "DustID.IceTorch",
        "⚡ Electric Sparks": "DustID.PurpleTorch", "🟢 Toxic Slime Bubbles": "DustID.Acid", "🌸 Cherry Blossoms": "DustID.PinkFairy",
        "🌌 Cosmic Nebulae": "DustID.Shadowflame", "🌋 Lava Sparks": "DustID.Lava", "💥 Explosion Cinders": "DustID.InfernoFork",
        "☀️ Solar Flares": "DustID.SolarFlare", "🍃 Forest Leaves": "DustID.Grass", "💧 Water Drops": "DustID.Water",
        "🌟 Starlight Rays": "DustID.Starfury", "🔮 Rune Symbols": "DustID.EnchantedNightcrawler", "🩸 Blood Spatters": "DustID.Blood",
        "👾 Cyber Glitch Pixels": "DustID.BlueCrystalShard", "💀 Shadow Smoke": "DustID.Smoke", "🪙 Golden Shimmers": "DustID.GoldFlame",
        "🕷️ Venom Drips": "DustID.Venom", "💨 Wind Gusts": "DustID.Cloud", "⚛️ Quantum Plasma": "DustID.Vortex",
        "⚡ Void Lightning": "DustID.ShadowbeamStaff", "🌧️ Snow Flakes": "DustID.Snow", "💥 Arcane Orbs": "DustID.Nebula",
        "💖 Heart Particles": "DustID.Heart"
    }
    dust_type_str = dust_id_map.get(particle_style, "DustID.Electric")
    
    csharp_code = f"""using Microsoft.Xna.Framework;
using Terraria;
using Terraria.ID;
using Terraria.ModLoader;

namespace YourModName.Items
{{
    public class CustomWeapon : ModItem
    {{
        public override void SetDefaults()
        {{
            Item.width = {rotated_base.width};
            Item.height = {rotated_base.height};
            Item.useStyle = {item_style};
            Item.useAnimation = 20;
            Item.useTime = 20;
            Item.damage = 50;
            Item.knockBack = 6f;
            Item.UseSound = SoundID.Item1;
            Item.autoReuse = true;
            Item.value = Item.buyPrice(gold: 1);
            Item.rare = ItemRarityID.Green;
        }}

        // Terraria Melee Dust Trail Effect ({particle_style})
        public override void MeleeEffects(Player player, Rectangle hitbox)
        {{
            if (Main.rand.NextBool(2))
            {{
                int dust = Dust.NewDust(
                    new Vector2(hitbox.X, hitbox.Y), 
                    hitbox.Width, 
                    hitbox.Height, 
                    {dust_type_str}, 
                    player.velocity.X * 0.2f, 
                    player.velocity.Y * 0.2f, 
                    100, 
                    default(Color), 
                    1.2f
                );
                Main.dust[dust].noGravity = true;
            }}
        }}
    }}
}}"""
    st.code(csharp_code, language="csharp")
    st.download_button("💾 Download Script C# (.cs)", data=csharp_code, file_name="CustomWeapon.cs", mime="text/plain", use_container_width=False)

    # GLOWMASK SECTION
    glow_base = None
    if enable_glowmask:
        st.markdown("---")
        st.markdown("### 🪄 Glowmask Texture (`Item_Glow.png`)")
        col_g1, col_g2 = st.columns([1, 1])
        glow_img = generate_glowmask(src_image, threshold=glow_threshold)
        glow_base = rotate_nearest_neighbor(glow_img, base_angle_val)
        
        with col_g1:
            st.image(glow_base, caption="Glowmask Only (Tekstur Menyala)", use_container_width=True)
        with col_g2:
            buf_glow = io.BytesIO()
            glow_base.save(buf_glow, format="PNG")
            st.download_button("💾 Download Glowmask PNG", data=buf_glow.getvalue(), file_name="Terraria_Item_Glow.png", mime="image/png", use_container_width=True)

    # SPRITE SHEET SECTION
    st.markdown("---")
    st.markdown("### 🖼️ 5. Frame Inspection & Custom Layout Sprite Sheet")
    
    cols_ui = st.columns(min(6, len(rendered_frames)))
    for i, frm in enumerate(rendered_frames):
        cols_ui[i % 6].image(frm, caption=f"Frame {i+1}")

    sprite_sheet, final_cols, final_rows = compile_custom_spritesheet(
        rendered_frames, frame_canvas_size, sheet_orientation, grid_limit, padding_between_frames
    )

    st.markdown(f"#### Grid Layout Sprite Sheet ({final_cols} Kolom x {final_rows} Baris):")
    st.image(sprite_sheet, caption=f"Sprite Sheet PNG ({sprite_sheet.width}x{sprite_sheet.height} px) - Layout: {sheet_orientation}", use_container_width=False)

    buf_sheet = io.BytesIO()
    sprite_sheet.save(buf_sheet, format="PNG")
    st.download_button("💾 Download Sprite Sheet PNG", data=buf_sheet.getvalue(), file_name="Terraria_Weapon_SwingSheet.png", mime="image/png", use_container_width=True)

    # ZIP EXPORTER SECTION
    st.markdown("---")
    st.markdown("### 📦 6. Export Complete Mod Package (.ZIP)")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("CustomWeapon.png", buf_rot.getvalue())
        if glow_base:
            zip_file.writestr("CustomWeapon_Glow.png", buf_glow.getvalue())
        zip_file.writestr("CustomWeapon_SwingSheet.png", buf_sheet.getvalue())
        zip_file.writestr("CustomWeapon_Animation.gif", gif_bytes)
        zip_file.writestr("CustomWeapon.cs", csharp_code)

    st.download_button("📦 Download Complete Mod Package (.ZIP)", data=zip_buffer.getvalue(), file_name="Terraria_Mod_Weapon_Package.zip", mime="application/zip", use_container_width=True)

else:
    st.info("👈 Silakan unggah file gambar PNG senjata milikmu di menu sebelah kiri untuk memulai studio!")
