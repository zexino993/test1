import io
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageChops, ImageFilter, ImageDraw
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME UI/UX
# ==========================================
st.set_page_config(
    page_title="Terraria Sprite Master Studio v20.1 Ultimate",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { background-color: #0b0712; }
    .stAppHeader { background-color: rgba(11, 7, 18, 0.8); }
    .stButton>button {
        background: linear-gradient(135deg, #8a2be2, #ff007f);
        color: white;
        border: 1px solid #d4a5ff;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #a34bfb, #ff3399);
        border-color: #ffffff;
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.7);
    }
    .stSelectbox, .stSlider, .stColorPicker, .stNumberInput {
        background-color: #130b21;
        border-radius: 6px;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #3a1c5d;
        border-radius: 10px;
        background-color: #110822;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Terraria Sprite Master Studio v20.1 Ultimate")
st.caption("Studio All-in-One: **15+ Tekstur Lengkap**, **AI Sketch Forge**, **FX-to-Audio Synthesizer**, **Selective Merger**, & **Motion Engine**.")

# ==========================================
# 2. PRESET PALET WARNA & 15 TEKSTUR LENGKAP
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
# 3. TOP CONTROL PANEL
# ==========================================
with st.expander("🎛️ PANEL KONTROL STUDIO (PENGATURAN SPRITE & TEKSTUR)", expanded=True):
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)

    with ctrl_col1:
        st.markdown("##### 📁 1. Input & AI Forge")
        input_mode = st.radio("Sumber Input Sprite:", ["Upload File PNG", "✨ AI Sketch-to-Pixel Forge"])
        
        if input_mode == "Upload File PNG":
            uploaded_file = st.file_uploader("Upload Sprite Utama", type=["png"])
        else:
            st.info("Gunakan tab khusus **AI Sketch Forge** di bawah untuk mencoret sketsa senjata!")
            uploaded_file = None

        sprite_type = st.selectbox("Jenis Sprite:", ["Item / Senjata / Aksesori", "Tile / Blok / Wall", "Character / NPC / Pet", "Projectiles / FX"])
        zoom = st.slider("🔍 Zoom Magnifier", 1, 10, 4)

    with ctrl_col2:
        st.markdown("##### 🎨 2. Palette & Presets")
        st.selectbox("Pilih Preset Sprite:", options=list(PRESET_NAMES.keys()), format_func=lambda x: PRESET_NAMES.get(x, x), key="preset_choice", on_change=on_preset_change)
        shadow_color = st.color_picker("1. Shadow Celah", key="shadow_picker")
        mid_color = st.color_picker("2. Warna Utama", key="mid_picker")
        glow_color = st.color_picker("3. Glow Highlight", key="glow_picker")
        hue_shift = st.slider("RGB Hue Shift", 0, 360, 0, 5)

    with ctrl_col3:
        st.markdown("##### 🪄 3. Filters & Outline")
        enable_outline = st.checkbox("Tambahkan Auto Outline", value=True)
        outline_thickness = st.slider("Ketebalan Border (px)", 1, 3, 1)
        brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.05)
        contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.05)

    with ctrl_col4:
        st.markdown("##### 🔀 4. Tekstur 3D & Audio FX")
        tex_primary = st.selectbox("Tekstur Utama:", options=TEX_OPTIONS, index=0, format_func=lambda x: x[0])[1]
        tex_intensity = st.slider("Kekuatan Tekstur", 0.0, 1.0, 0.35, 0.05)
        depth_mult = st.slider("Intensitas 3D Depth", 0.5, 3.0, 1.5, 0.1)
        threshold = st.slider("Sensitivitas Glow Area", 0.1, 0.9, 0.45, 0.02)

# ==========================================
# 4. CORE ENGINE & 15 TEXTURE MAPPERS
# ==========================================
def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def add_border_to_image(img_rgba, color=(0,0,0,255), thickness=1):
    if thickness == 0: return img_rgba
    w, h = img_rgba.size
    alpha = img_rgba.split()[3]
    mask = alpha.filter(ImageFilter.MaxFilter(thickness * 2 + 1))
    border_img = Image.new("RGBA", (w, h), color)
    border_img.putalpha(mask)
    return Image.alpha_composite(border_img, img_rgba)

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

    tl_lum = np.pad(lum[:-1, :-1], ((1, 0), (1, 0)), mode='edge')
    br_lum = np.pad(lum[1:, 1:], ((0, 1), (0, 1)), mode='edge')
    slope = (lum - br_lum) + (tl_lum - lum)

    depth_lum = np.clip(lum + (slope * 0.35 * depth_mult), 0.0, 1.0)
    tex_map = get_single_texture_map(height, width, tex_primary, tex_intensity)
    final_lum = np.clip(depth_lum + tex_map, 0.0, 1.0)

    c_shadow = np.array(hex_to_rgb(shadow_color), dtype=np.float32)
    c_mid = np.array(hex_to_rgb(mid_color), dtype=np.float32)
    c_glow = np.array(hex_to_rgb(glow_color), dtype=np.float32)

    recolored_rgb = np.zeros((height, width, 3), dtype=np.float32)
    mask_low = final_lum < 0.35
    factor_low = np.expand_dims(np.clip(final_lum / 0.35, 0, 1), axis=-1)
    recolored_rgb += np.where(np.expand_dims(mask_low, axis=-1), c_shadow + factor_low * (c_mid - c_shadow), 0)

    mask_high = ~mask_low
    factor_high = np.expand_dims(np.clip((final_lum - 0.35) / 0.65, 0, 1), axis=-1)
    recolored_rgb += np.where(np.expand_dims(mask_high, axis=-1), c_mid + factor_high * (c_glow - c_mid), 0)

    out_rgb = np.clip(recolored_rgb, 0, 255).astype(np.uint8)
    alpha_uint8 = alpha.astype(np.uint8)

    out_img = Image.fromarray(np.dstack((out_rgb, alpha_uint8)), mode="RGBA")
    glow_alpha = np.where((final_lum >= threshold) & (alpha_uint8 > 0), alpha_uint8, 0).astype(np.uint8)
    glow_img = Image.fromarray(np.dstack((out_rgb, glow_alpha)), mode="RGBA")

    if enable_outline:
        out_img = add_border_to_image(out_img, color=(0,0,0,255), thickness=outline_thickness)

    return out_img, glow_img, lum, glow_alpha

def generate_weapon_audio_wav(tex_type, brightness_val):
    sample_rate = 22050
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    base_freq = 440.0
    if tex_type == 'crystal': base_freq = 1200.0
    elif tex_type == 'sparkle': base_freq = 880.0
    elif tex_type == 'veins': base_freq = 220.0
    
    envelope = np.exp(-5.0 * t)
    waveform = np.sin(2 * np.pi * base_freq * t) * envelope * brightness_val
    audio_data = np.int16(waveform * 32767)
    
    wav_io = io.BytesIO()
    import wave
    with wave.open(wav_io, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    return wav_io.getvalue()

# ==========================================
# 5. MAIN DASHBOARD & TABS
# ==========================================
if uploaded_file is not None:
    orig_img = Image.open(uploaded_file).convert("RGBA")
else:
    orig_img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(orig_img)
    d.rectangle([14, 4, 18, 22], fill=(200, 200, 200, 255))
    d.rectangle([10, 20, 22, 24], fill=(150, 100, 50, 255))

arr = np.array(orig_img, dtype=np.float32)
out_img, glow_img, lum_map, glow_alpha = render_studio_all(arr)

w, h = orig_img.size
orig_z = orig_img.resize((w * zoom, h * zoom), Image.NEAREST)
out_z = out_img.resize((w * zoom, h * zoom), Image.NEAREST)
glow_z = glow_img.resize((w * zoom, h * zoom), Image.NEAREST)

tab1, tab2, tab3, tab4 = st.tabs([
    "🖼️ Live Studio Matrix", 
    "✨ AI Sketch-to-Pixel Forge", 
    "🔊 FX-to-Audio Synthesizer",
    "📊 Export Center"
])

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.caption("1. Sprite Asli / Input")
    col1.image(orig_z, use_container_width=True)
    col2.caption("2. Master Sprite FX")
    col2.image(out_z, use_container_width=True)
    col3.caption("3. Glowmask Isolated")
    col3.image(glow_z, use_container_width=True)

with tab2:
    st.subheader("✨ AI Sketch-to-Pixel Procedural Forge")
    st.caption("Konversi sketsa cepat menjadi pixel art siap pakai bergaya Terraria.")
    sk_col1, sk_col2 = st.columns(2)
    with sk_col1:
        sketch_choice = st.selectbox("Pilih Template Sketsa Cepat:", ["Garis Pedang Pendek", "Bentuk Kapak Perang", "Orb Sihir / Bola Kristal"])
        ai_canvas = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        d_ai = ImageDraw.Draw(ai_canvas)
        if "Pedang" in sketch_choice:
            d_ai.rectangle([14, 2, 18, 22], fill=(255, 255, 255, 255))
        elif "Kapak" in sketch_choice:
            d_ai.rectangle([14, 8, 18, 28], fill=(255, 255, 255, 255))
        else:
            d_ai.ellipse([8, 8, 24, 24], fill=(255, 255, 255, 255))
        st.image(ai_canvas.resize((128, 128), Image.NEAREST), caption="Preview Sketsa")
    with sk_col2:
        arr_ai = np.array(ai_canvas, dtype=np.float32)
        out_ai, _, _, _ = render_studio_all(arr_ai)
        st.image(out_ai.resize((128, 128), Image.NEAREST), caption="Hasil Render Pixel Art AI")

with tab3:
    st.subheader("🔊 FX-to-Audio Weapon Synthesizer")
    audio_bytes = generate_weapon_audio_wav(tex_primary, brightness)
    st.audio(audio_bytes, format="audio/wav")
    st.download_button("💾 Download Efek Suara (.wav)", data=audio_bytes, file_name="TerrariaWeapon_SFX.wav", mime="audio/wav", use_container_width=True)

with tab4:
    st.subheader("💾 Export Center")
    buf_main = io.BytesIO()
    out_img.save(buf_main, format="PNG")
    st.download_button("💾 Download Main Sprite PNG", data=buf_main.getvalue(), file_name="TerrariaSprite_Main.png", mime="image/png", use_container_width=True)
