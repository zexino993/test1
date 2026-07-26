import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io
import math
import random
import zipfile

st.set_page_config(page_title="Terraria Weapon Master Studio v7.0", layout="wide")

st.title("🗡️ Terraria Weapon Master Studio v7.0 (Pro Particle Engine)")
st.caption("Studio Modder Terraria: Temporal Particle Trailing Engine, Live GIF Previewer, Custom Rotation, & Full Exporter!")

# ==========================================
# 1. HELPER & ADVANCED PARTICLE ENGINE
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

def render_player_arm(canvas_size):
    arm = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(arm)
    center = canvas_size // 2
    draw.rectangle([center - 6, center + 4, center + 6, center + 18], fill=(198, 134, 100, 160)) # Skin
    draw.rectangle([center - 7, center + 12, center + 7, center + 22], fill=(80, 100, 180, 160)) # Shirt
    return arm

def generate_procedural_slash_effect(canvas_size, style_type, current_angle, arc_span, arc_radius_ratio, glow_color, intensity):
    layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    center = canvas_size // 2
    
    radius = int(canvas_size * arc_radius_ratio)
    bbox = [center - radius, center - radius, center + radius, center + radius]
    
    start_deg = -current_angle - (arc_span / 2.0)
    end_deg = -current_angle + (arc_span / 2.0)
    
    c_hex = glow_color.lstrip('#')
    r_c, g_c, b_c = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
    
    if style_type == "✨ Smooth Energy Arc":
        for i in range(3):
            w = int((6 + i * 4) * intensity)
            alpha = int((140 - i * 35) * min(1.0, intensity))
            draw.arc(bbox, start=start_deg, end=end_deg, fill=(r_c, g_c, b_c, alpha), width=max(1, w))
        draw.arc(bbox, start=start_deg, end=end_deg, fill=(255, 255, 255, int(220 * min(1.0, intensity))), width=max(2, int(3 * intensity)))
        glow = layer.filter(ImageFilter.GaussianBlur(radius=3))
        return Image.alpha_composite(glow, layer)

    elif style_type == "🔥 Flame Wave":
        for i in range(5):
            r_offset = radius + (i * 3)
            bb = [center - r_offset, center - r_offset, center + r_offset, center + r_offset]
            alpha = int((180 - i * 30) * min(1.0, intensity))
            draw.arc(bb, start=start_deg, end=end_deg, fill=(min(255, r_c + i*20), max(0, g_c - i*30), b_c, alpha), width=int(4 * intensity))
        glow = layer.filter(ImageFilter.GaussianBlur(radius=2))
        return Image.alpha_composite(glow, layer)

    elif style_type == "❄️ Ice Crescent":
        draw.arc(bbox, start=start_deg, end=end_deg, fill=(r_c, g_c, b_c, int(200 * min(1.0, intensity))), width=int(10 * intensity))
        draw.arc(bbox, start=start_deg + 10, end=end_deg - 10, fill=(255, 255, 255, 255), width=int(4 * intensity))
        return layer

    else:
        draw.arc(bbox, start=start_deg, end=end_deg, fill=(r_c, g_c, b_c, int(255 * min(1.0, intensity))), width=int(3 * intensity))
        draw.arc(bbox, start=start_deg, end=end_deg, fill=(255, 255, 255, 255), width=1)
        return layer

def render_advanced_dust_particles(canvas_size, base_rot_angle, swing_arc_range, p_style, p_count, p_color, p_seed, frame_idx, total_frames, arc_radius_ratio):
    """Sistem Partikel Lanjutan dengan Jejak Waktu (Temporal Trailing & Fade)."""
    layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    center = canvas_size // 2
    
    c_hex = p_color.lstrip('#')
    r_c, g_c, b_c = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
    
    base_radius = canvas_size * arc_radius_ratio
    swing_progress = frame_idx / float(max(1, total_frames - 1))
    half_range = swing_arc_range / 2.0

    random.seed(p_seed)
    
    for i in range(p_count):
        birth_progress = random.uniform(0.0, 1.0)
        
        # Hanya tampilkan partikel yang sudah terlahir di timeline swing
        if swing_progress >= birth_progress:
            age = (swing_progress - birth_progress) # Rentang umur (0.0 - 1.0)
            
            # Hitung sudut lahir di sepanjang ayunan
            angle_at_birth = (half_range - birth_progress * swing_arc_range) + base_rot_angle
            spawn_rad = math.radians(-angle_at_birth)
            
            # Sebaran posisi lahir
            r_scatter = random.uniform(-6, 6)
            spawn_x = center + (base_radius + r_scatter) * math.cos(spawn_rad)
            spawn_y = center + (base_radius + r_scatter) * math.sin(spawn_rad)
            
            drift_x = random.uniform(-4, 4) * age * 10
            
            # 1. 🔥 FIRE EMBERS (Melayang ke atas & berubah warna)
            if p_style == "🔥 Fire Embers":
                drift_y = -random.uniform(5, 12) * age * 12
                p_r = max(1, int((1.0 - age * 0.7) * random.uniform(2, 5)))
                alpha = int(max(0, (1.0 - age) * 255))
                draw.ellipse(
                    [spawn_x + drift_x - p_r, spawn_y + drift_y - p_r, spawn_x + drift_x + p_r, spawn_y + drift_y + p_r], 
                    fill=(255, int(max(0, 200 - age * 200)), 0, alpha)
                )

            # 2. ✨ MAGIC SPARKLES (Bintang 4 sudut khas Terraria)
            elif p_style == "✨ Magic Sparkles":
                drift_y = random.uniform(-3, 3) * age * 8
                p_r = max(1, int((1.0 - age * 0.5) * random.uniform(2, 4)))
                alpha = int(max(0, (1.0 - age) * 255))
                px, py = spawn_x + drift_x, spawn_y + drift_y
                draw.line([(px - p_r * 2, py), (px + p_r * 2, py)], fill=(r_c, g_c, b_c, alpha), width=1)
                draw.line([(px, py - p_r * 2), (px, py + p_r * 2)], fill=(r_c, g_c, b_c, alpha), width=1)
                draw.rectangle([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255, alpha))

            # 3. ⚡ ELECTRIC SPARKS (Garis menyambar)
            elif p_style == "⚡ Electric Sparks":
                drift_y = random.uniform(-6, 6) * age * 8
                alpha = int(max(0, (1.0 - age * 1.2) * 255))
                px, py = spawn_x + drift_x, spawn_y + drift_y
                dx1, dy1 = random.randint(-4, 4), random.randint(-4, 4)
                dx2, dy2 = dx1 + random.randint(-4, 4), dy1 + random.randint(-4, 4)
                draw.line([(px, py), (px + dx1, py + dy1), (px + dx2, py + dy2)], fill=(r_c, g_c, 255, alpha), width=1)

            # 4. ❄️ ICE CRYSTALS (Kristal belah ketupat jatuh)
            elif p_style == "❄️ Ice Crystals":
                drift_y = random.uniform(2, 8) * age * 8
                p_r = max(1, int((1.0 - age * 0.4) * random.uniform(2, 4)))
                alpha = int(max(0, (1.0 - age) * 240))
                px, py = spawn_x + drift_x, spawn_y + drift_y
                draw.polygon([(px, py - p_r), (px + p_r, py), (px, py + p_r), (px - p_r, py)], fill=(200, 240, 255, alpha))

            # 5. 🟢 TOXIC SLIME BUBBLES (Gelembung menetes)
            else:
                drift_y = random.uniform(3, 10) * age * 10
                p_r = max(1, int((1.0 - age * 0.3) * random.uniform(2, 5)))
                alpha = int(max(0, (1.0 - age) * 220))
                px, py = spawn_x + drift_x, spawn_y + drift_y
                draw.ellipse([px - p_r, py - p_r, px + p_r, py + p_r], outline=(50, 255, 100, alpha), width=1)
                draw.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(150, 255, 150, alpha))

    glow = layer.filter(ImageFilter.GaussianBlur(radius=2))
    return Image.alpha_composite(glow, layer)

def overlay_custom_effect_image(effect_img, angle, eff_extra_rot, flip_h, flip_v, distance_offset, scale_val, opacity_val, canvas_size):
    canvas_center = canvas_size // 2
    proc_eff = effect_img.copy()
    if flip_h: proc_eff = proc_eff.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_v: proc_eff = proc_eff.transpose(Image.FLIP_TOP_BOTTOM)
    
    new_w = max(1, int(proc_eff.width * scale_val))
    new_h = max(1, int(proc_eff.height * scale_val))
    resized_effect = proc_eff.resize((new_w, new_h), resample=Image.NEAREST)
    
    if opacity_val < 1.0:
        eff_np = np.array(resized_effect).copy()
        eff_np[:, :, 3] = (eff_np[:, :, 3] * opacity_val).astype(np.uint8)
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
                            slash_style, glow_color, arc_intensity, arc_span, arc_rad_ratio, 
                            p_style, p_count, p_color, enable_dust,
                            custom_effect_img, eff_extra_rot, eff_flip_h, eff_flip_v, eff_offset, eff_scale, eff_opacity, show_arm):
    frame = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    canvas_center = canvas_size // 2

    if show_arm:
        frame = Image.alpha_composite(frame, render_player_arm(canvas_size))

    half_range = swing_arc_range / 2.0
    if w_type == "⚔️ Broadsword / Sword":
        angle = np.linspace(half_range, -half_range, total_frames)[frame_idx] + base_rot_angle
    elif w_type == "🌙 Scythe / Axe (360° Spin)":
        angle = (frame_idx / float(total_frames)) * 360 + base_rot_angle
    elif w_type == "🪀 Yoyo Spin":
        angle = (frame_idx / float(total_frames)) * 180 + base_rot_angle
    else: # Spear
        angle = base_rot_angle

    # 1. Overlay Custom PNG Effect
    if custom_effect_img is not None:
        eff_layer = overlay_custom_effect_image(
            custom_effect_img, angle, eff_extra_rot, eff_flip_h, eff_flip_v, 
            eff_offset, eff_scale, eff_opacity, canvas_size
        )
        frame = Image.alpha_composite(frame, eff_layer)

    # 2. Overlay Procedural Slash Effect
    if arc_intensity > 0 and w_type != "🔱 Spear / Polearm":
        span = 360 if "Scythe" in w_type else arc_span
        proc_arc = generate_procedural_slash_effect(canvas_size, slash_style, angle, span, arc_rad_ratio, glow_color, arc_intensity)
        frame = Image.alpha_composite(frame, proc_arc)

    # 3. Overlay Advanced Dust Particles (Temporal Engine)
    if enable_dust and w_type != "🔱 Spear / Polearm":
        dust_layer = render_advanced_dust_particles(
            canvas_size, base_rot_angle, swing_arc_range, p_style, p_count, p_color, 
            p_seed=42, frame_idx=frame_idx, total_frames=total_frames, arc_radius_ratio=arc_rad_ratio
        )
        frame = Image.alpha_composite(frame, dust_layer)

    # 4. Render Main Weapon
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
    else: # Vertical Strip
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
        else: # Vertical Strip
            r = idx
            c = 0
            
        pos_x = padding_px + c * (frame_size + padding_px)
        pos_y = padding_px + r * (frame_size + padding_px)
        sheet.paste(frame, (pos_x, pos_y))

    return sheet, cols, rows

# ==========================================
# 2. SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("📁 1. Input Sprite Senjata")
uploaded_file = st.sidebar.file_uploader("Upload PNG Senjata Utama:", type=["png"])

st.sidebar.markdown("---")
st.sidebar.header("✨ 2. Custom Image Swing Effect (Opsional)")
uploaded_effect = st.sidebar.file_uploader("Upload PNG Efek External:", type=["png"])

if uploaded_effect is not None:
    custom_eff_img = Image.open(uploaded_effect).convert("RGBA")
    st.sidebar.markdown("**Transformasi & Rotasi Efek Custom:**")
    eff_rot_extra = st.sidebar.slider("Rotasi Ekstra Efek (°):", -180, 180, 0)
    col_f1, col_f2 = st.sidebar.columns(2)
    eff_flip_h = col_f1.checkbox("Flip Horizontal", value=False)
    eff_flip_v = col_f2.checkbox("Flip Vertikal", value=False)
    eff_scale_val = st.sidebar.slider("Skala Efek Custom:", 0.2, 3.0, 1.0, 0.1)
    eff_dist_offset = st.sidebar.slider("Offset Jarak Efek:", -50, 80, 15, 1)
    eff_opacity_val = st.sidebar.slider("Transparansi (Opacity):", 0.1, 1.0, 0.9, 0.05)
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
    st.sidebar.header("⚙️ 3. Tipe Senjata & Pengaturan Rotasi")
    weapon_type = st.sidebar.selectbox("Kategori Senjata:", ["⚔️ Broadsword / Sword", "🔱 Spear / Polearm", "🌙 Scythe / Axe (360° Spin)", "🪀 Yoyo Spin"])
    base_angle_val = st.sidebar.slider("Sudut Rotasi Awal/Base (°):", -180, 180, 45)
    swing_arc_range_val = st.sidebar.slider("Rentang Sudut Ayunan Tebasan (°):", 30, 240, 130, 5)

    st.sidebar.markdown("---")
    st.sidebar.header("📐 4. Grip Pivot Position")
    preset_choice = st.sidebar.radio("Preset Pegangan Cepat:", ["Custom", "🗡️ Dagger/Shortsword", "⚔️ Broadsword", "🔱 Spear"])
    if preset_choice == "🗡️ Dagger/Shortsword": def_x, def_y = 15, 85
    elif preset_choice == "⚔️ Broadsword": def_x, def_y = 25, 75
    elif preset_choice == "🔱 Spear": def_x, def_y = 40, 60
    else: def_x, def_y = 25, 75

    pivot_x_pct = st.sidebar.slider("Grip Posisi X (%):", 0, 100, def_x)
    pivot_y_pct = st.sidebar.slider("Grip Posisi Y (%):", 0, 100, def_y)
    pivot_x_px = int((pivot_x_pct / 100.0) * src_image.width)
    pivot_y_px = int((pivot_y_pct / 100.0) * src_image.height)
    show_dummy_arm = st.sidebar.checkbox("Tampilkan Dummy Arm Karakter", value=True)

    st.sidebar.markdown("---")
    st.sidebar.header("🎨 5. Procedural Slash FX Generator")
    slash_fx_style = st.sidebar.selectbox("Model Efek Tebasan Python:", ["✨ Smooth Energy Arc", "🔥 Flame Wave", "❄️ Ice Crescent", "⚡ Laser Blade Sharp"])
    arc_color = st.sidebar.color_picker("Warna Efek Arc:", "#00FFFF")
    arc_power = st.sidebar.slider("Intensitas Efek Arc:", 0.0, 2.5, 1.2, 0.1)
    arc_span_deg = st.sidebar.slider("Sudut Panjang Busur Arc (°):", 30, 180, 90, 5)
    arc_radius_val = st.sidebar.slider("Jangkauan Radius (% Canvas):", 20, 50, 42, 1) / 100.0

    st.sidebar.markdown("---")
    st.sidebar.header("✨ 6. Pro Particle & Dust Trail Engine")
    enable_dust = st.sidebar.checkbox("Aktifkan Dust Trail FX", value=True)
    particle_style = st.sidebar.selectbox("Model Dust Partikel:", ["✨ Magic Sparkles", "🔥 Fire Embers", "❄️ Ice Crystals", "⚡ Electric Sparks", "🟢 Toxic Slime Bubbles"])
    particle_count = st.sidebar.slider("Kepadatan Dust Partikel:", 5, 50, 25)
    particle_color = st.sidebar.color_picker("Warna Dust Partikel:", "#00FFFF")

    st.sidebar.markdown("---")
    st.sidebar.header("🖼️ 7. Pengaturan Layout Sprite Sheet")
    sheet_orientation = st.sidebar.selectbox("Arah Susunan (Orientasi Layout):", ["Horizontal Grid (Kiri ke Kanan)", "Vertical Grid (Atas ke Bawah)", "Horizontal Strip (1 Baris Horizontal)", "Vertical Strip (1 Kolom Vertikal)"])
    grid_limit = st.sidebar.slider("Jumlah Kolom/Baris Utama Grid:", 2, 8, 4) if "Grid" in sheet_orientation else 1
    padding_between_frames = st.sidebar.slider("Jarak Antar Frame (Padding Px):", 0, 16, 0)

    st.sidebar.markdown("---")
    st.sidebar.header("🪄 8. Glowmask Generator")
    enable_glowmask = st.sidebar.checkbox("Generate Glowmask", value=False)
    glow_threshold = st.sidebar.slider("Glow Threshold:", 50, 255, 180)

    st.sidebar.markdown("---")
    st.sidebar.header("🎬 9. Frame Export Settings")
    sheet_frames_count = st.sidebar.slider("Jumlah Frame Animasi:", 3, 12, 6)
    frame_canvas_size = st.sidebar.select_slider("Canvas Size per Frame (Px):", options=[64, 80, 96, 128], value=80)
    anim_fps = st.select_slider("Kecepatan Preview Animasi (FPS):", options=[5, 8, 10, 12, 15, 20], value=10)

    # ==========================================
    # 3. MAIN DASHBOARD VIEW
    # ==========================================
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 1. Pivot Inspection & Hitbox")
        pivot_inspect_img = src_image.copy()
        draw_insp = ImageDraw.Draw(pivot_inspect_img)
        cs = 4
        draw_insp.line([(pivot_x_px - cs, pivot_y_px), (pivot_x_px + cs, pivot_y_px)], fill=(255, 0, 0, 255), width=2)
        draw_insp.line([(pivot_x_px, pivot_y_px - cs), (pivot_x_px, pivot_y_px + cs)], fill=(255, 0, 0, 255), width=2)
        st.image(pivot_inspect_img, caption=f"Original Sprite ({src_image.width}x{src_image.height} px)", use_container_width=True)

    with col2:
        st.subheader(f"⚔️ 2. Hasil Rotasi ({base_angle_val}°)")
        rotated_base = rotate_nearest_neighbor(src_image, base_angle_val)
        st.image(rotated_base, caption=f"Ready Sprite {base_angle_val}° ({rotated_base.width}x{rotated_base.height} px)", use_container_width=True)
        
        buf_rot = io.BytesIO()
        rotated_base.save(buf_rot, format="PNG")
        st.download_button(f"💾 Download PNG Senjata ({base_angle_val}°)", data=buf_rot.getvalue(), file_name=f"Terraria_Item_{base_angle_val}deg.png", mime="image/png", use_container_width=True)

    # RENDER ANIMATION FRAMES
    rendered_frames = [
        generate_weapon_frame(
            src_image, weapon_type, idx, sheet_frames_count, 
            base_angle_val, swing_arc_range_val, pivot_x_px, pivot_y_px, frame_canvas_size, 
            slash_fx_style, arc_color, arc_power, 
            arc_span_deg, arc_radius_val, 
            particle_style, particle_count, particle_color, enable_dust,
            custom_eff_img, eff_rot_extra, eff_flip_h, eff_flip_v, eff_dist_offset, eff_scale_val, eff_opacity_val, show_dummy_arm
        )
        for idx in range(sheet_frames_count)
    ]

    # LIVE ANIMATED PREVIEW (GIF PLAYER)
    st.markdown("---")
    col_anim1, col_anim2 = st.columns([1, 1])

    with col_anim1:
        st.subheader("🎬 3. Live Animated Swing Preview")
        
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
        
        st.image(gif_bytes, caption=f"Live Loop Preview ({anim_fps} FPS)", use_container_width=True)
        st.download_button("💾 Download Animated GIF Preview (.gif)", data=gif_bytes, file_name="Terraria_Weapon_Swing_Animation.gif", mime="image/gif", use_container_width=True)

    with col_anim2:
        st.subheader("💻 4. TModLoader C# Code Snippet")
        item_style = "ItemUseStyleID.Swing" if "Sword" in weapon_type or "Scythe" in weapon_type else ("ItemUseStyleID.Thrust" if "Spear" in weapon_type else "ItemUseStyleID.Shoot")
        dust_id_map = {"✨ Magic Sparkles": "DustID.Electric", "🔥 Fire Embers": "DustID.Torch", "❄️ Ice Crystals": "DustID.IceTorch", "⚡ Electric Sparks": "DustID.PurpleTorch", "🟢 Toxic Slime Bubbles": "DustID.Acid"}
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

        // Terraria Melee Dust Trail Effect
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
        st.download_button("💾 Download Script C# (.cs)", data=csharp_code, file_name="CustomWeapon.cs", mime="text/plain", use_container_width=True)

    # GLOWMASK SECTION
    glow_base = None
    if enable_glowmask:
        st.markdown("---")
        st.subheader("🪄 Glowmask Texture (`Item_Glow.png`)")
        col_g1, col_g2 = st.columns([1, 1])
        glow_img = generate_glowmask(src_image, threshold=glow_threshold)
        glow_base = rotate_nearest_neighbor(glow_img, base_angle_val)
        
        with col_g1:
            st.image(glow_base, caption="Glowmask Only (Bagian Menyala)", use_container_width=True)
        with col_g2:
            buf_glow = io.BytesIO()
            glow_base.save(buf_glow, format="PNG")
            st.download_button("💾 Download Glowmask PNG", data=buf_glow.getvalue(), file_name="Terraria_Item_Glow.png", mime="image/png", use_container_width=True)

    # SPRITE SHEET DISPLAY & EXPORT
    st.markdown("---")
    st.subheader("🖼️ 5. Frame Inspection & Custom Layout Sprite Sheet")
    
    cols_ui = st.columns(min(6, len(rendered_frames)))
    for i, frm in enumerate(rendered_frames):
        cols_ui[i % 6].image(frm, caption=f"Frame {i+1}")

    sprite_sheet, final_cols, final_rows = compile_custom_spritesheet(
        rendered_frames, frame_canvas_size, sheet_orientation, grid_limit, padding_between_frames
    )

    st.markdown(f"#### Layout Grid Sprite Sheet ({final_cols} Kolom x {final_rows} Baris):")
    st.image(sprite_sheet, caption=f"Sprite Sheet PNG ({sprite_sheet.width}x{sprite_sheet.height} px) - Orientasi: {sheet_orientation}", use_container_width=False)

    buf_sheet = io.BytesIO()
    sprite_sheet.save(buf_sheet, format="PNG")
    st.download_button("💾 Download Sprite Sheet PNG", data=buf_sheet.getvalue(), file_name="Terraria_Weapon_SwingSheet.png", mime="image/png", use_container_width=True)

    # ALL-IN-ONE ZIP PACKAGE EXPORTER
    st.markdown("---")
    st.subheader("📦 6. Export Complete Mod Package (ZIP)")

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
    st.info("👈 Silakan unggah file gambar PNG senjata milikmu di menu sebelah kiri untuk memulai!")
