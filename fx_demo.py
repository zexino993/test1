import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import io
import base64

st.set_page_config(page_title="2D PNG Dual Shader Studio v3.4 Pro", layout="wide")

st.title("🖼️ Custom PNG Sprite Dual .FX Shader Studio v3.4")
st.caption("Unggah gambar PNG transparan, gabungkan **2 FX Shader sekaligus** secara real-time, dan rekam GIF!")

# ==========================================
# 1. INPUT FILE & DUAL SHADER CONTROLS
# ==========================================
col_ctrl, col_view = st.columns([1, 2])

fx_options = [
    "🔥 Inner Lava / Magma Flow FX",
    "⚡ Sci-Fi Hologram & Scanlines FX",
    "🛡️ Outer Energy Shield Aura FX",
    "🌈 Rainbow Chromatic Shift FX",
    "❄️ Frost Glaze & Ice Crystals FX",
    "🌌 Cosmic Nebula Swirl FX",
    "📜 Runic Magic Energy FX",
    "👾 Cyberpunk Digital Glitch FX",
    "🟢 Toxic Acid / Slime Bubbles FX",
    "✨ Celestial Golden Shimmer FX"
]

with col_ctrl:
    st.subheader("📁 1. Input Gambar PNG")
    uploaded_file = st.file_uploader("Pilih File PNG Transparan:", type=["png"])

    st.markdown("---")
    st.subheader("🔴 2. Pengaturan Shader 1")
    fx_choice_1 = st.selectbox("Pilih Shader 1:", fx_options, index=0)
    anim_speed_1 = st.slider("Kecepatan Shader 1", 0.1, 5.0, 1.2, 0.1, key="spd1")
    glow_intensity_1 = st.slider("Intensitas Cahaya (Glow Power 1)", 0.0, 4.0, 1.8, 0.1, key="int1")
    scale_freq_1 = st.slider("Frekuensi / Skala Detail 1", 1.0, 30.0, 12.0, 0.5, key="scl1")
    fx_color_1 = st.color_picker("Warna Utama Shader 1:", "#FF3300", key="col1")

    st.markdown("---")
    st.subheader("🔵 3. Pengaturan Shader 2")
    fx_choice_2 = st.selectbox("Pilih Shader 2:", fx_options, index=1)
    anim_speed_2 = st.slider("Kecepatan Shader 2", 0.1, 5.0, 2.0, 0.1, key="spd2")
    glow_intensity_2 = st.slider("Intensitas Cahaya (Glow Power 2)", 0.0, 4.0, 1.5, 0.1, key="int2")
    scale_freq_2 = st.slider("Frekuensi / Skala Detail 2", 1.0, 30.0, 20.0, 0.5, key="scl2")
    fx_color_2 = st.color_picker("Warna Utama Shader 2:", "#00FFFF", key="col2")

    st.markdown("---")
    st.subheader("🔀 4. Mode Penggabungan (Blending)")
    blend_mode_choice = st.selectbox(
        "Mode Blending Dual Shader:",
        ["Additive (Penjumlahan Glow)", "Mix / Interpolate (Campur Rasio)", "Screen (Cahaya Terang)"]
    )
    blend_ratio_val = st.slider("Rasio Campuran (Khusus Mode Mix)", 0.0, 1.0, 0.5, 0.05)

    st.markdown("---")
    st.subheader("🎬 5. Rekam GIF Fast")
    gif_duration = st.slider("Durasi Rekaman GIF (Detik):", 1, 5, 2)
    gif_fps = st.select_slider("Frame Rate (FPS):", options=[10, 12, 15, 20], value=15)

# Convert Colors HEX to RGB (0.0 - 1.0)
def hex_to_rgb_norm(hex_str):
    c = hex_str.lstrip('#')
    return int(c[0:2], 16) / 255.0, int(c[2:4], 16) / 255.0, int(c[4:6], 16) / 255.0

r1, g1, b1 = hex_to_rgb_norm(fx_color_1)
r2, g2, b2 = hex_to_rgb_norm(fx_color_2)

# Map Blending Mode
blend_mode_id = 0 if "Additive" in blend_mode_choice else (1 if "Mix" in blend_mode_choice else 2)

# ==========================================
# 2. PROSES IMAGE BASE64 & DUAL GLSL SHADER ENGINE
# ==========================================
if uploaded_file is not None:
    input_image = Image.open(uploaded_file).convert("RGBA")
    buffered = io.BytesIO()
    input_image.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    img_data_url = f"data:image/png;base64,{img_b64}"

    # GLSL COMPACT HELPER FUNCTIONS FOR SHADERS
    glsl_helpers = """
        vec3 getLava(vec2 uv, float t, float spd, float scl, float intns, vec3 col, vec3 orig) {
            float noise = sin(uv.x * scl + t * spd) * cos(uv.y * scl + t * spd);
            float vein = smoothstep(0.1, 0.5, abs(noise));
            return mix(col * intns, orig * 0.3, vein);
        }
        vec3 getHologram(vec2 uv, float t, float spd, float scl, float intns, vec3 col, vec3 orig) {
            float scanline = sin(uv.y * scl - t * spd * 4.0) * 0.5 + 0.5;
            scanline = pow(scanline, 2.0) * intns;
            return mix(orig, col, 0.6) * (scanline + 0.5);
        }
        vec3 getShield(vec2 uv, float t, float spd, float scl, float intns, vec3 col, vec3 orig) {
            float pulse = sin(t * spd * 3.0) * 0.3 + 0.7;
            vec3 auraColor = col * intns * pulse;
            return mix(orig, auraColor, 0.4);
        }
        vec3 getRainbow(vec2 uv, float t, float spd, float intns, vec3 orig) {
            float rainbow = uv.x + uv.y + t * spd * 0.5;
            vec3 rainbowColor = 0.5 + 0.5 * cos(rainbow * 6.28318 + vec3(0.0, 2.0, 4.0));
            return mix(orig, rainbowColor * intns, 0.6);
        }
        vec3 getFrost(vec2 uv, float t, float spd, float scl, float intns, vec3 col, vec3 orig) {
            float shard = abs(sin(uv.x * scl + uv.y * scl + t * spd));
            return mix(orig, col * intns, shard * 0.7);
        }
        vec3 getCosmic(vec2 uv, float t, float spd, float scl, float intns, vec3 col, vec3 orig) {
            float dist = distance(uv, vec2(0.5, 0.5));
            float swirl = sin(dist * scl - t * spd * 2.0);
            vec3 cosmicColor = mix(col * intns, vec3(0.1, 0.0, 0.2), swirl * 0.5 + 0.5);
            return mix(orig, cosmicColor, 0.7);
        }
        vec3 getRunic(vec2 uv, float t, float spd, float scl, float intns, vec3 col, vec3 orig) {
            float grid = step(0.85, sin(uv.x * scl) * sin(uv.y * scl));
            float pulse = sin(t * spd * 3.0) * 0.5 + 0.5;
            return mix(orig, col * intns, grid * pulse);
        }
        vec3 getGlitch(vec2 uv, float t, float spd, float intns, sampler2D tex) {
            float glitchTime = floor(t * spd * 10.0);
            float noise = sin(uv.y * 50.0 + glitchTime) * 0.01;
            return texture2D(tex, vec2(uv.x + noise, uv.y)).rgb * intns;
        }
        vec3 getToxic(vec2 uv, float t, float spd, float scl, float intns, vec3 orig) {
            float bubbles = sin(uv.x * scl) * cos(uv.y * scl + t * spd * 2.0);
            return mix(vec3(0.1, 0.9, 0.1) * intns, orig, smoothstep(0.2, 0.8, abs(bubbles)));
        }
        vec3 getGold(vec2 uv, float t, float spd, float scl, float intns, vec3 col, vec3 orig) {
            float shimmer = sin((uv.x + uv.y) * scl + t * spd * 3.0) * 0.5 + 0.5;
            return mix(orig, col * intns, pow(shimmer, 2.0) * 0.8);
        }

        vec3 computeShader(int type, vec2 uv, float t, float spd, float scl, float intns, vec3 col, vec3 orig, sampler2D tex) {
            if (type == 0) return getLava(uv, t, spd, scl, intns, col, orig);
            if (type == 1) return getHologram(uv, t, spd, scl, intns, col, orig);
            if (type == 2) return getShield(uv, t, spd, scl, intns, col, orig);
            if (type == 3) return getRainbow(uv, t, spd, intns, orig);
            if (type == 4) return getFrost(uv, t, spd, scl, intns, col, orig);
            if (type == 5) return getCosmic(uv, t, spd, scl, intns, col, orig);
            if (type == 6) return getRunic(uv, t, spd, scl, intns, col, orig);
            if (type == 7) return getGlitch(uv, t, spd, intns, tex);
            if (type == 8) return getToxic(uv, t, spd, scl, intns, orig);
            return getGold(uv, t, spd, scl, intns, col, orig);
        }
    """

    def get_fx_id(fx_name):
        return fx_options.index(fx_name)

    fx_id_1 = get_fx_id(fx_choice_1)
    fx_id_2 = get_fx_id(fx_choice_2)

    fragment_shader = f"""
        uniform sampler2D u_texture;
        uniform float u_time;
        
        uniform int u_type1;
        uniform float u_speed1;
        uniform float u_scale1;
        uniform float u_intensity1;
        uniform vec3 u_color1;

        uniform int u_type2;
        uniform float u_speed2;
        uniform float u_scale2;
        uniform float u_intensity2;
        uniform vec3 u_color2;

        uniform int u_blendMode;
        uniform float u_blendRatio;

        varying vec2 vUv;

        {glsl_helpers}

        void main() {{
            vec4 texColor = texture2D(u_texture, vUv);
            if (texColor.a < 0.1) {{ discard; }}

            vec3 origRgb = texColor.rgb;

            vec3 rgb1 = computeShader(u_type1, vUv, u_time, u_speed1, u_scale1, u_intensity1, u_color1, origRgb, u_texture);
            vec3 rgb2 = computeShader(u_type2, vUv, u_time, u_speed2, u_scale2, u_intensity2, u_color2, origRgb, u_texture);

            vec3 finalRgb = origRgb;

            if (u_blendMode == 0) {{ // Additive
                vec3 diff1 = rgb1 - origRgb;
                vec3 diff2 = rgb2 - origRgb;
                finalRgb = origRgb + diff1 + diff2;
            }} else if (u_blendMode == 1) {{ // Mix
                finalRgb = mix(rgb1, rgb2, u_blendRatio);
            }} else {{ // Screen
                finalRgb = 1.0 - (1.0 - rgb1) * (1.0 - rgb2);
            }}

            gl_FragColor = vec4(clamp(finalRgb, 0.0, 1.0), texColor.a);
        }}
    """

    vertex_shader = """
        varying vec2 vUv;
        void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    """

    # HTML / WEBGL DUAL SHADER ENGINE DENGAN OMGIF EXPORTER
    html_png_shader_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; overflow: hidden; background: #0b0712; font-family: sans-serif; text-align: center; color: white; }}
            #container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }}
            canvas {{ width: 320px; height: 320px; display: block; image-rendering: pixelated; margin-bottom: 12px; border: 1px solid #3a1c5d; border-radius: 8px; background: #110822; }}
            .btn {{
                background: linear-gradient(135deg, #8a2be2, #4b0082);
                color: white; border: 1px solid #d4a5ff; border-radius: 8px;
                padding: 10px 20px; font-weight: bold; cursor: pointer; font-size: 14px;
                transition: all 0.3s ease;
            }}
            .btn:hover {{ background: linear-gradient(135deg, #a34bfb, #6a0ded); box-shadow: 0 0 12px rgba(163, 75, 251, 0.6); }}
            #status {{ margin-top: 10px; font-size: 13px; color: #a3f3ff; font-weight: bold; }}
        </style>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/omggif@1.0.10/omggif.min.js"></script>
    </head>
    <body>
        <div id="container">
            <canvas id="canvas"></canvas>
            <div>
                <button id="recBtn" class="btn" onclick="startRecording()">⚡ Rekam & Buat Fast GIF ({gif_duration}s @ {gif_fps}fps)</button>
            </div>
            <div id="status">Tampilan Real-time (Klik tombol di atas untuk mengunduh GIF)</div>
        </div>

        <script>
            const canvas = document.getElementById('canvas');
            const statusDiv = document.getElementById('status');
            const recBtn = document.getElementById('recBtn');

            const renderer = new THREE.WebGLRenderer({{ canvas: canvas, antialias: true, alpha: true, preserveDrawingBuffer: true }});
            renderer.setSize(320, 320);
            renderer.setPixelRatio(1);

            const scene = new THREE.Scene();
            const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

            let isRecording = false;
            let recordDuration = {gif_duration};
            let fps = {gif_fps};
            let frameCount = recordDuration * fps;
            let recordedFrames = [];
            let simTime = 0;

            const loader = new THREE.TextureLoader();
            loader.load('{img_data_url}', function(texture) {{
                texture.minFilter = THREE.NearestFilter;
                texture.magFilter = THREE.NearestFilter;

                const aspect = texture.image.width / texture.image.height;
                const geometry = new THREE.PlaneGeometry(aspect >= 1 ? 1.6 : 1.6 * aspect, aspect >= 1 ? 1.6 / aspect : 1.6);

                const uniforms = {{
                    u_texture: {{ value: texture }},
                    u_time: {{ value: 0.0 }},
                    
                    u_type1: {{ value: {fx_id_1} }},
                    u_speed1: {{ value: {anim_speed_1} }},
                    u_scale1: {{ value: {scale_freq_1} }},
                    u_intensity1: {{ value: {glow_intensity_1} }},
                    u_color1: {{ value: new THREE.Color({r1}, {g1}, {b1}) }},

                    u_type2: {{ value: {fx_id_2} }},
                    u_speed2: {{ value: {anim_speed_2} }},
                    u_scale2: {{ value: {scale_freq_2} }},
                    u_intensity2: {{ value: {glow_intensity_2} }},
                    u_color2: {{ value: new THREE.Color({r2}, {g2}, {b2}) }},

                    u_blendMode: {{ value: {blend_mode_id} }},
                    u_blendRatio: {{ value: {blend_ratio_val} }}
                }};

                const material = new THREE.ShaderMaterial({{
                    vertexShader: `{vertex_shader}`,
                    fragmentShader: `{fragment_shader}`,
                    uniforms: uniforms,
                    transparent: true,
                    side: THREE.DoubleSide
                }});

                const mesh = new THREE.Mesh(geometry, material);
                scene.add(mesh);

                function animate() {{
                    requestAnimationFrame(animate);
                    
                    if (!isRecording) {{
                        simTime += 0.03;
                        uniforms.u_time.value = simTime;
                        renderer.render(scene, camera);
                    }}
                }}
                animate();

                window.processRecording = function() {{
                    let currentFrame = 0;
                    recordedFrames = [];
                    let deltaT = 0.05;

                    function captureNext() {{
                        if (currentFrame < frameCount) {{
                            simTime += deltaT;
                            uniforms.u_time.value = simTime;
                            renderer.render(scene, camera);

                            let gl = renderer.getContext();
                            let pixels = new Uint8Array(320 * 320 * 4);
                            gl.readPixels(0, 0, 320, 320, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
                            recordedFrames.push(pixels);

                            currentFrame++;
                            statusDiv.innerText = "⚡ Perekaman GPU Dual-Shader: " + currentFrame + " / " + frameCount + " Frame";
                            setTimeout(captureNext, 10);
                        }} else {{
                            statusDiv.innerText = "⚙️ Mengompresi GIF Dual-Shader... Mohon tunggu.";
                            setTimeout(compileGIF, 50);
                        }}
                    }}
                    captureNext();
                }};
            }});

            function startRecording() {{
                if (isRecording) return;
                isRecording = true;
                recBtn.disabled = true;
                statusDiv.innerText = "⚡ Memulai Perekaman...";
                window.processRecording();
            }}

            function compileGIF() {{
                const width = 320;
                const height = 320;
                let gifBuffer = new Uint8Array(width * height * frameCount * 5);
                let gifWriter = new omggif.GifWriter(gifBuffer, width, height, {{ loop: 0 }});

                let palette = [];
                for (let r = 0; r < 8; r++) {{
                    for (let g = 0; g < 8; g++) {{
                        for (let b = 0; b < 4; b++) {{
                            palette.push((r * 36 << 16) | (g * 36 << 8) | (b * 85));
                        }}
                    }}
                }}

                for (let f = 0; f < recordedFrames.length; f++) {{
                    let pixels = recordedFrames[f];
                    let indexedPixels = new Uint8Array(width * height);
                    
                    for (let y = 0; y < height; y++) {{
                        for (let x = 0; x < width; x++) {{
                            let srcIdx = ((height - 1 - y) * width + x) * 4;
                            let dstIdx = y * width + x;
                            
                            let r = pixels[srcIdx];
                            let g = pixels[srcIdx + 1];
                            let b = pixels[srcIdx + 2];
                            
                            let rIdx = Math.min(7, Math.floor(r / 32));
                            let gIdx = Math.min(7, Math.floor(g / 32));
                            let bIdx = Math.min(3, Math.floor(b / 64));
                            
                            indexedPixels[dstIdx] = (rIdx * 32) + (gIdx * 4) + bIdx;
                        }}
                    }}
                    
                    gifWriter.addFrame(0, 0, width, height, indexedPixels, {{
                        palette: palette,
                        delay: Math.round(100 / fps)
                    }});
                }}

                let realLen = gifWriter.end();
                let finalBlob = new Blob([gifBuffer.subarray(0, realLen)], {{ type: 'image/gif' }});
                let downloadUrl = URL.createObjectURL(finalBlob);
                
                let a = document.createElement('a');
                a.href = downloadUrl;
                a.download = "Terraria_Dual_Shader_FX.gif";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);

                isRecording = false;
                recBtn.disabled = false;
                statusDiv.innerText = "✅ GIF Dual-Shader Berhasil Diunduh!";
            }}
        </script>
    </body>
    </html>
    """

    with col_view:
        st.subheader("📺 Hasil Visual Dual Shader & Fast GIF Generator")
        components.html(html_png_shader_code, height=520)

else:
    with col_view:
        st.info("👈 Silakan unggah gambar PNG transparan di menu sebelah kiri untuk memulai studio & mengunduh GIF!")
