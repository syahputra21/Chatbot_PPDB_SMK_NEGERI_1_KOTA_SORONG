"""
# =========================================================
# FILE: test_pdf_reader.py 
# (Sebelumnya bernama "diagnose_pdf.py")
#
# FUNGSI: Alat / Tester Bacaan PDF
# DESKRIPSI: Digunakan hanya oleh programmer/developer secara 
# manual untuk mengecek apakah komputer bisa membaca urutan 
# teks dari dokumen PDF yang dijadikan referensi chatbot.
# =========================================================
"""

import os
from pypdf import PdfReader

def diagnostic():
    # Mengambil otomatis path folder utama (dinamis)
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path menuju contoh dokumen, ubah nama filenya sesuai dengan file yang Anda tes.
    # Contoh kita tes PDF PPDB yang ada di dalam folder data.
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'Penerimaan Peserta Didik Baru.pdf')
    
    if not os.path.exists(file_path):
        print(f"File PDF tidak ditemukan di: {file_path}")
        print("Pastikan terdapat file dengan nama tersebut di folder 'data'.")
        return

    print(f"--- DIAGNOSA FILE PDF ---")
    try:
        reader = PdfReader(file_path)
        total_text = ""
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                print(f"\n[INFO] --- Isi Halaman {i+1} ---")
                print(text)
                total_text += text
            else:
                print(f"\n[INFO] --- Halaman {i+1} (TEKS KOSONG atau berisi GAMBAR SAJA) ---")
        
        print(f"\nTotal panjang karakter terbaca: {len(total_text)} huruf/simbol.")
        if "jurusan" in total_text.lower():
            print("[HASIL] > Kata patokan 'jurusan' DITEMUKAN dalam teks ekstraksi sukses.")
        else:
            print("[HASIL] > Kata 'jurusan' TIDAK DITEMUKAN. (Mungkin tulisannya terenkripsi/hanya scan gambar).")
            
    except Exception as e:
        print(f"[ERROR MUNCUL]: {e}")

if __name__ == "__main__":
    diagnostic()
