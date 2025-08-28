# COBOL + FastAPI Debug Task

Your task:

1. Fix `main.cob` so it works correctly.
2. Fix `Dockerfile` so the app runs end-to-end.

Rules:

- **Do NOT modify** `app.py` or `index.html`.
- You can change anything in `main.cob` and `Dockerfile`.
- Input/output files (`input.txt`, `output.txt`, `accounts.txt`) are provided.

How to test:

```bash
docker build -t cobol-app .
docker run --rm -p 8000:8000 cobol-app
docker run --rm cobol-app ./main --apply-interest
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/interest.yaml
kubectl apply -f k8s/ingress.yaml
```

---

## Keterangan Bonus yang Dikerjakan

- **(2 poin) Konversi ke Rupiah**
  Ditambahkan logika di `main.cob` untuk mengonversi saldo dari satuan _Rai Stone_ ke **IDR** sebelum ditulis ke `output.txt`. Dengan ini, setiap saldo otomatis ditampilkan dalam Rupiah.

- **(3 poin) Deploy dengan Kubernetes**
  Membuat manifest di folder `k8s/` (`deployment.yaml`, `service.yaml`, `interest.yaml`, `ingress.yaml`). Deployment ini memastikan aplikasi COBOL + FastAPI berjalan di dalam cluster Kubernetes dan bisa diakses lewat service & ingress.

- **(4 poin) Auto-Interest tiap 23 detik**
  Menambahkan fitur `--apply-interest` pada `main.cob`. Saat argumen ini dipakai, program menghitung bunga berdasarkan saldo dan menambahkannya secara otomatis setiap 23 detik. Di Kubernetes, hal ini dijalankan menggunakan (`interest.yaml`).

- **(2 poin) Reverse Proxy**
  Menambahkan konfigurasi reverse proxy (nginx) agar akses ke aplikasi lebih stabil dan bisa diatur routing-nya, misalnya untuk load balancing atau integrasi dengan ingress.

---

## Bonus yang Tidak Dikerjakan

- **(2 poin) Domain + HTTPS** → tidak dikerjakan.
