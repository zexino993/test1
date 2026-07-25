import io
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageChops, ImageFilter
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME UI/UX
# ==========================================
st.set_page_config(
    page_title="Terraria Sprite Master Studio",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme CSS (Terraria Dark Studio UI)
st.markdown("""
<style>
    .main {
        background-color: #0b0712;
    }
    .stAppHeader {
        background-color: rgba(11, 7, 18, 0.8);
    }
    .stButton>button {
        background: linear-gradient(135deg, #8a2be2, #4b0082);
        color: white;
        border: 1px solid #d4a5ff;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #a34bfb, #6a0ded);
        border-color: #ffffff;
        box-shadow: 0 0 12px rgba(163, 75, 251, 0.6);
    }
    .stSelectbox, .stSlider, .stColorPicker {
        background-color: #130b21;
        border-radius: 6px;
    }
    .stTab {
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚔️ Terraria Sprite Master Studio v15.0")
st.caption("Studio All-in-One: **Extended Texture Engine (15 Textures)**, **Sprite Recoloring**, & **Sprite Sheet Generator**.")

# ==========================================
# 2. PRESET PALET WARNA LENGKAP & MAPPING
# ==========================================
PRESET_NAMES = {
    'manual': 'Custom (Manual)',
    'true_nights_edge': "⚔️ True Night's Edge",
    'terra_blade': '🌿 Terra Blade Green',
    'excalibur': '🗡️ Excalibur Holy Gold',
    'meowmere': '🐱 Meowmere Rainbow',
    'zenith': '🌌 Zenith Dark Cosmic',
    'vampire_crimson': '🩸 Vampire Crimson',
    'pastel_cotton_candy': '🌸 Pastel Cotton Candy',
    'pastel_mint': '🍵 Pastel Mint Matcha',
    'pastel_lavender': '💜 Pastel Soft Lavender',
    'pastel_peach': '🍑 Pastel Peach Cream',
    'hellstone': '🔥 Hellstone Flame',
    'chlorophyte': '🌿 Chlorophyte Green',
    'luminite': '🌌 Luminite Cosmic',
    'cobalt': '🔷 Cobalt Blue',
    'orichalcum': '🌸 Orichalcum Pink',
    'adamantite': '🔴 Adamantite Red',
    'shroomite': '🍄 Shroomite Cyan'
}

PRESETS = {
    'manual': None,
    'true_nights_edge': {'shadow': '#0f001e', 'mid': '#5a189a', 'glow': '#00ffcc'},
    'terra_blade': {'shadow': '#001b00', 'mid': '#2ec4b6', 'glow': '#80ff00'},
    'excalibur': {'shadow': '#2b1e00', 'mid': '#ffb703', 'glow': '#ffffff'},
    'meowmere': {'shadow': '#3a0ca3', 'mid': '#f72585', 'glow': '#4cc9f0'},
    'zenith': {'shadow': '#120024', 'mid': '#7209b7', 'glow': '#ff007f'},
    'vampire_crimson': {'shadow': '#200000', 'mid': '#d90429', 'glow': '#ff70a6'},
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

# Session State Setup
if 'shadow_picker' not in st.session_state: st.session_state.shadow_picker = "#080214"
if 'mid_picker' not in st.session_state: st.session_state.mid_picker = "#AA19F5"
if 'glow_picker' not in st.session_state: st.session_state.glow_picker = "#FF78FF"
if 'pastel_mode_val' not in st.session_state: st.session_state.pastel_mode_val = False

def on_preset_change():
    p_key = st.session_state.preset_choice
    if p_key in PRESETS and PRESETS[p_key] is not None:
        st.session_state.shadow_picker = PRESETS[p_key]['shadow']
        st.session_state.mid_picker = PRESETS[p_key]['mid']
        st.session_state.glow_picker = PRESETS[p_key]['glow']
        st.session_state.pastel_mode_val = ('pastel' in p_key)

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("📁 1. Input Sprite & Mode")
uploaded_file = st.sidebar.file_uploader("Upload PNG Sprite / Tile", type=["png"])

sprite_type = st.sidebar.selectbox(
    "Jenis Sprite:",
    ["Item / Senjata / Aksesori", "Tile / Blok / Wall", "Character / NPC / Pet", "Projectiles / FX"]
)

use_orig_color = st.sidebar.checkbox("🔒 Gunakan Warna Asli (Matikan Recolor)", value=False)
if use_orig_color:
    st.sidebar.caption("⚠️ *Fitur Recolor & Preset dinonaktifkan karena 'Warna Asli' aktif.*")

pastel_mode = st.sidebar.checkbox("🌸 Soft RGB Pastel Tone", key="pastel_mode_val")
zoom = st.sidebar.slider("🔍 Zoom Magnifier", 1, 10, 4)

with st.sidebar.expander("🎨 2. Presets & Warna Palette", expanded=True):
    st.selectbox(
        "Pilih Preset Sprite:",
        options=list(PRESET_NAMES.keys()),
        format_func=lambda x: PRESET_NAMES.get(x, x),
        key="preset_choice",
        on_change=on_preset_change
    )
    
    shadow_color = st.color_picker("1. Shadow Celah", key="shadow_picker")
    mid_color = st.color_picker("2. Warna Utama", key="mid_picker")
    glow_color = st.color_picker("3. Glow Highlight", key="glow_picker")
    
    hue_shift = st.slider("RGB Hue Shift", 0, 360, 0, 5)
    vibrancy = st.slider("Saturasi / Vibrancy", 0.5, 2.0, 1.1, 0.1)

with st.sidebar.expander("✏️ 3. Terraria Outline / Border", expanded=False):
    enable_outline = st.checkbox("Tambahkan Auto Outline / Border", value=True)
    outline_color_mode = st.selectbox("Warna Outline:", ["Black (Terraria Classic)", "Custom Color", "Glowing Pulse Color"])
    outline_color = st.color_picker("Warna Outline Custom", "#000000")
    outline_thickness = st.slider("Ketebalan Border (px)", 1, 3, 1)

with st.sidebar.expander("🎛️ 4. Filter Foto & Adjustment", expanded=False):
    brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.05)
    contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.05)

with st.sidebar.expander("🔀 5. Textures & 3D Shading (15 Types)", expanded=False):
    TEX_OPTIONS = [
        ('Smooth Klasik (Tanpa Tekstur)', 'smooth'),
        ('💎 Crystal Facets (Faset Kristal)', 'crystal'),
        ('🪨 Stone Grain (Batuan Alami)', 'stone'),
        ('✨ Metallic Sparkle (Kilauan Logam)', 'sparkle'),
        ('🌋 Magma / Lava Veins (Urat Lava)', 'veins'),
        ('🔮 Obsidian Glass Slits (Kaca Striasi)', 'obsidian'),
        ('🌿 Organic Moss / Spores (Spora/Lumut)', 'moss'),
        ('🌌 Cosmic Swirl (Pusaran Nebula)', 'cosmic'),
        ('📜 Runic Glyphs (Ukiran Sihir/Rune)', 'runic'),
        ('🐉 Dragon Scales (Sisik Naga/Reptil)', 'scale'),
        ('🪵 Wood Grain (Serat Kayu Alami)', 'wood'),
        ('🍯 Honeycomb (Sarang Lebah/Hex)', 'honey'),
        ('👾 Cyber Glitch (Piksel Digital)', 'glitch'),
        ('🟢 Slime Bubbles (Gelembung Lendir)', 'slime'),
        ('❄️ Frost Shards (Kristal Es Sharp)', 'frost')
    ]
    tex_primary = st.selectbox("Tekstur Utama:", options=TEX_OPTIONS, index=0, format_func=lambda x: x[0])[1]
    tex_secondary = st.selectbox("Tekstur Kedua:", options=[('Tidak Ada', 'none')] + TEX_OPTIONS, index=0, format_func=lambda x: x[0])[1]
    blend_ratio = st.slider("Rasio Blend Tekstur", 0.0, 1.0, 0.3, 0.05)
    tex_intensity = st.slider("Kekuatan Tekstur", 0.0, 1.0, 0.35, 0.05)
    depth_mult = st.slider("Intensitas 3D Depth", 0.5, 3.0, 1.5, 0.1)

with st.sidebar.expander("💡 6. Glowmask & Pulse Settings", expanded=False):
    threshold = st.slider("Sensitivitas Glow Area", 0.1, 0.9, 0.45, 0.02)
    pulse_intensity = st.slider("Kekuatan Denyut Pulse", 0.1, 1.0, 0.5, 0.05)

# ==========================================
# 4. HELPER & CORE ENGINE FUNCTIONS
# ==========================================
def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def apply_hue_shift(rgb_array, hue_deg):
    if hue_deg == 0: return rgb_array
    img = Image.fromarray(rgb_array.astype(np.uint8), mode='RGB').convert('HSV')
    h, s, v = img.split()
    h_arr = (np.array(h, dtype=np.int16) + int((hue_deg / 360.0) * 255)) % 256
    return np.array(Image.merge('HSV', (Image.fromarray(h_arr.astype(np.uint8)), s, v)).convert('RGB'), dtype=np.float32)

def add_border_to_image(img_rgba, color=(0,0,0,255), thickness=1):
    if thickness == 0: return img_rgba
    w, h = img_rgba.size
    alpha = img_rgba.split()[3]
    mask = alpha.filter(ImageFilter.MaxFilter(thickness * 2 + 1))
    border_img = Image.new("RGBA", (w, h), color)
    border_img.putalpha(mask)
    return Image.alpha_composite(border_img, img_rgba)

# GENERATOR TEXTURE PROSEDURAL DENGAN 15 MODE
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
    elif tex_type == 'scale':
        s_wave = np.sin(x_indices * 0.5 + (y_indices % 4) * 0.8) * np.cos(y_indices * 0.4)
        tex = np.where(s_wave > 0.2, 0.4, -0.2) * intensity
    elif tex_type == 'wood':
        ring = np.sin(np.sqrt((x_indices - width*0.5)**2 + (y_indices - height*0.5)**2) * 0.4 + np.sin(y_indices * 0.1) * 2.0)
        tex = ring * 0.35 * intensity
    elif tex_type == 'honey':
        hex_wave = np.sin(x_indices * 0.4) + np.sin(x_indices * 0.2 + y_indices * 0.35) + np.sin(x_indices * 0.2 - y_indices * 0.35)
        tex = np.where(hex_wave > 1.2, 0.5, -0.2) * intensity
    elif tex_type == 'glitch':
        block_y, block_x = y_indices // 2, x_indices // 4
        g_noise = np.sin(block_y * 45.12 + block_x * 91.34) * 43758.5453
        tex = np.where((g_noise - np.floor(g_noise)) > 0.7, 0.6, -0.15) * intensity
    elif tex_type == 'slime':
        blobs = np.sin(x_indices * 0.25) * np.cos(y_indices * 0.25) + np.cos(x_indices * 0.1 + y_indices * 0.1)
        tex = np.where(blobs > 0.5, 0.45, -0.1) * intensity
    elif tex_type == 'frost':
        shard1 = np.abs(np.sin(x_indices * 0.5 + y_indices * 0.5))
        shard2 = np.abs(np.cos(x_indices * 0.5 - y_indices * 0.5))
        tex = (np.maximum(shard1, shard2) - 0.5) * 0.8 * intensity
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
    else:
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

        if st.session_state.pastel_mode_val:
            out_rgb = out_rgb * 0.6 + 255.0 * 0.4 * (out_rgb / 255.0)**0.5

        out_rgb = np.clip(out_rgb, 0, 255).astype(np.uint8)
        alpha_uint8 = alpha.astype(np.uint8)

        out_img = Image.fromarray(np.dstack((out_rgb, alpha_uint8)), mode="RGBA")
        glow_alpha = np.where((final_lum >= threshold) & (alpha_uint8 > 0), alpha_uint8, 0).astype(np.uint8)
        glow_img = Image.fromarray(np.dstack((out_rgb, glow_alpha)), mode="RGBA")

    if brightness != 1.0:
        out_img = ImageEnhance.Brightness(out_img).enhance(brightness)
    if contrast != 1.0:
        out_img = ImageEnhance.Contrast(out_img).enhance(contrast)

    if enable_outline:
        if outline_color_mode == "Black (Terraria Classic)":
            b_color = (0, 0, 0, 255)
        elif outline_color_mode == "Custom Color":
            b_rgb = hex_to_rgb(outline_color)
            b_color = (b_rgb[0], b_rgb[1], b_rgb[2], 255)
        else:
            b_color = (255, 255, 255, 255)
        out_img = add_border_to_image(out_img, color=b_color, thickness=outline_thickness)

    return out_img, glow_img, lum, glow_alpha

def create_spritesheet(frames, cols, padding=0):
    if not frames: return None
    n = len(frames)
    cols = max(1, min(cols, n))
    rows = math.ceil(n / cols)
    
    fw, fh = frames[0].size
    sheet_w = cols * fw + (cols + 1) * padding
    sheet_h = rows * fh + (rows + 1) * padding
    
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        r = idx // cols
        c = idx % cols
        x = padding + c * (fw + padding)
        y = padding + r * (fh + padding)
        sheet.paste(frame, (x, y))
        
    return sheet

# ==========================================
# 5. MAIN DASHBOARD STUDIO
# ==========================================
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

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🖼️ Quad-Preview Matrix", 
        "🧩 3x3 Tile Grid Test", 
        "📊 Sprite Sheet Builder", 
        "🎬 GIF Animation Studio", 
        "💾 Export Center"
    ])

    with tab1:
        st.subheader("🖼️ Preview Live Studio Matrix")
        col1, col2, col3, col4 = st.columns(4)
        col1.caption("1. Sprite Asli")
        col1.image(orig_z, use_container_width=True)
        col2.caption("2. Master Sprite FX")
        col2.image(out_z, use_container_width=True)
        col3.caption("3. Glowmask Isolated")
        col3.image(glow_z, use_container_width=True)
        col4.caption("4. RGB Spectrum Shift")
        col4.image(rgb_z, use_container_width=True)

    with tab2:
        st.subheader("🧩 3x3 Tile & Wall Seamless Test")
        st.caption("Uji pola seamless ubin/dinding dalam kisi 3x3 bertumpuk.")
        grid_3x3 = Image.new("RGBA", (w * zoom * 3, h * zoom * 3), (20, 15, 30, 255))
        for gy in range(3):
            for gx in range(3):
                grid_3x3.paste(out_z, (gx * w * zoom, gy * h * zoom))
        st.image(grid_3x3)

    with tab3:
        st.subheader("📊 Custom Sprite Sheet Generator")
        st.caption("Buat Sprite Sheet animasi berformat PNG transparan siap pakai untuk Mod Terraria / Game Engine.")

        ss_col1, ss_col2 = st.columns(2)
        with ss_col1:
            sheet_anim_type = st.selectbox(
                "Jenis Animasi Frame:",
                ["Glow Pulse Frames", "RGB Rainbow Hue Cycle", "Recolor Spectrum Wave"]
            )
            frame_count = st.slider("Jumlah Frame Animasi:", min_value=2, max_value=20, value=8, step=1)
            
        with ss_col2:
            layout_type = st.selectbox(
                "Format Layout Sheet:",
                ["Vertical Strip (1 Kolom - Format Terraria)", "Horizontal Strip (1 Baris)", "Custom Grid (Kolom & Baris)"]
            )
            if "Custom Grid" in layout_type:
                grid_cols = st.number_input("Jumlah Kolom Grid:", min_value=1, max_value=10, value=4)
            elif "Vertical" in layout_type:
                grid_cols = 1
            else:
                grid_cols = frame_count

            frame_padding = st.number_input("Jarak / Padding Antar Frame (px):", min_value=0, max_value=10, value=0)

        if st.button("🚀 Generate Sprite Sheet", use_container_width=True):
            sheet_frames = []
            
            if sheet_anim_type == "Glow Pulse Frames":
                base_rgb = np.array(out_img, dtype=np.float32)[:, :, :3]
                alpha_arr = np.array(out_img)[:, :, 3:]
                glow_mask_norm = np.expand_dims((glow_alpha.astype(np.float32) / 255.0), axis=-1)

                for i in range(frame_count):
                    pulse_factor = (math.sin(2 * math.pi * i / frame_count) + 1.0) * 0.5 * pulse_intensity
                    boosted_rgb = base_rgb + (base_rgb * 0.6 + 60.0) * glow_mask_norm * pulse_factor
                    boosted_rgb = np.clip(boosted_rgb, 0, 255).astype(np.uint8)
                    f_img = Image.fromarray(np.dstack((boosted_rgb, alpha_arr.astype(np.uint8))), mode="RGBA")
                    sheet_frames.append(f_img)
                    
            elif sheet_anim_type == "RGB Rainbow Hue Cycle":
                hue_step = 360 // frame_count
                for i in range(frame_count):
                    f_img, _, _, _ = render_studio_all(arr, extra_hue=(i * hue_step))
                    sheet_frames.append(f_img)

            elif sheet_anim_type == "Recolor Spectrum Wave":
                hue_step = 180 // frame_count
                for i in range(frame_count):
                    f_img, _, _, _ = render_studio_all(arr, extra_hue=(i * hue_step))
                    sheet_frames.append(f_img)

            spritesheet_img = create_spritesheet(sheet_frames, cols=grid_cols, padding=frame_padding)
            
            buf_ss = io.BytesIO()
            spritesheet_img.save(buf_ss, format="PNG")
            st.session_state['spritesheet_bytes'] = buf_ss.getvalue()
            st.session_state['spritesheet_size'] = spritesheet_img.size

        if 'spritesheet_bytes' in st.session_state:
            st.divider()
            sw, sh = st.session_state['spritesheet_size']
            st.write(f"📐 **Ukuran Sprite Sheet:** `{sw} x {sh} pixels`")
            
            ss_preview_img = Image.open(io.BytesIO(st.session_state['spritesheet_bytes']))
            st.image(ss_preview_img.resize((sw * max(1, zoom//2), sh * max(1, zoom//2)), Image.NEAREST))
            
            st.download_button(
                "💾 Download Sprite Sheet PNG", 
                data=st.session_state['spritesheet_bytes'], 
                file_name="TerrariaSprite_Sheet.png", 
                mime="image/png", 
                use_container_width=True
            )

    with tab4:
        st.subheader("🎬 GIF Animation Studio")
        gif_col1, gif_col2 = st.columns(2)

        with gif_col1:
            st.write("**1. Glow Pulse Animation**")
            if st.button("Preview Glow Pulse GIF 🎬", key="btn_pulse_prev", use_container_width=True):
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

        with gif_col2:
            st.write("**2. RGB / Rainbow Cycle Animation**")
            if st.button("Preview RGB Cycle GIF 🌈", key="btn_rgb_prev", use_container_width=True):
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

    with tab5:
        st.subheader("💾 Export Center")
        st.write("Unduh semua berkas hasil olahan sprite:")
        
        col_ex1, col_ex2 = st.columns(2)
        
        buf_main = io.BytesIO()
        out_img.save(buf_main, format="PNG")
        col_ex1.download_button("💾 Download Main Sprite PNG", data=buf_main.getvalue(), file_name="TerrariaSprite_Main.png", mime="image/png", use_container_width=True)

        buf_glow = io.BytesIO()
        glow_img.save(buf_glow, format="PNG")
        col_ex2.download_button("💡 Download Glowmask PNG", data=buf_glow.getvalue(), file_name="TerrariaSprite_Glow.png", mime="image/png", use_container_width=True)

        st.divider()
        col_ex3, col_ex4 = st.columns(2)
        if 'pulse_gif_bytes' in st.session_state:
            col_ex3.download_button("🎬 Download Glow Pulse GIF", data=st.session_state['pulse_gif_bytes'], file_name="TerrariaSprite_Pulse.gif", mime="image/gif", use_container_width=True)
        if 'rgb_gif_bytes' in st.session_state:
            col_ex4.download_button("🌈 Download RGB Cycle GIF", data=st.session_state['rgb_gif_bytes'], file_name="TerrariaSprite_RGB.gif", mime="image/gif", use_container_width=True)

        if 'spritesheet_bytes' in st.session_state:
            st.divider()
            st.download_button("📊 Download Sprite Sheet PNG", data=st.session_state['spritesheet_bytes'], file_name="TerrariaSprite_Sheet.png", mime="image/png", use_container_width=True)

else:
    st.info("👈 Silakan unggah sprite PNG (Senjata, Zirah, NPC, Tile, Pet) di sidebar kiri untuk memulai studio!")
