import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D FX Shader Studio Demo", layout="wide")

st.title("⚔️ 3D .FX Shader Interactive Web Engine")
st.caption("Uji coba penerapan Pixel & Vertex Shader pada **Objek 3D Nyata** secara interaktif di web.")

# ==========================================
# 1. KONTROL PARAMETER SHADER & OBJEK 3D
# ==========================================
col_ctrl, col_view = st.columns([1, 2])

with col_ctrl:
    st.subheader("🎛️ Objek & Shader Controls")
    
    obj_type = st.selectbox(
        "Pilih Objek 3D Target:",
        ["⚔️ Pedang / Senjata 3D (Broadsword)", "🌀 Torus Knot (Cincin Magis)", "🔮 Sphere (Bola Kristal)", "📦 Cube (Kubus Energi)"]
    )
    
    fx_type = st.selectbox(
        "Pilih Efek Shader (.FX Effect):",
        ["🔥 Magma Lava Veins FX", "⚡ Sci-Fi Hologram Scanlines FX", "🛡️ Energy Shield Forcefield FX"]
    )
    
    st.markdown("---")
    st.markdown("##### 🎚️ Parameter Adjustment")
    anim_speed = st.slider("Kecepatan Animasi Shader", 0.1, 5.0, 1.2, 0.1)
    intensity = st.slider("Intensitas Cahaya (Glow Power)", 0.5, 4.0, 2.0, 0.1)
    scale_freq = st.slider("Frekuensi Gelombang / Skala Detail", 1.0, 30.0, 12.0, 0.5)
    
    st.markdown("---")
    color_hex = st.color_picker("Warna Utama FX Shader:", "#FF3300" if "Magma" in fx_type else "#00FFFF")

# Convert Color HEX to Normalized RGB
color_hex_clean = color_hex.lstrip('#')
r_val = int(color_hex_clean[0:2], 16) / 255.0
g_val = int(color_hex_clean[2:4], 16) / 255.0
b_val = int(color_hex_clean[4:6], 16) / 255.0

# ==========================================
# 2. SHADER ENGINE CODE (GLSL / THREE.JS)
# ==========================================
# GLSL Shader Code Mapping
if "Magma" in fx_type:
    fragment_shader = """
        uniform float u_time;
        uniform float u_speed;
        uniform float u_scale;
        uniform float u_intensity;
        uniform vec3 u_color;
        varying vec3 vPosition;
        varying vec3 vNormal;

        void main() {
            vec3 norm = normalize(vNormal);
            float noise = sin(vPosition.x * u_scale + u_time * u_speed) * 
                          cos(vPosition.y * u_scale + u_time * u_speed) * 
                          sin(vPosition.z * u_scale + u_time * u_speed);
            
            float vein = smoothstep(0.1, 0.5, abs(noise));
            vec3 magmaColor = mix(u_color * u_intensity, vec3(0.05, 0.02, 0.05), vein);
            
            gl_FragColor = vec4(magmaColor, 1.0);
        }
    """
elif "Hologram" in fx_type:
    fragment_shader = """
        uniform float u_time;
        uniform float u_speed;
        uniform float u_scale;
        uniform float u_intensity;
        uniform vec3 u_color;
        varying vec3 vPosition;
        varying vec3 vNormal;

        void main() {
            float scanline = sin(vPosition.y * u_scale - u_time * u_speed * 3.0) * 0.5 + 0.5;
            scanline = pow(scanline, 3.0) * u_intensity;
            
            vec3 norm = normalize(vNormal);
            float fresnel = pow(1.0 - abs(dot(norm, vec3(0.0, 0.0, 1.0))), 2.0);
            
            vec3 finalColor = u_color * (scanline + fresnel * 1.5);
            float alpha = clamp(scanline + fresnel, 0.2, 0.9);
            
            gl_FragColor = vec4(finalColor, alpha);
        }
    """
else: # Energy Shield
    fragment_shader = """
        uniform float u_time;
        uniform float u_speed;
        uniform float u_scale;
        uniform float u_intensity;
        uniform vec3 u_color;
        varying vec3 vPosition;
        varying vec3 vNormal;

        void main() {
            vec3 norm = normalize(vNormal);
            float fresnel = pow(1.0 - abs(dot(norm, vec3(0.0, 0.0, 1.0))), 3.0);
            float hexGrid = sin(vPosition.x * u_scale) * sin(vPosition.y * u_scale) * sin(vPosition.z * u_scale);
            
            float pulse = sin(u_time * u_speed * 2.0) * 0.3 + 0.7;
            vec3 finalColor = u_color * (fresnel * u_intensity * pulse + abs(hexGrid) * 0.5);
            
            gl_FragColor = vec4(finalColor, fresnel * 0.8 + 0.2);
        }
    """

vertex_shader = """
    varying vec3 vPosition;
    varying vec3 vNormal;
    void main() {
        vPosition = position;
        vNormal = normalMatrix * normal;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
"""

# HTML/JS WebGL Embed Engine
html_3d_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; overflow: hidden; background: #0b0712; }}
        canvas {{ width: 100vw; height: 100vh; display: block; }}
        #info {{
            position: absolute; top: 10px; left: 10px; color: #a34bfb;
            font-family: monospace; font-size: 13px; background: rgba(0,0,0,0.6);
            padding: 8px 12px; border-radius: 6px; border: 1px solid #3a1c5d;
        }}
    </style>
</head>
<body>
    <div id="info">🖱️ Gunakan Mouse: Klik & Drag (Putar 3D) | Scroll (Zoom in/out)</div>
    <canvas id="webgl-canvas"></canvas>

    <!-- Import Three.js & OrbitControls -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        const canvas = document.getElementById('webgl-canvas');
        const renderer = new THREE.WebGLRenderer({{ canvas, antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 0, 5);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        // GEOMETRY GENERATOR
        let geometry;
        const objName = "{obj_type}";

        if (objName.includes("Pedang")) {{
            // Constructing Procedural 3D Sword
            const bladeGeo = new THREE.BoxGeometry(0.3, 3.2, 0.08);
            const guardGeo = new THREE.BoxGeometry(1.2, 0.15, 0.2);
            const hiltGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.8, 16);
            
            // Merge into group
            const group = new THREE.Group();
            const blade = new THREE.Mesh(bladeGeo); blade.position.y = 1.2;
            const guard = new THREE.Mesh(guardGeo); guard.position.y = -0.4;
            const hilt = new THREE.Mesh(hiltGeo); hilt.position.y = -0.8;
            group.add(blade, guard, hilt);
            
            // Convert to single mesh buffer for shader
            geometry = new THREE.BoxGeometry(0.3, 3.2, 0.08); // Single proxy geometry
        }} else if (objName.includes("Torus")) {{
            geometry = new THREE.TorusKnotGeometry(1, 0.35, 128, 32);
        }} else if (objName.includes("Sphere")) {{
            geometry = new THREE.SphereGeometry(1.4, 64, 64);
        }} else {{
            geometry = new THREE.BoxGeometry(1.8, 1.8, 1.8);
        }}

        // SHADER MATERIAL SETUP
        const uniforms = {{
            u_time: {{ value: 0.0 }},
            u_speed: {{ value: {anim_speed} }},
            u_scale: {{ value: {scale_freq} }},
            u_intensity: {{ value: {intensity} }},
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

        // ANIMATION LOOP
        const clock = new THREE.Clock();
        function animate() {{
            requestAnimationFrame(animate);
            const elapsedTime = clock.getElapsedTime();
            
            uniforms.u_time.value = elapsedTime;
            
            // Auto Rotate Object
            mesh.rotation.y = elapsedTime * 0.4;
            mesh.rotation.x = Math.sin(elapsedTime * 0.3) * 0.2;

            controls.update();
            renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
"""

with col_view:
    st.subheader("📺 3D Real-time Shader Preview")
    components.html(html_3d_code, height=550)
