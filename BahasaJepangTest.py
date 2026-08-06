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

# ==============================================================================
# DATABASE KANJI LENGKAP DENGAN CONTOH KALIMAT & KATEGORI
# ==============================================================================
DATA_KANJI = {
    "🔢 Angka Dasar (1 - 10)": [
        {
            "kanji": "一", "audio": "いち", "kunyomi": "ひとつ (hitotsu)", "onyomi": "イチ (ichi)", "arti": "Satu", 
            "pilihan": ["Satu", "Dua", "Tiga", "Empat"], "baca": "Ichi / Hitotsu",
            "kalimat_jp": "りんごを一つください。", "kalimat_romaji": "Ringo wo hitotsu kudasai.", "kalimat_arti": "Tolong beri saya satu buah apel."
        },
        {
            "kanji": "二", "audio": "に", "kunyomi": "ふたつ (futatsu)", "onyomi": "ニ (ni)", "arti": "Dua", 
            "pilihan": ["Tiga", "Dua", "Satu", "Lima"], "baca": "Ni / Futatsu",
            "kalimat_jp": "二月は寒いです。", "kalimat_romaji": "Nigatsu wa samui desu.", "kalimat_arti": "Bulan Februari dingin."
        },
        {
            "kanji": "三", "audio": "さん", "kunyomi": "みっつ (mittsu)", "onyomi": "サン (san)", "arti": "Tiga", 
            "pilihan": ["Empat", "Satu", "Tiga", "Dua"], "baca": "San / Mittsu",
            "kalimat_jp": "みかんが三分あります。", "kalimat_romaji": "Mikan ga mittsu arimasu.", "kalimat_arti": "Ada tiga buah jeruk."
        },
        {
            "kanji": "四", "audio": "よん", "kunyomi": "よっつ (yottsu)", "onyomi": "シ / ヨン (shi/yon)", "arti": "Empat", 
            "pilihan": ["Lima", "Empat", "Dua", "Tiga"], "baca": "Yon / Shi",
            "kalimat_jp": "四時に会いましょう。", "kalimat_romaji": "Yoji ni aimashou.", "kalimat_arti": "Mari bertemu di jam empat."
        },
        {
            "kanji": "五", "audio": "ご", "kunyomi": "いつつ (itsutsu)", "onyomi": "ゴ (go)", "arti": "Lima", 
            "pilihan": ["Lima", "Satu", "Empat", "Dua"], "baca": "Go / Itsutsu",
            "kalimat_jp": "五つの椅子があります。", "kalimat_romaji": "Itsutsu no isu ga arimasu.", "kalimat_arti": "Ada lima buah kursi."
        },
        {
            "kanji": "六", "audio": "ろく", "kunyomi": "むっつ (muttsu)", "onyomi": "ロク (roku)", "arti": "Enam", 
            "pilihan": ["Tujuh", "Enam", "Delapan", "Sembilan"], "baca": "Roku / Muttsu",
            "kalimat_jp": "六月に旅行します。", "kalimat_romaji": "Rokugatsu ni ryokou shimasu.", "kalimat_arti": "Saya akan bepergian pada bulan Juni."
        },
        {
            "kanji": "七", "audio": "なな", "kunyomi": "ななつ (nanatsu)", "onyomi": "シチ (shichi)", "arti": "Tujuh", 
            "pilihan": ["Tujuh", "Enam", "Sembilan", "Sepuluh"], "baca": "Nana / Shichi",
            "kalimat_jp": "七つの習慣。", "kalimat_romaji": "Nanatsu no shuukan.", "kalimat_arti": "Tujuh kebiasaan."
        },
        {
            "kanji": "八", "audio": "はち", "kunyomi": "やっつ (yattsu)", "onyomi": "ハチ (hachi)", "arti": "Delapan", 
            "pilihan": ["Enam", "Delapan", "Sepuluh", "Tujuh"], "baca": "Hachi / Yattsu",
            "kalimat_jp": "八時に起きます。", "kalimat_romaji": "Hachiji ni okimasu.", "kalimat_arti": "Saya bangun pada jam 8."
        },
        {
            "kanji": "九", "audio": "きゅう", "kunyomi": "ここのつ (kokonotsu)", "onyomi": "キュウ / ク (kyuu/ku)", "arti": "Sembilan", 
            "pilihan": ["Sembilan", "Delapan", "Tujuh", "Sepuluh"], "baca": "Kyuu / Kokonotsu",
            "kalimat_jp": "九歳の子ども。", "kalimat_romaji": "Kyuusai no kodomo.", "kalimat_arti": "Anak berusia sembilan tahun."
        },
        {
            "kanji": "十", "audio": "じゅう", "kunyomi": "とお (too)", "onyomi": "ジュウ (juu)", "arti": "Sepuluh", 
            "pilihan": ["Sembilan", "Sepuluh", "Seratus", "Lima"], "baca": "Juu / Too",
            "kalimat_jp": "十日になりました。", "kalimat_romaji": "Tooka ni narimashita.", "kalimat_arti": "Sudah tanggal sepuluh."
        },
    ],
    "🌿 Alam & Hari": [
        {
            "kanji": "日", "audio": "ひ", "kunyomi": "ひ / び (hi/bi)", "onyomi": "ニチ / ジツ (nichi/jitsu)", "arti": "Matahari / Hari (Minggu)", 
            "pilihan": ["Matahari / Hari", "Bulan", "Api", "Air"], "baca": "Nichi / Hi",
            "kalimat_jp": "日曜日に行きます。", "kalimat_romaji": "Nichiyoubi ni ikimasu.", "kalimat_arti": "Saya akan pergi pada hari Minggu."
        },
        {
            "kanji": "月", "audio": "つき", "kunyomi": "つき (tsuki)", "onyomi": "ゲツ / ガツ (getsu/gatsu)", "arti": "Bulan (Senin)", 
            "pilihan": ["Bulan", "Matahari", "Pohon", "Emas"], "baca": "Getsu / Tsuki",
            "kalimat_jp": "今月の月がきれいです。", "kalimat_romaji": "Kongetsu no tsuki ga kirei desu.", "kalimat_arti": "Bulan pada bulan ini sangat indah."
        },
        {
            "kanji": "火", "audio": "ひ", "kunyomi": "ひ (hi)", "onyomi": "カ (ka)", "arti": "Api (Selasa)", 
            "pilihan": ["Air", "Api", "Tanah", "Bulan"], "baca": "Ka / Hi",
            "kalimat_jp": "火曜日に勉強します。", "kalimat_romaji": "Kayoubi ni benkyou shimasu.", "kalimat_arti": "Saya belajar pada hari Selasa."
        },
        {
            "kanji": "水", "audio": "みず", "kunyomi": "みず (mizu)", "onyomi": "スイ (sui)", "arti": "Air (Rabu)", 
            "pilihan": ["Pohon", "Air", "Api", "Emas"], "baca": "Sui / Mizu",
            "kalimat_jp": "水を飲みます。", "kalimat_romaji": "Mizu wo nomimasu.", "kalimat_arti": "Saya minum air."
        },
        {
            "kanji": "木", "audio": "き", "kunyomi": "き (ki)", "onyomi": "モク / ボク (moku/boku)", "arti": "Pohon / Kayu (Kamis)", 
            "pilihan": ["Pohon", "Tanah", "Matahari", "Bulan"], "baca": "Moku / Ki",
            "kalimat_jp": "大きな木があります。", "kalimat_romaji": "Ookina ki ga arimasu.", "kalimat_arti": "Ada pohon yang besar."
        },
        {
            "kanji": "金", "audio": "かね", "kunyomi": "かね (kane)", "onyomi": "キン (kin)", "arti": "Emas / Uang (Jumat)", 
            "pilihan": ["Emas / Uang", "Air", "Api", "Tanah"], "baca": "Kin / Kane",
            "kalimat_jp": "お金がありません。", "kalimat_romaji": "Okane ga arimasen.", "kalimat_arti": "Saya tidak punya uang."
        },
        {
            "kanji": "土", "audio": "つち", "kunyomi": "つち (tsuchi)", "onyomi": "ド / ト (do/to)", "arti": "Tanah (Sabtu)", 
            "pilihan": ["Pohon", "Tanah", "Emas", "Air"], "baca": "Do / Tsuchi",
            "kalimat_jp": "土曜日にお休みします。", "kalimat_romaji": "Doyoubi ni oyasumi shimasu.", "kalimat_arti": "Saya libur pada hari Sabtu."
        },
    ],
    "📏 Ukuran & Kata Sifat": [
        {
            "kanji": "大", "audio": "おおきい", "kunyomi": "おお (oo)", "onyomi": "ダイ / タイ (dai/tai)", "arti": "Besar", 
            "pilihan": ["Besar", "Kecil", "Tinggi", "Murah"], "baca": "Dai / Oo",
            "kalimat_jp": "大学に行きます。", "kalimat_romaji": "Daigaku ni ikimasu.", "kalimat_arti": "Saya pergi ke Universitas."
        },
        {
            "kanji": "小", "audio": "ちいさい", "kunyomi": "ちい / こ (chii/ko)", "onyomi": "ショウ (shou)", "arti": "Kecil", 
            "pilihan": ["Kecil", "Besar", "Banyak", "Sedikit"], "baca": "Shou / Chii",
            "kalimat_jp": "小さい犬が好きです。", "kalimat_romaji": "Chiisai inu ga suki desu.", "kalimat_arti": "Saya suka anjing kecil."
        },
        {
            "kanji": "高", "audio": "たかい", "kunyomi": "たか (taka)", "onyomi": "コウ (kou)", "arti": "Tinggi / Mahal", 
            "pilihan": ["Murah", "Kecil", "Tinggi / Mahal", "Banyak"], "baca": "Kou / Taka",
            "kalimat_jp": "この本は高いです。", "kalimat_romaji": "Kono hon wa takai desu.", "kalimat_arti": "Buku ini mahal."
        },
        {
            "kanji": "安", "audio": "やすい", "kunyomi": "やす (yasu)", "onyomi": "アン (an)", "arti": "Murah / Aman", 
            "pilihan": ["Murah / Aman", "Mahal", "Besar", "Kecil"], "baca": "An / Yasu",
            "kalimat_jp": "安い服を買いました。", "kalimat_romaji": "Yasui fuku wo kaimashita.", "kalimat_arti": "Saya membeli baju murah."
        },
        {
            "kanji": "多", "audio": "おい", "kunyomi": "おお (oo)", "onyomi": "タ (ta)", "arti": "Banyak", 
            "pilihan": ["Sedikit", "Banyak", "Besar", "Tinggi"], "baca": "Ta / Oo",
            "kalimat_jp": "人が多いです。", "kalimat_romaji": "Hito ga oi desu.", "kalimat_arti": "Ada banyak orang."
        },
        {
            "kanji": "少", "audio": "すくない", "kunyomi": "すく / すこ (suku/suko)", "onyomi": "ショウ (shou)", "arti": "Sedikit", 
            "pilihan": ["Banyak", "Sedikit", "Murah", "Kecil"], "baca": "Shou / Suku",
            "kalimat_jp": "少し待ってください。", "kalimat_romaji": "Sukoshi matte kudasai.", "kalimat_arti": "Tolong tunggu sebentar."
        },
    ],
    "👤 Manusia & Aktivitas": [
        {
            "kanji": "人", "audio": "ひと", "kunyomi": "ひと (hito)", "onyomi": "ジン / ニン (jin/nin)", "arti": "Orang / Manusia", 
            "pilihan": ["Orang / Manusia", "Mulut", "Mata", "Tangan"], "baca": "Jin / Nin / Hito",
            "kalimat_jp": "あの人は日本人です。", "kalimat_romaji": "Ano hito wa nihonjin desu.", "kalimat_arti": "Orang itu adalah orang Jepang."
        },
        {
            "kanji": "口", "audio": "くち", "kunyomi": "くち (kuchi)", "onyomi": "コウ (kou)", "arti": "Mulut", 
            "pilihan": ["Mata", "Mulut", "Tangan", "Orang"], "baca": "Kou / Kuchi",
            "kalimat_jp": "入口はこちらです。", "kalimat_romaji": "Iriguchi wa kochira desu.", "kalimat_arti": "Pintu masuk ada di sebelah sini."
        },
        {
            "kanji": "目", "audio": "め", "kunyomi": "め (me)", "onyomi": "モク (moku)", "arti": "Mata", 
            "pilihan": ["Mulut", "Mata", "Telinga", "Tangan"], "baca": "Moku / Me",
            "kalimat_jp": "目が痛いです。", "kalimat_romaji": "Me ga itai desu.", "kalimat_arti": "Mata saya sakit."
        },
        {
            "kanji": "手", "audio": "て", "kunyomi": "て (te)", "onyomi": "シュ (shu)", "arti": "Tangan", 
            "pilihan": ["Kaki", "Mata", "Tangan", "Mulut"], "baca": "Shu / Te",
            "kalimat_jp": "手を洗います。", "kalimat_romaji": "Te wo araimasu.", "kalimat_arti": "Saya mencuci tangan."
        },
        {
            "kanji": "見", "audio": "みる", "kunyomi": "み (mi)", "onyomi": "ケン (ken)", "arti": "Melihat", 
            "pilihan": ["Mendengar", "Melihat", "Makan", "Minum"], "baca": "Ken / Mi",
            "kalimat_jp": "映画を見ます。", "kalimat_romaji": "Eiga wo mimasu.", "kalimat_arti": "Saya menonton film."
        },
        {
            "kanji": "食", "audio": "たべる", "kunyomi": "た (ta)", "onyomi": "ショク (shoku)", "arti": "Makan", 
            "pilihan": ["Minum", "Makan", "Melihat", "Pergi"], "baca": "Shoku / Ta",
            "kalimat_jp": "ご飯を食べます。", "kalimat_romaji": "Gohan wo tabemasu.", "kalimat_arti": "Saya makan nasi."
        },
        {
            "kanji": "飲", "audio": "のむ", "kunyomi": "の (no)", "onyomi": "イン (in)", "arti": "Minum", 
            "pilihan": ["Makan", "Minum", "Melihat", "Datang"], "baca": "In / No",
            "kalimat_jp": "お茶を飲みます。", "kalimat_romaji": "Ocha wo nomimasu.", "kalimat_arti": "Saya minum teh."
        },
    ]
}

# --- MENU NAVIGASI PADA SIDEBAR ---
st.sidebar.title("📌 Menu Belajar")
menu = st.sidebar.radio("Pilih Mode:", ["⛩️ Belajar Kanji Dasar", "📝 Kuis Kanji Interaktif", "🔊 Coba Pelafalan Bebas"])

# ==============================================================================
# MODE 1: BELAJAR KANJI DASAR
# ==============================================================================
if menu == "⛩️ Belajar Kanji Dasar":
    st.title("⛩️ Modul Belajar Kanji")
    st.caption("Pilih kategori kanji yang ingin kamu pelajari di bawah ini.")

    kategori_pilihan = st.selectbox("📂 Pilih Kategori Kanji:", list(DATA_KANJI.keys()))
    list_materi = DATA_KANJI[kategori_pilihan]

    st.write(f"Showing {len(list_materi)} Kanji dalam kategori **{kategori_pilihan}**:")

    for item in list_materi:
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"<h1 style='text-align: center; font-size: 70px;'>{item['kanji']}</h1>", unsafe_allow_html=True)
                audio_bytes = generate_audio(item["audio"], lang="ja")
                st.write("🔊 **Pengucapan Kanji:**")
                st.audio(audio_bytes, format="audio/mp3")

            with col2:
                st.markdown(f"### Arti: **{item['arti']}**")
                st.write(f"🇯🇵 **Kunyomi (Jepang):** {item['kunyomi']}")
                st.write(f"🇨🇳 **Onyomi (Cina):** {item['onyomi']}")
                
                st.divider()
                st.write("📝 **Contoh Kalimat:**")
                st.markdown(f"**{item['kalimat_jp']}**")
                st.caption(f"🗣️ *{item['kalimat_romaji']}*")
                st.write(f"🇮🇩 {item['kalimat_arti']}")
                
                # Audio untuk Kalimat
                audio_kalimat = generate_audio(item["kalimat_jp"], lang="ja")
                st.audio(audio_kalimat, format="audio/mp3")

# ==============================================================================
# MODE 2: KUIS KANJI INTERAKTIF
# ==============================================================================
elif menu == "📝 Kuis Kanji Interaktif":
    st.title("📝 Kuis Hafalan Kanji")
    st.caption("Uji ingatanmu berdasarkan kategori kanji yang kamu pilih!")

    kategori_kuis = st.selectbox("🎯 Pilih Kategori Kuis:", list(DATA_KANJI.keys()), key="kuis_kat")
    list_soal = DATA_KANJI[kategori_kuis]

    # Restart session jika kategori kuis diganti
    if "last_kategori" not in st.session_state or st.session_state.last_kategori != kategori_kuis:
        st.session_state.last_kategori = kategori_kuis
        st.session_state.kanji_skor = 0
        st.session_state.kanji_idx = 0
        st.session_state.kanji_soal_acak = list(enumerate(list_soal))
        random.shuffle(st.session_state.kanji_soal_acak)
        st.session_state.sudah_dijawab = False

    def reset_kanji_kuis():
        st.session_state.kanji_skor = 0
        st.session_state.kanji_idx = 0
        st.session_state.sudah_dijawab = False
        random.shuffle(st.session_state.kanji_soal_acak)

    def lanjut_soal():
        st.session_state.kanji_idx += 1
        st.session_state.sudah_dijawab = False

    total_soal = len(list_soal)
    curr_idx = st.session_state.kanji_idx

    if curr_idx < total_soal:
        _, data = st.session_state.kanji_soal_acak[curr_idx]
        
        # Progress Bar
        st.progress((curr_idx) / total_soal)
        st.write(f"**Soal {curr_idx + 1} dari {total_soal}** | Kategori: *{kategori_kuis}*")
        
        # Header Soal
        st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{data['kanji']}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Apa arti dari kanji di atas?</p>", unsafe_allow_html=True)
        
        # Audio Pelafalan Kanji
        audio_bytes = generate_audio(data["audio"], lang="ja")
        st.audio(audio_bytes, format="audio/mp3")
        
        # Form Pilihan Jawaban
        with st.form(key=f"kanji_form_{kategori_kuis}_{curr_idx}"):
            pilihan = st.radio("Pilih jawaban yang benar:", data["pilihan"])
            submit_button = st.form_submit_button(label="Jawab 🚀")
            
            if submit_button:
                st.session_state.sudah_dijawab = True
                if pilihan == data["arti"]:
                    st.session_state.jawaban_benar = True
                    st.session_state.kanji_skor += 1
                else:
                    st.session_state.jawaban_benar = False
                    
        # Menampilkan Feedback, Contoh Kalimat, & Tombol Lanjut di luar Form
        if st.session_state.sudah_dijawab:
            if st.session_state.jawaban_benar:
                st.success(f"✨ Benar sekali! Cara bacanya: {data['baca']}")
            else:
                st.error(f"❌ Kurang tepat. Jawaban yang benar adalah: **{data['arti']}** ({data['baca']})")
            
            # Menampilkan contoh kalimat sebagai bahan pembelajaran tambahan
            with st.expander("💡 Lihat Contoh Kalimat Penggunaan Kanji Ini", expanded=True):
                st.markdown(f"**{data['kalimat_jp']}**")
                st.caption(f"🗣️ *{data['kalimat_romaji']}*")
                st.write(f"🇮🇩 {data['kalimat_arti']}")
                audio_kalimat_kuis = generate_audio(data["kalimat_jp"], lang="ja")
                st.audio(audio_kalimat_kuis, format="audio/mp3")

            st.button("Lanjut ke Soal Berikutnya ➡️", on_click=lanjut_soal)

    else:
        # Halaman Hasil Akhir
        st.balloons()
        st.success("🎉 Selamat! Kamu telah menyelesaikan kuis kategori ini!")
        st.metric(label="Skor Akhir Kamu", value=f"{st.session_state.kanji_skor} / {total_soal}")
        
        st.button("🔄 Ulangi Kuis Kategori Ini", on_click=reset_kanji_kuis)

# ==============================================================================
# MODE 3: PELAFALAN BEBAS
# ==============================================================================
elif menu == "🔊 Coba Pelafalan Bebas":
    st.title("🔊 Latihan Pelafalan Bebas")
    st.caption("Ketik kalimat atau kata Bahasa Jepang apa saja di sini untuk mendengarkan pengucapannya.")

    user_text = st.text_input("Masukkan teks Jepang:", value="日曜日にお茶を飲みます。")

    if user_text:
        audio_free = generate_audio(user_text, lang="ja")
        st.write("🔊 **Hasil Pelafalan:**")
        st.audio(audio_free, format="audio/mp3")
