import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io
import math
import random
import zipfile

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Terraria Weapon Master Studio v14.0",
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
    <div class="studio-title">🗡️ Terraria Weapon Master Studio Pro v14.0</div>
    <div class="studio-subtitle">Studio Modding Terraria Pro: Geometry Dash Style Advanced Particle Physics Engine (Gravity, AccelRad, AccelTan, PosVar), Trajectory Modes, & FX Export.</div>
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

def render_gd_particle_layer(draw, layer_canvas, canvas_size, weapon_radius, base_rot_angle, swing_arc_range, p_cfg, p_seed, frame_idx, total_frames, fade_mult, trajectory_mode, linear_travel_dist):
    center = canvas_size // 2
    c_hex = p_cfg["color"].lstrip('#')
    r_c, g_c, b_c = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
    
    swing_progress = frame_idx / float(max(1, total_frames - 1))
    random.seed(p_seed)
    
    max_particles = p_cfg["max_particles"]
    lifetime = p_cfg["lifetime"]
    speed = p_cfg["speed"]
    angle_deg = p_cfg["angle"]
    angle_var = p_cfg["angle_var"]
    pos_var_x = p_cfg["pos_var_x"]
    pos_var_y = p_cfg["pos_var_y"]
    grav_x = p_cfg["gravity_x"]
    grav_y = p_cfg["gravity_y"]
    accel_rad = p_cfg["accel_rad"]
    accel_tan = p_cfg["accel_tan"]

    for i in range(max_particles):
        birth_progress = random.uniform(0.0, 0.8)
        if swing_progress >= birth_progress:
            age_norm = (swing_progress - birth_progress) / max(0.1, lifetime)
            if age_norm > 1.0:
                continue

            # Base emitter position based on trajectory
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

            # Position Variance (PosVar X & Y)
            px = emit_x + random.uniform(-pos_var_x, pos_var_x)
            py = emit_y + random.uniform(-pos_var_y, pos_var_y)

            # Physics calculation with Angle, Speed, Gravity, and Acceleration (GD Style)
            particle_angle = math.radians(angle_deg + random.uniform(-angle_var, angle_var))
            current_speed = speed * (1.0 + age_norm)
            
            # Displacement from physics
            dx = current_speed * math.cos(particle_angle) * (swing_progress - birth_progress) * 5
            dy = current_speed * math.sin(particle_angle) * (swing_progress - birth_progress) * 5
            
            # Gravity and Acceleration influence
            dx += 0.5 * grav_x * (swing_progress - birth_progress)**2 * 50
            dy += 0.5 * grav_y * (swing_progress - birth_progress)**2 * 50

            # Radial & Tangential acceleration
            if accel_rad != 0 or accel_tan != 0:
                vec_x = px - emit_x
                vec_y = py - emit_y
                dist = math.hypot(vec_x, vec_y) + 0.001
                nx, ny = vec_x / dist, vec_y / dist
                tx, ty = -ny, nx
                dx += (nx * accel_rad + tx * accel_tan) * (swing_progress - birth_progress) * 20
                dy += (ny * accel_rad + ty * accel_tan) * (swing_progress - birth_progress) * 20

            final_x = px + dx
            final_y = py + dy

            base_alpha = max(0, (1.0 - age_norm) * 255)
            alpha = int(base_alpha * fade_mult)
            p_r = max(1, int((1.0 - age_norm * 0.5) * random.uniform(2, 5)))

            # Render custom or preset particle
            p_style = p_cfg["style"]
            custom_part_img = p_cfg.get("custom_img", None)
            custom_part_scale = p_cfg.get("custom_scale", 1.0)

            if p_style == "📁 Custom PNG Particle" and custom_part_img is not None:
                scale_factor = (1.0 - age_norm * 0.3) * custom_part_scale
                w_p = max(1, int(custom_part_img.width * scale_factor))
                h_p = max(1, int(custom_part_img.height * scale_factor))
                resized_p = custom_part_img.resize((w_p, h_p), resample=Image.NEAREST)
                p_np = np.array(resized_p).copy()
                p_np[:, :, 3] = (p_np[:, :, 3] * (alpha / 255.0)).astype(np.uint8)
                resized_p = Image.fromarray(p_np)
                rot_deg = random.randint(0, 360)
                rotated_p = rotate_nearest_neighbor(resized_p, rot_deg)
                layer_canvas.paste(rotated_p, (int(final_x - rotated_p.width // 2), int(final_y - rotated_p.height // 2)), rotated_p)
            elif p_style == "🔥 Fire Embers (Api Unggul)":
                draw.ellipse([final_x - p_r, final_y - p_r, final_x + p_r, final_y + p_r], fill=(255, int(max(0, 220 - age_norm * 200)), 20, alpha))
            elif p_style == "✨ Magic Sparkles":
                draw.line([(final_x - p_r * 2, final_y), (final_x + p_r * 2, final_y)], fill=(r_c, g_c, b_c, alpha), width=1)
                draw.line([(final_x, final_y - p_r * 2), (final_x, final_y + p_r * 2)], fill=(r_c, g_c, b_c, alpha), width=1)
                draw.rectangle([final_x - 1, final_y - 1, final_x + 1, final_y + 1], fill=(255, 255, 255, alpha))
            elif p_style == "❄️ Ice Crystals":
                draw.polygon([(final_x, final_y - p_r), (final_x + p_r, final_y), (final_x, final_y + p_r), (final_x - p_r, final_y)], fill=(200, 240, 255, alpha))
            elif p_style == "⚡ Electric Sparks":
                dx1, dy1 = random.randint(-4, 4), random.randint(-4, 4)
                draw.line([(final_x, final_y), (final_x + dx1, final_y + dy1)], fill=(r_c, g_c, 255, alpha), width=1)
            elif p_style == "🟢 Toxic Slime Bubbles":
                draw.ellipse([final_x - p_r, final_y - p_r, final_x + p_r, final_y + p_r], outline=(50, 255, 100, alpha), width=1)
            elif p_style == "🌸 Cherry Blossoms":
                draw.ellipse([final_x - p_r, final_y - p_r, final_x + p_r, final_y + p_r], fill=(255, 182, 193, alpha))
            elif p_style == "🌌 Cosmic Nebulae":
                draw.ellipse([final_x - p_r*2, final_y - p_r*2, final_x + p_r*2, final_y + p_r*2], fill=(138, 43, 226, int(alpha*0.5)))
            elif p_style == "🌋 Lava Sparks":
                draw.rectangle([final_x - 1, final_y - 1, final_x + 1, final_y + 1], fill=(255, 68, 0, alpha))
            elif p_style == "💥 Explosion Cinders":
                draw.polygon([(final_x, final_y - p_r), (final_x + p_r, final_y), (final_x, final_y + p_r)], fill=(255, 140, 0, alpha))
            elif p_style == "☀️ Solar Flares":
                draw.ellipse([final_x - p_r*1.5, final_y - p_r*1.5, final_x + p_r*1.5, final_y + p_r*1.5], fill=(255, 215, 0, alpha))
            elif p_style == "🍃 Forest Leaves":
                draw.polygon([(final_x - p_r, final_y), (final_x, final_y - p_r*2), (final_x + p_r, final_y), (final_x, final_y + p_r)], fill=(34, 139, 34, alpha))
            elif p_style == "💧 Water Drops":
                draw.ellipse([final_x - 1, final_y - p_r*1.5, final_x + 1, final_y + p_r*1.5], fill=(30, 144, 255, alpha))
            elif p_style == "🌟 Starlight Rays":
                draw.line([(final_x - p_r*3, final_y), (final_x + p_r*3, final_y)], fill=(255, 255, 255, alpha), width=1)
            elif p_style == "🔮 Rune Symbols":
                draw.rectangle([final_x - p_r, final_y - p_r, final_x + p_r, final_y + p_r], outline=(147, 112, 219, alpha), width=1)
            elif p_style == "🩸 Blood Spatters":
                draw.ellipse([final_x - p_r, final_y - p_r, final_x + p_r, final_y + p_r], fill=(178, 34, 34, alpha))
            elif p_style == "👾 Cyber Glitch Pixels":
                draw.rectangle([final_x - 2, final_y - 1, final_x + 2, final_y + 1], fill=(0, 255, 255, alpha))
            elif p_style == "💀 Shadow Smoke":
                draw.ellipse([final_x - p_r*2, final_y - p_r*2, final_x + p_r*2, final_y + p_r*2], fill=(40, 40, 50, int(alpha*0.4)))
            elif p_style == "🪙 Golden Shimmers":
                draw.polygon([(final_x, final_y - p_r), (final_x + p_r, final_y), (final_x, final_y + p_r), (final_x - p_r, final_y)], fill=(255, 223, 0, alpha))
            elif p_style == "🕷️ Venom Drips":
                draw.line([(final_x, final_y), (final_x, final_y + p_r*2)], fill=(128, 0, 128, alpha), width=2)
            elif p_style == "💨 Wind Gusts":
                draw.arc([final_x - 5, final_y - 5, final_x + 5, final_y + 5], start=0, end=180, fill=(240, 248, 255, alpha), width=1)
            elif p_style == "⚛️ Quantum Plasma":
                draw.ellipse([final_x - p_r, final_y - p_r, final_x + p_r, final_y + p_r], fill=(0, 255, 200, alpha))
            elif p_style == "⚡ Void Lightning":
                draw.line([(final_x, final_y), (final_x + 3, final_y + 3), (final_x - 2, final_y + 6)], fill=(138, 43, 226, alpha), width=1)
            elif p_style == "🌧️ Snow Flakes":
                draw.rectangle([final_x - p_r, final_y - p_r, final_x + p_r, final_y + p_r], fill=(255, 255, 255, alpha))
            elif p_style == "💥 Arcane Orbs":
                draw.ellipse([final_x - p_r, final_y - p_r, final_x + p_r, final_y + p_r], fill=(218, 112, 214, alpha))
            else: 
                draw.polygon([(final_x - 2, final_y), (final_x, final_y - 2), (final_x + 2, final_y), (final_x, final_y + 3)], fill=(255, 105, 180, alpha))

def render_multi_particle_engine(canvas_size, weapon_radius, base_rot_angle, swing_arc_range, particle_layers, frame_idx, total_frames, fade_mult, trajectory_mode, linear_travel_dist):
    master_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    for idx, p_cfg in enumerate(particle_layers):
        if not p_cfg.get("enabled", True):
            continue
        layer_canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer_canvas)
        render_gd_particle_layer(
            draw=draw, layer_canvas=layer_canvas, canvas_size=canvas_size,
            weapon_radius=weapon_radius, base_rot_angle=base_rot_angle, swing_arc_range=swing_arc_range,
            p_cfg=p_cfg, p_seed=42 + idx * 99, frame_idx=frame_idx, total_frames=total_frames, fade_mult=fade_mult,
            trajectory_mode=trajectory_mode, linear_travel_dist=linear_travel_dist
        )
        glow = layer_canvas.filter(ImageFilter.GaussianBlur(radius=2))
        combined = Image.alpha_composite(glow, layer_canvas)
        master_layer = Image.alpha_composite(master_layer, combined)
    return master_layer

def overlay_custom_effect_image(effect_img, angle, eff_extra_rot, flip_h, flip_v, distance_offset, scale_val, opacity_val, canvas_size, fade_mult):
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
            eff_offset, eff_scale, eff_opacity, canvas_size, fade_mult
        )
        frame = Image.alpha_composite(frame, eff_layer)

    if enable_dust and w_type != "🔱 Spear / Polearm" and render_mode in ["🌟 Full Weapon + FX", "✨ FX & Particles Only"]:
        dust_layer = render_multi_particle_engine(
            canvas_size, weapon_radius, base_rot_angle, swing_arc_range, 
            particle_layers, frame_idx, total_frames, fade_mult,
            trajectory_mode, linear_travel_dist
        )
        frame = Image.alpha_composite(frame, dust_layer)

    if render_mode in ["🌟 Full Weapon + FX", "🗡️ Weapon Only"]:
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
# 7. SIDEBAR CONTROLS
# ==========================================
st.sidebar.markdown("### 🎬 1. Mode Output & Render Switcher")
render_mode_choice = st.sidebar.radio(
    "Pilih Objek Yang Ingin Dirender:",
    ["🌟 Full Weapon + FX", "✨ FX & Particles Only", "🗡️ Weapon Only"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📁 2. Sprite Input")
uploaded_file = st.sidebar.file_uploader("Upload File Senjata / Projectile PNG:", type=["png"])

st.sidebar.markdown("---")
st.sidebar.markdown("### ✨ 3. Custom Image FX (Opsional)")
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
    st.sidebar.markdown("### ⚙️ 4. Lintasan Gerak & Rotasi (Trajectory Mode)")
    trajectory_mode = st.sidebar.radio(
        "Pilih Jenis Lintasan Animasi:",
        ["🌀 Arc Swing (Rotasi Berputar)", "➡️ Straight Line / Projectile (Garis Lurus)"]
    )

    weapon_type = st.sidebar.selectbox("Kategori Senjata/Proyektil:", ["⚔️ Broadsword / Sword", "🔱 Spear / Polearm", "🌙 Scythe / Axe (360° Spin)", "🪀 Yoyo Spin"])
    base_angle_val = sync_control("base_angle", 45, -180, 180, 1, "Sudut Arah Hadap / Rotasi (°)")
    
    if trajectory_mode == "🌀 Arc Swing (Rotasi Berputar)":
        swing_arc_range_val = sync_control("swing_arc_range", 130, 30, 240, 5, "Rentang Sudut Tebasan (°)")
        linear_travel_dist = 0
    else:
        swing_arc_range_val = 0
        linear_travel_dist = sync_control("linear_travel_dist", 100, 10, 400, 10, "Jarak Tempuh Garis Lurus (Px)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 5. Smooth Fade In & Fade Out Engine")
    fade_in_pct_val = sync_control("fade_in_pct", 20, 0, 50, 5, "Fade In Ratio (%)")
    fade_out_pct_val = sync_control("fade_out_pct", 25, 0, 50, 5, "Fade Out Ratio (%)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 6. Grip Pivot Position")
    preset_choice = st.sidebar.radio("Preset Pegangan Cepat:", ["Custom", "🗡️ Shortsword (15,85)", "⚔️ Broadsword (25,75)", "🔱 Spear (40,60)"])
    if preset_choice == "🗡️ Shortsword (15,85)": def_x, def_y = 15, 85
    elif preset_choice == "⚔️ Broadsword (25,75)": def_x, def_y = 25, 75
    elif preset_choice == "🔱 Spear (40,60)": def_x, def_y = 40, 60
    else: def_x, def_y = st.session_state.get("pivot_x", 25), st.session_state.get("pivot_y", 75)

    pivot_x_pct = sync_control("pivot_x", def_x, 0, 100, 1, "Grip Posisi X (%)")
    pivot_y_pct = sync_control("pivot_y", def_y, 0, 100, 1, "Grip Posisi Y (%)")
    pivot_x_px = int((pivot_x_pct / 100.0) * src_image.width)
    pivot_y_px = int((pivot_y_pct / 100.0) * src_image.height)

    corners = [(0, 0), (src_image.width, 0), (0, src_image.height), (src_image.width, src_image.height)]
    weapon_radius = max(math.hypot(cx - pivot_x_px, cy - pivot_y_px) for cx, cy in corners)

    # ==========================================
    # 8. GEOMETRY DASH STYLE ADVANCED PARTICLE EDITOR
    # ==========================================
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔥 7. GD Style Advanced Particle Editor")
    enable_dust = st.sidebar.checkbox("Aktifkan Dust & Particle FX", value=True)
    
    num_particle_layers = st.sidebar.radio(
        "Berapa Banyak Layer Partikel?",
        [1, 2, 3],
        index=0,
        format_func=lambda x: f"{x} Layer Partikel"
    )

    particle_options = [
        "📁 Custom PNG Particle",
        "🔥 Fire Embers (Api Unggul)", "✨ Magic Sparkles", "❄️ Ice Crystals", "⚡ Electric Sparks", "🟢 Toxic Slime Bubbles",
        "🌸 Cherry Blossoms", "🌌 Cosmic Nebulae", "🌋 Lava Sparks", "💥 Explosion Cinders", "☀️ Solar Flares",
        "🍃 Forest Leaves", "💧 Water Drops", "🌟 Starlight Rays", "🔮 Rune Symbols", "🩸 Blood Spatters",
        "👾 Cyber Glitch Pixels", "💀 Shadow Smoke", "🪙 Golden Shimmers", "🕷️ Venom Drips", "💨 Wind Gusts",
        "⚛️ Quantum Plasma", "⚡ Void Lightning", "🌧️ Snow Flakes", "💥 Arcane Orbs", "💖 Heart Particles"
    ]

    particle_layers_config = []
    for l_idx in range(num_particle_layers):
        st.sidebar.markdown(f"#### 🎛️ GD Particle Config #{l_idx + 1}")
        p_style = st.sidebar.selectbox(f"Model Partikel L{l_idx + 1}:", particle_options, key=f"p_style_{l_idx}")
        
        c_img = None
        c_scale = 1.0
        if p_style == "📁 Custom PNG Particle":
            up_p_file = st.sidebar.file_uploader(f"Upload Custom PNG L{l_idx + 1}:", type=["png"], key=f"up_p_{l_idx}")
            if up_p_file is not None:
                c_img = Image.open(up_p_file).convert("RGBA")
            c_scale = st.sidebar.slider(f"Skala PNG L{l_idx + 1}:", 0.1, 2.0, 0.5, 0.05, key=f"p_scale_{l_idx}")

        # GD Parameters Sync Controls
        max_p = sync_control(f"max_p_{l_idx}", 30, 5, 100, 1, f"Max Particles L{l_idx + 1}")
        lifetime = sync_control(f"lifetime_{l_idx}", 100, 10, 500, 10, f"Lifetime L{l_idx + 1}") / 100.0
        speed = sync_control(f"speed_{l_idx}", 30, 0, 150, 5, f"Speed L{l_idx + 1}")
        angle = sync_control(f"angle_{l_idx}", -90, -180, 180, 5, f"Angle L{l_idx + 1}")
        angle_var = sync_control(f"angle_var_{l_idx}", 90, 0, 180, 5, f"Angle Var (±) L{l_idx + 1}")
        pos_var_x = sync_control(f"pos_var_x_{l_idx}", 10, 0, 50, 1, f"PosVar X L{l_idx + 1}")
        pos_var_y = sync_control(f"pos_var_y_{l_idx}", 10, 0, 50, 1, f"PosVar Y L{l_idx + 1}")
        gravity_x = sync_control(f"grav_x_{l_idx}", 0, -50, 50, 1, f"Gravity X L{l_idx + 1}")
        gravity_y = sync_control(f"grav_y_{l_idx}", 0, -50, 50, 1, f"Gravity Y L{l_idx + 1}")
        accel_rad = sync_control(f"accel_rad_{l_idx}", 0, -50, 50, 1, f"AccelRad L{l_idx + 1}")
        accel_tan = sync_control(f"accel_tan_{l_idx}", 0, -50, 50, 1, f"AccelTan L{l_idx + 1}")
        
        default_colors = ["#FF4500", "#00FFFF", "#FFD700"]
        p_clr = st.sidebar.color_picker(f"Warna Tint L{l_idx + 1}:", default_colors[l_idx % 3], key=f"p_clr_{l_idx}")

        particle_layers_config.append({
            "enabled": True,
            "style": p_style,
            "max_particles": max_p,
            "lifetime": lifetime,
            "speed": speed,
            "angle": angle,
            "angle_var": angle_var,
            "pos_var_x": pos_var_x,
            "pos_var_y": pos_var_y,
            "gravity_x": gravity_x,
            "gravity_y": gravity_y,
            "accel_rad": accel_rad,
            "accel_tan": accel_tan,
            "color": p_clr,
            "custom_img": c_img,
            "custom_scale": c_scale
        })

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🖼️ 8. Sprite Sheet Layout")
    sheet_orientation = st.sidebar.selectbox(
        "Arah Layout Grid:", 
        ["Horizontal Grid (Kiri ke Kanan)", "Vertical Grid (Atas ke Bawah)", "Horizontal Strip (1 Baris Horizontal)", "Vertical Strip (1 Kolom Vertikal)"],
        index=3
    )
    grid_limit = sync_control("grid_limit", 4, 2, 8, 1, "Jumlah Kolom/Baris Grid") if "Grid" in sheet_orientation else 1
    padding_between_frames = sync_control("padding_frames", 0, 0, 16, 1, "Padding Antar Frame (Px)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🪄 9. Glowmask Generator")
    enable_glowmask = st.sidebar.checkbox("Generate Glowmask", value=False)
    glow_threshold = sync_control("glow_thresh", 180, 50, 255, 5, "Threshold Glow")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎬 10. Export & Preview Settings")
    
    safe_canvas_size = max(128, int((weapon_radius * 2) + linear_travel_dist + 60))
    safe_canvas_size = min(1024, safe_canvas_size)
    
    sheet_frames_count = sync_control("sheet_frames", 6, 3, 16, 1, "Jumlah Frame Animasi")
    st.sidebar.caption(f"*(Saran Anti-Crop: Auto-Canvas = {safe_canvas_size}px)*")
    frame_canvas_size = sync_control("frame_canvas_size", safe_canvas_size, 64, 1024, 8, "Resolusi Canvas (Px)")
    anim_fps = sync_control("anim_fps", 10, 5, 30, 1, "Frame Rate Preview (FPS)")

    # ==========================================
    # 9. MAIN STUDIO DASHBOARD VIEW
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

    # RENDER ANIMATION FRAMES
    rendered_frames = [
        generate_weapon_frame(
            src_image, weapon_type, idx, sheet_frames_count, 
            base_angle_val, swing_arc_range_val, pivot_x_px, pivot_y_px, frame_canvas_size, 
            particle_layers_config, enable_dust,
            custom_effect_img, eff_rot_extra, eff_flip_h, eff_flip_v, eff_dist_offset, eff_scale_val, eff_opacity_val,
            fade_in_pct_val, fade_out_pct_val, weapon_radius,
            render_mode_choice, trajectory_mode, linear_travel_dist
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
        
        st.image(gif_bytes, caption=f"GD Particle Loop Preview ({render_mode_choice})", use_container_width=True)
        st.download_button("💾 Download GIF Preview (.gif)", data=gif_bytes, file_name=f"Terraria_GD_Particle_{render_mode_choice}.gif", mime="image/gif", use_container_width=True)

    # C# CODE SNIPPET SECTION
    st.markdown("---")
    st.markdown("### 💻 4. TModLoader C# Code Generator")
    item_style = "ItemUseStyleID.Shoot" if trajectory_mode == "➡️ Straight Line / Projectile (Garis Lurus)" else ("ItemUseStyleID.Swing" if "Sword" in weapon_type or "Scythe" in weapon_type else "ItemUseStyleID.Thrust")
    dust_id_map = {
        "📁 Custom PNG Particle": "DustID.Electric",
        "🔥 Fire Embers (Api Unggul)": "DustID.Torch", "✨ Magic Sparkles": "DustID.Electric", "❄️ Ice Crystals": "DustID.IceTorch",
        "⚡ Electric Sparks": "DustID.PurpleTorch", "🟢 Toxic Slime Bubbles": "DustID.Acid", "🌸 Cherry Blossoms": "DustID.PinkFairy",
        "🌌 Cosmic Nebulae": "DustID.Shadowflame", "🌋 Lava Sparks": "DustID.Lava", "💥 Explosion Cinders": "DustID.InfernoFork",
        "☀️ Solar Flares": "DustID.SolarFlare", "🍃 Forest Leaves": "DustID.Grass", "💧 Water Drops": "DustID.Water",
        "🌟 Starlight Rays": "DustID.Starfury", "🔮 Rune Symbols": "DustID.EnchantedNightcrawler", "🩸 Blood Spatters": "DustID.Blood",
        "👾 Cyber Glitch Pixels": "DustID.BlueCrystalShard", "💀 Shadow Smoke": "DustID.Smoke", "🪙 Golden Shimmers": "DustID.GoldFlame",
        "🕷️ Venom Drips": "DustID.Venom", "💨 Wind Gusts": "DustID.Cloud", "⚛️ Quantum Plasma": "DustID.Vortex",
        "⚡ Void Lightning": "DustID.ShadowbeamStaff", "🌧️ Snow Flakes": "DustID.Snow", "💥 Arcane Orbs": "DustID.Nebula",
        "💖 Heart Particles": "DustID.Heart"
    }
    primary_p_style = particle_layers_config[0]["style"]
    dust_type_str = dust_id_map.get(primary_p_style, "DustID.Torch")
    
    csharp_code = f"""using Microsoft.Xna.Framework;
using Terraria;
using Terraria.ID;
using Terraria.ModLoader;

namespace YourModName.Items
{{
    public class CustomGDParticleItem : ModItem
    {{
        public override void SetDefaults()
        {{
            Item.width = {rotated_base.width};
            Item.height = {rotated_base.height};
            Item.useStyle = {item_style};
            Item.useAnimation = 20;
            Item.useTime = 20;
            Item.damage = 50;
            Item.knockBack = 5f;
            Item.UseSound = SoundID.Item20;
            Item.autoReuse = true;
            Item.value = Item.buyPrice(gold: 2);
            Item.rare = ItemRarityID.Orange;
        }}

        public override void MeleeEffects(Player player, Rectangle hitbox)
        {{
            if (Main.rand.NextBool(2))
            {{
                int dust = Dust.NewDust(
                    new Vector2(hitbox.X, hitbox.Y), 
                    hitbox.Width, 
                    hitbox.Height, 
                    {dust_type_str}, 
                    player.velocity.X * 0.3f, 
                    player.velocity.Y * 0.3f, 
                    120, 
                    default(Color), 
                    1.4f
                );
                Main.dust[dust].noGravity = true;
            }}
        }}
    }}
}}"""
    st.code(csharp_code, language="csharp")
    st.download_button("💾 Download Script C# (.cs)", data=csharp_code, file_name="CustomGDParticleItem.cs", mime="text/plain", use_container_width=False)

    # SPRITE SHEET SECTION
    st.markdown("---")
    st.markdown("### 🖼️ 5. Frame Inspection & Custom Layout Sprite Sheet")
    
    cols_ui = st.columns(min(6, len(rendered_frames)))
    for i, frm in enumerate(rendered_frames):
        cols_ui[i % 6].image(frm, caption=f"Frame {i+1}")

    sprite_sheet, final_cols, final_rows = compile_custom_spritesheet(
        rendered_frames, frame_canvas_size, sheet_orientation, grid_limit, padding_between_frames
    )

    st.markdown(f"#### Layout Grid Sprite Sheet ({final_cols} Kolom x {final_rows} Baris) - Mode: {render_mode_choice}:")
    st.image(sprite_sheet, caption=f"Sprite Sheet PNG ({sprite_sheet.width}x{sprite_sheet.height} px)", use_container_width=False)

    buf_sheet = io.BytesIO()
    sprite_sheet.save(buf_sheet, format="PNG")
    st.download_button(
        f"💾 Download Sprite Sheet PNG ({'FX ONLY' if 'FX' in render_mode_choice else 'FULL'})", 
        data=buf_sheet.getvalue(), 
        file_name="Terraria_GD_Particle_Sheet.png", 
        mime="image/png", 
        use_container_width=True
    )

    # ZIP EXPORTER SECTION
    st.markdown("---")
    st.markdown("### 📦 6. Export Complete Mod Package (.ZIP)")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("CustomItem.png", buf_rot.getvalue())
        zip_file.writestr("CustomItem_Sheet.png", buf_sheet.getvalue())
        zip_file.writestr("CustomItem_Animation.gif", gif_bytes)
        zip_file.writestr("CustomGDParticleItem.cs", csharp_code)

    st.download_button("📦 Download Complete Mod Package (.ZIP)", data=zip_buffer.getvalue(), file_name="Terraria_Mod_GD_Particle_Package.zip", mime="application/zip", use_container_width=True)

else:
    st.info("👈 Silakan unggah file gambar PNG senjata atau proyektil milikmu di menu sebelah kiri untuk memulai studio!")
