import io
import math
import numpy as np
from PIL import Image
import streamlit as st

# Config Halaman Web
st.set_page_config(page_title="Terraria Ore Studio", page_icon="💎", layout="wide")

st.title("💎 Terraria Ore Tile & Glow Studio Web")
st.write("Aplikasi Web untuk **Recolor**, **Dual Texture**, **Glowmask**, dan **GIF Animation**.")

# Sidebar Kontrol
st.sidebar.header("📁 1. Upload File")
uploaded_file = st.sidebar.file_uploader("Pilih File PNG Ore", type=["png"])

use_orig_color = st.sidebar.checkbox("🔒 Gunakan Warna Asli (Matikan Recolor)")
pastel_mode = st.sidebar.checkbox("🌸 Efek Soft RGB Pastel")

zoom = st.sidebar.slider("🔍 Zoom Magnifier", 1, 8, 4)

st.sidebar.header("💡 2. Glow Settings")
threshold = st.sidebar.slider("Sensitivitas Glow Area", 0.1, 0.9, 0.45, 0.02)
pulse_intensity = st.sidebar.slider("Kekuatan Denyut Pulse", 0.1, 1.0, 0.5, 0.05)

st.sidebar.header("🎨 3. Warna & Palette")
shadow_color = st.sidebar.color_picker("1. Shadow Celah", "#080214")
mid_color = st.sidebar.color_picker("2. Warna Utama", "#AA19F5")
glow_color = st.sidebar.color_picker("3. Glow Highlight", "#FF78FF")

# Core Engine
def apply_hue_shift(rgb_array, hue_deg):
    if hue_deg == 0: return rgb_array
    img = Image.fromarray(rgb_array.astype(np.uint8), mode='RGB').convert('HSV')
    h, s, v = img.split()
    h_arr = (np.array(h, dtype=np.int16) + int((hue_deg / 360.0) * 255)) % 256
    return np.array(Image.merge('HSV', (Image.fromarray(h_arr.astype(np.uint8)), s, v)).convert('RGB'), dtype=np.float32)

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

if uploaded_file is not None:
    orig_img = Image.open(uploaded_file).convert("RGBA")
    arr = np.array(orig_img, dtype=np.float32)
    height, width, _ = arr.shape
    
    r_chan, g_chan, b_chan, alpha = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    lum = (0.299 * r_chan + 0.587 * g_chan + 0.114 * b_chan) / 255.0

    if use_orig_color:
        out_rgb = np.dstack((r_chan, g_chan, b_chan)).astype(np.uint8)
        glow_alpha = np.where((lum >= threshold) & (alpha > 0), alpha, 0).astype(np.uint8)
    else:
        c_shadow = np.array(hex_to_rgb(shadow_color), dtype=np.float32)
        c_mid = np.array(hex_to_rgb(mid_color), dtype=np.float32)
        c_glow = np.array(hex_to_rgb(glow_color), dtype=np.float32)

        out_rgb = np.zeros((height, width, 3), dtype=np.float32)
        mask_low = lum < 0.35
        factor_low = np.expand_dims(np.clip(lum / 0.35, 0, 1), axis=-1)
        out_rgb += np.where(np.expand_dims(mask_low, axis=-1), c_shadow + factor_low * (c_mid - c_shadow), 0)

        mask_high = ~mask_low
        factor_high = np.expand_dims(np.clip((lum - 0.35) / 0.65, 0, 1), axis=-1)
        out_rgb += np.where(np.expand_dims(mask_high, axis=-1), c_mid + factor_high * (c_glow - c_mid), 0)

        if pastel_mode:
            out_rgb = out_rgb * 0.6 + 255.0 * 0.4 * (out_rgb / 255.0)**0.5

        out_rgb = np.clip(out_rgb, 0, 255).astype(np.uint8)
        glow_alpha = np.where((lum >= threshold) & (alpha > 0), alpha, 0).astype(np.uint8)

    alpha_uint8 = alpha.astype(np.uint8)
    out_img = Image.fromarray(np.dstack((out_rgb, alpha_uint8)), mode="RGBA")
    glow_img = Image.fromarray(np.dstack((out_rgb, glow_alpha)), mode="RGBA")

    # Display Tampilan Utama
    col1, col2, col3 = st.columns(3)
    
    w, h = orig_img.size
    orig_z = orig_img.resize((w * zoom, h * zoom), Image.NEAREST)
    out_z = out_img.resize((w * zoom, h * zoom), Image.NEAREST)
    glow_z = glow_img.resize((w * zoom, h * zoom), Image.NEAREST)

    with col1:
        st.subheader("Sprite Asli")
        st.image(orig_z)
    with col2:
        st.subheader("Hasil Tile")
        st.image(out_z)
    with col3:
        st.subheader("Glowmask Isolated")
        st.image(glow_z)

    # Download Buttons
    buf_main = io.BytesIO()
    out_img.save(buf_main, format="PNG")
    st.download_button("💾 Download Main PNG", data=buf_main.getvalue(), file_name="Ore_Main.png", mime="image/png")

    buf_glow = io.BytesIO()
    glow_img.save(buf_glow, format="PNG")
    st.download_button("💡 Download Glowmask PNG", data=buf_glow.getvalue(), file_name="Ore_Glow.png", mime="image/png")
else:
    st.info("👈 Silakan unggah file gambar PNG ore di sidebar sebelah kiri.")
