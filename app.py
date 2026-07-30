import io
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageChops, ImageFilter, ImageDraw
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME UI/UX
# ==========================================
st.set_page_config(
    page_title="Terraria Sprite Master Studio v24.1 Ultimate",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { background-color: #08040f; }
    .stAppHeader { background-color: rgba(8, 4, 15, 0.9); }
    .stButton>button {
        background: linear-gradient(135deg, #7b2cbf, #ff007f);
        color: white;
        border: 1px solid #e0aaff;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #9d4edd, #ff3399);
        border-color: #ffffff;
        box-shadow: 0 0 18px rgba(255, 0, 127, 0.8);
    }
    .stSelectbox, .stSlider, .stColorPicker, .stNumberInput {
        background-color: #150a24;
        border-radius: 6px;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #480ca8;
        border-radius: 12px;
        background-color: #10061d;
        box-shadow: 0 4px 20px rgba(72, 12, 168, 0.3);
    }
    h1, h2, h3 {
        color: #f72585;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Terraria Sprite Master Studio v24.1 Ultimate")
st.caption("Studio All-in-One: **Pilihan Layout Vertikal/Horizontal Sprite Sheet**, **Separate Glow/Non-Glow Opacity & Color**.")

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
with st.expander("🎛️ PANEL KONTROL STUDIO (WARNA, OPASITAS, & TEKSTUR)", expanded=True):
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)

    with ctrl_col1:
        st.markdown("##### 📁 1. Input & Color Lock")
        input_mode = st.radio("Sumber Input Sprite:", ["Upload File PNG", "✨ AI Sketch-to-Pixel Forge"])
        uploaded_file = st.file_uploader("Upload PNG Utama", type=["png"]) if input_mode == "Upload File PNG" else None

        use_orig_color = st.checkbox("🔒 Gunakan Warna Asli (Color Lock)", value=False)
        pastel_mode = st.checkbox("🌸 Soft RGB Pastel Tone", key="pastel_mode_val")
        sprite_type = st.selectbox("Jenis Sprite:", ["Item / Senjata / Aksesori", "Tile / Blok / Wall", "Character / NPC / Pet", "Projectiles / FX"])
        zoom = st.slider("🔍 Zoom Magnifier", 1, 10, 4)

    with ctrl_col2:
        st.markdown("##### 🎨 2. Non-Glow & Glow Customizer")
        st.selectbox("Pilih Preset Sprite:", options=list(PRESET_NAMES.keys()), format_func=lambda x: PRESET_NAMES.get(x, x), key="preset_choice", on_change=on_preset_change)
        
        st.markdown("**Area Non-Glow (Dasar/Mid):**")
        non_glow_color = st.color_picker("Warna Non-Glow", key="mid_picker")
        non_glow_opacity = st.slider("Opasitas Non-Glow", 0.0, 1.0, 1.0, 0.05)

        st.markdown("**Area Glow (Bersinar):**")
        glow_custom_color = st.color_picker("Warna Glow Terpisah", key="glow_picker")
        glow_opacity = st.slider("Opasitas Glow", 0.0, 1.0, 1.0, 0.05)

    with ctrl_col3:
        st.markdown("##### 🪄 3. Shadow & Outline")
        shadow_color = st.color_picker("Warna Shadow Celah", key="shadow_picker")
        hue_shift = st.slider("RGB Hue Shift", 0, 360, 0, 5)
        vibrancy = st.slider("Saturasi / Vibrancy", 0.5, 2.0, 1.1, 0.1)
        enable_outline = st.checkbox("Tambahkan Auto Outline", value=True)
        outline_thickness = st.slider("Ketebalan Border (px)", 1, 3, 1)
        brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.05)

    with ctrl_col4:
        st.markdown("##### 🔀 4. Tekstur 3D & Animation")
        tex_primary = st.selectbox("Tekstur Utama:", options=TEX_OPTIONS, index=0, format_func=lambda x: x[0])[1]
        tex_secondary = st.selectbox("Tekstur Kedua:", options=[('Tidak Ada', 'none')] + TEX_OPTIONS, index=0, format_func=lambda x: x[0])[1]
        blend_ratio = st.slider("Rasio Blend Tekstur", 0.0, 1.0, 0.3, 0.05)
        tex_intensity = st.slider("Kekuatan Tekstur", 0.0, 1.0, 0.35, 0.05)
        depth_mult = st.slider("Intensitas 3D Depth", 0.5, 3.0, 1.5, 0.1)
        threshold = st.slider("Sensitivitas Glow Area", 0.1, 0.9, 0.45, 0.02)
        
        anim_motion_mode = st.selectbox("Jenis Gerakan Animasi:", ["Pulse Light Wave", "Floating / Bobbing Up-Down", "360° Weapon Swing", "Sci-Fi Glitch Flicker"])
        pulse_intensity = st.slider("Kekuatan Motion", 0.1, 1.0, 0.5, 0.05)

# ==========================================
# 4. CORE ENGINE & MAPPERS
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

def get_single_texture_map(height, width, tex_type, intensity):
    if tex_type in ['smooth', 'none'] or intensity == 0:
        return np.zeros((height, width), dtype=np.float32)
    y_indices, x_indices = np.indices((height, width))
    if tex_type == 'crystal':
        cell_size = 5
        grid_y, grid_x = y_indices // cell_size, x_indices // cell_size
        hash_val = np.sin(grid_y * 12.9898 + grid_x * 78.233) * 43758.5453
        return ((hash_val - np.floor(hash_val)) - 0.5) * intensity
    elif tex_type == 'sparkle':
        np.random.seed(123)
        return np.where(np.random.rand(height, width) > (1.0 - 0.08 * intensity), 0.8, 0.0)
    elif tex_type == 'veins':
        wave = np.sin(x_indices * 0.2 + np.cos(y_indices * 0.15) * 3.0)
        return np.where(np.abs(wave) < 0.35, 0.4, -0.15) * intensity
    else:
        np.random.seed(42)
        return (np.random.uniform(-0.3, 0.3, (height, width))) * intensity

def render_studio_all(arr, extra_hue=0):
    height, width, _ = arr.shape
    r_chan, g_chan, b_chan, alpha = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    lum = (0.299 * r_chan + 0.587 * g_chan + 0.114 * b_chan) / 255.0

    if use_orig_color:
        main_rgb = np.dstack((r_chan, g_chan, b_chan)).astype(np.float32)
        if (hue_shift + extra_hue) > 0:
            main_rgb = apply_hue_shift(main_rgb, (hue_shift + extra_hue) % 360)
        
        custom_alpha = alpha.astype(np.float32)
        out_rgb = main_rgb.astype(np.uint8)
        out_img = Image.fromarray(np.dstack((out_rgb, custom_alpha.astype(np.uint8))), mode="RGBA")
        glow_alpha = np.where((lum >= threshold) & (alpha > 0), alpha * glow_opacity, 0).astype(np.uint8)
        glow_img = Image.fromarray(np.dstack((out_rgb, glow_alpha)), mode="RGBA")
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
        c_nonglow = np.array(hex_to_rgb(non_glow_color), dtype=np.float32)
        c_glow = np.array(hex_to_rgb(glow_custom_color), dtype=np.float32)

        recolored_rgb = np.zeros((height, width, 3), dtype=np.float32)
        mask_low = final_lum < threshold
        
        factor_low = np.expand_dims(np.clip(final_lum / threshold, 0, 1), axis=-1)
        recolored_rgb += np.where(np.expand_dims(mask_low, axis=-1), c_shadow + factor_low * (c_nonglow - c_shadow), 0)

        mask_high = ~mask_low
        factor_high = np.expand_dims(np.clip((final_lum - threshold) / (1.0 - threshold), 0, 1), axis=-1)
        recolored_rgb += np.where(np.expand_dims(mask_high, axis=-1), c_nonglow + factor_high * (c_glow - c_nonglow), 0)

        total_hue = (hue_shift + extra_hue) % 360
        if total_hue > 0:
            recolored_rgb = apply_hue_shift(recolored_rgb, total_hue)

        out_rgb = np.clip(recolored_rgb, 0, 255).astype(np.uint8)
        
        alpha_float = alpha.astype(np.float32) / 255.0
        final_alpha_map = np.where(mask_low, alpha_float * non_glow_opacity, alpha_float * glow_opacity) * 255.0
        
        out_img = Image.fromarray(np.dstack((out_rgb, final_alpha_map.astype(np.uint8))), mode="RGBA")
        glow_alpha_map = np.where((final_lum >= threshold) & (alpha > 0), alpha_float * glow_opacity * 255.0, 0).astype(np.uint8)
        glow_img = Image.fromarray(np.dstack((out_rgb, glow_alpha_map)), mode="RGBA")

    if brightness != 1.0:
        out_img = ImageEnhance.Brightness(out_img).enhance(brightness)
    if enable_outline:
        out_img = add_border_to_image(out_img, color=(0,0,0,255), thickness=outline_thickness)

    return out_img, glow_img, lum, glow_alpha_map if 'glow_alpha_map' in locals() else glow_alpha

def generate_pulse_frame(out_img, glow_alpha, frame_idx, total_frames, p_intensity, motion_mode):
    if motion_mode == "360° Weapon Swing":
        return out_img.rotate((frame_idx / float(total_frames)) * 360.0, resample=Image.BICUBIC)
    elif motion_mode == "Floating / Bobbing Up-Down":
        offset_y = int(math.sin(2.0 * math.pi * (frame_idx / float(total_frames))) * 4.0 * p_intensity)
        w, h = out_img.size
        shifted = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        shifted.paste(out_img, (0, offset_y))
        return shifted
    return out_img

def create_spritesheet(frames, layout="Vertical (Terraria Style)", padding=0):
    if not frames: return None
    n = len(frames)
    fw, fh = frames[0].size
    
    if "Vertical" in layout:
        cols = 1
        rows = n
    else:
        cols = n
        rows = 1
        
    sheet = Image.new("RGBA", (cols * fw + (cols + 1) * padding, rows * fh + (rows + 1) * padding), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        r = idx // cols if "Vertical" in layout else 0
        c = idx % cols if "Vertical" in layout else idx
        sheet.paste(frame, (padding + c * (fw + padding), padding + r * (fh + padding)))
    return sheet

def generate_fitting_preview(sprite_img, slot_type):
    mannequin = Image.new("RGBA", (40, 56), (30, 20, 45, 255))
    head = Image.new("RGBA", (12, 12), (220, 170, 130, 255))
    body = Image.new("RGBA", (14, 18), (100, 100, 150, 255))
    legs = Image.new("RGBA", (12, 14), (60, 60, 80, 255))
    mannequin.paste(head, (14, 6))
    mannequin.paste(body, (13, 18))
    mannequin.paste(legs, (14, 36))
    fit_canvas = mannequin.copy()
    sp_w, sp_h = sprite_img.size
    fit_canvas.paste(sprite_img, (22, 16) if "Item" in slot_type else ((40 - sp_w)//2, (56 - sp_h)//2), sprite_img)
    return fit_canvas

def extract_palette_from_img(img_rgba, num_colors=6):
    colors = img_rgba.convert("RGB").getcolors(maxcolors=10000)
    if not colors: return []
    return [f"#{r:02x}{g:02x}{b:02x}" for count, (r, g, b) in sorted(colors, key=lambda x: x[0], reverse=True) if not (r < 10 and g < 10 and b < 10)][:num_colors]

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
rgb_shift_img, _, _, _ = render_studio_all(arr, extra_hue=120)

w, h = orig_img.size
orig_z = orig_img.resize((w * zoom, h * zoom), Image.NEAREST)
out_z = out_img.resize((w * zoom, h * zoom), Image.NEAREST)
glow_z = glow_img.resize((w * zoom, h * zoom), Image.NEAREST)
rgb_z = rgb_shift_img.resize((w * zoom, h * zoom), Image.NEAREST)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🖼️ Quad Matrix", 
    "🛡️ Character Fitting", 
    "📊 Sprite Sheet Builder", 
    "🎬 GIF Motion Studio", 
    "🔊 Audio Synth",
    "💾 Export Center"
])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.caption("1. Asli")
    col1.image(orig_z, use_container_width=True)
    col2.caption("2. Master FX")
    col2.image(out_z, use_container_width=True)
    col3.caption("3. Glowmask")
    col3.image(glow_z, use_container_width=True)
    col4.caption("4. RGB Shift")
    col4.image(rgb_z, use_container_width=True)

with tab2:
    st.subheader("🛡️ Terraria Character Fitting Preview")
    st.image(generate_fitting_preview(out_img, sprite_type).resize((40 * max(2, zoom), 56 * max(2, zoom)), Image.NEAREST))

with tab3:
    st.subheader("📊 Custom Sprite Sheet Generator")
    ss_col1, ss_col2 = st.columns(2)
    with ss_col1:
        sheet_layout_choice = st.selectbox("Format Layout Sheet:", ["Vertical (Terraria Style)", "Horizontal (1 Baris Melintang)"])
        frame_count = st.slider("Jumlah Frame Animasi:", 2, 20, 8)
    with ss_col2:
        st.info("Pilih format layout di atas sesuai kebutuhan game kamu.")

    if st.button("🚀 Generate Sprite Sheet", use_container_width=True):
        frames = [render_studio_all(arr, extra_hue=(i * (360 // frame_count)))[0] for i in range(frame_count)]
        ss_img = create_spritesheet(frames, layout=sheet_layout_choice)
        buf = io.BytesIO()
        ss_img.save(buf, format="PNG")
        st.session_state['ss_bytes'] = buf.getvalue()
    if 'ss_bytes' in st.session_state:
        st.image(Image.open(io.BytesIO(st.session_state['ss_bytes'])))
        st.download_button("💾 Download Sprite Sheet PNG", data=st.session_state['ss_bytes'], file_name="SpriteSheet.png", mime="image/png", use_container_width=True)

with tab4:
    st.subheader("🎬 GIF Motion Studio")
    if st.button("Preview Motion GIF 🎬", use_container_width=True):
        frames = [generate_pulse_frame(out_img, glow_alpha, i, 12, pulse_intensity, anim_motion_mode).resize((w * zoom, h * zoom), Image.NEAREST) for i in range(12)]
        buf = io.BytesIO()
        frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=90, loop=0)
        st.session_state['gif_bytes'] = buf.getvalue()
    if 'gif_bytes' in st.session_state:
        st.image(st.session_state['gif_bytes'])
        st.download_button("💾 Download Motion GIF", data=st.session_state['gif_bytes'], file_name="Motion.gif", mime="image/gif", use_container_width=True)

with tab5:
    st.subheader("🔊 FX-to-Audio Weapon Synthesizer")
    sample_rate = 22050
    t = np.linspace(0, 0.4, int(sample_rate * 0.4), endpoint=False)
    audio_data = np.int16(np.sin(2 * np.pi * 880.0 * t) * np.exp(-6.0 * t) * 32767)
    wav_io = io.BytesIO()
    import wave
    with wave.open(wav_io, 'w') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sample_rate); f.writeframes(audio_data.tobytes())
    st.audio(wav_io.getvalue(), format="audio/wav")
    st.download_button("💾 Download Efek Suara (.wav)", data=wav_io.getvalue(), file_name="SFX.wav", mime="image/png", use_container_width=True)

with tab6:
    st.subheader("💾 Export Center")
    extracted_colors = extract_palette_from_img(orig_img, num_colors=6)
    if extracted_colors:
        cols = st.columns(len(extracted_colors))
        for idx, hex_c in enumerate(extracted_colors):
            cols[idx].color_picker(f"C{idx+1}", hex_c, key=f"ex_{idx}")
    st.divider()
    buf = io.BytesIO()
    out_img.save(buf, format="PNG")
    st.download_button("💾 Download Main Sprite PNG", data=buf.getvalue(), file_name="TerrariaSprite_Main.png", mime="image/png", use_container_width=True)
