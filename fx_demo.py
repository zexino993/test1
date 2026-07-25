import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import io
import base64

st.set_page_config(page_title="2D PNG Shader Studio & GIF Exporter", layout="wide")

st.title("🖼️ Custom PNG Sprite .FX Shader & GIF Exporter")
st.caption("Unggah gambar PNG transparan, atur efek shader real-time, dan rekam hasilnya menjadi file GIF animasi!")

# ==========================================
# 1. INPUT FILE & SHADER CONTROLS
# ==========================================
col_ctrl, col_view = st.columns([1, 2])

with col_ctrl:
    st.subheader("📁 1. Input Gambar PNG")
    uploaded_file = st.file_uploader("Pilih File PNG Transparan:", type=["png"])

    st.markdown("---")
    st.subheader("🎛️ 2. Pengaturan Shader FX")
    
    fx_choice = st.selectbox(
        "Pilih Efek Shader:",
        [
            "🔥 Inner Lava / Magma Flow FX",
            "⚡ Sci-Fi Hologram & Scanlines FX",
            "🛡️ Outer Energy Shield Aura FX",
            "🌈 Rainbow Chromatic Shift FX"
        ]
    )

    anim_speed = st.slider("Kecepatan Animasi", 0.1, 5.0, 1.2, 0.1)
    glow_intensity = st.slider("Intensitas Cahaya (Glow Power)", 0.5, 4.0, 2.0, 0.1)
    scale_freq = st.slider("Frekuensi Gelombang / Skala", 1.0, 30.0, 12.0, 0.5)
    
    fx_color = st.color_picker("Warna Utama FX Shader:", "#FF3300" if "Lava" in fx_choice else "#00FFFF")

    st.markdown("---")
    st.subheader("🎬 3. Rekam GIF")
    gif_duration = st.slider("Durasi Rekaman GIF (Detik):", 1, 5, 2)

# Convert Color HEX to RGB (0.0 - 1.0)
color_hex_clean = fx_color.lstrip('#')
r_val = int(color_hex_clean[0:2], 16) / 255.0
g_val = int(color_hex_clean[2:4], 16) / 255.0
b_val = int(color_hex_clean[4:6], 16) / 255.0

# ==========================================
# 2. PROSES IMAGE BASE64 & SHADER ENGINE
# ==========================================
if uploaded_file is not None:
    input_image = Image.open(uploaded_file).convert("RGBA")
    buffered = io.BytesIO()
    input_image.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    img_data_url = f"data:image/png;base64,{img_b64}"

    # GLSL FRAGMENT SHADER LOGIC
    if "Lava" in fx_choice:
        fragment_shader = """
            uniform sampler2D u_texture;
            uniform float u_time;
            uniform float u_speed;
            uniform float u_scale;
            uniform float u_intensity;
            uniform vec3 u_color;
            varying vec2 vUv;

            void main() {
                vec4 texColor = texture2D(u_texture, vUv);
                if (texColor.a < 0.1) { discard; }

                float noise = sin(vUv.x * u_scale + u_time * u_speed) * cos(vUv.y * u_scale + u_time * u_speed);
                float vein = smoothstep(0.1, 0.5, abs(noise));
                
                vec3 magmaColor = mix(u_color * u_intensity, texColor.rgb * 0.3, vein);
                gl_FragColor = vec4(magmaColor, texColor.a);
            }
        """
    elif "Hologram" in fx_choice:
        fragment_shader = """
            uniform sampler2D u_texture;
            uniform float u_time;
            uniform float u_speed;
            uniform float u_scale;
            uniform float u_intensity;
            uniform vec3 u_color;
            varying vec2 vUv;

            void main() {
                vec4 texColor = texture2D(u_texture, vUv);
                if (texColor.a < 0.1) { discard; }

                float scanline = sin(vUv.y * u_scale - u_time * u_speed * 4.0) * 0.5 + 0.5;
                scanline = pow(scanline, 2.0) * u_intensity;

                vec3 holoColor = mix(texColor.rgb, u_color, 0.6) * (scanline + 0.5);
                gl_FragColor = vec4(holoColor, texColor.a * (scanline * 0.5 + 0.5));
            }
        """
    elif "Shield" in fx_choice:
        fragment_shader = """
            uniform sampler2D u_texture;
            uniform float u_time;
            uniform float u_speed;
            uniform float u_scale;
            uniform float u_intensity;
            uniform vec3 u_color;
            varying vec2 vUv;

            void main() {
                vec4 texColor = texture2D(u_texture, vUv);
                float pulse = sin(u_time * u_speed * 3.0) * 0.3 + 0.7;
                vec3 auraColor = u_color * u_intensity * pulse;

                if (texColor.a < 0.1) { discard; }

                vec3 finalColor = mix(texColor.rgb, auraColor, 0.4);
                gl_FragColor = vec4(finalColor, texColor.a);
            }
        """
    else: # Rainbow
        fragment_shader = """
            uniform sampler2D u_texture;
            uniform float u_time;
            uniform float u_speed;
            uniform float u_scale;
            uniform float u_intensity;
            varying vec2 vUv;

            void main() {
                vec4 texColor = texture2D(u_texture, vUv);
                if (texColor.a < 0.1) { discard; }

                float rainbow = vUv.x + vUv.y + u_time * u_speed * 0.5;
                vec3 rainbowColor = 0.5 + 0.5 * cos(rainbow * 6.28318 + vec3(0.0, 2.0, 4.0));

                vec3 finalColor = mix(texColor.rgb, rainbowColor * u_intensity, 0.6);
                gl_FragColor = vec4(finalColor, texColor.a);
            }
        """

    vertex_shader = """
        varying vec2 vUv;
        void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    """

    # HTML / WEBGL / CCAPTURE EMBED ENGINE
    html_png_shader_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; overflow: hidden; background: #0b0712; font-family: sans-serif; text-align: center; color: white; }}
            #container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }}
            canvas {{ max-width: 90%; max-height: 70vh; display: block; image-rendering: pixelated; margin-bottom: 15px; }}
            .btn {{
                background: linear-gradient(135deg, #8a2be2, #4b0082);
                color: white; border: 1px solid #d4a5ff; border-radius: 8px;
                padding: 10px 20px; font-weight: bold; cursor: pointer; font-size: 14px;
                transition: all 0.3s ease;
            }}
            .btn:hover {{ background: linear-gradient(135deg, #a34bfb, #6a0ded); box-shadow: 0 0 12px rgba(163, 75, 251, 0.6); }}
            #status {{ margin-top: 10px; font-size: 13px; color: #a3f3ff; font-weight: bold; }}
        </style>

        <!-- Library External Untuk Perekaman WebGL & Export GIF -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/ccapture.js@1.1.0/build/CCapture.all.min.js"></script>
    </head>
    <body>
        <div id="container">
            <canvas id="canvas"></canvas>
            <div>
                <button id="recBtn" class="btn" onclick="startRecording()">🔴 Rekam & Buat GIF ({gif_duration}s)</button>
            </div>
            <div id="status">Tampilan Real-time (Klik tombol di atas untuk mengunduh GIF)</div>
        </div>

        <script>
            const canvas = document.getElementById('canvas');
            const statusDiv = document.getElementById('status');
            const recBtn = document.getElementById('recBtn');

            const renderer = new THREE.WebGLRenderer({{ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true }});
            renderer.setPixelRatio(window.devicePixelRatio);

            const scene = new THREE.Scene();
            const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

            // Inisialisasi Perekam GIF (CCapture)
            const capturer = new CCapture({{
                format: 'gif',
                workersPath: 'https://cdn.jsdelivr.net/npm/ccapture.js@1.1.0/src/',
                framerate: 20,
                quality: 10
            }});

            let isRecording = false;
            let recordDuration = {gif_duration};
            let startTime = 0;

            const loader = new THREE.TextureLoader();
            loader.load('{img_data_url}', (texture) => {{
                texture.minFilter = THREE.NearestFilter;
                texture.magFilter = THREE.NearestFilter;

                const aspect = texture.image.width / texture.image.height;
                const geometry = new THREE.PlaneGeometry(aspect >= 1 ? 1.6 : 1.6 * aspect, aspect >= 1 ? 1.6 / aspect : 1.6);

                const uniforms = {{
                    u_texture: {{ value: texture }},
                    u_time: {{ value: 0.0 }},
                    u_speed: {{ value: {anim_speed} }},
                    u_scale: {{ value: {scale_freq} }},
                    u_intensity: {{ value: {glow_intensity} }},
                    u_color: {{ value: new THREE.Color({r_val}, {g_val}, {b_val}) }}
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

                renderer.setSize(400, 400);

                let simTime = 0;
                function animate() {{
                    requestAnimationFrame(animate);
                    
                    simTime += 0.03;
                    uniforms.u_time.value = simTime;
                    renderer.render(scene, camera);

                    if (isRecording) {{
                        capturer.capture(canvas);
                        let elapsed = (Date.now() - startTime) / 1000;
                        statusDiv.innerText = "⏳ Merekam Frame GPU: " + elapsed.toFixed(1) + "s / " + recordDuration + "s";
                        
                        if (elapsed >= recordDuration) {{
                            isRecording = false;
                            statusDiv.innerText = "⚙️ Mengompresi GIF... Mohon tunggu beberapa detik...";
                            recBtn.disabled = false;
                            capturer.stop();
                            capturer.save((blob) => {{
                                statusDiv.innerText = "✅ GIF Berhasil Diunduh!";
                            }});
                        }}
                    }}
                }}
                animate();
            }});

            function startRecording() {{
                isRecording = true;
                recBtn.disabled = true;
                startTime = Date.now();
                statusDiv.innerText = "🔴 Memulai Perekaman...";
                capturer.start();
            }}
        </script>
    </body>
    </html>
    """

    with col_view:
        st.subheader("📺 Hasil Visual & Modul Download GIF")
        components.html(html_png_shader_code, height=580)

else:
    with col_view:
        st.info("👈 Silakan unggah gambar PNG transparan di menu sebelah kiri untuk memulai studio & mengunduh GIF!")
