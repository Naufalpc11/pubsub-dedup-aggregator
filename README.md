# Panduan Pengujian UTS Pub-Sub Dedup Aggregator

Dokumen ini berisi urutan langkah pengujian dari awal (Docker running) sampai akhir testing.

## Asumsi

- Docker Desktop sudah terpasang dan Docker Engine dalam status Running.
- Port `8080` pada host tidak sedang dipakai aplikasi lain.
- Pengujian dilakukan lokal (localhost/container network), tanpa layanan eksternal publik.
- File project sudah lengkap (`Dockerfile`, `requirements.txt`, `src/`, `tests/`).
- Virtual environment Python tersedia untuk menjalankan unit test.
- Dedup store menggunakan SQLite lokal sehingga persistensi diuji pada konteks restart container.

## 1. Persiapan Awal

1. Buka Docker Desktop.
2. Pastikan status Docker Engine sudah Running.
3. Buka terminal PowerShell.
4. Masuk ke folder project.

```powershell
cd "D:\Semester 6\Sister\UTS\pubsub-dedup-aggregator"
```

### Bukti Gambar

![Struktur folder proyek](image/struktur-folder.png)

## 2. Build Image Aggregator

Jalankan build image sesuai instruksi deliverable.

```powershell
docker build -t uts-aggregator .
```

Ekspektasi:
- Build sukses tanpa error.
- Image bernama uts-aggregator muncul di Docker Images.

### Bukti Gambar

![Build image docker](image/(build-image)-docker-build--uts-aggregator.png)

## 3. Jalankan Service Aggregator (Single Container)

Jalankan container aggregator di port 8080.

```powershell
docker run --name uts-aggregator -p 8080:8080 uts-aggregator
```

Ekspektasi:
- Container running.
- Log uvicorn muncul.
- Service aktif di http://localhost:8080.

### Bukti Gambar

![Run container aggregator](image/run-container.png)

![Docker running](image/docker-running.png)

## 4. Uji Endpoint Dasar

Buka terminal baru (container tetap running), lalu jalankan:

Catatan PowerShell:
- Hindari `curl` alias bawaan PowerShell karena sering menimbulkan error parameter/escaping.
- Gunakan `irm` (Invoke-RestMethod) dengan body dari hashtable.

### 4.1 Health Check Root

```powershell
irm http://localhost:8080/
```

Ekspektasi:
- Response JSON berisi message bahwa aggregator aktif.

### Bukti Gambar

![Health check root](image/check-health-aggregator.png)

### 4.2 Publish Single Event

```powershell
$event = @{
  topic = "sensor"
  event_id = "evt-1"
  timestamp = "2026-01-01T10:00:00"
  source = "device-1"
  payload = @{ temp = 30 }
} | ConvertTo-Json -Depth 5

irm "http://localhost:8080/publish" -Method Post -ContentType "application/json" -Body $event
```

Ekspektasi:
- Status sukses.
- Field received bernilai 1.

### Bukti Gambar

![Kirim satu event](image/send-one-topic.png)

### 4.3 Publish Duplicate Event (Idempotency Test)

Kirim payload yang sama sekali lagi:

```powershell
$event = @{
  topic = "sensor"
  event_id = "evt-1"
  timestamp = "2026-01-01T10:00:00"
  source = "device-1"
  payload = @{ temp = 30 }
} | ConvertTo-Json -Depth 5

irm "http://localhost:8080/publish" -Method Post -ContentType "application/json" -Body $event
```

Ekspektasi:
- Request tetap diterima.
- Event duplikat tidak diproses ulang.

### Bukti Gambar

![Duplicate terdeteksi](./image/duplicate-detected-after-dedup.png)

### 4.4 Cek Event Tersimpan

```powershell
irm "http://localhost:8080/events?topic=sensor"
```

Ekspektasi:
- Event unik hanya muncul satu kali untuk event_id evt-1.

### Bukti Gambar

![Hasil query events topic sensor](image/irm-topic-sensor.png)

### 4.5 Cek Statistik

```powershell
irm "http://localhost:8080/stats"
```

Ekspektasi:
- Response memiliki field:
  - received
  - unique_processed
  - duplicate_dropped
  - topics
  - uptime

### Bukti Gambar

![Hasil endpoint stats](image/irm-stats.png)

## 5. Uji Validasi Skema (Schema Validation)

Kirim event tidak valid (tanpa timestamp):

```powershell
$invalidEvent = @{
  topic = "sensor"
  event_id = "invalid-1"
  source = "device-1"
  payload = @{}
} | ConvertTo-Json -Depth 5

try {
  irm "http://localhost:8080/publish" -Method Post -ContentType "application/json" -Body $invalidEvent
} catch {
  $_.Exception.Response.StatusCode.value__
}
```

Ekspektasi:
- API mengembalikan status 422 (validation error).

### Bukti Gambar

![Error 422 untuk skema invalid](image/error-422.png)

## 6. Uji Batch Event

Kirim batch event dalam satu request:

```powershell
$batch = @(
  @{
    topic = "sensor"
    event_id = "batch-1"
    timestamp = "2026-01-01T10:00:00"
    source = "device-1"
    payload = @{ v = 1 }
  },
  @{
    topic = "audit"
    event_id = "batch-2"
    timestamp = "2026-01-01T10:00:01"
    source = "device-2"
    payload = @{ v = 2 }
  }
) | ConvertTo-Json -Depth 5

irm "http://localhost:8080/publish" -Method Post -ContentType "application/json" -Body $batch
```

Ekspektasi:
- Request sukses.
- received bertambah sesuai jumlah item batch.

## 7. Uji Persistensi Dedup Setelah Restart

1. Pastikan sudah ada event yang pernah dipublish (misalnya evt-1).
2. Restart container:

```powershell
docker restart uts-aggregator
```

3. Kirim ulang event evt-1 yang sama.

Ekspektasi:
- Event tetap dianggap duplikat setelah restart.
- Menandakan dedup store persisten (SQLite) berjalan.
- Catatan: counter stats di memori akan reset setelah restart, sehingga nilai `received/unique_processed/duplicate_dropped` dihitung dari sejak container hidup kembali.
- Contoh setelah restart lalu kirim ulang `evt-1` sekali: `received = 1`, `unique_processed = 0`, `duplicate_dropped = 1`.

## 8. Uji dengan Docker Compose

Jalankan dua service (aggregator + publisher):

```powershell
docker compose up --build
```

Ekspektasi:
- Service aggregator dan publisher sama-sama running.
- Publisher mengirim event + duplicate ke aggregator.
- Log consumer menunjukkan processed dan duplicate.

### Bukti Gambar

![Docker compose up build](./image/(build%20image)-docker%20build-uts-aggregator.png)

Hentikan compose:

```powershell
docker compose down
```

### Troubleshooting Docker Compose (Bentrok Port/Container)

Jika muncul error seperti:
`failed to set up container networking` atau `port is already allocated`, biasanya masih ada container lama yang memakai port `8080`.

Langkah perbaikan:

```powershell
docker stop uts-aggregator
docker rm uts-aggregator
docker compose down
docker compose up --build
```

Jika masih bentrok, cek container yang sedang memakai port 8080:

```powershell
docker ps
```

Lalu stop dan hapus container yang memakai mapping `0.0.0.0:8080->...`.

## 9. Jalankan Unit Test (Wajib)

Aktifkan virtual environment (jika perlu), lalu jalankan pytest:

```powershell
& "../pubsub-dedup-aggregator/venv/Scripts/python.exe" -m pytest -q
```

Ekspektasi:
- Seluruh test lulus.
- Cakupan mencakup dedup, persistence, schema, stats/events consistency, dan mini-stress.

![Docker compose up build](./image/pytest.png)

## 10. Cleanup Setelah Pengujian

Jika menjalankan single container:

```powershell
docker stop uts-aggregator
docker rm uts-aggregator
```

Opsional hapus image:

```powershell
docker rmi uts-aggregator
```
