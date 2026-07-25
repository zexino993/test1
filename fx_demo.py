# Install library yang dibutuhkan
!pip install pillow imageio numpy ipywidgets -q

import io
import math
import numpy as np
from PIL import Image
import imageio
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
from google.colab import files

print("✅ Library berhasil di-install!")
print("👇 Upload file PNG transparan kamu di bawah ini:")

# Upload File PNG
uploaded = files.upload()
if uploaded:
    filename = list(uploaded.keys())[0]
    base_img = Image.open(filename).convert("RGBA")
    img_np = np.array(base_img)
    print(f"\n🖼️ Gambar '{filename}' ({base_img.width}x{base_img.height} px) berhasil dimuat!")
else:
    raise Exception("⚠️ Harap unggah file PNG terlebih dahulu!")

# ==========================================
# SHADER ENGINE (SINGLE & DUAL BLENDING)
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
                               blend_mode="Additive", blend_ratio=0.5):
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
# INTERACTIVE UI WIDGETS
# ==========================================
fx_options = [
    '🔥 Inner Lava / Magma Flow FX', '⚡ Sci-Fi Hologram FX', '🛡️ Outer Energy Shield FX',
    '🌈 Rainbow Chromatic FX', '❄️ Frost Glaze & Ice FX', '🌌 Cosmic Nebula Swirl FX',
    '📜 Runic Magic Energy FX', '👾 Cyberpunk Digital Glitch FX', '🟢 Toxic Acid / Slime FX',
    '✨ Celestial Golden Shimmer FX'
]

# Shader 1 Widgets
st_fx1 = widgets.Dropdown(options=fx_options, value=fx_options[0], description='Shader 1:')
st_color1 = widgets.ColorPicker(value='#FF3300', description='Warna 1:')
st_int1 = widgets.FloatSlider(value=1.8, min=0.0, max=4.0, step=0.1, description='Intensitas 1:')
st_speed1 = widgets.FloatSlider(value=1.2, min=0.1, max=5.0, step=0.1, description='Speed 1:')
st_scale1 = widgets.FloatSlider(value=12.0, min=1.0, max=30.0, step=0.5, description='Skala 1:')

# Shader 2 Widgets
st_fx2 = widgets.Dropdown(options=fx_options, value=fx_options[1], description='Shader 2:')
st_color2 = widgets.ColorPicker(value='#00FFFF', description='Warna 2:')
st_int2 = widgets.FloatSlider(value=1.5, min=0.0, max=4.0, step=0.1, description='Intensitas 2:')
st_speed2 = widgets.FloatSlider(value=2.0, min=0.1, max=5.0, step=0.1, description='Speed 2:')
st_scale2 = widgets.FloatSlider(value=20.0, min=1.0, max=30.0, step=0.5, description='Skala 2:')

# Blending Controls
st_blend_mode = widgets.Dropdown(
    options=['Additive (Penjumlahan Glow)', 'Mix / Interpolate (Campur Rasio)', 'Screen (Cahaya Terang)'],
    value='Additive (Penjumlahan Glow)', description='Blend Mode:'
)
st_blend_ratio = widgets.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.05, description='Rasio Mix:')

# Export Controls
st_duration = widgets.IntSlider(value=2, min=1, max=5, step=1, description='Durasi (s):')
st_fps = widgets.SelectionSlider(options=[10, 12, 15, 20, 25], value=15, description='FPS:')

btn_render = widgets.Button(description='⚡ Render Dual Shader GIF', button_style='success', icon='download')
preview_output = widgets.Output()

def update_preview(*args):
    with preview_output:
        clear_output(wait=True)
        sample_frame = process_dual_shader_frame(
            img_np, t=0.5,
            fx1=st_fx1.value, speed1=st_speed1.value, int1=st_int1.value, scale1=st_scale1.value, col1=st_color1.value,
            fx2=st_fx2.value, speed2=st_speed2.value, int2=st_int2.value, scale2=st_scale2.value, col2=st_color2.value,
            blend_mode=st_blend_mode.value, blend_ratio=st_blend_ratio.value
        )
        img_preview = Image.fromarray(sample_frame)
        buf = io.BytesIO()
        img_preview.save(buf, format='PNG')
        display(HTML("<h4>👁️ Live Dual-Shader Preview:</h4>"))
        display(Image.open(buf))

for w in [st_fx1, st_color1, st_int1, st_speed1, st_scale1,
          st_fx2, st_color2, st_int2, st_speed2, st_scale2,
          st_blend_mode, st_blend_ratio]:
    w.observe(update_preview, 'value')

def on_render_click(b):
    with preview_output:
        print("\n⚙️ Rendering Dual-Shader GIF...")
        total_frames = st_duration.value * st_fps.value
        frames = []
        for i in range(total_frames):
            t = (i / float(total_frames)) * 2.0 * math.pi
            f = process_dual_shader_frame(
                img_np, t=t,
                fx1=st_fx1.value, speed1=st_speed1.value, int1=st_int1.value, scale1=st_scale1.value, col1=st_color1.value,
                fx2=st_fx2.value, speed2=st_speed2.value, int2=st_int2.value, scale2=st_scale2.value, col2=st_color2.value,
                blend_mode=st_blend_mode.value, blend_ratio=st_blend_ratio.value
            )
            frames.append(f)
            
        out_filename = "Dual_Shader_Combined.gif"
        imageio.mimsave(out_filename, frames, fps=st_fps.value, loop=0)
        print(f"✅ Selesai! Mengunduh {out_filename}...")
        files.download(out_filename)

btn_render.on_click(on_render_click)

panel_s1 = widgets.VBox([widgets.HTML("<b>🔴 SHADER 1:</b>"), st_fx1, st_color1, st_int1, st_speed1, st_scale1])
panel_s2 = widgets.VBox([widgets.HTML("<b>🔵 SHADER 2:</b>"), st_fx2, st_color2, st_int2, st_speed2, st_scale2])
panel_blend = widgets.VBox([widgets.HTML("<hr><b>🔀 BLENDING & EXPORT:</b>"), st_blend_mode, st_blend_ratio, st_duration, st_fps, widgets.HTML("<br>"), btn_render])

display(widgets.HBox([widgets.VBox([panel_s1, panel_s2, panel_blend]), preview_output]))
update_preview()
