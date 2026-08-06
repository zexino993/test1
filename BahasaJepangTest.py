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
# DATABASE KANJI LENGKAP (48 KANJI / 7 KATEGORI)
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
    "💯 Angka Puluhan/Ratusan & Satuan": [
        {
            "kanji": "百", "audio": "ひゃく", "kunyomi": "- (tidak umum)", "onyomi": "ヒャク (hyaku)", "arti": "Ratus / Seratus",
            "pilihan": ["Ratus / Seratus", "Ribu", "Sepuluh Ribu", "Puluh"], "baca": "Hyaku",
            "kalimat_jp": "百円のパンを買いました。", "kalimat_romaji": "Hyakuen no pan wo kaimashita.", "kalimat_arti": "Saya membeli roti seharga 100 yen."
        },
        {
            "kanji": "千", "audio": "せん", "kunyomi": "ち (chi)", "onyomi": "セン (sen)", "arti": "Ribu / Seribu",
            "pilihan": ["Ratus", "Ribu / Seribu", "Sepuluh Ribu", "Seratus"], "baca": "Sen / Chi",
            "kalimat_jp": "三千円かかります。", "kalimat_romaji": "Sanzen'en kakarimasu.", "kalimat_arti": "Membutuhkan biaya 3000 yen."
        },
        {
            "kanji": "万", "audio": "まん", "kunyomi": "- (tidak ada)", "onyomi": "マン / バン (man/ban)", "arti": "Sepuluh Ribu",
            "pilihan": ["Ribu", "Seratus", "Sepuluh Ribu", "Satu Juta"], "baca": "Man",
            "kalimat_jp": "一万円札を出します。", "kalimat_romaji": "Ichiman'ensatsu wo dashimasu.", "kalimat_arti": "Saya mengeluarkan uang kertas 10.000 yen."
        },
        {
            "kanji": "円", "audio": "えん", "kunyomi": "まるい (marui)", "onyomi": "エン (en)", "arti": "Yen / Lingkaran",
            "pilihan": ["Yen / Lingkaran", "Dolar", "Uang", "Emas"], "baca": "En / Marui",
            "kalimat_jp": "これは五百円です。", "kalimat_romaji": "Kore wa gohyakuen desu.", "kalimat_arti": "Ini harganya 500 yen."
        },
        {
            "kanji": "半", "audio": "はん", "kunyomi": "なかば (nakaba)", "onyomi": "ハン (han)", "arti": "Setengah / Separuh",
            "pilihan": ["Setengah / Separuh", "Penuh", "Tiga Perempat", "Satu"], "baca": "Han",
            "kalimat_jp": "七時半に学校へ行きます。", "kalimat_romaji": "Shichijihan ni gakkou e ikimasu.", "kalimat_arti": "Saya pergi ke sekolah jam 7 setengah."
        },
    ],
    "🌿 Alam, Hari & Cuaca": [
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
        {
            "kanji": "山", "audio": "やま", "kunyomi": "やま (yama)", "onyomi": "サン / サン (san/zan)", "arti": "Gunung",
            "pilihan": ["Gunung", "Sungai", "Sawah", "Batu"], "baca": "San / Yama",
            "kalimat_jp": "富士山は高いです。", "kalimat_romaji": "Fujisan wa takai desu.", "kalimat_arti": "Gunung Fuji tinggi."
        },
        {
            "kanji": "川", "audio": "かわ", "kunyomi": "かわ (kawa)", "onyomi": "セン (sen)", "arti": "Sungai",
            "pilihan": ["Gunung", "Sungai", "Laut", "Danau"], "baca": "Kawa / Sen",
            "kalimat_jp": "川できれいに泳ぎます。", "kalimat_romaji": "Kawa de kirei ni oyogimasu.", "kalimat_arti": "Berenang dengan indah di sungai."
        },
        {
            "kanji": "雨", "audio": "あめ", "kunyomi": "あめ (ame)", "onyomi": "ウ (u)", "arti": "Hujan",
            "pilihan": ["Awan", "Angin", "Hujan", "Salju"], "baca": "Ame / U",
            "kalimat_jp": "今日は雨が降っています。", "kalimat_romaji": "Kyou wa ame ga futte imasu.", "kalimat_arti": "Hari ini hujan turun."
        },
    ],
    "🧭 Arah & Posisi": [
        {
            "kanji": "上", "audio": "うえ", "kunyomi": "うえ / あがる (ue/agaru)", "onyomi": "ジョウ (jou)", "arti": "Atas / Naik",
            "pilihan": ["Atas / Naik", "Bawah", "Depan", "Belakang"], "baca": "Jou / Ue",
            "kalimat_jp": "机の上に本があります。", "kalimat_romaji": "Tsukue no ue ni hon ga arimasu.", "kalimat_arti": "Ada buku di atas meja."
        },
        {
            "kanji": "下", "audio": "した", "kunyomi": "した / さがる (shita/sagaru)", "onyomi": "カ / ゲ (ka/ge)", "arti": "Bawah / Turun",
            "pilihan": ["Atas", "Bawah / Turun", "Samping", "Dalam"], "baca": "Ka / Shita",
            "kalimat_jp": "椅子の下に猫がいます。", "kalimat_romaji": "Isu no shita ni neko ga imasu.", "kalimat_arti": "Ada kucing di bawah kursi."
        },
        {
            "kanji": "中", "audio": "なか", "kunyomi": "なか (naka)", "onyomi": "チュウ (chuu)", "arti": "Dalam / Tengah",
            "pilihan": ["Luar", "Dalam / Tengah", "Atas", "Kiri"], "baca": "Chuu / Naka",
            "kalimat_jp": "箱の中に何がありますか。", "kalimat_romaji": "Hako no naka ni nani ga arimasu ka.", "kalimat_arti": "Ada apa di dalam kotak?"
        },
        {
            "kanji": "右", "audio": "みぎ", "kunyomi": "みぎ (migi)", "onyomi": "ウ / ユウ (u/yuu)", "arti": "Kanan",
            "pilihan": ["Kiri", "Kanan", "Depan", "Belakang"], "baca": "U / Migi",
            "kalimat_jp": "右に曲がってください。", "kalimat_romaji": "Migi ni magatte kudasai.", "kalimat_arti": "Tolong belok ke kanan."
        },
        {
            "kanji": "左", "audio": "ひだり", "kunyomi": "ひだり (hidari)", "onyomi": "サ (sa)", "arti": "Kiri",
            "pilihan": ["Kanan", "Kiri", "Atas", "Bawah"], "baca": "Sa / Hidari",
            "kalimat_jp": "左手に時計があります。", "kalimat_romaji": "Hidarite ni tokei ga arimasu.", "kalimat_arti": "Ada jam di tangan kiri."
        },
        {
            "kanji": "前", "audio": "まえ", "kunyomi": "まえ (mae)", "onyomi": "ゼン (zen)", "arti": "Depan / Sebelum",
            "pilihan": ["Depan / Sebelum", "Belakang", "Samping", "Luar"], "baca": "Zen / Mae",
            "kalimat_jp": "駅の前で待ちます。", "kalimat_romaji": "Eki no mae de machimasu.", "kalimat_arti": "Saya menunggu di depan stasiun."
        },
        {
            "kanji": "後", "audio": "うしろ", "kunyomi": "うしろ / あと (ushiro/ato)", "onyomi": "ゴ / コウ (go/kou)", "arti": "Belakang / Setelah",
            "pilihan": ["Depan", "Belakang / Setelah", "Dalam", "Atas"], "baca": "Go / Ushiro",
            "kalimat_jp": "テストの後でご飯を食べます。", "kalimat_romaji": "Tesuto no ato de gohan wo tabemasu.", "kalimat_arti": "Setelah tes saya makan nasi."
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
            "kanji": "高", "audio": "たかい", "kunyomi": "たかい (takai)", "onyomi": "コウ (kou)", "arti": "Tinggi / Mahal", 
            "pilihan": ["Murah", "Kecil", "Tinggi / Mahal", "Banyak"], "baca": "Kou / Taka",
            "kalimat_jp": "この本は高いです。", "kalimat_romaji": "Kono hon wa takai desu.", "kalimat_arti": "Buku ini mahal."
        },
        {
            "kanji": "安", "audio": "やすい", "kunyomi": "やすい (yasui)", "onyomi": "アン (an)", "arti": "Murah / Aman", 
            "pilihan": ["Murah / Aman", "Mahal", "Besar", "Kecil"], "baca": "An / Yasu",
            "kalimat_jp": "安い服を買いました。", "kalimat_romaji": "Yasui fuku wo kaimashita.", "kalimat_arti": "Saya membeli baju murah."
        },
        {
            "kanji": "多", "audio": "おい", "kunyomi": "おおい (ooi)", "onyomi": "タ (ta)", "arti": "Banyak", 
            "pilihan": ["Sedikit", "Banyak", "Besar", "Tinggi"], "baca": "Ta / Oo",
            "kalimat_jp": "人が多いです。", "kalimat_romaji": "Hito ga oi desu.", "kalimat_arti": "Ada banyak orang."
        },
        {
            "kanji": "少", "audio": "すくない", "kunyomi": "すくない (sukunai)", "onyomi": "ショウ (shou)", "arti": "Sedikit", 
            "pilihan": ["Banyak", "Sedikit", "Murah", "Kecil"], "baca": "Shou / Suku",
            "kalimat_jp": "少し待ってください。", "kalimat_romaji": "Sukoshi matte kudasai.", "kalimat_arti": "Tolong tunggu sebentar."
        },
        {
            "kanji": "長", "audio": "ながい", "kunyomi": "ながい (nagai)", "onyomi": "チョウ (chou)", "arti": "Panjang / Pemimpin",
            "pilihan": ["Pendek", "Panjang / Pemimpin", "Lebar", "Tinggi"], "baca": "Chou / Nagai",
            "kalimat_jp": "社長と話します。", "kalimat_romaji": "Shachou to hanashimasu.", "kalimat_arti": "Saya berbicara dengan direktur perusahaan."
        },
        {
            "kanji": "古", "audio": "ふるい", "kunyomi": "ふるい (furui)", "onyomi": "コ (ko)", "arti": "Lama / Kuno / Tua",
            "pilihan": ["Baru", "Lama / Kuno / Tua", "Muda", "Bagus"], "baca": "Ko / Furui",
            "kalimat_jp": "古本を買いました。", "kalimat_romaji": "Furuhon wo kaimashita.", "kalimat_arti": "Saya membeli buku bekas."
        },
        {
            "kanji": "新", "audio": "あたらしい", "kunyomi": "あたらしい (atarashii)", "onyomi": "シン (shin)", "arti": "Baru",
            "pilihan": ["Lama", "Baru", "Tua", "Mahal"], "baca": "Shin / Atarashii",
            "kalimat_jp": "新幹線に乗ります。", "kalimat_romaji": "Shinkansen ni norimasu.", "kalimat_arti": "Saya naik kereta cepat Shinkansen."
        },
    ],
    "👤 Manusia & Anggota Tubuh": [
        {
            "kanji": "人", "audio": "ひと", "kunyomi": "ひと (hito)", "onyomi": "ジン / ニン (jin/nin)", "arti": "Orang / Manusia", 
            "pilihan": ["Orang / Manusia", "Mulut", "Mata", "Tangan"], "baca": "Jin / Nin / Hito",
            "kalimat_jp": "あの人は日本人です。", "kalimat_romaji": "Ano hito wa nihonjin desu.", "kalimat_arti": "Orang itu adalah orang Jepang."
        },
        {
            "kanji": "男", "audio": "おとこ", "kunyomi": "おとこ (otoko)", "onyomi": "ダン / ナン (dan/nan)", "arti": "Laki-laki",
            "pilihan": ["Perempuan", "Laki-laki", "Anak", "Orang"], "baca": "Dan / Otoko",
            "kalimat_jp": "男の子が遊んでいます。", "kalimat_romaji": "Otoko no ko ga asonde imasu.", "kalimat_arti": "Anak laki-laki sedang bermain."
        },
        {
            "kanji": "女", "audio": "おんな", "kunyomi": "おんな (onna)", "onyomi": "ジョ / ニョ (jo/nyo)", "arti": "Perempuan",
            "pilihan": ["Laki-laki", "Perempuan", "Ibu", "Ayah"], "baca": "Jo / Onna",
            "kalimat_jp": "彼女は優しい女の人です。", "kalimat_romaji": "Kanojo wa yasashii onna no hito desu.", "kalimat_arti": "Dia adalah wanita yang baik hati."
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
            "kanji": "耳", "audio": "みみ", "kunyomi": "みみ (mimi)", "onyomi": "ジ (ji)", "arti": "Telinga",
            "pilihan": ["Mata", "Mulut", "Telinga", "Tangan"], "baca": "Ji / Mimi",
            "kalimat_jp": "うさぎの耳は長いです。", "kalimat_romaji": "Usagi no mimi wa nagai desu.", "kalimat_arti": "Telinga kelinci panjang."
        },
        {
            "kanji": "手", "audio": "て", "kunyomi": "て (te)", "onyomi": "シュ (shu)", "arti": "Tangan", 
            "pilihan": ["Kaki", "Mata", "Tangan", "Mulut"], "baca": "Shu / Te",
            "kalimat_jp": "手を洗います。", "kalimat_romaji": "Te wo araimasu.", "kalimat_arti": "Saya mencuci tangan."
        },
        {
            "kanji": "足", "audio": "あし", "kunyomi": "あし (ashi)", "onyomi": "ソク (soku)", "arti": "Kaki / Cukup",
            "pilihan": ["Tangan", "Kaki / Cukup", "Kepala", "Badan"], "baca": "Soku / Ashi",
            "kalimat_jp": "足が速いです。", "kalimat_romaji": "Ashi ga hayai desu.", "kalimat_arti": "Kakinya (larinya) cepat."
        },
    ],
    "🚶 Aktivitas & Kata Kerja": [
        {
            "kanji": "見", "audio": "みる", "kunyomi": "みる (miru)", "onyomi": "ケン (ken)", "arti": "Melihat", 
            "pilihan": ["Mendengar", "Melihat", "Makan", "Minum"], "baca": "Ken / Mi",
            "kalimat_jp": "映画を見ます。", "kalimat_romaji": "Eiga wo mimasu.", "kalimat_arti": "Saya menonton film."
        },
        {
            "kanji": "聞", "audio": "きく", "kunyomi": "きく (kiku)", "onyomi": "ブン / モン (bun/mon)", "arti": "Mendengar / Bertanya",
            "pilihan": ["Melihat", "Mendengar / Bertanya", "Membaca", "Menulis"], "baca": "Bun / Ki",
            "kalimat_jp": "音楽を聞きます。", "kalimat_romaji": "Ongaku wo kikimasu.", "kalimat_arti": "Saya mendengarkan musik."
        },
        {
            "kanji": "食", "audio": "たべる", "kunyomi": "たべる (taberu)", "onyomi": "ショク (shoku)", "arti": "Makan", 
            "pilihan": ["Minum", "Makan", "Melihat", "Pergi"], "baca": "Shoku / Ta",
            "kalimat_jp": "ご飯を食べます。", "kalimat_romaji": "Gohan wo tabemasu.", "kalimat_arti": "Saya makan nasi."
        },
        {
            "kanji": "飲", "audio": "のむ", "kunyomi": "のむ (nomu)", "onyomi": "イン (in)", "arti": "Minum", 
            "pilihan": ["Makan", "Minum", "Melihat", "Datang"], "baca": "In / No",
            "kalimat_jp": "お茶を飲みます。", "kalimat_romaji": "Ocha wo nomimasu.", "kalimat_arti": "Saya minum teh."
        },
        {
            "kanji": "行", "audio": "いく", "kunyomi": "いく (iku)", "onyomi": "コウ (kou)", "arti": "Pergi",
            "pilihan": ["Datang", "Pergi", "Pulang", "Jalan"], "baca": "Kou / I",
            "kalimat_jp": "東京へ行きます。", "kalimat_romaji": "Toukyou e ikimasu.", "kalimat_arti": "Saya pergi ke Tokyo."
        },
        {
            "kanji": "来", "audio": "くる", "kunyomi": "くる (kuru)", "onyomi": "ライ (rai)", "arti": "Datang",
            "pilihan": ["Pergi", "Datang", "Pulang", "Masuk"], "baca": "Rai / Ku",
            "kalimat_jp": "友達が家に来ます。", "kalimat_romaji": "Tomodachi ga ie ni kimasu.", "kalimat_arti": "Teman datang ke rumah."
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

    user_text = st.text_input("Masukkan teks Jepang:", value="新幹線で東京へ行きます。")

    if user_text:
        audio_free = generate_audio(user_text, lang="ja")
        st.write("🔊 **Hasil Pelafalan:**")
        st.audio(audio_free, format="audio/mp3")
