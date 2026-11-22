@extends('layouts.app')
@section('title', 'Evaluasi')
@section('content')
@php
    $b = $r['metrics_base'];
    $g = $r['metrics_comb'];
    $v = $r['validity'];
    $dF1 = $g['f1'] - $b['f1'];
    $verdictBg = $dF1 > 0.005 ? 'bg-green-50 border-green-200' : ($dF1 < -0.005 ? 'bg-red-50 border-red-200' : 'bg-blue-50 border-blue-200');
    $cm = $g['confusion_matrix'];
    $cmMax = max(1, max($cm[0][0], $cm[0][1], $cm[1][0], $cm[1][1]));
    $kpis = ['accuracy' => 'Akurasi', 'precision' => 'Precision churn', 'recall' => 'Recall churn', 'f1' => 'F1 churn'];
    $baseVals = [$b['accuracy'], $b['precision'], $b['recall'], $b['f1']];
    $combVals = [$g['accuracy'], $g['precision'], $g['recall'], $g['f1']];
@endphp

<div class="mb-6 flex flex-wrap items-start justify-between gap-4">
    <div>
        <h1 class="text-3xl font-bold">Evaluasi</h1>
        <p class="mt-1 text-slate-500">Eksperimen #{{ $exp->id }} · {{ $exp->dataset->name }} · pengujian pada data uji ({{ $r['n_test'] ?? '-' }} baris)</p>
    </div>
    <a href="{{ route('experiments.show', $exp) }}" class="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold hover:bg-slate-50">← Kembali ke Hasil</a>
</div>

<div class="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
    @foreach($kpis as $key => $label)
        @php $d = $g[$key] - $b[$key]; @endphp
        <x-kpi :label="$label" :value="number_format($g[$key], 3)" :sub="sprintf('%+.1f poin vs baseline', $d * 100)" :tone="$d > 0.005 ? 'green' : ($d < -0.005 ? 'red' : 'muted')" />
    @endforeach
</div>

<x-card title="Metrik Klasifikasi" subtitle="Kelas churn sebagai kelas positif, dihitung pada data uji.">
    <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
            <thead class="bg-slate-100 text-xs uppercase text-slate-500"><tr><th class="px-3 py-2">Model</th><th class="px-3 py-2">Akurasi</th><th class="px-3 py-2">Precision</th><th class="px-3 py-2">Recall</th><th class="px-3 py-2">F1</th></tr></thead>
            <tbody>
            @foreach(['KNN baseline (tanpa membership)' => $b, 'FCM + KNN (gabungan)' => $g] as $name => $m)
                <tr class="border-t border-slate-100 {{ $loop->last ? 'bg-blue-50 font-semibold' : '' }}">
                    <td class="px-3 py-2">{{ $name }}</td>
                    <td class="px-3 py-2">{{ number_format($m['accuracy'], 3) }}</td>
                    <td class="px-3 py-2">{{ number_format($m['precision'], 3) }}</td>
                    <td class="px-3 py-2">{{ number_format($m['recall'], 3) }}</td>
                    <td class="px-3 py-2">{{ number_format($m['f1'], 3) }}</td>
                </tr>
            @endforeach
            </tbody>
        </table>
    </div>
</x-card>

<x-card title="Kualitas Clustering FCM" subtitle="Dihitung pada data latih.">
    <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
            <thead class="bg-slate-100 text-xs uppercase text-slate-500"><tr><th class="px-3 py-2">Silhouette</th><th class="px-3 py-2">Partition Coefficient</th><th class="px-3 py-2">Partition Entropy</th><th class="px-3 py-2">J akhir</th><th class="px-3 py-2">Iterasi</th><th class="px-3 py-2">Konvergen</th></tr></thead>
            <tbody>
            <tr class="border-t border-slate-100">
                <td class="px-3 py-2">{{ $v['silhouette'] === null ? 'n/a' : number_format($v['silhouette'], 3) }}</td>
                <td class="px-3 py-2">{{ number_format($v['pc'], 3) }}</td>
                <td class="px-3 py-2">{{ number_format($v['pe'], 3) }}</td>
                <td class="px-3 py-2">{{ number_format($v['J'], 2) }}</td>
                <td class="px-3 py-2">{{ $v['iterations'] }}</td>
                <td class="px-3 py-2">{{ $v['converged'] ? 'Ya' : 'Tidak' }}</td>
            </tr>
            </tbody>
        </table>
    </div>
</x-card>

<div class="grid gap-6 lg:grid-cols-2">
    <x-card title="Perbandingan Metrik">
        <div class="relative h-72"><canvas id="cmp"></canvas></div>
    </x-card>
    <x-card title="Confusion Matrix FCM + KNN">
        <div class="mx-auto max-w-sm">
            <div class="grid grid-cols-[auto_1fr_1fr] items-center gap-2 text-center text-sm">
                <div></div><div class="font-semibold text-slate-500">Prediksi: Tidak</div><div class="font-semibold text-slate-500">Prediksi: Churn</div>
                @foreach([0, 1] as $i)
                    <div class="pr-2 text-right font-semibold text-slate-500">Aktual: {{ $i ? 'Churn' : 'Tidak' }}</div>
                    @foreach([0, 1] as $j)
                        @php $ratio = $cm[$i][$j] / $cmMax; @endphp
                        <div class="rounded-xl py-8 text-2xl font-bold {{ $ratio > 0.5 ? 'text-white' : 'text-slate-900' }}"
                             style="background: rgba(37, 99, 235, {{ round(0.1 + 0.9 * $ratio, 2) }})">{{ $cm[$i][$j] }}</div>
                    @endforeach
                @endforeach
            </div>
        </div>
    </x-card>
</div>

<x-card title="Analisis">
    <div class="rounded-xl border p-4 text-sm text-slate-800 {{ $verdictBg }}"><p class="whitespace-pre-line">{{ $r['text_comparison'] }}</p></div>
    <div class="mt-4 text-sm text-slate-600">
        @foreach(explode("\n", $r['limitations']) as $line)
            @if(str_starts_with($line, '- '))
                <p class="ml-4 mt-1 list-item">{{ substr($line, 2) }}</p>
            @else
                <p class="mt-1 font-semibold text-slate-800">{{ $line }}</p>
            @endif
        @endforeach
    </div>
</x-card>
@endsection

@push('scripts')
<script>
    const base = @json($baseVals);
    const comb = @json($combVals);
    new Chart(document.getElementById('cmp'), {
        type: 'bar',
        data: {
            labels: ['Akurasi', 'Precision', 'Recall', 'F1'],
            datasets: [
                {label: 'Baseline', data: base, backgroundColor: '#cbd5e1'},
                {label: 'FCM + KNN', data: comb, backgroundColor: '#2563eb'}
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {y: {min: 0, max: 1}},
            plugins: {legend: {position: 'bottom'}}
        }
    });
</script>
@endpush
