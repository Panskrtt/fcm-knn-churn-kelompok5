@extends('layouts.app')
@section('title', 'Informasi Sistem')
@section('content')
<h1 class="text-3xl font-bold">Informasi Sistem</h1>
<p class="mb-6 mt-1 text-slate-500">Penjelasan metode, arsitektur, parameter, dan cara penggunaan.</p>

@foreach([
    'Arsitektur' => "Browser → Laravel (tampilan, validasi form, database MySQL) → HTTP/JSON → API Python (FastAPI).\nSeluruh perhitungan FCM dan KNN dilakukan di API Python; Laravel menyimpan dataset, hasil eksperimen, dan riwayat prediksi.",
    'Fuzzy C-Means (FCM)' => "Input: matriks data numerik X (tenure, MonthlyCharges, TotalCharges yang distandarisasi).\nParameter: jumlah cluster c, fuzzifier m (>1), epsilon, iterasi maksimum.\nRumus: J = Σi Σj (u_ij^m) ||x_i - c_j||²\nPusat cluster: c_j = Σi (u_ij^m) x_i / Σi (u_ij^m)\nKeanggotaan: u_ij = 1 / Σk (||x_i - c_j|| / ||x_i - c_k||)^(2/(m-1))\nIterasi: ulangi pembaruan pusat dan U sampai max|U_baru - U_lama| < epsilon.\nOutput: pusat cluster dan matriks keanggotaan U (tiap baris berjumlah 1).",
    'K-Nearest Neighbor (KNN)' => "Input: fitur asli terstandarisasi (one-hot + numerik) digabung dengan bobot × derajat keanggotaan FCM.\nParameter: jumlah tetangga k, bobot fitur membership.\nProses: jarak Euclidean ke seluruh data latih, ambil k tetangga terdekat, voting mayoritas.\nOutput: prediksi churn dan proporsi tetangga churn.",
    'Integrasi FCM dan KNN' => 'FCM dilatih pada data latih saja. Derajat keanggotaan data latih, data uji, dan data baru dihitung terhadap pusat cluster yang sama, lalu ditambahkan sebagai kolom fitur KNN. KNN baseline (tanpa kolom membership) dilatih pada pembagian data yang sama sebagai pembanding.',
    'Teknologi' => "Laravel + Tailwind CSS + Chart.js: antarmuka dan grafik.\nMySQL: dataset, eksperimen, riwayat prediksi.\nFastAPI: API Python.\nNumPy: FCM (ditulis mandiri). Pandas: pembersihan data. scikit-learn: StandardScaler, train_test_split, KNeighborsClassifier, metrik evaluasi.",
    'Petunjuk penggunaan' => "1) Input Data: unggah CSV.  2) Proses: atur parameter dan jalankan.  3) Hasil: lihat segmen dan membership.  4) Evaluasi: lihat metrik dan perbandingan.  5) Prediksi: prediksi satu pelanggan.  6) Riwayat: lihat data tersimpan.\nPastikan MySQL (XAMPP) dan API Python (uvicorn) sedang berjalan.",
] as $title => $body)
    <x-card :title="$title">
        <p class="whitespace-pre-line text-sm leading-relaxed text-slate-700">{{ $body }}</p>
    </x-card>
@endforeach
@endsection
