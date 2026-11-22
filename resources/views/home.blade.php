@extends('layouts.app')
@section('title', 'Beranda')
@section('content')
<div class="mb-6 rounded-3xl bg-gradient-to-br from-blue-600 to-blue-700 p-8 text-white shadow-lg lg:p-10">
    <p class="text-sm font-semibold text-blue-200">Final Project Teknologi Logika Fuzzy</p>
    <h1 class="mt-2 text-3xl font-bold leading-tight lg:text-4xl">Segmentasi &amp; Prediksi Churn<br>Pelanggan Telekomunikasi</h1>
    <p class="mt-3 max-w-2xl text-blue-100">Pelanggan dikelompokkan secara fuzzy dengan Fuzzy C-Means, lalu derajat keanggotaannya dipakai KNN untuk memprediksi pelanggan yang berisiko berhenti berlangganan.</p>
    <div class="mt-6 flex flex-wrap items-center gap-3">
        <a href="{{ route('datasets.index') }}" class="rounded-xl bg-white px-5 py-2.5 text-sm font-semibold text-blue-700 hover:bg-blue-50">Mulai: Input Data →</a>
        @if($apiOk)
            <span class="rounded-full bg-green-400/20 px-3 py-1 text-xs font-medium text-green-100">● API Python aktif</span>
        @else
            <span class="rounded-full bg-red-400/30 px-3 py-1 text-xs font-medium text-red-100">● API Python tidak aktif, jalankan uvicorn</span>
        @endif
    </div>
</div>

<div class="mb-6 grid gap-4 sm:grid-cols-3">
    <x-kpi label="Dataset tersimpan" :value="$nDatasets" tone="blue" />
    <x-kpi label="Eksperimen (proses)" :value="$nExperiments" tone="blue" />
    <x-kpi label="Riwayat prediksi" :value="$nPredictions" tone="blue" />
</div>

<div class="mb-6 grid gap-4 md:grid-cols-3">
    @foreach([
        ['1', 'Segmentasi Fuzzy', 'FCM memberi tiap pelanggan derajat keanggotaan ke beberapa segmen sekaligus, bukan satu label kaku.'],
        ['2', 'Prediksi dengan KNN', 'Derajat keanggotaan ditambahkan sebagai fitur KNN untuk memprediksi churn.'],
        ['3', 'Evaluasi Jelas', 'Dibandingkan dengan KNN tanpa membership, lengkap dengan metrik dan interpretasi.'],
    ] as [$n, $t, $d])
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <span class="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-600">{{ $n }}</span>
            <h3 class="mt-3 font-bold">{{ $t }}</h3>
            <p class="mt-1 text-sm text-slate-500">{{ $d }}</p>
        </div>
    @endforeach
</div>

<x-card title="Alur Metode">
    <div class="flex flex-wrap items-center gap-2 text-sm font-semibold">
        @foreach(['Data', 'Preprocessing', 'FCM', 'Membership (μ)', 'KNN', 'Prediksi'] as $i => $chip)
            <span class="rounded-lg bg-blue-50 px-3 py-1.5 text-blue-700">{{ $chip }}</span>
            @if($i < 5)<span class="text-slate-400">→</span>@endif
        @endforeach
    </div>
</x-card>

<x-card title="Panduan Cepat">
    <ol class="space-y-2 text-sm">
        @foreach([
            'Input Data: unggah file CSV Telco Customer Churn.',
            'Proses: atur parameter (atau biarkan default), lalu jalankan.',
            'Hasil: lihat segmentasi, tabel membership, dan interpretasi segmen.',
            'Evaluasi: lihat metrik dan perbandingan baseline vs FCM + KNN.',
            'Prediksi: coba prediksi satu pelanggan; hasilnya tersimpan di riwayat.',
            'Riwayat: lihat kembali eksperimen dan prediksi yang sudah disimpan di database.',
        ] as $i => $step)
            <li class="flex items-center gap-3">
                <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">{{ $i + 1 }}</span>{{ $step }}
            </li>
        @endforeach
    </ol>
</x-card>

@if($latest)
    <x-card title="Eksperimen Terakhir">
        <p class="text-sm text-slate-600">#{{ $latest->id }} · {{ $latest->dataset->name }} · c = {{ $latest->n_clusters }}, k = {{ $latest->k }} ·
            F1 churn {{ number_format($latest->f1_comb, 3) }} (baseline {{ number_format($latest->f1_base, 3) }})</p>
        <div class="mt-3 flex gap-2">
            <a href="{{ route('experiments.show', $latest) }}" class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Lihat Hasil</a>
            <a href="{{ route('experiments.evaluation', $latest) }}" class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold hover:bg-slate-50">Evaluasi</a>
        </div>
    </x-card>
@endif
@endsection
