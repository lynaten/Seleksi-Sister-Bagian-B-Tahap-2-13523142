# BTC – Simple Blockchain Network

Proyek ini adalah implementasi sederhana dari konsep Bitcoin Network menggunakan Python + Flask.
Mendukung transaksi, mining dengan Proof-of-Work, sinkronisasi antar-node, dan konfigurasi difficulty.

📑 **Video Demonstrasi:**
[LINK YOUTUBE](https://youtu.be/-xoo5lX9Vx8)

---

## Persiapan Lingkungan

1. **Masuk ke folder project**

   ```bash
   cd '$BTC'
   ```

2. **Buat virtual environment (opsional tapi disarankan)**

   Di WSL/Linux:

   ```bash
   python3 -m venv venv
   ```

   Di Windows (PowerShell):

   ```powershell
   python -m venv venv
   ```

3. **Aktifkan virtual environment**

   - WSL/Linux:

     ```bash
     source ./venv/bin/activate
     ```

   - Windows (PowerShell):

     ```powershell
     .\venv\Scripts\activate
     ```

4. **Install dependency**

   ```bash
   python3 -m pip install -r requirements.txt
   ```

---

## Menjalankan Node

Setiap node dijalankan dengan `run_node.py` menggunakan port berbeda.

- Node pertama (bootstrap node, port 5001):

  ```bash
  python run_node.py 5001 --difficulty 4
  ```

- Node kedua (akan otomatis bootstrap ke node 5001):

  ```bash
  python run_node.py 5002 --difficulty 4
  ```

- Node ketiga:

  ```bash
  python run_node.py 5003 --difficulty 4
  ```

> Difficulty bisa diubah dengan argumen `--difficulty` saat startup,
> atau runtime lewat endpoint `/set_difficulty`.

---

## Endpoint Penting

### Tambah Transaksi

```bash
curl -X POST http://localhost:5002/transaction \
     -H "Content-Type: application/json" \
     -d '{"sender":"Alice","recipient":"Bob","amount":15}'
```

### Mining Block

```bash
curl http://localhost:5002/mine
```

### Lihat Blockchain

```bash
curl http://localhost:5002/chain
```

### Ubah Difficulty (opsional)

```bash
curl -X POST http://localhost:5002/set_difficulty \
     -H "Content-Type: application/json" \
     -d '{"difficulty": 5}'
```

---

## Catatan

- Node bootstrap harus selalu dijalankan dulu di port `5001`.
- Node lain akan otomatis mendaftarkan diri ke bootstrap node.
- Chain sinkronisasi menggunakan **Longest Chain Rule**.
- Tidak ada mekanisme tie-breaker untuk chain dengan panjang sama → node akan menunggu sampai salah satu chain lebih panjang.
