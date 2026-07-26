import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io
import math
import random
import zipfile

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Terraria Weapon Master Studio v15.1",
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
    <div class="studio-title">🗡️ Terraria Weapon Master Studio Pro v15.1</div>
    <div class="studio-subtitle">Rotatable Particle & Effect Edition: Atur Sudut Putar & Kecepatan Rotasi Partikel/FX secara Dinamis!</div>
</div>
""", unsafe_allow_html=True)

# 4. FIXED PERFECT SYNC FUNCTION (CALLBACK BASED)
def sync_control(key_name, default_val, min_val, max_val, step_val, label_text):
    if key_name not in st.session_state:
        st.session_state[key_name] = default_val

    col_a, col_b = st.sidebar.columns([2, 1])
    
    def update_from_slider():
        st.session_state[key_name] = st.session_state[f"{key_name}_slide"]
        
    def update_from_number():
        st.session_state[key_name] = st.session_state[f"{key_name}_num"]

    col_b.number_input(
        f"{label_text} (#)", min_value=min_val, max_value=max_val, 
        value=st.session_state[key_name], step=step_val, key=f"{key_name}_num", on_change=update_from_number
    )
    
    col_a.slider(
        label_text, min_value=min_val, max_value=max_val, 
        value=st.session_state[key_name], step=step_val, key=f"{key_name}_slide", on_change=update_from_slider
    )
    
    return st.session_state[key_name]

# 5. FADE IN & FADE OUT ALPHA CALCULATOR
def calculate_fade_multiplier(frame_idx, total_frames, fade_in_pct, fade_out_pct):
    progress = frame_idx / float(max(1, total_frames - 1))
    fade_in_threshold = fade_in_pct / 100.0
    fade_out_threshold = 1.0 - (fade_out_pct / 100.0)
    alpha_mult = 1.0
    if fade_in_threshold > 0 and progress < fade_in_threshold:
        alpha_mult *= (progress / fade_in_threshold)
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

def render_rotatable_particle_layer(draw, layer_canvas, canvas_size, weapon_radius, base_rot_angle, swing_arc_range, p_cfg, p_seed, frame_idx, total_frames, fade_mult, trajectory_mode, linear_travel_dist):
    center = canvas_size // 2
    c_hex = p_cfg["color"].lstrip('#')
    r_c, g_c, b_c = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
    
    swing_progress = frame_idx / float(max(1, total_frames - 1))
    random.seed(p_seed)
    
    p_count = p_cfg["count"]
    spin_speed = p_cfg["spin_speed"] # Kecepatan putar partikel
    
    for i in range(p_count):
        birth_progress = random.uniform(0.0, 0.8)
        if swing_progress >= birth_progress:
            age = (swing_progress - birth_progress)
            if age > 1.0:
                continue

            if trajectory_mode == "🌀 Arc Swing (Rotasi Berputar)":
                base_radius = weapon_radius * 0.85
                half_range = swing_arc_range / 2.0
                angle_at_birth = (half_range - birth_progress * swing_arc_range) + base_rot_angle
                spawn_rad = math.radians(-angle_at_birth)
                emit_x = center + base_radius * math.cos(spawn_rad)
                emit_y = center + base_radius * math.sin(spawn_rad)
            else:
                travel_progress = birth_progress * linear_travel_dist
                rad_lin = math.radians(-base_rot_angle)
                emit_x = center + travel_progress * math.cos(rad_lin)
                emit_y = center + travel_progress * math.sin(rad_lin)

            px = emit_x + random.uniform(-10, 10)
            py = emit_y + random.uniform(-10, 10)

            base_alpha = max(0, (1.0 - age) * 255)
            alpha = int(base_alpha * fade_mult)
            p_r = max(1, int((1.0 - age * 0.5) * random.uniform(2, 5)))

            p_style = p_cfg["style"]
            custom_part_img = p_cfg.get("custom_img", None)
            custom_part_scale = p_cfg.get("custom_scale", 1.0)

            # Hitung sudut rotasi partikel dinamis berdasarkan frame & spin speed
            particle_angle = (frame_idx * spin_speed + (i * 30)) % 360

            if p_style == "📁 Custom PNG Particle" and custom_part_img is not None:
                scale_factor = (1.0 - age * 0.3) * custom_part_scale
                w_p = max(1, int(custom_part_img.width * scale_factor))
                h_p = max(1, int(custom_part_img.height * scale_factor))
                resized_p = custom_part_img.resize((w_p, h_p), resample=Image.NEAREST)
                p_np = np.array(resized_p).copy()
                p_np[:, :, 3] = (p_np[:, :, 3] * (alpha / 255.0)).astype(np.uint8)
                resized_p = Image.fromarray(p_np)
                
                # Terapkan Rotasi pada Custom Partikel PNG
                rotated_p = rotate_nearest_neighbor(resized_p, particle_angle)
                layer_canvas.paste(rotated_p, (int(px - rotated_p.width // 2), int(py - rotated_p.height // 2)), rotated_p)
            elif p_style == "🔥 Fire Embers (Api Berputar)":
                # Gambar bentuk api yang ikut berputar
                temp_img = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
                d_temp = ImageDraw.Draw(temp_img)
                d_temp.ellipse([2, 2, 18, 18], fill=(255, int(max(0, 200 - age * 200)), 0, alpha))
                rot_fire = rotate_nearest_neighbor(temp_img, particle_angle)
                layer_canvas.paste(rot_fire, (int(px - 10), int(py - 10)), rot_fire)
            elif p_style == "✨ Magic Sparkles (Bintang Berputar)":
                temp_img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
                d_temp = ImageDraw.Draw(temp_img)
                d_temp.line([(2, 12), (22, 12)], fill=(r_c, g_c, b_c, alpha), width=2)
                d_temp.line([(12, 2), (12, 22)], fill=(r_c, g_c, b_c, alpha), width=2)
                rot_star = rotate_nearest_neighbor(temp_img, particle_angle)
                layer_canvas.paste(rot_star, (int(px - 12), int(py - 12)), rot_star)
            elif p_style == "❄️ Ice Crystals (Es)":
                draw.polygon([(px, py - p_r), (px + p_r, py), (px, py + p_r), (px - p_r, py)], fill=(200, 240, 255, alpha))
            elif p_style == "⚡ Electric Sparks (Listrik)":
                dx1, dy1 = random.randint(-4, 4), random.randint(-4, 4)
                draw.line([(px, py), (px + dx1, py + dy1)], fill=(r_c, g_c, 255, alpha), width=1)
            elif p_style == "🟢 Toxic Slime (Racun)":
                draw.ellipse([px - p_r, py - p_r, px + p_r, py + p_r], outline=(50, 255, 100, alpha), width=1)
            elif p_style == "🌸 Cherry Blossoms (Kelopak)":
                draw.ellipse([px - p_r, py - p_r, px + p_r, py + p_r], fill=(255, 182, 193, alpha))
            elif p_style == "🌌 Cosmic Nebulae (Kosmik)":
                draw.ellipse([px - p_r*2, py - p_r*2, px + p_r*2, py + p_r*2], fill=(138, 43, 226, int(alpha*0.5)))
            elif p_style == "🩸 Blood Spatters (Darah)":
                draw.ellipse([px - p_r, py - p_r, px + p_r, py + p_r], fill=(178, 34, 34, alpha))
            elif p_style == "🪙 Golden Shimmers (Emas)":
                draw.polygon([(px, py - p_r), (px + p_r, py), (px, py + p_r), (px - p_r, py)], fill=(255, 223, 0, alpha))
            elif p_style == "💨 Wind Gusts (Angin)":
                draw.arc([px - 5, py - 5, px + 5, py + 5], start=0, end=180, fill=(240, 248, 255, alpha), width=1)
            else: 
                draw.polygon([(px - 2, py), (px, py - 2), (px + 2, py), (px, py + 3)], fill=(255, 105, 180, alpha))

def render_multi_particle_engine(canvas_size, weapon_radius, base_rot_angle, swing_arc_range, particle_layers, frame_idx, total_frames, fade_mult, trajectory_mode, linear_travel_dist):
    master_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    for idx, p_cfg in enumerate(particle_layers):
        if not p_cfg.get("enabled", True):
            continue
        layer_canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer_canvas)
        render_rotatable_particle_layer(
            draw=draw, layer_canvas=layer_canvas, canvas_size=canvas_size,
            weapon_radius=weapon_radius, base_rot_angle=base_rot_angle, swing_arc_range=swing_arc_range,
            p_cfg=p_cfg, p_seed=42 + idx * 99, frame_idx=frame_idx, total_frames=total_frames, fade_mult=fade_mult,
            trajectory_mode=trajectory_mode, linear_travel_dist=linear_travel_dist
        )
        glow = layer_canvas.filter(ImageFilter.GaussianBlur(radius=2))
        combined = Image.alpha_composite(glow, layer_canvas)
        master_layer = Image.alpha_composite(master_layer, combined)
    return master_layer

def overlay_custom_effect_image(effect_img, angle, eff_extra_rot, flip_h, flip_v, distance_offset, scale_val, opacity_val, canvas_size, fade_mult, frame_idx):
    canvas_center = canvas_size // 2
    proc_eff = effect_img.copy()
    if flip_h: proc_eff = proc_eff.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_v: proc_eff = proc_eff.transpose(Image.FLIP_TOP_BOTTOM)
    
    new_w = max(1, int(proc_eff.width * scale_val))
    new_h = max(1, int(proc_eff.height * scale_val))
    resized_effect = proc_eff.resize((new_w, new_h), resample=Image.NEAREST)
    final_opacity = max(0.0, min(1.0, opacity_val * fade_mult))
    eff_np = np.array(resized_effect).copy()
    eff_np[:, :, 3] = (eff_np[:, :, 3] * final_opacity).astype(np.uint8)
    resized_effect = Image.fromarray(eff_np)
    
    # Efek gambar tambahan bisa diatur berputar otomatis seiring frame animasi berjalan jika diinginkan
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
                            particle_layers, enable_dust,
                            custom_effect_img, eff_extra_rot, eff_flip_h, eff_flip_v, eff_offset, eff_scale, eff_opacity,
                            fade_in_pct, fade_out_pct, weapon_radius, render_mode,
                            trajectory_mode, linear_travel_dist):
    frame = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    canvas_center = canvas_size // 2
    fade_mult = calculate_fade_multiplier(frame_idx, total_frames, fade_in_pct, fade_out_pct)

    if trajectory_mode == "🌀 Arc Swing (Rotasi Berputar)":
        half_range = swing_arc_range / 2.0
        if w_type == "⚔️ Broadsword / Sword":
            angle = np.linspace(half_range, -half_range, total_frames)[frame_idx] + base_rot_angle
        elif w_type == "🌙 Scythe / Axe (360° Spin)":
            angle = (frame_idx / float(total_frames)) * 360 + base_rot_angle
        elif w_type == "🪀 Yoyo Spin":
            angle = (frame_idx / float(total_frames)) * 180 + base_rot_angle
        else:
            angle = base_rot_angle
    else:
        angle = base_rot_angle

    if custom_effect_img is not None and render_mode in ["🌟 Full Weapon + FX", "✨ FX & Particles Only"]:
        eff_layer = overlay_custom_effect_image(
            custom_effect_img, angle, eff_extra_rot, eff_flip_h, eff_flip_v, 
            eff_offset, eff_scale, eff_opacity, canvas_size, fade_mult, frame_idx
        )
        frame = Image.alpha_composite(frame, eff_layer)

    if enable_dust and w_type != "🔱 Spear / Polearm" and render_mode in ["🌟 Full Weapon + FX", "✨ FX & Particles Only"]:
        dust_layer = render_multi_particle_engine(
            canvas_size, weapon_radius, base_rot_angle, swing_arc_range, 
            particle_layers, frame_idx, total_frames, fade_mult,
            trajectory_mode, linear_travel_dist
        )
        frame = Image.alpha_composite(frame, dust_layer)

    if render_mode in ["🌟 Full Weapon + FX", "🗡️ Weapon Only"] and weapon_img is not None:
        if trajectory_mode == "➡️ Straight Line / Projectile (Garis Lurus)":
            progress = frame_idx / float(max(1, total_frames - 1))
            current_dist = progress * linear_travel_dist
            rad = math.radians(-base_rot_angle)
            off_x = int(current_dist * math.cos(rad))
            off_y = int(current_dist * math.sin(rad))
            rotated = rotate_nearest_neighbor(weapon_img, base_rot_angle)
            paste_x = canvas_center - (rotated.width // 2) + off_x
            paste_y = canvas_center - (rotated.height // 2) + off_y
            frame.paste(rotated, (paste_x, paste_y), rotated)
        else:
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
# 7. GLOBAL SAFE DEFAULTS FOR CUSTOM EFFECT
# ==========================================
custom_effect_img = None
eff_extra_rot = 0
eff_flip_h = False
eff_flip_v = False
eff_offset = 0
eff_scale = 1.0
eff_opacity = 1.0

# ==========================================
# 8. SIDEBAR CONTROLS
# ==========================================
st.sidebar.markdown("### 🎬 1. Mode Output & Render Switcher")
render_mode_choice = st.sidebar.radio(
    "Pilih Objek Yang Ingin Dirender:",
    ["🌟 Full Weapon + FX", "✨ FX & Particles Only", "🗡️ Weapon Only"],
    index=1 # Default ke FX & Particles Only agar fokus ke efek/api
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📁 2. Sprite Input (Opsional)")
uploaded_file = st.sidebar.file_uploader("Upload File Senjata / Projectile PNG (Opsional jika ingin FX saja):", type=["png"])

st.sidebar.markdown("---")
st.sidebar.markdown("### ✨ 3. Custom Image FX (Opsional)")
uploaded_effect = st.sidebar.file_uploader("Upload Efek External PNG:", type=["png"])

if uploaded_effect is not None:
    custom_effect_img = Image.open(uploaded_effect).convert("RGBA")
    st.sidebar.markdown("**Transformasi Efek Custom:**")
    eff_extra_rot = sync_control("eff_extra_rot", 0, -180, 180, 1, "Rotasi Ekstra Efek")
    col_f1, col_f2 = st.sidebar.columns(2)
    eff_flip_h = col_f1.checkbox("Flip H", value=False)
    eff_flip_v = col_f2.checkbox("Flip V", value=False)
    eff_scale = st.sidebar.slider("Skala Efek:", 0.2, 3.0, 1.0, 0.1)
    eff_offset = sync_control("eff_offset", 15, -50, 80, 1, "Offset Jarak Efek")
    eff_opacity = st.sidebar.slider("Transparansi:", 0.1, 1.0, 0.9, 0.05)

# Tentukan ukuran dummy atau asli gambar
if uploaded_file is not None:
    src_image = Image.open(uploaded_file).convert("RGBA")
else:
    # Buat dummy transparan ukuran 64x64 jika user hanya ingin merender partikel/efek saja tanpa senjata
    src_image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ 4. Lintasan Gerak & Rotasi (Trajectory Mode)")
trajectory_mode = st.sidebar.radio(
    "Pilih Jenis Lintasan Animasi:",
    ["🌀 Arc Swing (Rotasi Berputar)", "➡️ Straight Line / Projectile (Garis Lurus)"]
)

weapon_type = st.sidebar.selectbox("Kategori Pergerakan:", ["⚔️ Broadsword / Sword", "🔱 Spear / Polearm", "🌙 Scythe / Axe (360° Spin)", "🪀 Yoyo Spin"])
base_angle_val = sync_control("base_angle", 45, -180, 180, 1, "Sudut Arah Hadap / Rotasi (°)")

if trajectory_mode == "🌀 Arc Swing (Rotasi Berputar)":
    swing_arc_range_val = sync_control("swing_arc_range", 130, 30, 240, 5, "Rentang Sudut Putar (°)")
    linear_travel_dist = 0
else:
    swing_arc_range_val = 0
    linear_travel_dist = sync_control("linear_travel_dist", 100, 10, 400, 10, "Jarak Tempuh Garis Lurus (Px)")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 5. Smooth Fade In & Fade Out Engine")
fade_in_pct_val = sync_control("fade_in_pct", 20, 0, 50, 5, "Fade In Ratio (%)")
fade_out_pct_val = sync_control("fade_out_pct", 25, 0, 50, 5, "Fade Out Ratio (%)")

# Hitung radius
pivot_x_px, pivot_y_px = src_image.width // 2, src_image.height // 2
corners = [(0, 0), (src_image.width, 0), (0, src_image.height), (src_image.width, src_image.height)]
weapon_radius = max(math.hypot(cx - pivot_x_px, cy - pivot_y_px) for cx, cy in corners)

# ==========================================
# 9. ROTATABLE PARTICLE ENGINE (UP TO 3 LAYERS)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.markdown("### ✨ 6. Rotatable Particle Engine")
enable_dust = st.sidebar.checkbox("Aktifkan Partikel / Api FX", value=True)

num_particle_layers = st.sidebar.radio(
    "Berapa Banyak Layer Partikel?",
    [1, 2, 3],
    index=0,
    format_func=lambda x: f"{x} Layer Partikel"
)

particle_options = [
    "📁 Custom PNG Particle",
    "🔥 Fire Embers (Api Berputar)", "✨ Magic Sparkles (Bintang Berputar)", "❄️ Ice Crystals (Es)", "⚡ Electric Sparks (Listrik)",
    "🟢 Toxic Slime (Racun)", "🌸 Cherry Blossoms (Kelopak)", "🌌 Cosmic Nebulae (Kosmik)", "🩸 Blood Spatters (Darah)",
    "🪙 Golden Shimmers (Emas)", "💨 Wind Gusts (Angin)"
]

particle_layers_config = []
for l_idx in range(num_particle_layers):
    st.sidebar.markdown(f"#### 🎨 Partikel Layer #{l_idx + 1}")
    p_style = st.sidebar.selectbox(f"Model Partikel L{l_idx + 1}:", particle_options, key=f"p_style_{l_idx}")
    
    c_img = None
    c_scale = 1.0
    if p_style == "📁 Custom PNG Particle":
        up_p_file = st.sidebar.file_uploader(f"Upload PNG Partikel L{l_idx + 1}:", type=["png"], key=f"up_p_{l_idx}")
        if up_p_file is not None:
            c_img = Image.open(up_p_file).convert("RGBA")
        c_scale = st.sidebar.slider(f"Skala PNG L{l_idx + 1}:", 0.1, 2.0, 0.5, 0.05, key=f"p_scale_{l_idx}")

    p_count = sync_control(f"p_cnt_{l_idx}", 20 if l_idx == 0 else 15, 5, 60, 1, f"Jumlah Partikel L{l_idx + 1}")
    spin_speed = sync_control(f"spin_spd_{l_idx}", 15, 0, 90, 5, f"Kecepatan Rotasi/Putar L{l_idx + 1} (°/frame)")
    default_colors = ["#FF4500", "#00FFFF", "#FFD700"]
    p_clr = st.sidebar.color_picker(f"Warna Tint L{l_idx + 1}:", default_colors[l_idx % 3], key=f"p_clr_{l_idx}")

    particle_layers_config.append({
        "enabled": True,
        "style": p_style,
        "count": p_count,
        "spin_speed": spin_speed,
        "color": p_clr,
        "custom_img": c_img,
        "custom_scale": c_scale
    })

st.sidebar.markdown("---")
st.sidebar.markdown("### 🖼️ 7. Sprite Sheet Layout")
sheet_orientation = st.sidebar.selectbox(
    "Arah Layout Grid:", 
    ["Horizontal Grid (Kiri ke Kanan)", "Vertical Grid (Atas ke Bawah)", "Horizontal Strip (1 Baris Horizontal)", "Vertical Strip (1 Kolom Vertikal)"],
    index=3
)
grid_limit = sync_control("grid_limit", 4, 2, 8, 1, "Jumlah Kolom/Baris Grid") if "Grid" in sheet_orientation else 1
padding_between_frames = sync_control("padding_frames", 0, 0, 16, 1, "Padding Antar Frame (Px)")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎬 8. Export & Preview Settings")

safe_canvas_size = max(128, int((weapon_radius * 2) + linear_travel_dist + 60))
safe_canvas_size = min(1024, safe_canvas_size)

sheet_frames_count = sync_control("sheet_frames", 6, 3, 16, 1, "Jumlah Frame Animasi")
frame_canvas_size = sync_control("frame_canvas_size", safe_canvas_size, 64, 1024, 8, "Resolusi Canvas (Px)")
anim_fps = sync_control("anim_fps", 10, 5, 30, 1, "Frame Rate Preview (FPS)")

# ==========================================
# 10. MAIN STUDIO DASHBOARD VIEW
# ==========================================
col_v1, col_v2 = st.columns([1, 1])

with col_v1:
    st.subheader(f"🔥 Live Preview Animasi ({render_mode_choice})")

    # RENDER ANIMATION FRAMES
    rendered_frames = [
        generate_weapon_frame(
            src_image if uploaded_file is not None else None, weapon_type, idx, sheet_frames_count, 
            base_angle_val, swing_arc_range_val, pivot_x_px, pivot_y_px, frame_canvas_size, 
            particle_layers_config, enable_dust,
            custom_effect_img, eff_extra_rot, eff_flip_h, eff_flip_v, eff_offset, eff_scale, eff_opacity,
            fade_in_pct_val, fade_out_pct_val, weapon_radius,
            render_mode_choice, trajectory_mode, linear_travel_dist
        )
        for idx in range(sheet_frames_count)
    ]

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
    
    st.image(gif_bytes, caption=f"Rotatable Particle Loop Preview ({render_mode_choice})", use_container_width=True)
    st.download_button("💾 Download GIF Preview (.gif)", data=gif_bytes, file_name=f"Terraria_Rotatable_FX.gif", mime="image/gif", use_container_width=True)

with col_v2:
    st.subheader("🖼️ Sprite Sheet Export")
    
    sprite_sheet, final_cols, final_rows = compile_custom_spritesheet(
        rendered_frames, frame_canvas_size, sheet_orientation, grid_limit, padding_between_frames
    )

    st.image(sprite_sheet, caption=f"Sprite Sheet PNG ({sprite_sheet.width}x{sprite_sheet.height} px)", use_container_width=True)

    buf_sheet = io.BytesIO()
    sprite_sheet.save(buf_sheet, format="PNG")
    st.download_button(
        "💾 Download Sprite Sheet PNG", 
        data=buf_sheet.getvalue(), 
        file_name="Terraria_Rotatable_FX_Sheet.png", 
        mime="image/png", 
        use_container_width=True
    )

# ZIP EXPORTER SECTION
st.markdown("---")
st.markdown("### 📦 Export Complete Mod Package (.ZIP)")

zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
    zip_file.writestr("Effect_Sheet.png", buf_sheet.getvalue())
    zip_file.writestr("Effect_Animation.gif", gif_bytes)

st.download_button("📦 Download Complete Package (.ZIP)", data=zip_buffer.getvalue(), file_name="Terraria_Rotatable_FX_Package.zip", mime="application/zip", use_container_width=True)
