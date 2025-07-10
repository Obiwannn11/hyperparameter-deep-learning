// Mengambil semua elemen yang dibutuhkan dari HTML
const image1Input = document.getElementById('image1-input');
const image2Input = document.getElementById('image2-input');
const compareBtn = document.getElementById('compare-btn');
const viewerContainer = document.getElementById('image-compare-container');

const options = {

  // UI Theme Defaults

  controlColor: "#FFFFFF",
  controlShadow: true,
  addCircle: false,
  addCircleBlur: true,

  // Label Defaults
  // pemberian label di setiap gambar

  showLabels: true,
  labelOptions: {
    before: 'Before',
    after: 'After',
    onHover: false
  },

  // Smoothing

  smoothing: true,
  smoothingAmount: 100,

  // Other options

  hoverStart: false,
  verticalMode: false,
  startingPoint: 50,
  fluidMode: false,
};

// Fungsi helper untuk membaca file sebagai Data URL menggunakan Promise (tetap sama)
function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
    });
}

// Menambahkan event listener ke tombol "Bandingkan Gambar"
compareBtn.addEventListener('click', async () => {
    const file1 = image1Input.files[0];
    const file2 = image2Input.files[0];

    // Validasi: Pastikan kedua file sudah dipilih
    if (!file1 || !file2) {
        alert("Harap pilih kedua gambar terlebih dahulu!");
        return;
    }

    // Tampilkan pesan "loading"
    viewerContainer.innerHTML = '<h2>Memuat gambar...</h2>';

    try {
        // Baca kedua file secara bersamaan dan tunggu keduanya selesai
        const [image1DataURL, image2DataURL] = await Promise.all([
            readFileAsDataURL(file1),
            readFileAsDataURL(file2)
        ]);

        // --- PERUBAHAN UTAMA DIMULAI DI SINI ---

        // 1. Kosongkan kontainer dari pesan "loading"
        viewerContainer.innerHTML = '';

        // 2. Buat elemen <img> pertama secara dinamis
        const img1 = document.createElement('img');
        img1.src = image1DataURL;
        img1.alt = "Gambar Sebelum";

        // 3. Buat elemen <img> kedua secara dinamis
        const img2 = document.createElement('img');
        img2.src = image2DataURL;
        img2.alt = "Gambar Sesudah";

        // 4. Masukkan kedua elemen <img> ke dalam kontainer
        viewerContainer.appendChild(img1);
        viewerContainer.appendChild(img2);

        // 5. Inisialisasi library pada kontainer yang SEKARANG sudah berisi dua gambar.
        //    Kita tidak perlu lagi memberikan options sumber gambar.
        new ImageCompare(viewerContainer, options).mount();

        // --- PERUBAHAN UTAMA SELESAI ---

    } catch (error) {
        console.error("Gagal membaca file:", error);
        viewerContainer.innerHTML = '<h2>Gagal memuat salah satu gambar.</h2><p>Pastikan file yang Anda pilih adalah gambar yang valid.</p>';
    }
});