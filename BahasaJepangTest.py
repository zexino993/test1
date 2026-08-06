import streamlit as st
from gtts import gTTS
import io
import random

# --- CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Belajar Bahasa Jepang Interaktif", 
    page_icon="⛩️", 
    layout="centered"
)

# --- FUNGSI GENERATE AUDIO DENGAN CACHING ---
@st.cache_data
def generate_audio(teks, lang='ja'):
    """Mengubah teks Jepang menjadi audio bytes di RAM (tidak perlu simpan file di disk)"""
    tts = gTTS(text=teks, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# --- DATA BELAJAR & KUIS ---
DATA_KUSI = [
    {
        "soal": "あ", 
        "audio_teks": "あ", 
        "pilihan": ["a", "i", "u", "e"], 
        "jawaban": "a", 
        "tipe": "Hiragana"
    },
    {
        "soal": "い", 
        "audio_teks": "い", 
        "pilihan": ["e", "i", "o", "u"], 
        "jawaban": "i", 
        "tipe": "Hiragana"
    },
    {
        "soal": "ありがとう", 
        "audio_teks": "ありがとう", 
        "pilihan": ["Selamat Pagi", "Terima Kasih", "Selamat Tinggal", "Maaf"], 
        "jawaban": "Terima Kasih", 
        "tipe": "Kosakata"
    },
    {
        "soal": "さようなら", 
        "audio_teks": "さようなら", 
        "pilihan": ["Halo", "Sampai Jumpa", "Terima Kasih", "Selamat Malam"], 
        "jawaban": "Sampai Jumpa", 
        "tipe": "Kosakata"
    },
    {
        "soal": "猫 (Neko)", 
        "audio_teks": "ねこ", 
        "pilihan": ["Anjing", "Burung", "Kucing", "Ikan"], 
        "jawaban": "Kucing", 
        "tipe": "Kosakata"
    },
]

DATA_FLASHCARD = [
    {"kanji": "こんにちは", "romaji": "Konnichiwa", "arti": "Halo / Selamat Siang"},
    {"kanji": "ありがとうございます", "romaji": "Arigatou gozaimasu", "arti": "Terima kasih banyak"},
    {"kanji": "おいしい", "romaji": "Oishii", "arti": "Enak"},
    {"kanji": "さようなら", "romaji": "Sayounara", "arti": "Sampai jumpa"},
    {"kanji": "すみません", "romaji": "Sumimasen", "arti": "Permisi / Maaf"},
]

# --- MENU NAVIGASI PADA SIDEBAR ---
st.sidebar.title("📌 Menu Belajar")
menu = st.sidebar.radio("Pilih Mode:", ["🎮 Kuis Interaktif", "🎴 Flashcard", "🔊 Coba Pelafalan Bebas"])

# ==============================================================================
# MODE 1: KUIS INTERAKTIF
# ==============================================================================
if menu == "🎮 Kuis Interaktif":
    st.title("🎮 Kuis Bahasa Jepang")
    st.caption("Uji pemahamanmu dan dengarkan suara pelafalannya!")

    # Inisialisasi State Skor dan Progres
    if "skor" not in st.session_state:
        st.session_state.skor = 0
    if "index_soal" not in st.session_state:
        st.session_state.index_soal = 0
    if "soal_acak" not in st.session_state:
        st.session_state.soal_acak = list(enumerate(DATA_KUSI))
        random.shuffle(st.session_state.soal_acak)

    def reset_kuis():
        st.session_state.skor = 0
        st.session_state.index_soal = 0
        random.shuffle(st.session_state.soal_acak)

    total_soal = len(DATA_KUSI)
    curr_idx = st.session_state.index_soal

    if curr_idx < total_soal:
        _, data = st.session_state.soal_acak[curr_idx]
        
        # Progress Bar
        st.progress((curr_idx) / total_soal)
        st.write(f"**Soal {curr_idx + 1} dari {total_soal}** | Kategori: *{data['tipe']}*")
        
        # Header Soal
        st.markdown(f"### Apa arti / cara baca dari: **{data['soal']}** ?")
        
        # Audio Pelafalan
        audio_bytes = generate_audio(data["audio_teks"], lang="ja")
        st.write("🔊 **Dengarkan Pelafalan:**")
        st.audio(audio_bytes, format="audio/mp3")
        
        # Form Pilihan Jawaban
        with st.form(key=f"form_{curr_idx}"):
            pilihan = st.radio("Pilih jawaban yang benar:", data["pilihan"])
            submit_button = st.form_submit_button(label="Jawab 🚀")
            
            if submit_button:
                if pilihan == data["jawaban"]:
                    st.success("✨ Benar sekali! Sugoi!")
                    st.session_state.skor += 1
                else:
                    st.error(f"❌ Kurang tepat. Jawaban yang benar adalah: **{data['jawaban']}**")
                
                st.session_state.index_soal += 1
                st.button("Lanjut ke Soal Berikutnya ➡️")

    else:
        # Halaman Hasil Akhir
        st.balloons()
        st.success("🎉 Selamat! Kamu telah menyelesaikan kuis.")
        st.metric(label="Skor Akhir Kamu", value=f"{st.session_state.skor} / {total_soal}")
        
        persentase = (st.session_state.skor / total_soal) * 100
        if persentase == 100:
            st.write("🌟 **Sempurna! Pemahamanmu sangat luar biasa!**")
        elif persentase >= 60:
            st.write("👍 **Bagus! Teruskan latihannya.**")
        else:
            st.write("💪 **Jangan menyerah, ayo coba lagi!**")
            
        st.button("🔄 Ulangi Kuis", on_click=reset_kuis)

# ==============================================================================
# MODE 2: FLASHCARD
# ==============================================================================
elif menu == "🎴 Flashcard":
    st.title("🎴 Flashcard Hafalan")
    st.caption("Klik tombol untuk membalik kartu dan mendengarkan suara cara bacanya.")

    if "flash_idx" not in st.session_state:
        st.session_state.flash_idx = 0
    if "show_meaning" not in st.session_state:
        st.session_state.show_meaning = False

    item = DATA_FLASHCARD[st.session_state.flash_idx]

    # Desain Kartu Flashcard
    with st.container(border=True):
        st.markdown(f"<h1 style='text-align: center;'>{item['kanji']}</h1>", unsafe_allow_html=True)
        
        # Audio
        audio_card = generate_audio(item["kanji"], lang="ja")
        st.audio(audio_card, format="audio/mp3")

        st.divider()

        if st.session_state.show_meaning:
            st.markdown(f"**Cara Baca:** {item['romaji']}")
            st.markdown(f"**Arti:** {item['arti']}")
        else:
            st.info("🔒 Klik tombol 'Balik Kartu' di bawah untuk melihat arti.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Sebelumnya"):
            st.session_state.flash_idx = (st.session_state.flash_idx - 1) % len(DATA_FLASHCARD)
            st.session_state.show_meaning = False
            st.rerun()

    with col2:
        if st.button("🔄 Balik Kartu"):
            st.session_state.show_meaning = not st.session_state.show_meaning
            st.rerun()

    with col3:
        if st.button("Berikutnya ➡️"):
            st.session_state.flash_idx = (st.session_state.flash_idx + 1) % len(DATA_FLASHCARD)
            st.session_state.show_meaning = False
            st.rerun()

# ==============================================================================
# MODE 3: PELAFALAN BEBAS
# ==============================================================================
elif menu == "🔊 Coba Pelafalan Bebas":
    st.title("🔊 Latihan Pelafalan Bebas")
    st.caption("Ketik kalimat atau kata Bahasa Jepang apa saja di sini untuk mendengarkan pengucapannya.")

    user_text = st.text_input("Masukkan teks Jepang:", value="はじめまして、よろしくお願いいたします")

    if user_text:
        audio_free = generate_audio(user_text, lang="ja")
        st.write("🔊 **Hasil Pelafalan:**")
        st.audio(audio_free, format="audio/mp3")
