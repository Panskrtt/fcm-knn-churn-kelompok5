@extends('layouts.app')
@section('title', 'Prediksi')
@section('content')
<h1 class="text-3xl font-bold">Prediksi Pelanggan</h1>
<p class="mb-6 mt-1 text-slate-500">Masukkan data satu pelanggan. Hasil prediksi dan derajat keanggotaannya disimpan ke riwayat.</p>

@if($experiments->isEmpty())
    <x-card>
        <p class="text-sm text-slate-600">Belum ada model. <a class="font-semibold text-blue-600 underline" href="{{ route('experiments.create') }}">Jalankan proses</a> terlebih dahulu.</p>
    </x-card>
@else
@php
    $opt = config('fuzzy.options');
    $palette = ['#2563eb', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#64748b'];
    $res = session('result');
    $selects = [
        'SeniorCitizen' => ['Senior citizen (0/1)', '0'],
        'Contract' => ['Kontrak', 'Month-to-month'],
        'InternetService' => ['Layanan internet', 'Fiber optic'],
        'PaymentMethod' => ['Metode pembayaran', 'Electronic check'],
        'PaperlessBilling' => ['Tagihan tanpa kertas', 'Yes'],
        'TechSupport' => ['Dukungan teknis', 'No'],
        'OnlineSecurity' => ['Keamanan online', 'No'],
    ];
@endphp
<div class="grid gap-6 lg:grid-cols-5">
    <div class="lg:col-span-3">
        <x-card title="Data Pelanggan" subtitle="Kolom lain diisi nilai paling umum dari data latih.">
            <form method="POST" action="{{ route('predictions.store') }}" data-loading="Memprediksi...">
                @csrf
                <label class="text-sm font-semibold">Model (eksperimen)</label>
                <select name="experiment_id" class="mb-5 mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm"
                        onchange="location.href='{{ route('predictions.create') }}?experiment=' + this.value">
                    @foreach($experiments as $e)
                        <option value="{{ $e->id }}" {{ $selected && $selected->id === $e->id ? 'selected' : '' }}>
                            #{{ $e->id }} · {{ $e->dataset->name }} · c={{ $e->n_clusters }}, k={{ $e->k }} · F1 {{ number_format($e->f1_comb, 3) }}
                        </option>
                    @endforeach
                </select>

                <div class="grid gap-4 sm:grid-cols-2">
                    <div>
                        <label class="text-sm font-semibold">Lama berlangganan (bulan)</label>
                        <input name="tenure" type="number" step="1" value="{{ old('tenure', 12) }}" class="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm">
                    </div>
                    <div>
                        <label class="text-sm font-semibold">Tagihan bulanan ($)</label>
                        <input name="MonthlyCharges" type="number" step="any" value="{{ old('MonthlyCharges', 70) }}" class="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm">
                    </div>
                    <div class="sm:col-span-2">
                        <label class="text-sm font-semibold">Total tagihan ($) <span class="font-normal text-slate-500">(kosongkan = tenure × tagihan bulanan)</span></label>
                        <input name="TotalCharges" type="number" step="any" value="{{ old('TotalCharges') }}" class="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm">
                    </div>
                    @foreach($selects as $name => [$label, $default])
                        <div>
                            <label class="text-sm font-semibold">{{ $label }}</label>
                            <select name="{{ $name }}" class="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm">
                                @foreach($opt[$name] as $o)
                                    <option value="{{ $o }}" {{ (string) old($name, $default) === (string) $o ? 'selected' : '' }}>{{ $o }}</option>
                                @endforeach
                            </select>
                        </div>
                    @endforeach
                </div>
                <button class="mt-6 rounded-xl bg-blue-600 px-6 py-3 text-sm font-bold text-white hover:bg-blue-700">Prediksi Pelanggan</button>
            </form>
        </x-card>
    </div>

    <div class="lg:col-span-2">
        <x-card title="Hasil Prediksi">
            @if($res)
                @if($res['pred'])
                    <div class="rounded-xl bg-red-100 px-4 py-3 font-bold text-red-700">⚠ BERISIKO CHURN ({{ number_format($res['proba_churn'] * 100) }}% tetangga churn)</div>
                @else
                    <div class="rounded-xl bg-green-100 px-4 py-3 font-bold text-green-700">✓ Kemungkinan bertahan ({{ number_format($res['proba_churn'] * 100) }}% tetangga churn)</div>
                @endif
                <p class="mt-3 text-sm text-slate-600">Prediksi KNN baseline: <b>{{ $res['pred_base'] ? 'churn' : 'bertahan' }}</b></p>
                <p class="mt-4 text-sm font-semibold">Derajat keanggotaan</p>
                <div class="mt-2 space-y-2">
                    @foreach($res['membership'] as $i => $mu)
                        <div>
                            <div class="flex justify-between text-xs"><span>Cluster {{ $i + 1 }}</span><span class="font-semibold">{{ number_format($mu, 3) }}</span></div>
                            <div class="h-2.5 rounded-full bg-slate-100"><div class="h-2.5 rounded-full" style="width: {{ round($mu * 100, 1) }}%; background: {{ $palette[$i % 10] }}"></div></div>
                        </div>
                    @endforeach
                </div>
                @if(isset($res['cluster_churn_rate']))
                    <p class="mt-4 text-sm text-slate-600">Segmen dominan (Cluster {{ $res['cluster'] }}) memiliki churn historis {{ number_format($res['cluster_churn_rate'] * 100, 1) }}% di data latih.</p>
                @endif
            @else
                <p class="text-sm text-slate-500">Belum ada prediksi. Isi form lalu klik Prediksi Pelanggan.</p>
            @endif
        </x-card>
    </div>
</div>

<x-card title="Riwayat Prediksi (model terpilih, 10 terakhir)">
    @if($history->isEmpty())
        <p class="text-sm text-slate-500">Belum ada riwayat untuk model ini.</p>
    @else
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
                <thead class="bg-slate-100 text-xs uppercase text-slate-500"><tr><th class="px-3 py-2">Waktu</th><th class="px-3 py-2">Tenure</th><th class="px-3 py-2">Tagihan</th><th class="px-3 py-2">Kontrak</th><th class="px-3 py-2">Cluster</th><th class="px-3 py-2">Hasil</th><th class="px-3 py-2">Proporsi churn</th></tr></thead>
                <tbody>
                @foreach($history as $h)
                    <tr class="border-t border-slate-100">
                        <td class="px-3 py-2 text-slate-500">{{ $h->created_at->format('d M H:i') }}</td>
                        <td class="px-3 py-2">{{ $h->input['tenure'] }}</td>
                        <td class="px-3 py-2">${{ number_format($h->input['MonthlyCharges'], 2) }}</td>
                        <td class="px-3 py-2">{{ $h->input['Contract'] }}</td>
                        <td class="px-3 py-2">Cluster {{ $h->cluster }}</td>
                        <td class="px-3 py-2"><span class="rounded-full px-2.5 py-0.5 text-xs font-semibold {{ $h->pred ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700' }}">{{ $h->pred ? 'Churn' : 'Bertahan' }}</span></td>
                        <td class="px-3 py-2">{{ number_format($h->proba_churn * 100) }}%</td>
                    </tr>
                @endforeach
                </tbody>
            </table>
        </div>
    @endif
</x-card>
@endif
@endsection
