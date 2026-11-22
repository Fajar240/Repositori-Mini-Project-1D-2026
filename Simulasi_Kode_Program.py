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

def hitung_persentase_fasilitas_aman(baris):
    total_kelas = baris["Ruang kelas(baik)"] + baris["Ruang kelas(rusak ringan)"] + baris["Ruang kelas(rusak sedang)"] + baris["Ruang kelas(rusak berat)"]
    persentase = hitung_persen(baris["Ruang kelas(baik)"], total_kelas)
    if persentase >= 80:
        return persentase, "Baik"
    else:
        return persentase, "Cukup"

def hitung_persentase_pemerataan(baris, kolom_atas, kolom_bawah):
    atas = baris[kolom_atas]
    persentase = hitung_persen(atas, atas + baris[kolom_bawah])
    if persentase >= 80:
        return persentase, "Tercapai"
    else:
        return persentase, "Perlu pemerataan"

def tentukan_indikator_dominan(persentase_hasil, baris):

    persentase_rusak, _ = hitung_persentase_fasilitas_perbaikan(baris)

    guru_belum_s1 = baris["Kepala Sekolah dan Guru(<S1)"]
    total_guru = guru_belum_s1 + baris["Kepala Sekolah dan Guru(≥ S1)"]
    persentase_guru_belum_s1 = hitung_persen(guru_belum_s1, total_guru)

    d1 = abs(persentase_hasil - persentase_rusak)
    d2 = abs(persentase_hasil - persentase_guru_belum_s1)
    if d1 > d2:
        return "Fasilitas"
    else:
        return "Kualifikasi guru"

def hitung_persentase_keberlanjutan(baris, kolom):
    persentase = hitung_persen(baris[kolom], baris["Siswa"])
    return persentase, tentukan_indikator_dominan(persentase, baris)

LEBAR = 66

def cetak_menu(judul, subjudul, daftar_opsi):
    lebar_isi = LEBAR - 2

    print("\n╔" + "═" * lebar_isi + "╗")
    for teks in (judul, subjudul):
        baris = ""
        for kata in teks.split():
            if baris == "":
                baris = kata
            elif len(baris) + 1 + len(kata) <= lebar_isi - 4:
                baris = baris + " " + kata
            else:
                print("║" + baris.center(lebar_isi) + "║")
                baris = kata
        if baris != "":
            print("║" + baris.center(lebar_isi) + "║")
    print("╚" + "═" * lebar_isi + "╝\n")

    for nomor, teks, ikon, keterangan in daftar_opsi:
        print(f"  [{nomor}] {ikon} {teks}".rstrip())
        if keterangan:
            print(f"        ↳ {keterangan}")
        print()

    print("─" * LEBAR)

def pilih_dari_daftar(judul, daftar_opsi, subjudul="", ikon_opsi=None, keterangan=None):
    while True:
        opsi_tampil = []
        for indeks, opsi in enumerate(daftar_opsi):
            ikon = ikon_opsi[indeks] if ikon_opsi else "▶"
            ket = keterangan[indeks] if keterangan else ""
            opsi_tampil.append((indeks + 1, opsi, ikon, ket))
        cetak_menu(judul.upper(), subjudul, opsi_tampil)
        pilihan = input("  ➤ Silahkan ketik angka yang diinginkan: ").strip()

        if pilihan.isdigit() and 1 <= int(pilihan) <= len(daftar_opsi):
            return int(pilihan)
        print("\n  ⚠  Pilihan tidak valid, silahkan coba lagi.")

INFO_PULAU = {
    "Sumatera":             ("🐘", "Potensi yang beragam"),
    "Jawa":                 ("🌋", "Dinamika yang berkembang"),
    "Kalimantan":           ("🌳", "Luasnya peluang"),
    "Sulawesi":             ("⛵", "Semangat kemajuan"),
    "Bali & Nusa Tenggara": ("🏝", "Keberagaman potensi"),
    "Maluku":               ("🌴", "Menembus keterbatasan"),
    "Papua":                ("🦜", "Potensi masa depan"),
}

def pilih_pulau(per_pulau):
    nama_pulau = [pulau for pulau in per_pulau if pulau != "Tidak diketahui"]
    ikon = [INFO_PULAU.get(p, ("📍", ""))[0] for p in nama_pulau]
    ket = [INFO_PULAU.get(p, ("📍", ""))[1] for p in nama_pulau]

    nomor = pilih_dari_daftar("Pilih Wilayah Pulau", nama_pulau,
                              "Data pulau yang ingin dilihat?", ikon, ket)
    return nama_pulau[nomor - 1]

def tampilkan_tabel(judul, nama_pulau, daftar, fungsi_hitung, judul_persen, jenis, judul_status="Status"):
    hasil = []
    for baris in daftar:
        persentase, status = fungsi_hitung(baris)
        hasil.append((persentase, baris["Provinsi"].replace("Prov. ", ""), status))

    hasil.sort(reverse=True)

    if jenis == "buruk":
        keterangan = "diurutkan dari tingkas kelayakan terendah ke tertinggi"
    else:
        keterangan = "diurutkan dari tingkat kelayakan tertinggi ke terendah"

    baris_tabel = [
        (str(nomor), nama_provinsi, f"{persentase:.2f}%", status)
        for nomor, (persentase, nama_provinsi, status) in enumerate(hasil, start=1)
    ]

    total_pulau = {"Provinsi": "TOTAL PULAU"}
    for kolom in KOLOM_NUMERIK:
        total_pulau[kolom] = sum(baris[kolom] for baris in daftar)
    persentase, status = fungsi_hitung(total_pulau)
    baris_tabel.append(("", "TOTAL PULAU", f"{persentase:.2f}%", status))
    header = ("No.", "Provinsi", judul_persen, judul_status)
    lebar_kolom = [5, 28, 22, len(judul_status)]
    for baris in [header] + baris_tabel:
        for indeks, nilai in enumerate(baris):
            lebar_kolom[indeks] = max(lebar_kolom[indeks], len(nilai))

    def format_baris(kolom, total=False):
        pemisah = "  " if total else "| "
        return (
            f"| {kolom[0]:<{lebar_kolom[0]}} "
            f"{pemisah}{kolom[1]:<{lebar_kolom[1]}} "
            f"| {kolom[2]:>{lebar_kolom[2]}} "
            f"| {kolom[3]:<{lebar_kolom[3]}} |"
        )

    garis = "-" * (sum(lebar_kolom) + 13)
    print(f"\n=== {judul} - Pulau {nama_pulau} ===")
    print(f"({keterangan})")
    print(garis)
    print(format_baris(header))
    print(garis)
    for baris in baris_tabel[:-1]:
        print(format_baris(baris))
    print(garis)
    print(format_baris(baris_tabel[-1], total=True))
    print(garis)