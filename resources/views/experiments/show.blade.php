@extends('layouts.app')
@section('title', 'Hasil')
@section('content')
@php
    $v = $r['validity'];
    $p = $r['params'];
    $palette = ['#2563eb', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#64748b'];
    $lines = explode("\n", $r['text_clusters']);
    $nProfile = count($r['profile']);
@endphp

<div class="mb-6 flex flex-wrap items-start justify-between gap-4">
    <div>
        <h1 class="text-3xl font-bold">Hasil Pengolahan</h1>
        <p class="mt-1 text-slate-500">Eksperimen #{{ $exp->id }} · {{ $exp->dataset->name }} · {{ $exp->created_at->format('d M Y H:i') }}</p>
    </div>
    <div class="flex gap-2">
        <a href="{{ route('experiments.evaluation', $exp) }}" class="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700">Lihat Evaluasi →</a>
        <a href="{{ route('predictions.create', ['experiment' => $exp->id]) }}" class="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold hover:bg-slate-50">Prediksi pelanggan</a>
    </div>
</div>

<div class="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
    <x-kpi label="Jumlah cluster" :value="$p['n_clusters']" :sub="'fuzzifier m = ' . $p['m']" tone="blue" />
    <x-kpi label="Iterasi FCM" :value="$v['iterations']" :sub="$v['converged'] ? 'konvergen' : 'belum konvergen'" :tone="$v['converged'] ? 'green' : 'red'" />
    <x-kpi label="Silhouette" :value="$v['silhouette'] === null ? 'n/a' : number_format($v['silhouette'], 3)" sub="makin mendekati 1 makin baik" />
    <x-kpi label="Partition Coefficient" :value="number_format($v['pc'], 3)" sub="makin besar makin tegas" />
</div>

<x-card title="Segmentasi Pelanggan (Fuzzy C-Means)" subtitle="Warna = cluster dengan keanggotaan tertinggi. Tanda ◆ gelap = pusat cluster.">
    <div class="relative h-[420px]"><canvas id="scatter"></canvas></div>
</x-card>

<x-card title="Pusat Cluster dan Profil Segmen">
    <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
            <thead class="bg-slate-100 text-xs uppercase text-slate-500">
            <tr><th class="px-3 py-2">Cluster</th><th class="px-3 py-2">Jumlah</th><th class="px-3 py-2">Porsi</th><th class="px-3 py-2">Pusat tenure</th><th class="px-3 py-2">Pusat MonthlyCharges</th><th class="px-3 py-2">Pusat TotalCharges</th><th class="px-3 py-2">Churn</th></tr>
            </thead>
            <tbody>
            @foreach($r['profile'] as $row)
                @php $c = $r['centers'][$row['cluster'] - 1]; @endphp
                <tr class="border-t border-slate-100 {{ $loop->odd ? '' : 'bg-slate-50' }}">
                    <td class="px-3 py-2 font-semibold"><span class="mr-2 inline-block h-3 w-3 rounded-full" style="background: {{ $palette[($row['cluster'] - 1) % 10] }}"></span>Cluster {{ $row['cluster'] }}</td>
                    <td class="px-3 py-2">{{ $row['n'] }}</td>
                    <td class="px-3 py-2">{{ number_format($row['pct'], 1) }}%</td>
                    <td class="px-3 py-2">{{ number_format($c[0], 1) }}</td>
                    <td class="px-3 py-2">{{ number_format($c[1], 2) }}</td>
                    <td class="px-3 py-2">{{ number_format($c[2], 1) }}</td>
                    <td class="px-3 py-2 font-semibold">{{ number_format($row['churn'] * 100, 1) }}%</td>
                </tr>
            @endforeach
            </tbody>
        </table>
    </div>
</x-card>

<x-card title="Interpretasi Segmen">
    <div class="space-y-3">
        @foreach($r['profile'] as $i => $row)
            <div class="flex items-start gap-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
                <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white" style="background: {{ $palette[($row['cluster'] - 1) % 10] }}">C{{ $row['cluster'] }}</span>
                <p class="text-sm text-slate-700">{{ $lines[$i] ?? '' }}</p>
            </div>
        @endforeach
    </div>
    <p class="mt-4 whitespace-pre-line text-sm text-slate-500">{{ trim(implode("\n", array_slice($lines, $nProfile))) }}</p>
</x-card>

<x-card title="Konvergensi FCM" subtitle="Nilai fungsi objektif J pada tiap iterasi.">
    <div class="relative h-64"><canvas id="conv"></canvas></div>
</x-card>

<x-card title="Derajat Keanggotaan dan Prediksi (data uji)" subtitle="300 baris pertama. Merah = prediksi berbeda dari label aktual.">
    <div class="max-h-96 overflow-auto rounded-lg border border-slate-200">
        <table class="min-w-full text-left text-xs">
            <thead class="sticky top-0 bg-slate-100 text-slate-600">
            <tr>
                <th class="px-3 py-2">No</th>
                @for($j = 1; $j <= $p['n_clusters']; $j++)<th class="px-3 py-2">μ Cluster {{ $j }}</th>@endfor
                <th class="px-3 py-2">Cluster dominan</th><th class="px-3 py-2">Aktual</th><th class="px-3 py-2">Prediksi FCM+KNN</th>
            </tr>
            </thead>
            <tbody>
            @foreach($r['test_rows'] as $i => $row)
                @php $max = max($row['mu']); @endphp
                <tr class="border-t border-slate-100 {{ $i % 2 ? 'bg-slate-50' : '' }}">
                    <td class="px-3 py-1.5">{{ $i + 1 }}</td>
                    @foreach($row['mu'] as $mu)
                        <td class="px-3 py-1.5 {{ $mu === $max ? 'font-bold text-blue-700' : 'text-slate-500' }}">{{ number_format($mu, 3) }}</td>
                    @endforeach
                    <td class="px-3 py-1.5">Cluster {{ $row['cluster'] }}</td>
                    <td class="px-3 py-1.5">{{ $row['actual'] ? 'Churn' : 'Tidak' }}</td>
                    <td class="px-3 py-1.5 font-semibold {{ $row['actual'] === $row['pred'] ? 'text-slate-800' : 'text-red-600' }}">{{ $row['pred'] ? 'Churn' : 'Tidak' }}</td>
                </tr>
            @endforeach
            </tbody>
        </table>
    </div>
</x-card>

<x-card>
    <details>
        <summary class="cursor-pointer text-sm font-semibold text-slate-700">Log proses dan hasil antara</summary>
        <pre class="mt-3 overflow-x-auto rounded-lg bg-slate-900 p-4 text-xs leading-relaxed text-slate-100">{{ implode("\n", $r['logs']) }}</pre>
    </details>
</x-card>

<form method="POST" action="{{ route('experiments.destroy', $exp) }}" onsubmit="return confirm('Hapus eksperimen ini beserta riwayat prediksinya?')">
    @csrf @method('DELETE')
    <button class="rounded-lg border border-red-200 px-4 py-2 text-sm font-semibold text-red-600 hover:bg-red-50">Hapus eksperimen ini</button>
</form>
@endsection

@push('scripts')
<script>
    const palette = @json($palette);
    const scatter = @json($r['scatter']);
    const centers = @json($r['centers']);
    const history = @json($r['history']);
    const nC = {{ (int) $p['n_clusters'] }};

    const sets = Array.from({length: nC}, function (_, j) {
        return {
            label: 'Cluster ' + (j + 1),
            data: scatter.filter(function (pt) { return pt[2] === j; }).map(function (pt) { return {x: pt[0], y: pt[1]}; }),
            backgroundColor: palette[j % palette.length] + '99',
            pointRadius: 3
        };
    });
    sets.push({
        label: 'Pusat cluster',
        data: centers.map(function (c) { return {x: c[0], y: c[1]}; }),
        backgroundColor: '#0f172a', borderColor: '#ffffff', borderWidth: 2,
        pointStyle: 'rectRot', pointRadius: 9
    });
    new Chart(document.getElementById('scatter'), {
        type: 'scatter',
        data: {datasets: sets},
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                x: {title: {display: true, text: 'Tenure (bulan)'}},
                y: {title: {display: true, text: 'MonthlyCharges ($)'}}
            },
            plugins: {legend: {position: 'bottom'}}
        }
    });

    new Chart(document.getElementById('conv'), {
        type: 'line',
        data: {
            labels: history.map(function (h) { return h[0]; }),
            datasets: [{label: 'Fungsi objektif J', data: history.map(function (h) { return h[1]; }),
                borderColor: '#2563eb', backgroundColor: '#2563eb22', fill: true, pointRadius: 0, tension: 0.2}]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {x: {title: {display: true, text: 'Iterasi'}}, y: {title: {display: true, text: 'J'}}},
            plugins: {legend: {display: false}}
        }
    });
</script>
@endpush
