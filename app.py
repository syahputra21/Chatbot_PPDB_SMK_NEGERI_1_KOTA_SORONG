"""
# =========================================================
# FILE: app.py
# FUNGSI: Server Utama / Backend / API / Core Application
# DESKRIPSI: Tempat di mana seluruh pengolahan chatbot,
# integrasi AI, pembacaan PDF, database, & web berada.
# =========================================================
"""
import os
import sqlite3
import datetime
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from werkzeug.utils import secure_filename

# ---------------------------------------------------------
# 1. KONFIGURASI AWAL
# ---------------------------------------------------------
load_dotenv() # Membaca variabel dari file .env (seperti GEMINI_API_KEY)
basedir = os.path.abspath(os.path.dirname(__file__))

# Cek apakah dijalankan di Vercel (karena Vercel read-only, hanya bisa nulis di /tmp)
IS_VERCEL = os.environ.get('VERCEL') == '1'

app = Flask(__name__)
# Secret key diperlukan untuk Sistem Session (Fitur Login Admin)
app.secret_key = 'skripsi-sorong-2026'

# Menetapkan folder tempat menyimpan file dokumen PDF
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'dataset')
if not IS_VERCEL and not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Konfigurasi Path Dinamis untuk Vercel
DB_PATH = '/tmp/stats.db' if IS_VERCEL else 'stats.db'
FAISS_INDEX_PATH = os.path.join(basedir, "faiss_index")

# ---------------------------------------------------------
# 2. INISIALISASI DATABASE (SQLite)
# ---------------------------------------------------------
def init_db():
    """Membuat tabel db jika belum ada. Untuk log pengunjung dan token."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tabel visitors mencatat jumlah kunjungan harian
    cursor.execute('CREATE TABLE IF NOT EXISTS visitors (date TEXT PRIMARY KEY, count INTEGER)')
    # Tabel usage mencatat konsumsi token (berapa banyak AI berpikir)
    cursor.execute('CREATE TABLE IF NOT EXISTS usage (id INTEGER PRIMARY KEY AUTOINCREMENT, tokens INTEGER, ts DATETIME)')
    conn.commit()
    conn.close()

def log_visit():
    """Menambah '+1' pada jumlah kunjungan di hari ini saat orang membuka web."""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR IGNORE INTO visitors (date, count) VALUES (?, 0)", (today,))
    conn.execute("UPDATE visitors SET count = count + 1 WHERE date = ?", (today,))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 3. KECERDASAN BUATAN (AI & RAG SYSTEM)
# ---------------------------------------------------------
# Hubungkan ke Google Gemini AI
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Model Embedding untuk mencerna teks PDF mentah menjadi vektor angka
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=os.getenv("GEMINI_API_KEY"))
vector_store = None

def initialize_rag(force_rebuild=False):
    """
    Fungsi ini dipanggil oleh sistem untuk membaca ulang seluruh file PDF yang ada.
    Dijalankan saat server dinyalakan, serta tiap ada dokumen baru/dihapus.
    """
    global vector_store
    
    if not force_rebuild and os.path.exists(FAISS_INDEX_PATH):
        try:
            vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            print("[INFO] Memuat Index RAG (FAISS) dari penyimpanan lokal!")
            return
        except Exception as e:
            print(f"[WARNING] Gagal memuat index lokal: {e}.")
            
    if IS_VERCEL:
        print("[WARNING] Berjalan di Vercel, proses indexing FAISS baru dilewati untuk mencegah timeout.")
        return

    print("[INFO] Membangun ulang Index RAG (FAISS)...")
    all_text = ""
    # 1. Baca semua file di folder "data" yang berakhiran ".pdf"
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        if f.endswith('.pdf'):
            reader = PdfReader(os.path.join(app.config['UPLOAD_FOLDER'], f))
            # 2. Ekstrak huruf/teks dari seluruh halamannya
            for p in reader.pages: 
                all_text += p.extract_text() or ""
    
    # 3. Masukkan ke memori AI jika teks tidak kosong
    if all_text:
        # Teks dipotong-potong supaya konteks tidak terputus (overlap diperbesar)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
        chunks = splitter.split_text(all_text)
        docs = [Document(page_content=t) for t in chunks]
        
        # Simpan teks hasil potongan tersebut menjadi Searchable Vektor Database (FAISS)
        vector_store = FAISS.from_documents(docs, embeddings)
        vector_store.save_local(FAISS_INDEX_PATH)
        print("[INFO] Sistem RAG (Retrieval-Augmented Generation) Siap dan disimpan ke lokal!")
    else:
        # Jika folder PDF kosong
        vector_store = None

# Jalankan inisialisasi pada saat server pertama direstart
init_db()
initialize_rag()

# ---------------------------------------------------------
# 4. RUTE HALAMAN / TAMPILAN WEB MAP (HTML)
# ---------------------------------------------------------
@app.route('/')
def index_page():
    """Menampilkan halaman muka (Beranda Utama)"""
    log_visit()
    return render_template('index.html')

@app.route('/chatbot')
def chatbot_page():
    """Menampilkan halaman Chatbot (Terpisah dari Beranda)"""
    log_visit()
    return render_template('chatbot.html')

@app.route('/login')
def login_page():
    """Menampilkan halaman Login Khusus Admin"""
    if session.get('logged_in'):
        from flask import redirect
        return redirect('/admin')
    return render_template('login.html')

@app.route('/admin')
def admin_page():
    """Menampilkan halaman Dashboard (Login Admin)"""
    from flask import redirect
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('admin.html')

@app.route('/informasi')
def informasi_page():
    """Menampilkan halaman statis berisi informasi, jadwal, dan syarat PPDB"""
    return render_template('informasi.html')

@app.route('/tentang')
def tentang_page():
    """Menampilkan profil sekolah, visi misi, dan Google Maps"""
    return render_template('tentang.html')

# ---------------------------------------------------------
# 5. RUTE API / LOGIKA PEMROSESAN WEB (Backend Controller)
# ---------------------------------------------------------

@app.route('/chat', methods=['POST'])
def chat():
    """Jantung AI: Menerima Chat Siswa dan membalasnya dengan dokumen terkait secara Streaming."""
    msg = request.json.get('message', '')
    if not msg: 
        return jsonify({"reply": "Pesan kosong."})
    
    context = ""
    # Ambil referensi dokumen yang topiknya mirip/sama dengan chat siswa
    if vector_store:
        try:
            # K-diperbesar agar AI dapat membaca lebih banyak referensi dari dataset
            docs = vector_store.similarity_search(msg, k=8)
            context = "\n".join([d.page_content for d in docs])
        except Exception: 
            pass
    
    history_arr = request.json.get('history', [])
    history_text = ""
    if history_arr:
        history_text = "Riwayat Obrolan Sebelumnya:\n"
        for h in history_arr:
            role = "Siswa" if h.get("role") == "user" else "Asisten"
            history_text += f"{role}: {h.get('text')}\n"
        history_text += "\n"
        
    prompt = f"""Anda adalah asisten virtual PPDB SMKN 1 Sorong. Jawablah pertanyaan siswa dengan ramah, jelas, dan informatif.
Data pedoman:
{context}

{history_text}Pertanyaan Siswa saat ini: {msg}

(Penting: 
1. Berikan jawaban SECARA SPESIFIK dan AKURAT HANYA berdasarkan Data pedoman di atas. Jangan berhalusinasi informasi.
2. JANGAN MENGULANG poin, paragraf, atau kalimat yang sama berkali-kali. Pastikan setiap poin berbeda dan alur jawaban logis.
3. JANGAN menggunakan backtick (`) saat menulis alamat URL/Website. Tulis dengan format Markdown Link (contoh: [Website Pendaftaran](https://contoh.id)).
4. Jika jawaban tidak ditemukan dalam Data pedoman, sampaikan permohonan maaf dan sarankan siswa untuk menghubungi panitia PPDB SMKN 1 Sorong.
5. Berikan langsung jawaban Anda sebagai asisten tanpa membuat dialog tambahan.
6. Buatlah format jawaban yang rapi (paragraf pendek atau poin-poin). Gunakan gaya bahasa yang bersahabat dan tidak kaku.)"""
    
    def generate():
        import time
        max_retries = 2
        for attempt in range(max_retries):
            try:
                local_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                response_stream = local_client.models.generate_content_stream(
                    model='gemini-2.5-flash-lite',
                    contents=prompt
                )
                full_response = ""
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        yield chunk.text
                break  # Sukses, keluar dari loop retry, lanjut ke pencatatan token
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1) # Tunggu sejenak sebelum retry
                    continue
                else:
                    print(f"[ERROR GEMINI] {str(e)}")
                    yield "\nMaaf, server AI saat ini sedang sangat sibuk (Overload). Mohon coba tanyakan lagi dalam beberapa saat ya."
                
        # Catat biaya token prompt dan balasan setelah stream selesai
        try:
            tokens = len(prompt.split()) + len(full_response.split())
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO usage (tokens, ts) VALUES (?, ?)", (tokens, datetime.datetime.now()))
            conn.commit()
            conn.close()
        except:
            pass

    from flask import Response
    return Response(generate(), mimetype='text/plain')
@app.route('/api/login', methods=['POST'])
def login():
    """Verifikasi Username & Password Admin (HARDCODED)"""
    d = request.json
    if d.get('username') == 'admin' and d.get('password') == 'admin123':
        session['logged_in'] = True
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/api/admin_stats')
def admin_stats():
    """Sajikan Data Statistik Pengunjung, Total Token Pemakaian dan Total PDF"""
    conn = sqlite3.connect(DB_PATH)
    v = conn.execute("SELECT * FROM visitors ORDER BY date DESC LIMIT 7").fetchall()
    t = conn.execute("SELECT SUM(tokens) FROM usage").fetchone()[0] or 0
    conn.close()
    return jsonify({"visitors": v, "total_tokens": t, "docs_count": len(os.listdir(app.config['UPLOAD_FOLDER']))})

@app.route('/api/clear_stats', methods=['POST'])
def clear_stats():
    """Menghapus data log pengunjung dan usage (reset)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM visitors")
        conn.execute("DELETE FROM usage")
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/list_files')
def list_files(): 
    """Mendeteksi seluruh nama file di folder data bagi halaman Admin."""
    return jsonify(os.listdir(app.config['UPLOAD_FOLDER']))

@app.route('/api/upload_pdf', methods=['POST'])
def upload():
    """Menerima unggahan File PDF dan merekam ulang ke memori AI (RAG)."""
    if IS_VERCEL:
        return jsonify({"success": False, "error": "Vercel bersifat Read-Only. Tidak bisa upload PDF baru di server Vercel."}), 403
        
    f = request.files.get('file')
    if f:
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        initialize_rag(force_rebuild=True) # WAJIB dipanggil agar AI pintar mengenai PDF yang baru saja masuk
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/delete_file', methods=['POST'])
def delete():
    """Menghapus PDF tertentu dari folder Data dan menyesuaikan otak AI."""
    if IS_VERCEL:
        return jsonify({"success": False, "error": "Vercel bersifat Read-Only. Tidak bisa menghapus PDF di server Vercel."}), 403
        
    fn = request.json.get('filename')
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fn))
        initialize_rag(force_rebuild=True)
        return jsonify({"success": True})
    except Exception: 
        return jsonify({"success": False})

@app.route('/api/logout', methods=['POST'])
def logout(): 
    """Keluar dari akun Admin."""
    session.pop('logged_in', None)
    return jsonify({"success": True})

# ---------------------------------------------------------
# MENJALANKAN SERVER
# ---------------------------------------------------------
if __name__ == '__main__':
    # Buka alamat => http://127.0.0.1:5000/ pada browser
    print("\n" + "="*50)
    print("🚀 SERVER WEBSITE & CHATBOT PPDB AKTIF")
    print("="*50)
    print("🔑 AKUN ADMIN DEFAULT (Untuk Login):")
    print("   Username : admin")
    print("   Password : admin123")
    print("="*50 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
