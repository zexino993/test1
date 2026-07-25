import io
import math
import numpy as np
from PIL import Image
import imageio
import streamlit as st

st.set_page_config(page_title="Dual Shader Master Studio", layout="wide")

st.title("⚔️ Dual PNG Shader Master Studio v4.0")
st.caption("Unggah gambar PNG transparan, gabungkan **2 FX Shader sekaligus**, dan unduh GIF animasi langsung dari server!")

# ==========================================
# 1. HELPER & SHADER CORE ENGINE (PYTHON NUMPY)
# ==========================================
def apply_single_shader(img_np, t, fx_type, speed, intensity, scale, hex_color):
    h, w, _ = img_np.shape
    y_idx, x_idx = np.indices((h, w), dtype=np.float32)
    uv_x = x_idx / max(1.0, w - 1.0)
    uv_y = y_idx / max(1.0, h - 1.0)
    
    hex_color = hex_color.lstrip('#')
    c_rgb = np.array([int(hex_color[i:i+2], 16) for i in (0, 2, 4)], dtype=np.float32)
    
    alpha = img_np[:, :, 3] / 255.0
    orig_rgb = img_np[:, :, :3].astype(np.float32)
    
    if "Lava" in fx_type:
        noise = np.sin(uv_x * scale + t * speed) * np.cos(uv_y * scale + t * speed)
        vein = np.clip(np.abs(noise), 0.1, 0.6)
        mask = np.expand_dims(vein * alpha, axis=-1)
        out_rgb = orig_rgb * (1.0 - mask) + (c_rgb * intensity) * mask

    elif "Hologram" in fx_type:
        scanline = (np.sin(uv_y * scale - t * speed * 3.0) * 0.5 + 0.5)**2
        mask = np.expand_dims(scanline * alpha, axis=-1)
        out_rgb = orig_rgb * 0.4 + (c_rgb * intensity) * mask

    elif "Shield" in fx_type:
        pulse = (math.sin(t * speed * 2.0) * 0.3 + 0.7) * intensity
        mask = np.expand_dims(alpha * pulse * 0.5, axis=-1)
        out_rgb = orig_rgb + c_rgb * mask

    elif "Rainbow" in fx_type:
        rainbow_phase = uv_x + uv_y + t * speed * 0.2
        r = (np.cos(rainbow_phase * 6.28 + 0.0) * 0.5 + 0.5) * 255.0
        g = (np.cos(rainbow_phase * 6.28 + 2.0) * 0.5 + 0.5) * 255.0
        b = (np.cos(rainbow_phase * 6.28 + 4.0) * 0.5 + 0.5) * 255.0
        rainbow_rgb = np.dstack((r, g, b)) * intensity
        mask = np.expand_dims(alpha * 0.6, axis=-1)
        out_rgb = orig_rgb * (1.0 - mask) + rainbow_rgb * mask

    elif "Frost" in fx_type:
        shard = np.abs(np.sin(uv_x * scale + uv_y * scale + t * speed))
        mask = np.expand_dims(shard * alpha * 0.7, axis=-1)
        out_rgb = orig_rgb * (1.0 - mask) + (c_rgb * intensity) * mask

    elif "Cosmic" in fx_type:
        dist_c = np.sqrt((uv_x - 0.5)**2 + (uv_y - 0.5)**2)
        swirl = np.sin(dist_c * scale - t * speed * 2.0) * 0.5 + 0.5
        mask = np.expand_dims(swirl * alpha * 0.7, axis=-1)
        out_rgb = orig_rgb * (1.0 - mask) + (c_rgb * intensity) * mask

    elif "Runic" in fx_type:
        grid = (np.sin(uv_x * scale) * np.sin(uv_y * scale) > 0.5).astype(np.float32)
        pulse = (math.sin(t * speed * 3.0) * 0.5 + 0.5)
        mask = np.expand_dims(grid * pulse * alpha, axis=-1)
        out_rgb = orig_rgb * (1.0 - mask) + (c_rgb * intensity) * mask

    elif "Glitch" in fx_type:
        glitch_time = math.floor(t * speed * 5.0)
        noise_shift = math.sin(uv_y[0, 0] * 50.0 + glitch_time) * 10.0
        out_rgb = np.roll(orig_rgb, int(noise_shift), axis=1) * intensity

    elif "Toxic" in fx_type:
        bubbles = np.sin(uv_x * scale) * np.cos(uv_y * scale + t * speed * 2.0)
        toxic_color = np.array([25.0, 230.0, 25.0], dtype=np.float32) * intensity
        mask = np.expand_dims(np.clip(np.abs(bubbles), 0.1, 0.7) * alpha, axis=-1)
        out_rgb = orig_rgb * (1.0 - mask) + toxic_color * mask

    else: # Gold Shimmer
        shimmer = (np.sin((uv_x + uv_y) * scale + t * speed * 3.0) * 0.5 + 0.5)**2
        mask = np.expand_dims(shimmer * alpha * 0.8, axis=-1)
        out_rgb = orig_rgb * (1.0 - mask) + (c_rgb * intensity) * mask

    out_rgb = np.clip(out_rgb, 0, 255).astype(np.uint8)
    return np.dstack((out_rgb, img_np[:, :, 3]))

def process_dual_shader_frame(img_array, t, 
                               fx1, speed1, int1, scale1, col1,
                               fx2, speed2, int2, scale2, col2,
                               blend_mode="Additive (Penjumlahan Glow)", blend_ratio=0.5):
    f1 = apply_single_shader(img_array, t, fx1, speed1, int1, scale1, col1)
    f2 = apply_single_shader(img_array, t, fx2, speed2, int2, scale2, col2)
    
    alpha = img_array[:, :, 3:4]
    rgb1 = f1[:, :, :3].astype(np.float32)
    rgb2 = f2[:, :, :3].astype(np.float32)
    orig_rgb = img_array[:, :, :3].astype(np.float32)
    
    if blend_mode == "Additive (Penjumlahan Glow)":
        diff1 = rgb1 - orig_rgb
        diff2 = rgb2 - orig_rgb
        out_rgb = orig_rgb + diff1 + diff2
    elif blend_mode == "Mix / Interpolate (Campur Rasio)":
        out_rgb = rgb1 * (1.0 - blend_ratio) + rgb2 * blend_ratio
    else: # Screen
        out_rgb = 255.0 - (255.0 - rgb1) * (255.0 - rgb2) / 255.0
        
    out_rgb = np.clip(out_rgb, 0, 255).astype(np.uint8)
    return np.dstack((out_rgb, alpha.squeeze(-1)))

# ==========================================
# 2. STREAMLIT SIDEBAR CONTROLS
# ==========================================
fx_options = [
    '🔥 Inner Lava / Magma Flow FX', '⚡ Sci-Fi Hologram FX', '🛡️ Outer Energy Shield FX',
    '🌈 Rainbow Chromatic FX', '❄️ Frost Glaze & Ice FX', '🌌 Cosmic Nebula Swirl FX',
    '📜 Runic Magic Energy FX', '👾 Cyberpunk Digital Glitch FX', '🟢 Toxic Acid / Slime FX',
    '✨ Celestial Golden Shimmer FX'
]

st.sidebar.header("📁 1. Input Gambar")
uploaded_file = st.sidebar.file_uploader("Upload PNG Transparan:", type=["png"])

if uploaded_file is not None:
    base_img = Image.open(uploaded_file).convert("RGBA")
    img_np = np.array(base_img)

    st.sidebar.markdown("---")
    st.sidebar.header("🔴 2. SHADER 1")
    fx1 = st.sidebar.selectbox("Efek Shader 1:", fx_options, index=0)
    col1 = st.sidebar.color_picker("Warna Utama 1:", "#FF3300")
    int1 = st.sidebar.slider("Intensitas Glow 1:", 0.0, 4.0, 1.8, 0.1)
    speed1 = st.sidebar.slider("Kecepatan 1:", 0.1, 5.0, 1.2, 0.1)
    scale1 = st.sidebar.slider("Skala Detail 1:", 1.0, 30.0, 12.0, 0.5)

    st.sidebar.markdown("---")
    st.sidebar.header("🔵 3. SHADER 2")
    fx2 = st.sidebar.selectbox("Efek Shader 2:", fx_options, index=1)
    col2 = st.sidebar.color_picker("Warna Utama 2:", "#00FFFF")
    int2 = st.sidebar.slider("Intensitas Glow 2:", 0.0, 4.0, 1.5, 0.1)
    speed2 = st.sidebar.slider("Kecepatan 2:", 0.1, 5.0, 2.0, 0.1)
    scale2 = st.sidebar.slider("Skala Detail 2:", 1.0, 30.0, 20.0, 0.5)

    st.sidebar.markdown("---")
    st.sidebar.header("🔀 4. BLENDING MODES")
    blend_mode = st.sidebar.selectbox("Mode Penggabungan:", ["Additive (Penjumlahan Glow)", "Mix / Interpolate (Campur Rasio)", "Screen (Cahaya Terang)"])
    blend_ratio = st.sidebar.slider("Rasio Pencampuran (Jika Mix Mode):", 0.0, 1.0, 0.5, 0.05)

    st.sidebar.markdown("---")
    st.sidebar.header("🎬 5. EXPORT GIF")
    gif_duration = st.sidebar.slider("Durasi GIF (Detik):", 1, 5, 2)
    gif_fps = st.sidebar.select_slider("Frame Rate (FPS):", options=[10, 12, 15, 20, 25], value=15)

    # ==========================================
    # 3. MAIN DASHBOARD VIEW
    # ==========================================
    col_v1, col_v2 = st.columns([1, 1])

    with col_v1:
        st.subheader("👁️ Live Frame Preview")
        # Render 1 Frame Cuplikan
        preview_frame = process_dual_shader_frame(
            img_np, t=0.5,
            fx1=fx1, speed1=speed1, int1=int1, scale1=scale1, col1=col1,
            fx2=fx2, speed2=speed2, int2=int2, scale2=scale2, col2=col2,
            blend_mode=blend_mode, blend_ratio=blend_ratio
        )
        st.image(preview_frame, use_container_width=True)

    with col_v2:
        st.subheader("🚀 Export Dual Shader GIF")
        st.write("Klik tombol di bawah ini untuk merender animasi secara langsung di server!")
        
        if st.button("🎬 Render & Buat GIF Sekarang", use_container_width=True):
            with st.spinner("⚙️ Sedang memproses semua frame animasi... Mohon tunggu sebentar."):
                total_frames = gif_duration * gif_fps
                frames = []
                
                for i in range(total_frames):
                    t = (i / float(total_frames)) * 2.0 * math.pi
                    frame = process_dual_shader_frame(
                        img_np, t=t,
                        fx1=fx1, speed1=speed1, int1=int1, scale1=scale1, col1=col1,
                        fx2=fx2, speed2=speed2, int2=int2, scale2=scale2, col2=col2,
                        blend_mode=blend_mode, blend_ratio=blend_ratio
                    )
                    frames.append(frame)

                # Simpan GIF ke RAM buffer
                gif_buffer = io.BytesIO()
                imageio.mimsave(gif_buffer, frames, format="GIF", fps=gif_fps, loop=0)
                gif_bytes = gif_buffer.getvalue()

            st.success("✅ Rendering selesai!")
            st.image(gif_bytes, caption="GIF Hasil Export", use_container_width=True)
            
            st.download_button(
                label="💾 Download Dual Shader GIF",
                data=gif_bytes,
                file_name="Terraria_Dual_Shader.gif",
                mime="image/gif",
                use_container_width=True
            )

else:
    st.info("👈 Silakan unggah gambar PNG transparan di menu Sidebar sebelah kiri untuk memulai studio!")
