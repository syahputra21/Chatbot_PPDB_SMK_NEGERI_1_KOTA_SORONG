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
            "Untuk pendaftaran peserta didik baru, apa saja pilihan program studi atau jurusan yang saat ini ditawarkan di SMK Negeri 1 Sorong?",
            "Saya masih kurang paham mengenai tahapannya, tolong berikan panduan lengkap tata cara mendaftar sebagai siswa baru secara online maupun offline.",
            "Apakah ada syarat tambahan seperti tes fisik atau tes bebas buta warna jika saya berminat mendaftar di program keahlian Teknik Komputer Jaringan?",
            "Kapan jadwal resmi pendaftaran Penerimaan Peserta Didik Baru (PPDB) tahun ajaran ini akan mulai dibuka?",
            "Mohon informasi mengenai alamat lengkap SMK Negeri 1 Kota Sorong untuk keperluan pengumpulan berkas.",
            "Terkait proses pendaftaran awal di sekolah ini, apakah calon siswa baru diwajibkan untuk membayar sejumlah uang pendaftaran tertentu?",
            "Apakah sekolah ini menerima pendaftaran siswa baru melalui jalur prestasi akademik atau non-akademik?",
            "Kegiatan ekstrakurikuler apa saja yang tersedia di sekolah ini untuk pengembangan minat bakat siswa?",
            "Berkas dan dokumen penting apa saja yang harus disiapkan oleh calon siswa baru saat melakukan daftar ulang?",
            "Berapa total kuota penerimaan peserta didik baru yang disediakan oleh SMKN 1 Sorong pada tahun ini?"
        ],
        "Jawaban_Reference_(Ground Truth)": [ 
            "Terdapat 9 jurusan yaitu TKJ, AKL, OTKP, BDP, Multimedia, DPIB, BKP, Geomatika, dan Perhotelan.",
            "Pendaftaran dilakukan secara online melalui website resmi atau datang langsung ke sekolah.",
            "Syarat masuk TKJ antara lain nilai rapot yang cukup, tidak buta warna, dan lulus tes fisik.",
            "Pendaftaran PPDB biasanya dibuka pada bulan Juni hingga Juli setiap tahunnya.",
            "Alamat sekolah berada di Jalan Jendral Sudirman, Kota Sorong, Papua Barat Daya.",
            "Pendaftaran PPDB di SMKN 1 Sorong tidak dipungut biaya alias gratis.",
            "Ya, terdapat jalur prestasi akademik dan non-akademik dengan kuota tertentu.",
            "Terdapat berbagai ekstrakurikuler seperti Pramuka, Paskibra, PMR, Rohis, dan Olahraga.",
            "Berkas daftar ulang meliputi fotokopi SKHU, pas foto 3x4, fotokopi KK, dan akta kelahiran.",
            "Kuota penerimaan siswa baru tahun ini adalah sebanyak 360 siswa yang terbagi ke dalam 9 jurusan."
        ],
        "Jawaban_Generated_(Hasil AI)": [    
            "Halo! Saya asisten PPDB. Terdapat 9 jurusan yang bisa dipilih yaitu TKJ, AKL, OTKP, BDP, Multimedia, DPIB, BKP, Geomatika, dan Perhotelan. Semoga membantu!",
            "Tentu, berikut informasinya: Untuk mendaftar, proses pendaftaran dilakukan secara online melalui website resmi atau datang langsung ke sekolah. Jika ada pertanyaan lain, silakan tanyakan.",
            "Tentu, berikut adalah jawaban: Syarat masuk jurusan TKJ antara lain meliputi nilai rapot yang cukup, tidak buta warna, dan dinyatakan lulus tes fisik.",
            "Pendaftaran mulai dibuka pada pertengahan tahun, biasanya sekitar bulan Juni.",
            "SMKN 1 berlokasi di pusat Kota Sorong, tepatnya di Jl. Jendral Sudirman.",
            "Halo! Saya asisten PPDB. Proses pendaftaran PPDB di SMKN 1 Sorong tidak dipungut biaya alias gratis.",
            "Tentu saja! Ada jalur prestasi akademik dan non-akademik bagi siswa berprestasi.",
            "Di SMKN 1 Sorong ada ekstrakurikuler wajib seperti Pramuka, dan pilihan seperti PMR atau Olahraga.",
            "Anda perlu menyiapkan dokumen seperti SKHU, fotokopi KK, Akta kelahiran dan pas foto ukuran 3x4.",
            "Tahun ini kuota yang tersedia adalah sekitar 360 siswa untuk semua jurusan yang ada."
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
