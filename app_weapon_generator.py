import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io
import math
import zipfile

st.set_page_config(page_title="Terraria Weapon Master Studio v3.2 Pro", layout="wide")

st.title("🗡️ Terraria Weapon Master Studio v3.2 Pro")
st.caption("Studio Modder Terraria: Improved Custom Swing Arc FX, Download Terpisah Setiap Aset, Custom Layout, & Zip Package!")

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
    arm = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(arm)
    center = canvas_size // 2
    draw.rectangle([center - 6, center + 4, center + 6, center + 18], fill=(198, 134, 100, 160)) # Skin
    draw.rectangle([center - 7, center + 12, center + 7, center + 22], fill=(80, 100, 180, 160)) # Shirt
    return arm

def generate_improved_swing_arc(canvas_size, current_angle, arc_span, arc_radius_ratio, glow_color, arc_intensity):
    """Menghasilkan efek pendaran busur tebasan energi (Swing Arc) multi-layer yang halus dan profesional."""
    arc_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(arc_layer)
    center = canvas_size // 2
    
    radius = int(canvas_size * arc_radius_ratio)
    bbox = [center - radius, center - radius, center + radius, center + radius]
    
    # Hitung Rentang Sudut Tebasan
    # Sudut visual diurutkan agar mengikuti orientasi ayunan pedang Terraria
    start_deg = -current_angle - (arc_span / 2.0)
    end_deg = -current_angle + (arc_span / 2.0)
    
    c_hex = glow_color.lstrip('#')
    r_c, g_c, b_c = int(c_hex[0:2], 16), int(c_hex[2:4], 16), int(c_hex[4:6], 16)
    
    # 1. Outer Soft Glow Layers
    for i in range(3):
        w = int((6 + i * 4) * arc_intensity)
        alpha = int((140 - i * 35) * min(1.0, arc_intensity))
        draw.arc(bbox, start=start_deg, end=end_deg, fill=(r_c, g_c, b_c, alpha), width=max(1, w))
        
    # 2. Core Bright Hotspot Center
    draw.arc(bbox, start=start_deg, end=end_deg, fill=(255, 255, 255, int(220 * min(1.0, arc_intensity))), width=max(2, int(3 * arc_intensity)))
    
    # Blur halus untuk pendaran sihir
    arc_glow = arc_layer.filter(ImageFilter.GaussianBlur(radius=3))
    final_arc = Image.alpha_composite(arc_glow, arc_layer)
    
    return final_arc

def generate_weapon_frame(weapon_img, w_type, frame_idx, total_frames, pivot_x, pivot_y, canvas_size, glow_color, arc_intensity, arc_span, arc_rad_ratio, show_arm):
    frame = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    canvas_center = canvas_size // 2

    # Render Player Arm
    if show_arm:
        arm_layer = render_player_arm(canvas_size)
        frame = Image.alpha_composite(frame, arm_layer)

    # 1. SWORD SWING
    if w_type == "⚔️ Broadsword / Sword":
        angle = np.linspace(65, -65, total_frames)[frame_idx] + 45
        rotated = rotate_nearest_neighbor(weapon_img, angle)
        
        orig_cx, orig_cy = weapon_img.width / 2.0, weapon_img.height / 2.0
        rad = math.radians(-angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rx = (pivot_x - orig_cx) * cos_a - (pivot_y - orig_cy) * sin_a + (rotated.width / 2.0)
        ry = (pivot_x - orig_cx) * sin_a + (pivot_y - orig_cy) * cos_a + (rotated.height / 2.0)
        
        paste_x, paste_y = int(canvas_center - rx), int(canvas_center - ry)
        
        if arc_intensity > 0:
            arc_fx = generate_improved_swing_arc(canvas_size, angle, arc_span, arc_rad_ratio, glow_color, arc_intensity)
            frame = Image.alpha_composite(frame, arc_fx)

        frame.paste(rotated, (paste_x, paste_y), rotated)

    # 2. SPEAR THRUST
    elif w_type == "🔱 Spear / Polearm":
        angle = 45
        thrust_dist = np.sin((frame_idx / float(max(1, total_frames - 1))) * math.pi) * (canvas_size * 0.25)
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
            arc_fx = generate_improved_swing_arc(canvas_size, angle, 360, arc_rad_ratio, glow_color, arc_intensity)
            frame = Image.alpha_composite(frame, arc_fx)

        frame.paste(rotated, (paste_x, paste_y), rotated)

    # 4. YOYO SPIN
    else:
        angle = (frame_idx / float(total_frames)) * 180
        rotated = rotate_nearest_neighbor(weapon_img, angle)
        paste_x = canvas_center - (rotated.width // 2)
        paste_y = canvas_center - (rotated.height // 2)
        
        draw = ImageDraw.Draw(frame)
        draw.line([(0, canvas_size), (canvas_center, canvas_center)], fill=(220, 220, 220, 200), width=1)
        frame.paste(rotated, (paste_x, paste_y), rotated)

    return frame

def compile_custom_spritesheet(frames, frame_size, orientation, grid_value, padding_px):
    num_frames = len(frames)
    
    if orientation == "Horizontal Grid (Kiri ke Kanan)":
        cols = grid_value
        rows = math.ceil(num_frames / cols)
    elif orientation == "Vertical Grid (Atas ke Bawah)":
        rows = grid_value
        cols = math.ceil(num_frames / rows)
    elif orientation == "Horizontal Strip (1 Baris Horizontal)":
        cols = num_frames
        rows = 1
    else: # Vertical Strip
        cols = 1
        rows = num_frames

    total_w = (frame_size + padding_px) * cols + padding_px
    total_h = (frame_size + padding_px) * rows + padding_px
    
    sheet = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))

    for idx, frame in enumerate(frames):
        if orientation == "Horizontal Grid (Kiri ke Kanan)":
            r = idx // cols
            c = idx % cols
        elif orientation == "Vertical Grid (Atas ke Bawah)":
            c = idx // rows
            r = idx % rows
        elif orientation == "Horizontal Strip (1 Baris Horizontal)":
            r = 0
            c = idx
        else: # Vertical Strip
            r = idx
            c = 0
            
        pos_x = padding_px + c * (frame_size + padding_px)
        pos_y = padding_px + r * (frame_size + padding_px)
        sheet.paste(frame, (pos_x, pos_y))

    return sheet, cols, rows

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
    st.sidebar.header("✨ 4. Kustomisasi Swing Arc FX")
    enable_arc = st.sidebar.checkbox("Aktifkan Swing Arc FX", value=True)
    arc_color = st.sidebar.color_picker("Warna Pendaran Arc:", "#00FFFF")
    arc_power = st.sidebar.slider("Intensitas Cahaya Arc:", 0.0, 2.5, 1.2, 0.1)
    arc_span_deg = st.sidebar.slider("Sudut Panjang Busur Arc (°):", 30, 180, 90, 5)
    arc_radius_val = st.sidebar.slider("Jangkauan Radius Arc (% Canvas):", 20, 50, 42, 1) / 100.0

    st.sidebar.markdown("---")
    st.sidebar.header("🖼️ 5. Pengaturan Layout Sprite Sheet")
    sheet_orientation = st.sidebar.selectbox(
        "Arah Susunan (Orientasi Layout):",
        [
            "Horizontal Grid (Kiri ke Kanan)",
            "Vertical Grid (Atas ke Bawah)",
            "Horizontal Strip (1 Baris Horizontal)",
            "Vertical Strip (1 Kolom Vertikal)"
        ]
    )
    grid_limit = st.sidebar.slider("Jumlah Kolom/Baris Utama Grid:", 2, 8, 4) if "Grid" in sheet_orientation else 1
    padding_between_frames = st.sidebar.slider("Jarak Antar Frame (Padding Px):", 0, 16, 0)

    st.sidebar.markdown("---")
    st.sidebar.header("🪄 6. Glowmask Generator")
    enable_glowmask = st.sidebar.checkbox("Generate Glowmask", value=False)
    glow_threshold = st.sidebar.slider("Glow Threshold:", 50, 255, 180)

    st.sidebar.markdown("---")
    st.sidebar.header("🎬 7. Frame Export Settings")
    sheet_frames_count = st.sidebar.slider("Jumlah Frame Animasi:", 3, 12, 4)
    frame_canvas_size = st.sidebar.select_slider("Canvas Size per Frame (Px):", options=[64, 80, 96, 128], value=80)

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
        
        # FITUR DOWNLOAD TERPISAH: Single 45 Degree PNG
        buf_rot45 = io.BytesIO()
        rotated_45.save(buf_rot45, format="PNG")
        st.download_button(
            label="💾 Download PNG Senjata 45°",
            data=buf_rot45.getvalue(),
            file_name="Terraria_Item_45deg.png",
            mime="image/png",
            use_container_width=True
        )

    # GLOWMASK SECTION
    glow_45 = None
    if enable_glowmask:
        st.markdown("---")
        st.subheader("🪄 Glowmask Texture (`Item_Glow.png`)")
        col_g1, col_g2 = st.columns([1, 1])
        glow_img = generate_glowmask(src_image, threshold=glow_threshold)
        glow_45 = rotate_nearest_neighbor(glow_img, 45)
        
        with col_g1:
            st.image(glow_45, caption="Glowmask Only (Bagian Menyala)", use_container_width=True)
        with col_g2:
            st.write("Tekstur bagian menyala di tempat gelap untuk Terraria.")
            # FITUR DOWNLOAD TERPISAH: Glowmask PNG
            buf_glow = io.BytesIO()
            glow_45.save(buf_glow, format="PNG")
            st.download_button(
                label="💾 Download Glowmask PNG",
                data=buf_glow.getvalue(),
                file_name="Terraria_Item_Glow.png",
                mime="image/png",
                use_container_width=True
            )

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
    
    # FITUR DOWNLOAD TERPISAH: C# Script File
    st.download_button(
        label="💾 Download Script C# (.cs)",
        data=csharp_code,
        file_name="CustomWeapon.cs",
        mime="text/plain",
        use_container_width=False
    )

    # ANIMATED TRAJECTORY SHEET
    st.markdown("---")
    st.subheader("🎬 4. Multi-Type Weapon Trajectory & Custom Sprite Sheet")
    
    rendered_frames = [
        generate_weapon_frame(
            src_image, weapon_type, idx, sheet_frames_count, 
            pivot_x_px, pivot_y_px, frame_canvas_size, 
            arc_color, arc_power if enable_arc else 0.0, 
            arc_span_deg, arc_radius_val, show_dummy_arm
        )
        for idx in range(sheet_frames_count)
    ]

    cols_ui = st.columns(min(6, len(rendered_frames)))
    for i, frm in enumerate(rendered_frames):
        cols_ui[i % 6].image(frm, caption=f"Frame {i+1}")

    # Build Custom Sprite Sheet
    sprite_sheet, final_cols, final_rows = compile_custom_spritesheet(
        rendered_frames, frame_canvas_size, sheet_orientation, grid_limit, padding_between_frames
    )

    st.markdown(f"#### 🖼️ Custom Layout Sprite Sheet ({final_cols} Kolom x {final_rows} Baris):")
    st.image(sprite_sheet, caption=f"Sprite Sheet PNG ({sprite_sheet.width}x{sprite_sheet.height} px) - Orientasi: {sheet_orientation}", use_container_width=False)

    # FITUR DOWNLOAD TERPISAH: Sprite Sheet PNG
    buf_sheet = io.BytesIO()
    sprite_sheet.save(buf_sheet, format="PNG")
    st.download_button(
        label="💾 Download Sprite Sheet PNG",
        data=buf_sheet.getvalue(),
        file_name="Terraria_Weapon_SwingSheet.png",
        mime="image/png",
        use_container_width=True
    )

    # ALL-IN-ONE ZIP PACKAGE EXPORTER
    st.markdown("---")
    st.subheader("📦 5. Export Complete Mod Package (ZIP)")
    st.write("Atau unduh semua aset sekaligus dalam 1 file `.zip` ringkas:")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("CustomWeapon.png", buf_rot45.getvalue())
        if glow_45:
            zip_file.writestr("CustomWeapon_Glow.png", buf_glow.getvalue())
        zip_file.writestr("CustomWeapon_SwingSheet.png", buf_sheet.getvalue())
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
