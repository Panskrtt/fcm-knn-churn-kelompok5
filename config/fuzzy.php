<?php

return [
    'api_url' => env('FUZZY_API_URL', 'http://127.0.0.1:8001'),
    'timeout' => (int) env('FUZZY_API_TIMEOUT', 300),

    // Pilihan untuk form prediksi manual (sesuai kategori dataset Telco Customer Churn)
    'options' => [
        'SeniorCitizen' => ['0', '1'],
        'Contract' => ['Month-to-month', 'One year', 'Two year'],
        'InternetService' => ['DSL', 'Fiber optic', 'No'],
        'PaymentMethod' => ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'],
        'PaperlessBilling' => ['Yes', 'No'],
        'TechSupport' => ['No', 'Yes', 'No internet service'],
        'OnlineSecurity' => ['No', 'Yes', 'No internet service'],
    ],

    'column_descriptions' => [
        'customerID' => 'ID pelanggan (tidak dipakai dalam perhitungan).',
        'gender' => 'Jenis kelamin pelanggan (Male/Female).',
        'SeniorCitizen' => 'Apakah pelanggan lansia (1 = ya, 0 = tidak).',
        'Partner' => 'Memiliki pasangan (Yes/No).',
        'Dependents' => 'Memiliki tanggungan (Yes/No).',
        'tenure' => 'Lama berlangganan dalam bulan. [Fitur FCM]',
        'PhoneService' => 'Berlangganan layanan telepon (Yes/No).',
        'MultipleLines' => 'Memiliki banyak jalur telepon (Yes/No/No phone service).',
        'InternetService' => 'Jenis layanan internet (DSL/Fiber optic/No).',
        'OnlineSecurity' => 'Layanan keamanan online (Yes/No/No internet service).',
        'OnlineBackup' => 'Layanan backup online (Yes/No/No internet service).',
        'DeviceProtection' => 'Proteksi perangkat (Yes/No/No internet service).',
        'TechSupport' => 'Dukungan teknis (Yes/No/No internet service).',
        'StreamingTV' => 'Layanan streaming TV (Yes/No/No internet service).',
        'StreamingMovies' => 'Layanan streaming film (Yes/No/No internet service).',
        'Contract' => 'Jenis kontrak (Month-to-month/One year/Two year).',
        'PaperlessBilling' => 'Tagihan tanpa kertas (Yes/No).',
        'PaymentMethod' => 'Metode pembayaran (4 kategori).',
        'MonthlyCharges' => 'Tagihan bulanan dalam dolar. [Fitur FCM]',
        'TotalCharges' => 'Total tagihan selama berlangganan dalam dolar. [Fitur FCM]',
        'Churn' => 'TARGET: pelanggan berhenti berlangganan (Yes/No).',
    ],
];
