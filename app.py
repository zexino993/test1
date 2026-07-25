import io
import math
import numpy as np
from PIL import Image
import streamlit as st

# 1. Konfigurasi Halaman Web
st.set_page_config(
    page_title="Terraria Ore Studio Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Title Header
st.title("💎 Terraria Ore Tile & Glow Studio Web (v12.1 Pro)")
st.caption("Studio Lengkap: **Recolor**, **Dual Texture 3D**, **Soft RGB Pastel**, **Quad-Preview**, & **GIF Animation Studio**.")

# 2. Dictionary Presets Warna
PRESETS = {
    'manual': None,
    'pastel_cotton_candy': {'shadow': '#3a1c4d', 'mid': '#f3a6ff', 'glow': '#a3f3ff'},
    'pastel_mint': {'shadow': '#1b3b32', 'mid': '#80e8c6', 'glow': '#d1fff0'},
    'pastel_lavender': {'shadow': '#2a1a4a', 'mid': '#b39ddb', 'glow': '#f3e5f5'},
    'pastel_peach': {'shadow': '#3e1a1a', 'mid': '#ffab91', 'glow': '#ffe0b2'},
    'hellstone': {'shadow': '#1a0000', 'mid': '#e63900', 'glow': '#ffcc00'},
    'chlorophyte': {'shadow': '#0a2000', 'mid': '#2ecc71', 'glow': '#a3ff00'},
    'luminite': {'shadow': '#001f24', 'mid': '#00b894', 'glow': '#81ecec'},
    'cobalt': {'shadow': '#001133', 'mid': '#0984e3', 'glow': '#74b9ff'},
    'orichalcum': {'shadow': '#2d001e', 'mid': '#e84393', 'glow': '#ff7675'},
    'adamantite': {'shadow': '#2b0000', 'mid': '#d63031', 'glow': '#ff7675'},
    'shroomite': {'shadow': '#000a1a', 'mid': '#0055ff', 'glow': '#00e1ff'}
}

# Session State Initialization untuk Presets
if 'shadow_val' not in st.session_state: st.session_state.shadow_val = "#080214"
if 'mid_val' not in st.session_state: st.session_state.mid_val = "#AA19F5"
if 'glow_val' not in st.session_state: st.session_state.glow_val = "#FF78FF"
if 'pastel_mode_val' not in st.session_state: st.session_state.pastel_mode_val = False

def on_preset_change():
    p_key = st.session_state.preset_choice
    if p_key in PRESETS and PRESETS[p_key] is not None:
        st.session_state.shadow_val = PRESETS[p_key]['shadow']
        st.session_state.mid_val = PRESETS[p_key]['mid']
        st.session_state.glow_val = PRESETS[p_key]['glow']
        if 'pastel' in p_key:
            st.session_state.pastel_mode_val = True

# 3. Sidebar Control Setup
st.sidebar.header("📁 1. File & Mode Utama")
uploaded_file = st.sidebar.file_uploader("Upload File PNG Ore Sprite", type=["png"])

use_orig_color = st.sidebar.checkbox("🔒 Gunakan Warna Asli (Matikan Recolor)", value=False)
pastel_mode = st.sidebar.checkbox("🌸 Efek Soft RGB Pastel (Aesthetic)", value=st.session_state.pastel_mode_val, key="pastel_mode_val")
zoom = st.sidebar.slider("🔍 Pixel Magnifier Zoom", 1, 8, 4)

with st.sidebar.expander("🎨 2. Presets & Warna Custom", expanded=True):
    st.selectbox(
        "Pilih Preset Warna / Pastel:",
        options=[
            ('Kustom (Manual)', 'manual'),
            ('🌸 Pastel Cotton Candy', 'pastel_cotton_candy'),
            ('🍵 Pastel Mint Matcha', 'pastel_mint'),
            ('💜 Pastel Soft Lavender', 'pastel_lavender'),
            ('🍑 Pastel Peach Cream', 'pastel_peach'),
            ('🔥 Hellstone (Lava Flame)', 'hellstone'),
            ('🌿 Chlorophyte (Jungle Green)', 'chlorophyte'),
            ('🌌 Luminite (Cosmic Teal)', 'luminite'),
            ('🔷 Cobalt (Deep Blue)', 'cobalt'),
            ('🌸 Orichalcum (Magenta Pink)', 'orichalcum'),
            ('🔴 Adamantite (Crimson Red)', 'adamantite'),
            ('🍄 Shroomite (Glowing Cyan)', 'shroomite')
        ],
        format_func=lambda x: x[0],
        key="preset_choice",
        on_change=on_preset_change
    )
    
    shadow_color = st.color_picker("1. Shadow Celah", st.session_state.shadow_val, key="shadow_picker")
    mid_color = st.color_picker("2. Warna Utama", st.session_state.mid_val, key="mid_picker")
    glow_color = st.color_picker("3. Glow Highlight", st.session_state.glow_val, key="glow_picker")
    
    hue_shift = st.slider("RGB Hue Shift", 0, 360, 0, 5)
    vibrancy = st.slider("Saturasi / Vibrancy", 0.5, 2.0, 1.1, 0.1)

with st.sidebar.expander("🔀 3. Dual Texture Blending Engine", expanded=False):
    TEX_OPTIONS = [
        ('Smooth Klasik (Tanpa Tekstur)', 'smooth'),
        ('💎 Crystal Facets', 'crystal'),
        ('🪨 Stone Grain', 'stone'),
        ('✨ Metallic Sparkle', 'sparkle'),
        ('🌋 Magma / Lava Veins', 'veins'),
        ('🔮 Obsidian Glass Slits', 'obsidian'),
        ('🌿 Organic Moss / Spores', 'moss'),
        ('🌌 Cosmic Swirl', 'cosmic'),
        ('📜 Runic Glyphs', 'runic')
    ]
    
    tex_primary = st.selectbox("Tekstur Utama:", options=TEX_OPTIONS, index=1, format_func=lambda x: x[0])[1]
    
    TEX_SEC_OPTIONS = [('Tidak Ada (Matikan Blend)', 'none')] + TEX_OPTIONS
    tex_secondary = st.selectbox("Tekstur Kedua (Blend):", options=TEX_SEC_OPTIONS, index=3, format_func=lambda x: x[0])[1]
    
    blend_ratio = st.slider("Rasio Blend Tekstur", 0.0, 1.0, 0.3, 0.05)
    tex_intensity = st.slider("Kekuatan Tekstur", 0.0, 1.0, 0.45, 0.05)
    depth_mult = st.slider("Intensitas 3D Depth", 0.5, 3.0, 1.8, 0.1)

with st.sidebar.expander("💡 4. Glowmask & Pulse Settings", expanded=False):
    threshold = st.slider("Sensitivitas Glow Area", 0.1, 0.9, 0.45, 0.02)
    pulse_intensity = st.slider("Kekuatan Denyut Pulse", 0.1, 1.0, 0.5, 0.05)

# 4. Helper Functions
def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def apply_hue_shift(rgb_array, hue_deg):
    if hue_deg == 0: return rgb_array
    img = Image.fromarray(rgb_array.astype(np.uint8), mode='RGB').convert('HSV')
    h, s, v = img.split()
    h_arr = (np.array(h, dtype=np.int16) + int((hue_deg / 360.0) * 255)) % 256
    return np.array(Image.merge('HSV', (Image.fromarray(h_arr.astype(np.uint8)), s, v)).convert('RGB'), dtype=np.float32)

def get_single_texture_map(height, width, tex_type, intensity):
    if tex_type in ['smooth', 'none'] or intensity == 0:
        return np.zeros((height, width), dtype=np.float32)

    y_indices, x_indices = np.indices((height, width))

    if tex_type == 'stone':
        np.random.seed(42)
        grain = np.random.uniform(-0.5, 0.5, (height, width))
        wave = np.sin(x_indices * 0.3) * np.cos(y_indices * 0.3) * 0.3
        tex = (grain + wave) * intensity
    elif tex_type == 'crystal':
        cell_size = 5
        grid_y, grid_x = y_indices // cell_size, x_indices // cell_size
        hash_val = np.sin(grid_y * 12.9898 + grid_x * 78.233) * 43758.5453
        facet_val = (hash_val - np.floor(hash_val)) - 0.5
        edge_y = (y_indices % cell_size == 0).astype(np.float32) * -0.25
        edge_x = (x_indices % cell_size == 0).astype(np.float32) * -0.25
        tex = (facet_val + edge_y + edge_x) * intensity
    elif tex_type == 'sparkle':
        np.random.seed(123)
        raw_noise = np.random.rand(height, width)
        tex = np.where(raw_noise > (1.0 - 0.08 * intensity), 0.8, 0.0)
    elif tex_type == 'veins':
        wave1 = np.sin(x_indices * 0.2 + np.cos(y_indices * 0.15) * 3.0)
        wave2 = np.cos(y_indices * 0.25 + np.sin(x_indices * 0.1) * 2.5)
        vein = np.abs(wave1 + wave2)
        tex = np.where(vein < 0.35, (0.35 - vein) * 2.2, -0.15) * intensity
    elif tex_type == 'obsidian':
        diag = np.sin((x_indices * 0.4 + y_indices * 0.6))
        tex = np.where(diag > 0.3, 0.4, -0.25) * intensity
    elif tex_type == 'moss':
        blob = np.sin(x_indices * 0.18) * np.cos(y_indices * 0.18) + np.sin(x_indices * 0.08 + y_indices * 0.08)
        tex = np.where(blob > 0.3, (blob - 0.3) * 0.9, -0.1) * intensity
    elif tex_type == 'cosmic':
        center_y, center_x = height / 2.0, width / 2.0
        r = np.sqrt((x_indices - center_x)**2 + (y_indices - center_y)**2)
        angle = np.arctan2(y_indices - center_y, x_indices - center_x)
        tex = np.sin(angle * 3.0 + r * 0.2) * 0.5 * intensity
    elif tex_type == 'runic':
        grid_mask = ((x_indices % 4 == 0) | (y_indices % 4 == 0)).astype(np.float32)
        hash_rune = np.sin((x_indices // 4) * 12.9898 + (y_indices // 4) * 78.233) * 43758.5453
        rune_pattern = ((hash_rune - np.floor(hash_rune)) > 0.55).astype(np.float32)
        tex = (grid_mask * rune_pattern * 0.6 - 0.1) * intensity
    else:
        tex = np.zeros((height, width), dtype=np.float32)

    return tex.astype(np.float32)

def render_studio_all(arr, extra_hue=0):
    height, width, _ = arr.shape
    r_chan, g_chan, b_chan, alpha = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    lum = (0.299 * r_chan + 0.587 * g_chan + 0.114 * b_chan) / 255.0

    if use_orig_color:
        main_rgb = np.dstack((r_chan, g_chan, b_chan)).astype(np.float32)
        if (hue_shift + extra_hue) > 0:
            main_rgb = apply_hue_shift(main_rgb, (hue_shift + extra_hue) % 360)
        
        out_img = Image.fromarray(np.dstack((main_rgb.astype(np.uint8), alpha.astype(np.uint8))), mode="RGBA")
        glow_alpha = np.where((lum >= threshold) & (alpha > 0), alpha, 0).astype(np.uint8)
        glow_img = Image.fromarray(np.dstack((main_rgb.astype(np.uint8), glow_alpha)), mode="RGBA")
        return out_img, glow_img, lum, glow_alpha

    tl_lum = np.pad(lum[:-1, :-1], ((1, 0), (1, 0)), mode='edge')
    br_lum = np.pad(lum[1:, 1:], ((0, 1), (0, 1)), mode='edge')
    slope = (lum - br_lum) + (tl_lum - lum)

    depth_lum = np.clip(lum + (slope * 0.35 * depth_mult), 0.0, 1.0)
    
    t1 = get_single_texture_map(height, width, tex_primary, tex_intensity)
    t2 = get_single_texture_map(height, width, tex_secondary, tex_intensity)
    tex_map = t1 if tex_secondary == 'none' else (t1 * (1.0 - blend_ratio) + t2 * blend_ratio)
    
    final_lum = np.clip(depth_lum + tex_map, 0.0, 1.0)

    c_shadow = np.array(hex_to_rgb(shadow_color), dtype=np.float32)
    c_mid = np.array(hex_to_rgb(mid_color), dtype=np.float32)
    c_glow = np.array(hex_to_rgb(glow_color), dtype=np.float32)

    out_rgb = np.zeros((height, width, 3), dtype=np.float32)
    mask_low = final_lum < 0.35
    factor_low = np.expand_dims(np.clip(final_lum / 0.35, 0, 1), axis=-1)
    out_rgb += np.where(np.expand_dims(mask_low, axis=-1), c_shadow + factor_low * (c_mid - c_shadow), 0)

    mask_high = ~mask_low
    factor_high = np.expand_dims(np.clip((final_lum - 0.35) / 0.65, 0, 1), axis=-1)
    out_rgb += np.where(np.expand_dims(mask_high, axis=-1), c_mid + factor_high * (c_glow - c_mid), 0)

    total_hue = (hue_shift + extra_hue) % 360
    if total_hue > 0:
        out_rgb = apply_hue_shift(out_rgb, total_hue)

    gray = np.expand_dims(0.299 * out_rgb[:, :, 0] + 0.587 * out_rgb[:, :, 1] + 0.114 * out_rgb[:, :, 2], axis=-1)
    out_rgb = gray + vibrancy * (out_rgb - gray)

    if pastel_mode:
        out_rgb = out_rgb * 0.6 + 255.0 * 0.4 * (out_rgb / 255.0)**0.5

    out_rgb = np.clip(out_rgb, 0, 255).astype(np.uint8)
    alpha_uint8 = alpha.astype(np.uint8)

    out_img = Image.fromarray(np.dstack((out_rgb, alpha_uint8)), mode="RGBA")
    glow_alpha = np.where((final_lum >= threshold) & (alpha_uint8 > 0), alpha_uint8, 0).astype(np.uint8)
    glow_img = Image.fromarray(np.dstack((out_rgb, glow_alpha)), mode="RGBA")

    return out_img, glow_img, final_lum, glow_alpha

# 5. Main Render Dashboard
if uploaded_file is not None:
    orig_img = Image.open(uploaded_file).convert("RGBA")
    arr = np.array(orig_img, dtype=np.float32)

    out_img, glow_img, lum_map, glow_alpha = render_studio_all(arr)
    rgb_shift_img, _, _, _ = render_studio_all(arr, extra_hue=120)

    w, h = orig_img.size
    orig_z = orig_img.resize((w * zoom, h * zoom), Image.NEAREST)
    out_z = out_img.resize((w * zoom, h * zoom), Image.NEAREST)
    glow_z = glow_img.resize((w * zoom, h * zoom), Image.NEAREST)
    rgb_z = rgb_shift_img.resize((w * zoom, h * zoom), Image.NEAREST)

    st.subheader("🖼️ Quad-Preview Matrix (Zoom Magnifier)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.caption("1. Sprite Asli")
        st.image(orig_z, use_container_width=True)
    with col2:
        st.caption("2. Tile Recolor/Pastel")
        st.image(out_z, use_container_width=True)
    with col3:
        st.caption("3. Glowmask Isolated")
        st.image(glow_z, use_container_width=True)
    with col4:
        st.caption("4. RGB Shift Preview")
        st.image(rgb_z, use_container_width=True)

    # Download PNG Section
    st.divider()
    st.subheader("💾 Download File PNG Gambar")
    col_d1, col_d2 = st.columns(2)
    
    buf_main = io.BytesIO()
    out_img.save(buf_main, format="PNG")
    col_d1.download_button("💾 Download Main Tile PNG", data=buf_main.getvalue(), file_name="TerrariaTile_Main.png", mime="image/png", use_container_width=True)

    buf_glow = io.BytesIO()
    glow_img.save(buf_glow, format="PNG")
    col_d2.download_button("💡 Download Glowmask PNG", data=buf_glow.getvalue(), file_name="TerrariaTile_Glow.png", mime="image/png", use_container_width=True)

    # GIF Studio Section
    st.divider()
    st.subheader("🎬 Studio GIF Animasi (Preview Dulu, Download Kemudian)")
    
    gif_col1, gif_col2 = st.columns(2)
    
    with gif_col1:
        st.write("**1. Animasi Glow Pulse**")
        if st.button("Preview GIF Glow Pulse 🎬", key="btn_pulse_prev", use_container_width=True):
            base_rgb = np.array(out_img, dtype=np.float32)[:, :, :3]
            alpha_arr = np.array(out_img)[:, :, 3:]
            glow_mask_norm = np.expand_dims((glow_alpha.astype(np.float32) / 255.0), axis=-1)

            frames = []
            for i in range(10):
                pulse_factor = (math.sin(2 * math.pi * i / 10) + 1.0) * 0.5 * pulse_intensity
                boosted_rgb = base_rgb + (base_rgb * 0.6 + 60.0) * glow_mask_norm * pulse_factor
                boosted_rgb = np.clip(boosted_rgb, 0, 255).astype(np.uint8)
                
                f_img = Image.fromarray(np.dstack((boosted_rgb, alpha_arr.astype(np.uint8))), mode="RGBA")
                if zoom > 1: f_img = f_img.resize((w * zoom, h * zoom), Image.NEAREST)
                frames.append(f_img)

            buf_pulse = io.BytesIO()
            frames[0].save(buf_pulse, format="GIF", save_all=True, append_images=frames[1:], duration=100, loop=0)
            st.session_state['pulse_gif_bytes'] = buf_pulse.getvalue()

        if 'pulse_gif_bytes' in st.session_state:
            st.image(st.session_state['pulse_gif_bytes'])
            st.download_button("💾 Download GIF Glow Pulse", data=st.session_state['pulse_gif_bytes'], file_name="TerrariaTile_Pulse.gif", mime="image/gif", use_container_width=True)

    with gif_col2:
        st.write("**2. Animasi RGB Cycle / Pastel**")
        if st.button("Preview GIF RGB Cycle 🌈", key="btn_rgb_prev", use_container_width=True):
            frames_rgb = []
            for h_shift in range(0, 360, 30):
                f_img, _, _, _ = render_studio_all(arr, extra_hue=h_shift)
                if zoom > 1: f_img = f_img.resize((w * zoom, h * zoom), Image.NEAREST)
                frames_rgb.append(f_img)

            buf_rgb = io.BytesIO()
            frames_rgb[0].save(buf_rgb, format="GIF", save_all=True, append_images=frames_rgb[1:], duration=100, loop=0)
            st.session_state['rgb_gif_bytes'] = buf_rgb.getvalue()

        if 'rgb_gif_bytes' in st.session_state:
            st.image(st.session_state['rgb_gif_bytes'])
            st.download_button("💾 Download GIF RGB Cycle", data=st.session_state['rgb_gif_bytes'], file_name="TerrariaTile_RGBCycle.gif", mime="image/gif", use_container_width=True)

else:
    st.info("👈 Silakan unggah file gambar PNG ore milikmu di menu Sidebar sebelah kiri untuk memulai studio!")
