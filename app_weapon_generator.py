import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io
import math

st.set_page_config(page_title="Terraria Weapon Master Studio v2.0", layout="wide")

st.title("🗡️ Terraria Weapon Master Studio v2.0 Pro")
st.caption("Studio Lengkap Modder Terraria: Auto 45°, Grip Preset, Swing Arc FX, Glowmask Generator, dan Auto C# Code Snippet!")

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================
def rotate_nearest_neighbor(image, angle):
    return image.rotate(angle, resample=Image.NEAREST, expand=True)

def generate_glowmask(image, threshold=200):
    """Memisahkan bagian bercahaya berdasarkan tingkat kecerahan piksel."""
    img_np = np.array(image).copy()
    # Hitung Kecerahan (Luminance)
    rgb = img_np[:, :, :3].astype(np.float32)
    luminance = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    
    # Masking piksel yang di bawah threshold
    mask = luminance < threshold
    img_np[mask, 3] = 0 # Set alpha ke 0 untuk bagian gelap
    
    return Image.fromarray(img_np)

def generate_swing_arc_frame(weapon_img, angle, pivot_x, pivot_y, canvas_size, glow_color, arc_intensity):
    frame = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    rotated_weapon = rotate_nearest_neighbor(weapon_img, angle)
    
    orig_cx, orig_cy = weapon_img.width / 2.0, weapon_img.height / 2.0
    rot_w, rot_h = rotated_weapon.size
    
    rad = math.radians(-angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    rx = (pivot_x - orig_cx) * cos_a - (pivot_y - orig_cy) * sin_a + (rot_w / 2.0)
    ry = (pivot_x - orig_cx) * sin_a + (pivot_y - orig_cy) * cos_a + (rot_h / 2.0)
    
    canvas_center = canvas_size // 2
    paste_x = int(canvas_center - rx)
    paste_y = int(canvas_center - ry)
    
    if arc_intensity > 0:
        arc_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(arc_layer)
        
        c_hex = glow_color.lstrip('#')
        r_c, g_c, b_c = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
        
        radius = int(max(weapon_img.width, weapon_img.height) * 0.85)
        bbox = [canvas_center - radius, canvas_center - radius, canvas_center + radius, canvas_center + radius]
        
        draw.arc(bbox, start=-angle - 60, end=-angle + 10, fill=(r_c, g_c, b_c, int(200 * arc_intensity)), width=int(8 * arc_intensity))
        
        arc_glow = arc_layer.filter(ImageFilter.GaussianBlur(radius=2))
        frame = Image.alpha_composite(frame, arc_glow)
        frame = Image.alpha_composite(frame, arc_layer)

    frame.paste(rotated_weapon, (paste_x, paste_y), rotated_weapon)
    return frame

# ==========================================
# 2. SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("📁 1. Input Sprite Senjata")
uploaded_file = st.sidebar.file_uploader("Upload PNG Senjata:", type=["png"])

if uploaded_file is not None:
    src_image = Image.open(uploaded_file).convert("RGBA")
    
    st.sidebar.markdown("---")
    st.sidebar.header("📐 2. Grip & Pivot Presets")
    
    preset_choice = st.sidebar.radio("Pilih Jenis Senjata:", ["Custom", "🗡️ Dagger/Shortsword", "⚔️ Broadsword", "🔱 Spear/Polearm"])
    
    if preset_choice == "🗡️ Dagger/Shortsword":
        def_x, def_y = 15, 85
    elif preset_choice == "⚔️ Broadsword":
        def_x, def_y = 25, 75
    elif preset_choice == "🔱 Spear/Polearm":
        def_x, def_y = 40, 60
    else:
        def_x, def_y = 20, 80

    pivot_x_pct = st.sidebar.slider("Grip Posisi X (%):", 0, 100, def_x)
    pivot_y_pct = st.sidebar.slider("Grip Posisi Y (%):", 0, 100, def_y)

    pivot_x_px = int((pivot_x_pct / 100.0) * src_image.width)
    pivot_y_px = int((pivot_y_pct / 100.0) * src_image.height)

    st.sidebar.markdown("---")
    st.sidebar.header("🪄 3. Glowmask Generator")
    enable_glowmask = st.sidebar.checkbox("Aktifkan Fitur Glowmask", value=False)
    glow_threshold = st.sidebar.slider("Batas Kecerahan Glow Threshold:", 50, 255, 180)

    st.sidebar.markdown("---")
    st.sidebar.header("💫 4. FX Slash Arc & Animasi")
    enable_arc = st.sidebar.checkbox("Aktifkan Slash Arc FX", value=True)
    arc_color = st.sidebar.color_picker("Warna Arc:", "#00FFFF")
    arc_power = st.sidebar.slider("Intensitas Arc:", 0.0, 2.0, 1.0, 0.1)
    sheet_frames_count = st.sidebar.slider("Jumlah Frame:", 3, 6, 4)
    frame_canvas_size = st.sidebar.select_slider("Canvas Size (Px):", options=[64, 80, 96, 128], value=80)

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
        st.subheader("⚔️ 2. Hasil Rotasi 45° Terraria")
        rotated_45 = rotate_nearest_neighbor(src_image, 45)
        st.image(rotated_45, caption=f"Terraria Ready 45° ({rotated_45.width}x{rotated_45.height} px)", use_container_width=True)

    # GLOWMASK SECTION
    if enable_glowmask:
        st.markdown("---")
        st.subheader("🪄 Glowmask Texture Extraction (`Item_Glow.png`)")
        col_g1, col_g2 = st.columns([1, 1])
        glow_img = generate_glowmask(src_image, threshold=glow_threshold)
        glow_45 = rotate_nearest_neighbor(glow_img, 45)
        
        with col_g1:
            st.image(glow_45, caption="Glowmask Only (Bagian Menyala)", use_container_width=True)
        with col_g2:
            buf_glow = io.BytesIO()
            glow_45.save(buf_glow, format="PNG")
            st.download_button("💾 Download Glowmask Texture (Item_Glow.png)", data=buf_glow.getvalue(), file_name="Item_Glow.png", mime="image/png", use_container_width=True)

    # C# CODE SNIPPET GENERATOR
    st.markdown("---")
    st.subheader("💻 3. TModLoader C# Code Snippet")
    csharp_code = f"""using Terraria;
using Terraria.ID;
using Terraria.ModLoader;

namespace YourModName.Items
{{
    public class CustomWeapon : ModItem
    {{
        public override void SetDefaults()
        {{
            Item.width = {rotated_45.width};
            Item.height = {rotated_45.height};
            Item.useStyle = ItemUseStyleID.Swing;
            Item.useAnimation = 20;
            Item.useTime = 20;
            Item.damage = 50;
            Item.knockBack = 6f;
            Item.UseSound = SoundID.Item1;
            Item.autoReuse = true;
            Item.value = Item.buyPrice(gold: 1);
            Item.rare = ItemRarityID.Green;
        }}
    }}
}}"""
    st.code(csharp_code, language="csharp")

    # ANIMATED SWING SHEET GENERATOR
    st.markdown("---")
    st.subheader("🎬 4. Animated Swing Arc Sprite Sheet")
    angles_sequence = np.linspace(60, -60, sheet_frames_count)
    rendered_frames = [
        generate_swing_arc_frame(src_image, ang + 45, pivot_x_px, pivot_y_px, frame_canvas_size, arc_color, arc_power if enable_arc else 0.0)
        for ang in angles_sequence
    ]

    cols_ui = st.columns(len(rendered_frames))
    for i, frm in enumerate(rendered_frames):
        cols_ui[i].image(frm, caption=f"Frame {i+1}")

    sheet_w = frame_canvas_size * sheet_frames_count
    sprite_sheet = Image.new("RGBA", (sheet_w, frame_canvas_size), (0, 0, 0, 0))
    for idx, frame in enumerate(rendered_frames):
        sprite_sheet.paste(frame, (idx * frame_canvas_size, 0))

    st.image(sprite_sheet, caption=f"Sprite Sheet Strip ({sheet_w}x{frame_canvas_size} px)", use_container_width=False)
    
    buf_sheet = io.BytesIO()
    sprite_sheet.save(buf_sheet, format="PNG")
    st.download_button("💾 Download Complete Swing Sheet PNG", data=buf_sheet.getvalue(), file_name="Terraria_Weapon_Swing_Sheet.png", mime="image/png", use_container_width=True)

else:
    st.info("👈 Silakan unggah file gambar PNG senjata milikmu di menu sebelah kiri untuk memulai!")
