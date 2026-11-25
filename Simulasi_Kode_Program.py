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
        masalah_baris = []

        for kolom in KOLOM_WAJIB:
            nilai = (baris.get(kolom) or "").strip()

            if not nilai:
                masalah_baris.append((kolom, "kolom kosong"))
                if kolom in KOLOM_NUMERIK:
                    baris_baru[kolom] = 0
            elif kolom in KOLOM_NUMERIK:
                try:
                    baris_baru[kolom] = int(nilai)
                except ValueError:
                    masalah_baris.append((kolom, "bukan data valid"))
                    baris_baru[kolom] = 0
            else:
                baris_baru[kolom] = nilai

        if masalah_baris:
            for kolom, keterangan in masalah_baris:
                data_invalid.append({
                    "nomor_baris": nomor_baris,
                    "kolom": kolom,
                    "keterangan": keterangan,
                })

        if baris_baru.get("Provinsi"):
            data.append(baris_baru)

    if data_invalid:
        masalah_per_baris = {}
        for item in data_invalid:
            masalah_per_baris.setdefault(item["nomor_baris"], []).append(
                (item["kolom"], item["keterangan"])
            )

        header = ("No.", "Baris", "Kolom", "Keterangan")
        data_tabel = [
            (
                str(nomor),
                str(nomor_baris),
                ", ".join(kolom for kolom, _ in masalah),
                ", ".join(keterangan for _, keterangan in masalah),
            )
            for nomor, (nomor_baris, masalah) in enumerate(masalah_per_baris.items(), start=1)
        ]

        lebar = [ max(len(header[indeks]), *(len(item[indeks]) for item in data_tabel)) for indeks in range(len(header)) ]

        garis = "--" + "---".join("-" * lebar[indeks] for indeks in range(len(lebar))) + "--"

        print("\n=== DATA TIDAK VALID ===")
        print(garis)
        print("| " + " | ".join(f"{nilai:<{lebar[indeks]}}" for indeks, nilai in enumerate(header)) + " |")
        print(garis)

        for item in data_tabel:
            print("| " + " | ".join(f"{nilai:<{lebar[indeks]}}" for indeks, nilai in enumerate(item)) + " |")

        print(garis)
        jumlah_baris_invalid = len({item["nomor_baris"] for item in data_invalid})
        print(f"Jumlah data tidak valid: {jumlah_baris_invalid} baris")

    jumlah_baris_invalid = len({item["nomor_baris"] for item in data_invalid})
    return data, data_invalid, jumlah_baris_invalid

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
    elif persentase >= 40:
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
    elif persentase >= 75:
        return persentase, "Sedang"
    else:
        return persentase, "Rendah"

def hitung_persentase_fasilitas_perbaikan(baris):
    total_kelas = baris["Ruang kelas(baik)"] + baris["Ruang kelas(rusak ringan)"] + baris["Ruang kelas(rusak sedang)"] + baris["Ruang kelas(rusak berat)"]
    ruang_kelas_rusak = total_kelas - baris["Ruang kelas(baik)"]

    persentase = hitung_persen(ruang_kelas_rusak, total_kelas)
    if persentase >= 62:
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

def tentukan_indikator_dominan(persentase, baris):

    persentase_rusak, _ = hitung_persentase_fasilitas_perbaikan(baris)

    guru_belum_s1 = baris["Kepala Sekolah dan Guru(<S1)"]
    total_guru = guru_belum_s1 + baris["Kepala Sekolah dan Guru(≥ S1)"]
    persentase_guru_belum_s1 = hitung_persen(guru_belum_s1, total_guru)

    d1 = abs(persentase - persentase_rusak)
    d2 = abs(persentase - persentase_guru_belum_s1)
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
        keterangan = "diurutkan dari tingkat kelayakan terendah ke tertinggi"
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

DAFTAR_MENU = {
    "1": {
        "judul": "Memilih sekolah dasar",
        "ikon": "🏫",
        "manfaat": "Pilih wilayah dengan kelas & guru terbaik",
        "pertanyaan": "Pilih kategori berdasarkan kualitas",
        "kategori": [
            {"nama": "Kelayakan kelas", "judul_tabel": "Kualitas kelas",
             "fungsi": hitung_persentase_kelayakan_kelas,
             "kolom_persen": "Ruang kelas baik", "jenis": "baik",
             "ikon": "🏠", "manfaat": "Tingkat kenyamanan ruang belajar"},
            {"nama": "Kualitas guru & tenaga pendidik", "judul_tabel": "Kualitas tenaga pendidik",
             "fungsi": hitung_persentase_kualitas_guru_tenaga,
             "kolom_persen": "Guru & tenaga S1/>SM", "jenis": "baik",
             "ikon": "👩‍🏫", "manfaat": "Tingkat kualitas pengajar"},
        ],
    },
    "2": {
        "judul": "Kondisi kelayakan fasilitas",
        "ikon": "🏗",
        "manfaat": "Identifikasi ruang kelas yang paling membutuhkan perbaikan",
        "pertanyaan": "Pilih kategori berdasarkan kualitas",
        "kategori": [
            {"nama": "Perlu perbaikan fasilitas", "judul_tabel": "Perlu perbaikan fasilitas",
             "fungsi": hitung_persentase_fasilitas_perbaikan,
             "kolom_persen": "Ruang kelas rusak", "jenis": "buruk",
             "ikon": "🔧", "manfaat": "Prioritas wilayah yang harus segera diperbaiki"},
            {"nama": "Tidak perlu perbaikan", "judul_tabel": "Tidak perlu perbaikan",
             "fungsi": hitung_persentase_fasilitas_aman,
             "kolom_persen": "Ruang kelas baik", "jenis": "baik",
             "ikon": "✅", "manfaat": "Wilayah dengan fasilitas yang baik"},
        ],
    },
    "3": {
        "judul": "Pemerataan kepala sekolah & guru dan tenaga pendidik",
        "ikon": "⚖",
        "manfaat": "Mengecek pemerataan kualitas pengajar",
        "pertanyaan": "Pilih kategori berdasarkan pemerataan",
        "kategori": [
            {"nama": "Kepala sekolah & guru", "judul_tabel": "Pemerataan kepala sekolah & guru",
             "fungsi": lambda baris: hitung_persentase_pemerataan(
                 baris, "Kepala Sekolah dan Guru(≥ S1)", "Kepala Sekolah dan Guru(<S1)"),
             "kolom_persen": "Guru berpendidikan S1", "jenis": "baik",
             "ikon": "🎓", "manfaat": "Pemerataan guru berpendidikan S1 ke atas"},
            {"nama": "Tenaga kependidikan", "judul_tabel": "Pemerataan tenaga kependidikan",
             "fungsi": lambda baris: hitung_persentase_pemerataan(
                 baris, "Tenaga Kependidikan(>SM)", "Tenaga Kependidikan(SM)"),
             "kolom_persen": "Tendik di atas SM", "jenis": "baik",
             "ikon": "🤝", "manfaat": "Pemerataan staf pendukung sekolah"},
        ],
    },
    "4": {
        "judul": "Keberlanjutan pendidikan",
        "ikon": "📈",
        "manfaat": "faktor utama siswa putus sekolah dan mengulang",
        "pertanyaan": "Pilih kategori berdasarkan faktor kegagalan",
        "kategori": [
            {"nama": "Putus sekolah", "judul_tabel": "Indikator dominan putus sekolah",
             "fungsi": lambda baris: hitung_persentase_keberlanjutan(baris, "Putus Sekolah"),
             "kolom_persen": "Putus sekolah", "jenis": "buruk", "kolom_status": "Indikator dominan",
             "ikon": "🚸", "manfaat": "Penyebab utama anak berhenti sekolah"},
            {"nama": "Mengulang", "judul_tabel": "Indikator dominan mengulang",
             "fungsi": lambda baris: hitung_persentase_keberlanjutan(baris, "Mengulang"),
             "kolom_persen": "Mengulang", "jenis": "buruk", "kolom_status": "Indikator dominan",
             "ikon": "🔄", "manfaat": "Penyebab utama anak mengulang kelas"},
        ],
    },
}

def jalankan_menu(per_pulau, menu):
    nama_pulau = pilih_pulau(per_pulau)

    nomor = pilih_dari_daftar(
        menu["pertanyaan"],
        [k["nama"] for k in menu["kategori"]],
        f"{menu['judul']} - Pulau {nama_pulau}",
        [k["ikon"] for k in menu["kategori"]],
        [k["manfaat"] for k in menu["kategori"]],
    )
    kategori = menu["kategori"][nomor - 1]

    tampilkan_tabel(kategori["judul_tabel"], nama_pulau, per_pulau[nama_pulau],
                    kategori["fungsi"], kategori["kolom_persen"], kategori["jenis"],
                    kategori.get("kolom_status", "Status"))

def menu_utama(per_pulau):
    while True:
        opsi_menu = []
        for nomor, menu in DAFTAR_MENU.items():
            opsi_menu.append((nomor, menu["judul"], menu["ikon"], menu["manfaat"]))
        opsi_menu.append(("5", "Akhiri program", "👋", ""))
        cetak_menu("ANALISIS KEMATANGAN PROSES PEMBELAJARAN TINGKAT SEKOLAH DASAR DI INDONESIA",
                   "Data untuk keputusan pendidikan yang lebih baik", opsi_menu)

        input_pengguna = input("  ➤ Silahkan ketik angka sesuai menu yg diinginkan: ").strip()

        if input_pengguna in DAFTAR_MENU:
            jalankan_menu(per_pulau, DAFTAR_MENU[input_pengguna])
        elif input_pengguna == "5":
            print("\n" + "─" * LEBAR)
            print("  Program analisis kematangan proses pembelajaran tingkat sekolah dasar")
            print("  di Indonesia telah selesai. Terima kasih telah menggunakan.")
            print("─" * LEBAR)
            break
        else:
            print("\n  ⚠  Pilihan tidak valid, silahkan ulangi.")
            continue

def main():
    daftar_baris = baca_csv(FILE_CSV)
    if daftar_baris is None:
        return

    data, data_invalid, jumlah_data_invalid = validasi_data(daftar_baris)
    per_pulau = kelompokkan_per_pulau(data)

    menu_utama(per_pulau)

if __name__ == "__main__":
    main()
