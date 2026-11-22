@extends('layouts.app')
@section('title', 'Proses')
@section('content')
<h1 class="text-3xl font-bold">Proses Pengolahan</h1>
<p class="mb-6 mt-1 text-slate-500">Atur parameter lalu jalankan alur FCM → KNN. Hasilnya disimpan ke database.</p>

@if($datasets->isEmpty())
    <x-card>
        <p class="text-sm text-slate-600">Belum ada dataset. <a class="font-semibold text-blue-600 underline" href="{{ route('datasets.index') }}">Unggah dataset</a> terlebih dahulu.</p>
    </x-card>
@else
<form method="POST" action="{{ route('experiments.store') }}" data-loading="Menjalankan FCM + KNN, mohon tunggu...">
    @csrf
    <x-card title="Dataset">
        <select name="dataset_id" class="w-full max-w-md rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm">
            @foreach($datasets as $d)
                <option value="{{ $d->id }}" {{ (string) old('dataset_id', request('dataset')) === (string) $d->id ? 'selected' : '' }}>
                    {{ $d->name }} ({{ number_format($d->n_rows) }} baris)
                </option>
            @endforeach
        </select>
    </x-card>

    <x-card title="Parameter">
        @php
            $fields = [
                ['n_clusters', 'Jumlah cluster (c)', '1', '2 - 10'],
                ['m', 'Fuzzifier (m)', 'any', '> 1 dan ≤ 5'],
                ['tol', 'Toleransi (epsilon)', 'any', 'contoh 0.00001'],
                ['max_iter', 'Iterasi maksimum', '1', '1 - 1000'],
                ['k', 'Tetangga KNN (k)', '1', '1 - 50'],
                ['test_size', 'Proporsi data uji', 'any', '0.1 - 0.5'],
                ['membership_weight', 'Bobot fitur membership', 'any', '0 - 10'],
                ['random_state', 'Random state', '1', 'bilangan bulat'],
            ];
        @endphp
        <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            @foreach($fields as [$name, $label, $step, $hint])
                <div>
                    <label class="text-sm font-semibold" for="{{ $name }}">{{ $label }}</label>
                    <input id="{{ $name }}" name="{{ $name }}" type="number" step="{{ $step }}" value="{{ old($name, $defaults[$name]) }}"
                           class="mt-1 w-full rounded-xl border px-3 py-2.5 text-sm {{ $errors->has($name) ? 'border-red-400' : 'border-slate-300' }}">
                    <p class="mt-1 text-xs text-slate-500">{{ $hint }}</p>
                    @error($name)<p class="text-xs text-red-600">{{ $message }}</p>@enderror
                </div>
            @endforeach
        </div>
    </x-card>

    <x-card title="Tahapan Pengolahan">
        <ol class="space-y-2 text-sm">
            @foreach([
                'Validasi dan pembersihan data (TotalCharges kosong diisi tenure × MonthlyCharges).',
                'Pembagian data latih/uji secara stratified agar proporsi churn terjaga.',
                'One-hot encoding fitur kategorikal dan standarisasi z-score fitur numerik (dari data latih saja).',
                'FCM pada tenure, MonthlyCharges, TotalCharges: hitung pusat cluster dan perbarui U sampai konvergen.',
                'Hitung derajat keanggotaan data latih dan data uji terhadap pusat cluster.',
                'KNN gabungan memakai [fitur asli | bobot × membership]; KNN baseline tanpa membership.',
                'Evaluasi: akurasi, precision, recall, F1, confusion matrix, silhouette, PC, PE.',
            ] as $i => $step)
                <li class="flex gap-3"><span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600">{{ $i + 1 }}</span>{{ $step }}</li>
            @endforeach
        </ol>
    </x-card>

    <button class="rounded-xl bg-blue-600 px-8 py-3 text-sm font-bold text-white shadow hover:bg-blue-700">▶ Jalankan Proses</button>
</form>
@endif
@endsection
