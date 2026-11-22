import csv

FILE_CSV = "kelayakan-pendidikan-indonesia.csv"

KOLOM_WAJIB = ["Provinsi", "Sekolah", "Siswa", "Mengulang", "Putus Sekolah", "Kepala Sekolah dan Guru(<S1)", "Kepala Sekolah dan Guru(≥ S1)", "Tenaga Kependidikan(SM)",
               "Tenaga Kependidikan(>SM)", "Ruang kelas(baik)", "Ruang kelas(rusak ringan)", "Ruang kelas(rusak sedang)", "Ruang kelas(rusak berat)"]

KOLOM_NUMERIK = [kolom for kolom in KOLOM_WAJIB if kolom != "Provinsi"]

def baca_csv(nama_file):
    try:
        with open(nama_file, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                print("Error: Dataset tidak memiliki header.")
                return None

            kolom_hilang = [kolom for kolom in KOLOM_WAJIB if kolom not in reader.fieldnames]
            if kolom_hilang:
                print("Error: Kolom berikut tidak ditemukan:")
                for kolom in kolom_hilang:
                    print(f"- {kolom}")
                return None

            return list(reader)

    except FileNotFoundError:
        print(f"Error: File '{nama_file}' tidak ditemukan.")
        return None

def validasi_data(daftar_baris):
    data = []
    data_invalid = []

    for nomor_baris, baris in enumerate(daftar_baris, start=2):
        baris_baru = {}
        masalah = None

        for kolom in KOLOM_WAJIB:
            nilai = (baris.get(kolom) or "").strip()

            if not nilai:
                masalah = f"kolom '{kolom}' kosong."
                break
            elif kolom in KOLOM_NUMERIK:
                try:
                    baris_baru[kolom] = int(nilai)
                except ValueError:
                    masalah = f"kolom '{kolom}' bukan data valid."
                    break
            else:
                baris_baru[kolom] = nilai

        if masalah:
            print(f"Peringatan baris {nomor_baris}: {masalah}")
            data_invalid.append(baris)
        else:
            data.append(baris_baru)

    return data, data_invalid, len(data_invalid)

def kelompokkan_per_pulau(data):
    pulau_provinsi = {
        "Sumatera": ["Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Kepulauan Riau", "Jambi", "Sumatera Selatan", "Bangka Belitung", 
                     "Kepulauan Bangka Belitung","Bengkulu", "Lampung",],
        "Jawa": ["DKI Jakarta", "Jawa Barat", "Banten", "Jawa Tengah","DI Yogyakarta", "Jawa Timur",],
        "Kalimantan": ["Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan","Kalimantan Timur", "Kalimantan Utara",],
        "Sulawesi": ["Sulawesi Utara", "Gorontalo", "Sulawesi Tengah", "Sulawesi Barat", "Sulawesi Selatan", "Sulawesi Tenggara",],
        "Bali & Nusa Tenggara": ["Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur",],
        "Maluku": ["Maluku", "Maluku Utara"],
        "Papua": ["Papua", "Papua Barat", "Papua Barat Daya", "Papua Selatan","Papua Tengah", "Papua Pegunungan",],
    }

    provinsi_ke_pulau = {}
    for pulau, daftar_provinsi in pulau_provinsi.items():
        for provinsi in daftar_provinsi:
            nama = " ".join(provinsi.lower().replace(".", "").split())
            provinsi_ke_pulau[nama] = pulau

    hasil = {}
    for baris in data:
        nama = " ".join(baris["Provinsi"].lower().replace(".", "").split())
        if nama.startswith("prov "):
            nama = nama[5:]
        pulau = provinsi_ke_pulau.get(nama, "Tidak diketahui")

        if pulau not in hasil:
            hasil[pulau] = []
        hasil[pulau].append(baris)

    return hasil

def hitung_persen(bagian, total):
    return bagian / total * 100 if total > 0 else 0


def hitung_persentase_kelayakan_kelas(baris):
    total_kelas = baris["Ruang kelas(baik)"] + baris["Ruang kelas(rusak ringan)"] + baris["Ruang kelas(rusak sedang)"] + baris["Ruang kelas(rusak berat)"]
    persentase = hitung_persen(baris["Ruang kelas(baik)"], total_kelas)

    if persentase >= 80:
        return persentase, "Baik"
    elif persentase >= 60:
        return persentase, "Kurang"
    else:
        return persentase, "Buruk"

def hitung_persentase_kualitas_guru_tenaga(baris):
    guru_s1 = baris["Kepala Sekolah dan Guru(≥ S1)"]
    tenaga_diatas_sm = baris["Tenaga Kependidikan(>SM)"]
    total = (guru_s1 + baris["Kepala Sekolah dan Guru(<S1)"]
             + baris["Tenaga Kependidikan(SM)"] + tenaga_diatas_sm)

    persentase = hitung_persen(guru_s1 + tenaga_diatas_sm, total)
    if persentase >= 80:
        return persentase, "Tinggi"
    elif persentase >= 60:
        return persentase, "Sedang"
    else:
        return persentase, "Rendah"

def hitung_persentase_fasilitas_perbaikan(baris):
    total_kelas = baris["Ruang kelas(baik)"] + baris["Ruang kelas(rusak ringan)"] + baris["Ruang kelas(rusak sedang)"] + baris["Ruang kelas(rusak berat)"]
    ruang_kelas_rusak = total_kelas - baris["Ruang kelas(baik)"]

    persentase = hitung_persen(ruang_kelas_rusak, total_kelas)
    if persentase >= 70:
        return persentase, "Kritis"
    else:
        return persentase, "Perlu perbaikan"