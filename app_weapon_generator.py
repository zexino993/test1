import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io
import math
import zipfile

st.set_page_config(page_title="Terraria Weapon Master Studio v3.0", layout="wide")

st.title("🗡️ Terraria Weapon Master Studio v3.0 Ultimate")
st.caption("Studio Modder Terraria: Player Arm Visualizer, Multi-Weapon Trajectory (Sword, Spear, Yoyo, Scythe), Glowmask, & Zip Exporter!")

# ==========================================
# 1. HELPER FUNCTIONS
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
    """Membuat dummy tangan karakter Terraria transparan."""
    arm = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(arm)
    center = canvas_size // 2
    # Gambar lengan piksel sederhana
    draw.rectangle([center - 6, center + 4, center + 6, center + 18], fill=(198, 134, 100, 160)) # Kulit
    draw.rectangle([center - 7, center + 12, center + 7, center + 22], fill=(80, 100, 180, 160)) # Baju
    return arm

def generate_weapon_frame(weapon_img, w_type, frame_idx, total_frames, pivot_x, pivot_y, canvas_size, glow_color, arc_intensity, show_arm):
    frame = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    canvas_center = canvas_size // 2

    # Render Player Arm
    if show_arm:
        arm_layer = render_player_arm(canvas_size)
        frame = Image.alpha_composite(frame, arm_layer)

    # 1. SWORD SWING (120 Deg Arc)
    if w_type == "⚔️ Broadsword / Sword":
        angle = np.linspace(60, -60, total_frames)[frame_idx] + 45
        rotated = rotate_nearest_neighbor(weapon_img, angle)
        
        orig_cx, orig_cy = weapon_img.width / 2.0, weapon_img.height / 2.0
        rad = math.radians(-angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rx = (pivot_x - orig_cx) * cos_a - (pivot_y - orig_cy) * sin_a + (rotated.width / 2.0)
        ry = (pivot_x - orig_cx) * sin_a + (pivot_y - orig_cy) * cos_a + (rotated.height / 2.0)
        
        paste_x, paste_y = int(canvas_center - rx), int(canvas_center - ry)
        
        if arc_intensity > 0:
            arc = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(arc)
            c_hex = glow_color.lstrip('#')
            r_c, g_c, b_c = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
            radius = int(max(weapon_img.width, weapon_img.height) * 0.85)
            bbox = [canvas_center - radius, canvas_center - radius, canvas_center + radius, canvas_center + radius]
            draw.arc(bbox, start=-angle - 60, end=-angle + 10, fill=(r_c, g_c, b_c, int(200 * arc_intensity)), width=int(8 * arc_intensity))
            frame = Image.alpha_composite(frame, arc.filter(ImageFilter.GaussianBlur(radius=2)))
            frame = Image.alpha_composite(frame, arc)

        frame.paste(rotated, (paste_x, paste_y), rotated)

    # 2. SPEAR THRUST (Linear Translation)
    elif w_type == "🔱 Spear / Polearm":
        angle = 45 # Tetap menghadap 45 derajat
        thrust_dist = np.sin((frame_idx / float(total_frames - 1)) * math.pi) * (canvas_size * 0.25)
        rotated = rotate_nearest_neighbor(weapon_img, angle)
        
        offset_x = int(thrust_dist * math.cos(math.radians(45)))
        offset_y = int(-thrust_dist * math.sin(math.radians(45)))
        
        paste_x = canvas_center - (rotated.width // 2) + offset_x
        paste_y = canvas_center - (rotated.height // 2) + offset_y
        frame.paste(rotated, (paste_x, paste_y), rotated)

    # 3. SCYTHE FULL SPIN (360 Deg)
    elif w_type == "🌙 Scythe / Axe (360° Spin)":
        angle = (frame_idx / float(total_frames)) * 360
        rotated = rotate_nearest_neighbor(weapon_img, angle)
        paste_x = canvas_center - (rotated.width // 2)
        paste_y = canvas_center - (rotated.height // 2)
        
        if arc_intensity > 0:
            arc = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(arc)
            c_hex = glow_color.lstrip('#')
            r_c, g_c, b_c = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
            radius = int(max(weapon_img.width, weapon_img.height) * 0.7)
            bbox = [canvas_center - radius, canvas_center - radius, canvas_center + radius, canvas_center + radius]
            draw.ellipse(bbox, outline=(r_c, g_c, b_c, int(180 * arc_intensity)), width=int(6 * arc_intensity))
            frame = Image.alpha_composite(frame, arc.filter(ImageFilter.GaussianBlur(radius=2)))

        frame.paste(rotated, (paste_x, paste_y), rotated)

    # 4. YOYO SPIN
    else:
        angle = (frame_idx / float(total_frames)) * 180
        rotated = rotate_nearest_neighbor(weapon_img, angle)
        paste_x = canvas_center - (rotated.width // 2)
        paste_y = canvas_center - (rotated.height // 2)
        
        # Gambar Benang Yoyo
        draw = ImageDraw.Draw(frame)
        draw.line([(0, canvas_size), (canvas_center, canvas_center)], fill=(220, 220, 220, 200), width=1)
        frame.paste(rotated, (paste_x, paste_y), rotated)

    return frame

# ==========================================
# 2. SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("📁 1. Input Sprite Senjata")
uploaded_file = st.sidebar.file_uploader("Upload PNG Senjata:", type=["png"])

if uploaded_file is not None:
    src_image = Image.open(uploaded_file).convert("RGBA")
    
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ 2. Tipe Senjata & Trajectory")
    weapon_type = st.sidebar.selectbox(
        "Kategori Senjata:",
        ["⚔️ Broadsword / Sword", "🔱 Spear / Polearm", "🌙 Scythe / Axe (360° Spin)", "🪀 Yoyo Spin"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.header("📐 3. Grip Pivot Position")
    pivot_x_pct = st.sidebar.slider("Grip Posisi X (%):", 0, 100, 25)
    pivot_y_pct = st.sidebar.slider("Grip Posisi Y (%):", 0, 100, 75)
    pivot_x_px = int((pivot_x_pct / 100.0) * src_image.width)
    pivot_y_px = int((pivot_y_pct / 100.0) * src_image.height)

    show_dummy_arm = st.sidebar.checkbox("Tampilkan Dummy Arm Karakter", value=True)

    st.sidebar.markdown("---")
    st.sidebar.header("🪄 4. Glowmask & FX")
    enable_glowmask = st.sidebar.checkbox("Generate Glowmask", value=False)
    glow_threshold = st.sidebar.slider("Glow Threshold:", 50, 255, 180)
    
    enable_arc = st.sidebar.checkbox("Aktifkan Trajectory FX", value=True)
    arc_color = st.sidebar.color_picker("Warna Trajectory FX:", "#00FFFF")
    arc_power = st.sidebar.slider("Intensitas FX:", 0.0, 2.0, 1.0, 0.1)

    st.sidebar.markdown("---")
    st.sidebar.header("🎬 5. Frame Export")
    sheet_frames_count = st.sidebar.slider("Jumlah Frame:", 3, 8, 4)
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
    glow_45 = None
    if enable_glowmask:
        st.markdown("---")
        st.subheader("🪄 Glowmask Texture (`Item_Glow.png`)")
        glow_img = generate_glowmask(src_image, threshold=glow_threshold)
        glow_45 = rotate_nearest_neighbor(glow_img, 45)
        st.image(glow_45, caption="Glowmask Only (Bagian Menyala)", use_container_width=False)

    # C# CODE GENERATOR
    st.markdown("---")
    st.subheader("💻 3. TModLoader C# Code Snippet")
    item_style = "ItemUseStyleID.Swing" if "Sword" in weapon_type or "Scythe" in weapon_type else ("ItemUseStyleID.Thrust" if "Spear" in weapon_type else "ItemUseStyleID.Shoot")
    
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
    }}
}}"""
    st.code(csharp_code, language="csharp")

    # ANIMATED TRAJECTORY SHEET
    st.markdown("---")
    st.subheader("🎬 4. Multi-Type Weapon Trajectory Animation")
    
    rendered_frames = [
        generate_weapon_frame(
            src_image, weapon_type, idx, sheet_frames_count, 
            pivot_x_px, pivot_y_px, frame_canvas_size, 
            arc_color, arc_power if enable_arc else 0.0, show_dummy_arm
        )
        for idx in range(sheet_frames_count)
    ]

    cols_ui = st.columns(len(rendered_frames))
    for i, frm in enumerate(rendered_frames):
        cols_ui[i].image(frm, caption=f"Frame {i+1}")

    sheet_w = frame_canvas_size * sheet_frames_count
    sprite_sheet = Image.new("RGBA", (sheet_w, frame_canvas_size), (0, 0, 0, 0))
    for idx, frame in enumerate(rendered_frames):
        sprite_sheet.paste(frame, (idx * frame_canvas_size, 0))

    st.image(sprite_sheet, caption=f"Sprite Sheet Strip ({sheet_w}x{frame_canvas_size} px)", use_container_width=False)

    # ALL-IN-ONE ZIP PACKAGE EXPORTER
    st.markdown("---")
    st.subheader("📦 5. Export Complete Mod Package (ZIP)")
    st.write("Unduh semua aset sekaligus (File PNG 45°, Glowmask, Sheet, dan Script C#) dalam 1 paket ZIP!")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Main Weapon PNG
        b_main = io.BytesIO()
        rotated_45.save(b_main, format="PNG")
        zip_file.writestr("CustomWeapon.png", b_main.getvalue())
        
        # 2. Glowmask PNG (If enabled)
        if glow_45:
            b_glow = io.BytesIO()
            glow_45.save(b_glow, format="PNG")
            zip_file.writestr("CustomWeapon_Glow.png", b_glow.getvalue())
            
        # 3. Sheet PNG
        b_sheet = io.BytesIO()
        sprite_sheet.save(b_sheet, format="PNG")
        zip_file.writestr("CustomWeapon_SwingSheet.png", b_sheet.getvalue())
        
        # 4. C# Code File
        zip_file.writestr("CustomWeapon.cs", csharp_code)

    st.download_button(
        label="📦 Download Complete Mod Package (.ZIP)",
        data=zip_buffer.getvalue(),
        file_name="Terraria_Mod_Weapon_Package.zip",
        mime="application/zip",
        use_container_width=True
    )

else:
    st.info("👈 Silakan unggah file gambar PNG senjata milikmu di menu sebelah kiri untuk memulai!")
