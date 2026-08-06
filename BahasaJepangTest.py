import streamlit as st
from gtts import gTTS
import io

st.set_page_config(page_title="Pelafalan Bahasa Jepang", page_icon="🔊")

st.title("🔊 Latihan Pelafalan Bahasa Jepang")
st.caption("Dengarkan cara pengucapan kata dan huruf Jepang menggunakan gTTS.")

# --- FUNGSI GENERATE AUDIO (DENGAN CACHING) ---
@st.cache_data
def generate_audio(teks, lang='ja'):
    """Mengubah teks menjadi audio bytes menggunakan gTTS"""
    tts = gTTS(text=teks, lang=lang)
    
    # Simpan audio di memori (BytesIO) agar tidak perlu membuat file fisik di disk
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# --- DATA KOSAKATA ---
data_jepang = [
    {"kanji": "こんにちは", "romaji": "Konnichiwa", "arti": "Halo / Selamat Siang"},
    {"kanji": "ありがとうございます", "romaji": "Arigatou gozaimasu", "arti": "Terima kasih banyak"},
    {"kanji": "おいしい", "romaji": "Oishii", "arti": "Enak"},
    {"kanji": "さようなら", "romaji": "Sayounara", "arti": "Sampai jumpa"},
]

st.subheader("🎴 Flashcard dengan Suara")

# Pilih kata dari dropdown
pilihan = st.selectbox("Pilih Kata:", options=data_jepang, format_func=lambda x: f"{x['kanji']} ({x['romaji']})")

if pilihan:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### Teks: **{pilihan['kanji']}**")
        st.write(f"**Cara baca:** {pilihan['romaji']}")
        st.write(f"**Arti:** {pilihan['arti']}")
        
    with col2:
        # Panggil fungsi gTTS dengan bahasa Jepang ('ja')
        audio_bytes = generate_audio(pilihan['kanji'], lang='ja')
        
        # Tampilkan pemutar audio
        st.write("🔊 **Dengarkan:**")
        st.audio(audio_bytes, format="audio/mp3")

st.divider()

# --- FITUR DUKUNGAN: KETIK TEKS BEBAS ---
st.subheader("✍️ Coba Ketik Teks Jepang Bebas")
user_input = st.text_input("Masukkan teks Jepang (Contoh: おやすみなさい):", value="おはようございます")

if user_input:
    audio_bebas = generate_audio(user_input, lang='ja')
    st.audio(audio_bebas, format="audio/mp3")
