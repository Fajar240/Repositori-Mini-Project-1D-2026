# Analisis Kualitas dan Fasilitas Pendidikan Tingkat Sekolah Dasar di Indonesia

Mini Project Pemrograman Komputer — Kelompok 1D
Laboratorium Sistem Informasi dan Keputusan, Departemen Teknik Industri, Fakultas Teknik, Universitas Andalas (2026)

## Latar Belakang

Data kelayakan pendidikan SD tahun 2023–2024 menunjukkan kualitas pendidikan dasar di Indonesia belum merata: keterbatasan guru berkualifikasi S1, tingginya kerusakan ruang kelas, serta angka putus sekolah dan mengulang yang masih tinggi di beberapa wilayah, terutama di Indonesia timur. Proyek ini mengkaji kondisi tersebut berdasarkan data yang tersedia.

## Tujuan

1. Menganalisis kualitas tenaga kependidikan dan kelayakan fasilitas SD di Indonesia.
2. Menganalisis kondisi kelayakan fasilitas SD tiap provinsi.
3. Menganalisis pemerataan kepala sekolah, guru, dan tenaga kependidikan tiap provinsi.
4. Menganalisis keterkaitan kualifikasi tenaga pendidik dan keterbatasan fasilitas terhadap angka putus sekolah dan siswa mengulang.

## Pengguna

Kemendikdasmen, Dinas Pendidikan Provinsi, akademisi (dosen, peneliti, mahasiswa), dan masyarakat umum (misalnya untuk memilih wilayah dengan kualitas SD yang diinginkan).

## Dataset

- Nama: [Dataset Pendidikan SD Indonesia Tahun 2023-2024](https://www.kaggle.com/datasets/puanbeningpastika/dataset-pendidikan-sd-indonesia-2023-2024) (Puan Bening Pastika, Kaggle)
- Sumber asli: Portal Data Kemendikbudristek
- Ukuran: 39 baris (data per provinsi)
- Kolom: Provinsi, Sekolah, Siswa, Mengulang, Putus Sekolah, Kepala Sekolah dan Guru (< S1), Kepala Sekolah dan Guru (≥ S1), Tenaga Kependidikan (SM), Tenaga Kependidikan (> SM), serta jumlah Ruang Kelas (Baik, Rusak Ringan, Rusak Sedang, Rusak Berat)
- File yang dibaca program: `kelayakan-pendidikan-indonesia.csv`

## Fitur Program

Menu utama menyediakan 4 analisis. Untuk tiap analisis, pengguna memilih **pulau** dan **kategori**, lalu program menampilkan tabel peringkat provinsi beserta total per pulau.

Fitur pendukung:
- Validasi data — mendeteksi kolom kosong dan nilai non-numerik, lalu menampilkan rekap baris tidak valid.
- Penanganan error — file tidak ditemukan, header hilang, kolom wajib tidak lengkap, dan pembagian dengan nol.
- Pengelompokan per pulau — Sumatera, Jawa, Kalimantan, Sulawesi, Bali & Nusa Tenggara, Maluku, Papua.

## Alur Program (IPO)

- Input — File CSV data pendidikan SD per provinsi 
- Process — Baca CSV → validasi data → kelompokkan per pulau → hitung persentase → klasifikasi
- Output — Tabel 3 kolom: provinsi, persentase, dan status/klasifikasi 

## Struktur Fungsi Utama

|                       Fungsi                     |                        Tugas                       |
|--------------------------------------------------|----------------------------------------------------|
| `baca_csv`                                       | Membaca CSV dan memeriksa header serta kolom wajib |
| `validasi_data`                                  | Memvalidasi dan mengonversi data per baris         |
| `kelompokkan_per_pulau`                          | Mengelompokkan provinsi ke pulau                   |
| `hitung_persen`                                  | Menghitung persentase (aman terhadap pembagian nol)|
| `hitung_persentase_*`                            | Menghitung persentase dan status tiap indikator    |
| `tentukan_indikator_dominan`                     | Menentukan faktor dominan putus sekolah/mengulang  |
| `cetak_menu`, `pilih_dari_daftar`, `pilih_pulau` | Antarmuka menu                                     |
| `tampilkan_tabel`, `jalankan_menu`, `menu_utama` | Menampilkan hasil dan menjalankan program          |

## Cara Menjalankan

Prasyarat: Python 3 (hanya memakai pustaka standar `csv`).

Pastikan kelayakan-pendidikan-indonesia.csv berada satu folder dengan file program python Simulasi_Kode_Program.py

Ikuti menu: pilih menu → pilih pulau → pilih kategori. Pilih `5` untuk mengakhiri program.

## Tim

|           Nama          |     NIM    |
|-------------------------|------------|
| Gania Faneza            | 2610931016 |
| Uwais Al Qarni          | 2610931024 |
| Muhammad Fajar Al Rizky | 2610932015 |

Asisten Pembimbing: Salma Livana
Dosen Pengampu: Ikhwan Arief, S.T., M.Sc.
