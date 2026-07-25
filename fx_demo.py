import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="FX Shader Web Demo Studio", layout="wide")

st.title("✨ WebGL / .FX Shader Interactive Web Engine")
st.caption("Demo pemrosesan Pixel Shader secara real-time di browser menggunakan Python + WebGL Engine.")

# ==========================================
# 1. KONTROL PARAMETER SHADER (PYTHON UI)
# ==========================================
col_ctrl, col_view = st.columns([1, 2])

with col_ctrl:
    st.subheader("🎛️ Shader Controls")
    speed = st.slider("Animation Speed", 0.1, 5.0, 1.0, 0.1)
    wave_scale = st.slider("Wave Frequency / Scale", 1.0, 30.0, 10.0, 0.5)
    color_r = st.slider("Red Component", 0.0, 1.0, 0.5, 0.05)
    color_g = st.slider("Green Component", 0.0, 1.0, 0.2, 0.05)
    color_b = st.slider("Blue Component", 0.0, 1.0, 0.8, 0.05)

# ==========================================
# 2. WEBGL SHADER ENGINE (HTML / GLSL)
# ==========================================
html_shader_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; }}
        canvas {{ width: 100vw; height: 100vh; display: block; }}
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.min.js"></script>
    <script>
        const canvas = document.getElementById('canvas');
        const renderer = new THREE.WebGLRenderer({{ canvas }});
        renderer.setSize(window.innerWidth, window.innerHeight);

        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

        // KODE PIXEL SHADER (FRAGMENT SHADER - GLSL / .FX SIMULATION)
        const fragmentShader = `
            uniform float u_time;
            uniform float u_speed;
            uniform float u_scale;
            uniform vec3 u_color;
            varying vec2 vUv;

            void main() {{
                vec2 uv = vUv;
                
                // Kalkulasi gelombang distorsi FX (Simulasi Pixel Shader .FX)
                float wave = sin(uv.x * u_scale + u_time * u_speed) * cos(uv.y * u_scale + u_time * u_speed);
                float glow = 0.05 / abs(wave);

                vec3 finalColor = u_color * glow;
                gl_FragColor = vec4(finalColor, 1.0);
            }}
        `;

        const vertexShader = `
            varying vec2 vUv;
            void main() {{
                vUv = uv;
                gl_Position = vec4(position, 1.0);
            }}
        `;

        const uniforms = {{
            u_time: {{ value: 0.0 }},
            u_speed: {{ value: {speed} }},
            u_scale: {{ value: {wave_scale} }},
            u_color: {{ value: new THREE.Color({color_r}, {color_g}, {color_b}) }}
        }};

        const material = new THREE.ShaderMaterial({{
            vertexShader: vertexShader,
            fragmentShader: fragmentShader,
            uniforms: uniforms
        }});

        const geometry = new THREE.PlaneGeometry(2, 2);
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        function animate(time) {{
            uniforms.u_time.value = time * 0.001;
            renderer.render(scene, camera);
            requestAnimationFrame(animate);
        }}
        requestAnimationFrame(animate);
    </script>
</body>
</html>
"""

with col_view:
    st.subheader("📺 Real-time Shader Output Preview")
    components.html(html_shader_code, height=500)
