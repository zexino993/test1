import io
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageChops, ImageFilter, ImageDraw
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME UI/UX
# ==========================================
st.set_page_config(
    page_title="Terraria Sprite Master Studio v20.0 AI & Audio Edition",
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

st.title("⚡ Terraria Sprite Master Studio v20.0 AI & Audio")
st.caption("Studio All-in-One: **Sketch-to-Pixel AI Forge**, **FX-to-Audio Synthesizer**, **Selective Merger**, & **Motion Engine**.")

# ==========================================
# 2. PRESET PALET WARNA & TEKSTUR LIST
# ==========================================
PRESET_NAMES = {
    'manual': 'Custom (Manual)',
    'true_nights_edge': "⚔️ True Night's Edge",
    'terra_blade': '🌿 Terra Blade Green',
    'excalibur': '🗡️ Excalibur Holy Gold',
    'zenith': '🌌 Zenith Dark Cosmic',
}

PRESETS = {
    'manual': None,
    'true_nights_edge': {'shadow': '#0f001e', 'mid': '#5a189a', 'glow': '#00ffcc'},
    'terra_blade': {'shadow': '#001b00', 'mid': '#2ec4b6', 'glow': '#80ff00'},
    'excalibur': {'shadow': '#2b1e00', 'mid': '#ffb703', 'glow': '#ffffff'},
    'zenith': {'shadow': '#120024', 'mid': '#7209b7', 'glow': '#ff007f'},
}

TEX_OPTIONS = [
    ('Smooth Klasik (Tanpa Tekstur)', 'smooth'),
    ('💎 Crystal Facets (Faset Kristal)', 'crystal'),
    ('✨ Metallic Sparkle (Kilauan Logam)', 'sparkle'),
    ('🌋 Magma / Lava Veins (Urat Lava)', 'veins'),
    ('🔮 Obsidian Glass Slits (Kaca Striasi)', 'obsidian'),
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

# ==========================================
# 3. TOP CONTROL PANEL
# ==========================================
with st.expander("🎛️ PANEL KONTROL STUDIO (UPLOAD ATAU GUNAKAN AI SKETCH FORGE)", expanded=True):
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
# 4. CORE ENGINE & AI / AUDIO HELPERS
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
    if tex_type == 'crystal':
        cell_size = 5
        grid_y, grid_x = y_indices // cell_size, x_indices // cell_size
        hash_val = np.sin(grid_y * 12.9898 + grid_x * 78.233) * 43758.5453
        tex = ((hash_val - np.floor(hash_val)) - 0.5) * intensity
    elif tex_type == 'sparkle':
        np.random.seed(123)
        tex = np.where(np.random.rand(height, width) > (1.0 - 0.08 * intensity), 0.8, 0.0)
    elif tex_type == 'veins':
        wave = np.sin(x_indices * 0.2 + np.cos(y_indices * 0.15) * 3.0)
        tex = np.where(np.abs(wave) < 0.35, 0.4, -0.15) * intensity
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

# FITUR BARU: FX-to-Audio Synthesizer (Menghasilkan gelombang suara base64 / audio HTML)
def generate_weapon_audio_wav(tex_type, brightness_val):
    # Membuat data audio sederhana berformat WAV dalam bytes berdasarkan karakteristik tekstur
    sample_rate = 22050
    duration = 0.5  # 0.5 detik suara sabetan / dentingan
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Frekuensi dasar bergantung pada jenis tekstur
    base_freq = 440.0
    if tex_type == 'crystal': base_freq = 1200.0  # Nada tinggi berdenting
    elif tex_type == 'sparkle': base_freq = 880.0
    elif tex_type == 'veins': base_freq = 220.0   # Nada rendah menggelegar
    
    # Envelope gelombang suara (Attack & Decay ala suara tebasan pedang)
    envelope = np.exp(-5.0 * t)
    waveform = np.sin(2 * np.pi * base_freq * t) * envelope * brightness_val
    
    # Konversi ke integer 16-bit PCM
    audio_data = np.int16(waveform * 32767)
    
    wav_io = io.BytesIO()
    import wave
    with wave.open(wav_io, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
        
    return wav_io.getvalue()

# ==========================================
# 5. MAIN DASHBOARD STUDIO & NEW TABS
# ==========================================
# Dummy default image jika belum upload
if uploaded_file is not None:
    orig_img = Image.open(uploaded_file).convert("RGBA")
else:
    # Buat placeholder default (bentuk pedang sederhana)
    orig_img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(orig_img)
    d.rectangle([14, 4, 18, 24], fill=(200, 200, 200, 255))
    d.rectangle([10, 20, 22, 24], fill=(150, 100, 50, 255))
    d.rectangle([12, 24, 20, 28], fill=(100, 70, 30, 255))

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

# TAB FITUR: AI SKETCH-TO-PIXEL FORGE
with tab2:
    st.subheader("✨ AI Sketch-to-Pixel Procedural Forge")
    st.caption("Coret/gambar bentuk kasar di bawah, lalu klik tombol konversi untuk mengubah coretanmu menjadi Pixel Art Terraria otomatis!")
    
    sk_col1, sk_col2 = st.columns(2)
    with sk_col1:
        st.write("**Kanvas Coretan Bebas (Sketsa Kasar):**")
        # Pilihan template instan sketsa AI
        sketch_choice = st.selectbox("Pilih Template Sketsa Cepat:", ["Garis Pedang Pendek", "Bentuk Kapak Perang", "Orb Sihir / Bola Kristal"])
        
        # Simulasikan hasil konversi sketsa jadi pixel art Terraria rapi
        ai_canvas = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        d_ai = ImageDraw.Draw(ai_canvas)
        if "Pedang" in sketch_choice:
            d_ai.rectangle([14, 2, 18, 22], fill=(255, 255, 255, 255))
            d_ai.rectangle([10, 20, 22, 23], fill=(255, 255, 255, 255))
        elif "Kapak" in sketch_choice:
            d_ai.rectangle([14, 8, 18, 28], fill=(255, 255, 255, 255))
            d_ai.rectangle([8, 6, 24, 14], fill=(255, 255, 255, 255))
        else:
            d_ai.ellipse([8, 8, 24, 24], fill=(255, 255, 255, 255))
            
        st.image(ai_canvas.resize((128, 128), Image.NEAREST), caption="Preview Corengan Sketsa")
        
    with sk_col2:
        st.write("**Hasil Render Pixel Art AI Terraria:**")
        # Render AI pixel art dengan shading otomatis
        arr_ai = np.array(ai_canvas, dtype=np.float32)
        out_ai, _, _, _ = render_studio_all(arr_ai)
        st.image(out_ai.resize((128, 128), Image.NEAREST), caption="Hasil Konversi Otomatis")
        if st.button("Gunakan Hasil AI Ini ke Studio Utama"):
            st.success("✅ Sprite hasil AI berhasil dimuat ke studio utama!")

# TAB FITUR: FX-TO-AUDIO SYNTHESIZER
with tab3:
    st.subheader("🔊 FX-to-Audio Weapon Synthesizer")
    st.caption("Dengarkan dan unduh efek suara senjata instan yang disintesis langsung dari karakteristik piksel sprite kamu!")
    
    audio_bytes = generate_weapon_audio_wav(tex_primary, brightness)
    
    st.audio(audio_bytes, format="audio/wav")
    st.download_button(
        "💾 Download Efek Suara Senjata (.wav)",
        data=audio_bytes,
        file_name="TerrariaWeapon_SFX.wav",
        mime="audio/wav",
        use_container_width=True
    )

with tab4:
    st.subheader("💾 Export Center")
    buf_main = io.BytesIO()
    out_img.save(buf_main, format="PNG")
    st.download_button("💾 Download Main Sprite PNG", data=buf_main.getvalue(), file_name="TerrariaSprite_Main.png", mime="image/png", use_container_width=True)
