import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import io
import base64

st.set_page_config(page_title="2D PNG Shader Studio Demo", layout="wide")

st.title("🖼️ Custom PNG Sprite .FX Shader Engine")
st.caption("Unggah gambar PNG transparan milikmu dan terapkan efek Pixel Shader (`.fx` / WebGL) secara real-time!")

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

# Convert Color HEX to RGB (0.0 - 1.0)
color_hex_clean = fx_color.lstrip('#')
r_val = int(color_hex_clean[0:2], 16) / 255.0
g_val = int(color_hex_clean[2:4], 16) / 255.0
b_val = int(color_hex_clean[4:6], 16) / 255.0

# ==========================================
# 2. PROSES IMAGE BASE64 & SHADER ENGINE
# ==========================================
if uploaded_file is not None:
    # Convert uploaded image to Base64 for WebGL Texture Embedding
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
                
                // Jika piksel transparan, jangan di-render
                if (texColor.a < 0.1) {
                    discard;
                }

                // Kalkulasi Pola Lava di dalam Sprite
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
                if (texColor.a < 0.1) {
                    discard;
                }

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
                
                // Efek Aura Luar
                float pulse = sin(u_time * u_speed * 3.0) * 0.3 + 0.7;
                vec3 auraColor = u_color * u_intensity * pulse;

                if (texColor.a < 0.1) {
                    discard;
                }

                vec3 finalColor = mix(texColor.rgb, auraColor, 0.4);
                gl_FragColor = vec4(finalColor, texColor.a);
            }
        """
    else: # Rainbow Wave
        fragment_shader = """
            uniform sampler2D u_texture;
            uniform float u_time;
            uniform float u_speed;
            uniform float u_scale;
            uniform float u_intensity;
            varying vec2 vUv;

            void main() {
                vec4 texColor = texture2D(u_texture, vUv);
                if (texColor.a < 0.1) {
                    discard;
                }

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

    # HTML / WEBGL EMBED ENGINE
    html_png_shader_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; overflow: hidden; background: #0b0712; display: flex; justify-content: center; align-items: center; height: 100vh; }}
            canvas {{ max-width: 100%; max-height: 100%; display: block; image-rendering: pixelated; }}
        </style>
    </head>
    <body>
        <canvas id="canvas"></canvas>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            const canvas = document.getElementById('canvas');
            const renderer = new THREE.WebGLRenderer({{ canvas, antialias: true, alpha: true }});
            renderer.setPixelRatio(window.devicePixelRatio);

            const scene = new THREE.Scene();
            const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

            // Load PNG Texture from Base64
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

                renderer.setSize(window.innerWidth, window.innerHeight);

                const clock = new THREE.Clock();
                function animate() {{
                    requestAnimationFrame(animate);
                    uniforms.u_time.value = clock.getElapsedTime();
                    renderer.render(scene, camera);
                }}
                animate();
            }});
        </script>
    </body>
    </html>
    """

    with col_view:
        st.subheader("📺 Hasil Visual PNG + FX Shader")
        components.html(html_png_shader_code, height=550)

else:
    with col_view:
        st.info("👈 Silakan unggah gambar PNG transparan di menu sebelah kiri untuk melihat efek shader!")
