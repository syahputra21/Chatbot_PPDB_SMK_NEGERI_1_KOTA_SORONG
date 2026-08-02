# Update Keseluruhan Sistem PPDB SMKN 1 Sorong (27 Juli 2026)
"""
# =========================================================
# FILE: evaluate.py
# FUNGSI: Script Evaluasi Akurasi dengan Metrik BERTScore
# DESKRIPSI: Digunakan untuk memberikan nilai F1, Precision,
# dan Recall pada performa AI. Sangat krusial untuk mengisi
# tabel Evaluasi pada Bab 4 Penulisan Skripsi.
# =========================================================
"""
import pandas as pd
# pyrefly: ignore [missing-import]
from bert_score import score
import time
import re

# ========== Kelas Warna (Visual Console) ==========
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    CYAN    = "\033[96m"   # Header/judul
    GREEN   = "\033[92m"   # Skor Bagus
    BLUE    = "\033[94m"   # Highlight Teks
    ORANGE  = "\033[38;5;214m" # Skor Sedang
    YELLOW  = "\033[93m"   # Skor Cukup
    RED     = "\033[91m"   # Skor Rendah
    WHITE   = "\033[97m"
    DIM     = "\033[2m"

def color_score(val):
    """Warnai skor berdasarkan nilainya"""
    if val >= 0.80:
        return f"{C.GREEN}{val:.4f}{C.RESET}"
    elif val >= 0.70:
        return f"{C.ORANGE}{val:.4f}{C.RESET}"
    else:
        return f"{C.YELLOW}{val:.4f}{C.RESET}"

# ========== Preprocessing ==========
def clean_candidate(text):
    """
    Membersihkan teks jawaban AI dari basa-basi agar 
    penilaian BERTScore menjadi adil dan berfokus pada inti jawaban.
    """
    # Hapus emoji
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F9FF"  # Misc symbols & pictographs
        "\u2600-\u27BF"          # Misc symbols
        "\u2700-\u27BF"          # Dingbats
        "\u274C\u2705\u2714\u2716"  
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub("", text)
    
    # Hapus intro/salam pembuka AI
    intro_patterns = [
        r"^(Tentu,?\s*)?((halo!?\s*)?(saya\s+)?(asisten|asisten PPDB|bot|saya)\s+(akan\s+)?(bantu|membantu|menjawab|siap|help).*?\.)\s*",
        r"^(Halo!?\s*)?(Selamat datang di.*?\.)\s*",
        r"^(Tentu,?\s*)?((berikut\s+)?(adalah\s+)?(jawaban|informasi).*?\:)\s*",
    ]
    for pattern in intro_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    # Hapus salam penutup AI
    outro_patterns = [
        r"(\s*Semoga\s+(membantu|informasi ini bermanfaat).*)$",
        r"(\s*Jika\s+(ada|masih ada)\s+(pertanyaan|yang ingin ditanyakan).*)$",
        r"(\s*Silahkan\s+(hubungi|tanyakan).*)$"
    ]
    for pattern in outro_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
    # Hapus whitespace berlebih
    text = re.sub(r"\s+", " ", text).strip()
    return text

def run_evaluation():
    print(f"\n{C.CYAN}{C.BOLD}{'='*60}")
    print(f"--- MEMULAI EVALUASI SISTEM CHATBOT PPDB (BERTSCORE) ---")
    print(f"{'='*60}{C.RESET}")
    
    # 1. Siapkan Draf Kasus Pengujian / Skenario
    data = {
        "Pertanyaan": [
            "Program keahlian atau jurusan apa saja yang tersedia bagi calon peserta didik baru di SMK Negeri 1 Sorong",
            "Bagaimana cara melakukan pendaftaran di SMK Negeri 1 Sorong",
            "Apakah terdapat persyaratan khusus, seperti tes fisik atau tes buta warna, untuk mendaftar pada program keahlian Teknik Jaringan Komputer dan Telekomunikasi",
            "Kapan pelaksanaan pendaftaran PPDB SMK Negeri 1 Sorong Tahun Ajaran 2026/2027 mulai dibuka",
            "Di mana alamat lengkap SMK Negeri 1 Sorong yang digunakan untuk proses pengumpulan dan verifikasi berkas pendaftaran",
            "Apakah calon peserta didik dikenakan biaya pada saat melakukan pendaftaran PPDB di SMK Negeri 1 Sorong",
            "Apakah SMK Negeri 1 Sorong menerima peserta didik baru melalui jalur prestasi akademik maupun non akademik",
            "Kegiatan ekstrakurikuler apa saja yang dapat diikuti peserta didik untuk mengembangkan minat dan bakat di SMK Negeri 1 Sorong",
            "Dokumen dan berkas apa saja yang harus disiapkan calon peserta didik saat melakukan daftar ulang",
            "Berapa jumlah kuota penerimaan peserta didik baru yang disediakan oleh SMK Negeri 1 Sorong pada Tahun Ajaran 2026/2027"
        ],
        "Jawaban_Reference_(Ground Truth)": [ 
            "SMK Negeri 1 Sorong menyediakan 9 Program Keahlian, yaitu Akuntansi dan Keuangan Lembaga, Manajemen Perkantoran dan Layanan Bisnis, Pemasaran (Kelas Alfamart), Teknik Jaringan Komputer dan Telekomunikasi, Desain Komunikasi Visual, Pengembangan Perangkat Lunak dan Gim, Teknik Geologi Pertambangan, Teknik Perminyakan, dan Teknik Energi Terbarukan.",
            "Pendaftaran dilakukan secara online dan offline. Calon peserta didik terlebih dahulu melakukan pendaftaran melalui sistem pendaftaran online (SPMB) pada laman spmbkota.sorongdigital.id, kemudian datang ke sekolah dengan membawa bukti pendaftaran dan dokumen persyaratan untuk proses verifikasi.",
            "Tidak ada persyaratan khusus seperti tes fisik atau tes bebas buta warna untuk mendaftar pada program keahlian Teknik Jaringan Komputer dan Telekomunikasi. Tahapan seleksi umum hanya terdiri atas tes tertulis dan wawancara serta pemenuhan batas usia maksimal 21 tahun.",
            "Pelaksanaan pendaftaran PPDB SMK Negeri 1 Sorong Tahun Ajaran 2026/2027 dibuka mulai tanggal 17 Juni 2026 sampai dengan 20 Juni 2026.",
            "SMK Negeri 1 Sorong beralamat di Jl. Basuki Rahmat, Kilometer 8, Kelurahan Malaingkedi, Kecamatan Malaimsimsa, Kota Sorong, Provinsi Papua Barat Daya. Gedung pelayanan panitia berada di sebelah kiri jalur masuk sekolah (bangunan dua lantai berwarna biru).",
            "Pendaftaran PPDB dan proses daftar ulang di SMK Negeri 1 Sorong tidak dikenakan biaya (gratis). Selain itu, sekolah juga tidak memungut biaya uang sekolah atau SPP.",
            "Ya, penerimaan peserta didik baru di SMK Negeri 1 Sorong dilaksanakan melalui Jalur Prestasi, yaitu jalur yang diperuntukkan bagi calon murid yang memiliki prestasi akademik maupun non akademik yang dibuktikan dengan sertifikat atau piagam penghargaan asli.",
            "Kegiatan ekstrakurikuler yang tersedia di SMK Negeri 1 Sorong antara lain Pramuka, Palang Merah Remaja (PMR), Mapala (Pecinta Alam), Paskibra, Basket, Futsal, Sepak Bola, Bulu Tangkis, Pencak Silat, dan Marching Band.",
            "Berkas daftar ulang meliputi fotokopi SKL, Akte Kelahiran, Kartu Keluarga terbaru, KPS/PKH/KIP (jalur afirmasi), rapor semester 1-5, Sertifikat TKA, piagam prestasi (jalur prestasi), Materai Rp10.000 (1 lembar), serta Map merah untuk OAP atau Map biru untuk non-OAP.",
            "Total kuota penerimaan peserta didik baru SMK Negeri 1 Sorong Tahun Ajaran 2026/2027 adalah sebanyak 684 peserta didik yang terbagi ke dalam 9 Program Keahlian."
        ],
        "Jawaban_Generated_(Hasil AI)": [    
            "SMK Negeri 1 Sorong menyediakan 9 program keahlian yang dapat dipilih oleh calon peserta didik baru, antara lain: Akuntansi dan Keuangan Lembaga, Manajemen Perkantoran dan Layanan Bisnis, Pemasaran (Kelas Alfamart), Teknik Jaringan Komputer dan Telekomunikasi, Desain Komunikasi Visual, Pengembangan Perangkat Lunak dan Gim, Teknik Geologi Pertambangan, Teknik Perminyakan, dan Teknik Energi Terbarukan.",
            "Proses pendaftaran PPDB dilakukan melalui dua tahapan, yaitu online dan offline. Pertama, calon peserta didik mendaftar secara online melalui website resmi spmbkota.sorongdigital.id. Setelah itu, calon peserta didik wajib datang langsung ke SMK Negeri 1 Sorong dengan membawa bukti pendaftaran dan dokumen persyaratan untuk dilakukan verifikasi oleh panitia.",
            "Untuk mendaftar di program keahlian Teknik Jaringan Komputer dan Telekomunikasi (TJKT), sekolah tidak mempersyaratkan tes fisik maupun tes buta warna. Seluruh calon peserta didik mengikuti ketentuan umum yaitu usia maksimal 21 tahun serta mengikuti seleksi tes tertulis dan wawancara.",
            "Jadwal pendaftaran PPDB di SMK Negeri 1 Sorong untuk Tahun Ajaran 2026/2027 dibuka pada tanggal 17 Juni 2026 hingga 20 Juni 2026.",
            "Alamat lengkap SMK Negeri 1 Sorong terletak di Jl. Basuki Rahmat, Kilometer 8, Kelurahan Malaingkedi, Kecamatan Malaimsimsa, Kota Sorong, Provinsi Papua Barat Daya. Untuk pengumpulan dan verifikasi berkas, calon peserta didik dapat menuju gedung model kantor dua lantai berwarna biru di sebelah kiri gerbang masuk.",
            "Calon peserta didik tidak dikenakan biaya sama sekali alias gratis saat melakukan pendaftaran PPDB maupun proses daftar ulang. SMK Negeri 1 Sorong juga tidak memungut biaya uang SPP.",
            "Ya, SMK Negeri 1 Sorong menerima peserta didik baru melalui Jalur Prestasi. Jalur ini diperuntukkan bagi siswa yang memiliki prestasi akademik maupun non akademik dengan melampirkan bukti sertifikat atau piagam penghargaan asli.",
            "Di SMK Negeri 1 Sorong terdapat berbagai kegiatan ekstrakurikuler untuk mengembangkan minat dan bakat peserta didik, antara lain Pramuka, PMR, Mapala, Paskibra, Basket, Futsal, Sepak Bola, Bulu Tangkis (Badminton), Pencak Silat, dan Marching Band.",
            "Dokumen yang harus disiapkan saat daftar ulang antara lain fotokopi Surat Keterangan Lulus (SKL), Akta Kelahiran, KK terbaru, rapor semester 1 sampai 5, sertifikat TKA, piagam prestasi (jika ada), KPS/KIP (jika ada), 1 lembar materai Rp10.000, serta map merah untuk siswa OAP dan map biru untuk siswa non-OAP.",
            "Jumlah kuota penerimaan peserta didik baru di SMK Negeri 1 Sorong pada Tahun Ajaran 2026/2027 adalah sebanyak 684 kursi yang tersebar di 9 program keahlian."
        ]
    }

    df = pd.DataFrame(data)
    
    # Lakukan Preprocessing / Pembersihan
    cleaned_candidates = [clean_candidate(ans) for ans in df['Jawaban_Generated_(Hasil AI)'].tolist()]

    # 2. Perhitungan Statistik via Pustaka BERTScore
    print(f"{C.DIM}[INFO] Mengeksekusi model BERT Multilingual untuk Bahasa Indonesia...{C.RESET}")
    print(f"{C.DIM}       Hal ini mungkin membutuhkan sedikit waktu (membutuhkan internet).{C.RESET}")
    start_time = time.time()
    
    Precision, Recall, F1 = score(
        cleaned_candidates, 
        df['Jawaban_Reference_(Ground Truth)'].tolist(), 
        lang="id", 
        verbose=True
    )
    
    df['Nilai Precision (P)'] = Precision.tolist()
    df['Nilai Recall (R)'] = Recall.tolist()
    df['Nilai F1-Score'] = F1.tolist()

    duration = time.time() - start_time
    print(f"\n{C.GREEN}[SUKSES]{C.RESET} Evaluasi BERTScore rampung dalam {C.BOLD}{duration:.2f} detik.{C.RESET}\n")

    # 3. Melakukan Print ke Layar CMD (Tampilan Tabel Berwarna)
    print(f"{C.CYAN}{C.BOLD}=== HASIL EVALUASI UNTUK BAB 4 SKRIPSI ==={C.RESET}")
    print(f"{C.BOLD}{'Pertanyaan (Singkat)':<36} | {'Precision':<9} | {'Recall':<9} | {'F1-Score':<9}{C.RESET}")
    print(f"{C.DIM}{'-' * 70}{C.RESET}")
    
    for _, row in df.iterrows():
        pertanyaan = str(row['Pertanyaan'])
        if len(pertanyaan) > 33:
            pertanyaan = pertanyaan[:30] + "..."
            
        p_val = color_score(row['Nilai Precision (P)'])
        r_val = color_score(row['Nilai Recall (R)'])
        f1_val = color_score(row['Nilai F1-Score'])
        
        # Pengecualian formatting karena kode ANSI mempengaruhi panjang string, 
        # kita print langsung dengan jarak tabulasi custom
        print(f"{C.WHITE}{pertanyaan:<36}{C.RESET} | {p_val:<18} | {r_val:<18} | {f1_val:<18}")
    
    # 4. Hitung Rata-rata dan Grading
    avg_p = df['Nilai Precision (P)'].mean()
    avg_r = df['Nilai Recall (R)'].mean()
    avg_f1 = df['Nilai F1-Score'].mean()
    
    print(f"{C.DIM}{'-' * 70}{C.RESET}")
    print(f"{C.BOLD}{'RATA-RATA KESELURUHAN':<36}{C.RESET} | {color_score(avg_p):<18} | {color_score(avg_r):<18} | {color_score(avg_f1):<18}")
    print(f"{C.CYAN}{C.BOLD}{'='*70}{C.RESET}")

    # Interpretasi (Grading)
    print(f"\n{C.CYAN}{C.BOLD}[INTERPRETASI KINERJA AI]{C.RESET}")
    if avg_f1 >= 0.75:
        grade = f"{C.GREEN}SANGAT BAIK{C.RESET}"
    elif avg_f1 >= 0.60:
        grade = f"{C.ORANGE}BAIK{C.RESET}"
    elif avg_f1 >= 0.45:
        grade = f"{C.YELLOW}CUKUP{C.RESET}"
    else:
        grade = f"{C.RED}KURANG{C.RESET}"

    print(f"   {C.BOLD}Skor F1 Gabungan : {C.BLUE}{avg_f1:.4f}{C.RESET}")
    print(f"   {C.BOLD}Kesimpulan       : Kinerja Bot PPDB tergolong {grade}")
    print()

    # 5. Eksport Hasil ke Format CSV
    excel_file = "hasil_evaluasi_bertscore.csv"
    df.to_csv(excel_file, index=False)
    print(f"{C.GREEN}[SUKSES]{C.RESET} Output mentah sukses diamankan dalam: {C.BLUE}{excel_file}{C.RESET}")
    print(f"{C.DIM}         (Buka Excel, import file CSV ini untuk merapikan tabel Bab 4).{C.RESET}\n")

if __name__ == "__main__":
    try:
        run_evaluation()
    except Exception as e:
        print(f"\n{C.RED}{C.BOLD}[GAGAL EROR] =>{C.RESET} {e}")
        print("\n*Apakah Anda sudah install semua pustaka Evaluasi?")
        print(f"  - {C.BLUE}pip install evaluate{C.RESET}")
        print(f"  - {C.BLUE}pip install bert-score pandas torch{C.RESET}")
