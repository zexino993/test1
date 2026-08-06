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
    """Mengubah teks Jepang menjadi audio bytes di RAM"""
    tts = gTTS(text=teks, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# --- DATA MATERI KANJI & KUIS ---
DATA_MATERI_KANJI = [
    {"kanji": "一", "kunyomi": "ひとつ (hitotsu)", "onyomi": "イチ (ichi)", "arti": "Satu", "contoh": "一つ (satu buah)"},
    {"kanji": "二", "kunyomi": "ふたつ (futatsu)", "onyomi": "ニ (ni)", "arti": "Dua", "contoh": "二月 (Februari)"},
    {"kanji": "三", "kunyomi": "みっつ (mittsu)", "onyomi": "サン (san)", "arti": "Tiga", "contoh": "三年 (Tiga tahun)"},
    {"kanji": "四", "kunyomi": "よっつ (yottsu)", "onyomi": "シ / ヨン (shi/yon)", "arti": "Empat", "contoh": "四 (yon)"},
    {"kanji": "五", "kunyomi": "いつつ (itsutsu)", "onyomi": "ゴ (go)", "arti": "Lima", "contoh": "五日 (Tanggal 5)"},
]

KUIS_KANJI = [
    {
        "kanji": "一",
        "audio": "いち",
        "pilihan": ["Tiga", "Satu", "Lima", "Dua"],
        "jawaban": "Satu",
        "baca": "Ichi / Hitotsu"
    },
    {
        "kanji": "三",
        "audio": "さん",
        "pilihan": ["Empat", "Satu", "Tiga", "Dua"],
        "jawaban": "Tiga",
        "baca": "San / Mittsu"
    },
    {
        "kanji": "四",
        "audio": "よん",
        "pilihan": ["Lima", "Empat", "Dua", "Tiga"],
        "jawaban": "Empat",
        "baca": "Yon / Shi"
    },
    {
        "kanji": "五",
        "audio": "ご",
        "pilihan": ["Lima", "Satu", "Empat", "Dua"],
        "jawaban": "Lima",
        "baca": "Go / Itsutsu"
    },
    {
        "kanji": "二",
        "audio": "に",
        "pilihan": ["Tiga", "Dua", "Satu", "Lima"],
        "jawaban": "Dua",
        "baca": "Ni / Futatsu"
    }
]

# --- MENU NAVIGASI PADA SIDEBAR ---
st.sidebar.title("📌 Menu Belajar")
menu = st.sidebar.radio("Pilih Mode:", ["⛩️ Belajar Kanji Dasar", "📝 Kuis Kanji", "🔊 Coba Pelafalan Bebas"])

# ==============================================================================
# MODE 1: BELAJAR KANJI DASAR
# ==============================================================================
if menu == "⛩️ Belajar Kanji Dasar":
    st.title("⛩️ Modul 1: Kanji Angka Dasar")
    st.caption("Pelajari bentuk kanji, cara baca Onyomi/Kunyomi, dan dengarkan suaranya.")

    for item in DATA_MATERI_KANJI:
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"<h1 style='text-align: center; font-size: 70px;'>{item['kanji']}</h1>", unsafe_allow_html=True)
                audio_bytes = generate_audio(item["kanji"], lang="ja")
                st.audio(audio_bytes, format="audio/mp3")

            with col2:
                st.markdown(f"### Arti: **{item['arti']}**")
                st.write(f"🇯🇵 **Kunyomi (Jepang):** {item['kunyomi']}")
                st.write(f"🇨🇳 **Onyomi (Cina):** {item['onyomi']}")
                st.write(f"💡 **Contoh:** {item['contoh']}")

# ==============================================================================
# MODE 2: KUIS KANJI (PERBAIKAN STREAMLIT FORM BUG)
# ==============================================================================
elif menu == "📝 Kuis Kanji":
    st.title("📝 Kuis Hafalan Kanji Angka")
    st.caption("Uji ingatanmu tentang kanji angka yang baru dipelajari!")

    # Inisialisasi State Skor dan Progres
    if "kanji_skor" not in st.session_state:
        st.session_state.kanji_skor = 0
    if "kanji_idx" not in st.session_state:
        st.session_state.kanji_idx = 0
    if "kanji_soal_acak" not in st.session_state:
        st.session_state.kanji_soal_acak = list(enumerate(KUIS_KANJI))
        random.shuffle(st.session_state.kanji_soal_acak)
    if "sudah_dijawab" not in st.session_state:
        st.session_state.sudah_dijawab = False

    def reset_kanji_kuis():
        st.session_state.kanji_skor = 0
        st.session_state.kanji_idx = 0
        st.session_state.sudah_dijawab = False
        random.shuffle(st.session_state.kanji_soal_acak)

    def lanjut_soal():
        st.session_state.kanji_idx += 1
        st.session_state.sudah_dijawab = False

    total_soal = len(KUIS_KANJI)
    curr_idx = st.session_state.kanji_idx

    if curr_idx < total_soal:
        _, data = st.session_state.kanji_soal_acak[curr_idx]
        
        # Progress Bar
        st.progress((curr_idx) / total_soal)
        st.write(f"**Soal {curr_idx + 1} dari {total_soal}**")
        
        # Header Soal
        st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{data['kanji']}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Apa arti dari kanji di atas?</p>", unsafe_allow_html=True)
        
        # Audio Pelafalan
        audio_bytes = generate_audio(data["audio"], lang="ja")
        st.audio(audio_bytes, format="audio/mp3")
        
        # Form Pilihan Jawaban
        with st.form(key=f"kanji_form_{curr_idx}"):
            pilihan = st.radio("Pilih jawaban yang benar:", data["pilihan"])
            submit_button = st.form_submit_button(label="Jawab 🚀")
            
            if submit_button:
                st.session_state.sudah_dijawab = True
                if pilihan == data["jawaban"]:
                    st.session_state.jawaban_benar = True
                else:
                    st.session_state.jawaban_benar = False
                    
        # Menampilkan Feedback & Tombol Lanjut di luar Form
        if st.session_state.sudah_dijawab:
            if st.session_state.jawaban_benar:
                st.success(f"✨ Benar sekali! Cara bacanya: {data['baca']}")
            else:
                st.error(f"❌ Kurang tepat. Jawaban yang benar adalah: **{data['jawaban']}** ({data['baca']})")
                
            st.button("Lanjut ke Soal Berikutnya ➡️", on_click=lanjut_soal)

    else:
        # Halaman Hasil Akhir
        st.balloons()
        st.success("🎉 Selamat! Kamu telah menyelesaikan Kuis Kanji!")
        st.metric(label="Skor Akhir Kamu", value=f"{st.session_state.kanji_skor} / {total_soal}")
        
        st.button("🔄 Ulangi Kuis Kanji", on_click=reset_kanji_kuis)

# ==============================================================================
# MODE 3: PELAFALAN BEBAS
# ==============================================================================
elif menu == "🔊 Coba Pelafalan Bebas":
    st.title("🔊 Latihan Pelafalan Bebas")
    st.caption("Ketik kalimat atau kata Bahasa Jepang apa saja di sini untuk mendengarkan pengucapannya.")

    user_text = st.text_input("Masukkan teks Jepang:", value="一 二 三 四 五")

    if user_text:
        audio_free = generate_audio(user_text, lang="ja")
        st.write("🔊 **Hasil Pelafalan:**")
        st.audio(audio_free, format="audio/mp3")
