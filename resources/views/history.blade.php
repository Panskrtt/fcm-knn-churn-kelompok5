@extends('layouts.app')
@section('title', 'Riwayat')
@section('content')
<h1 class="text-3xl font-bold">Riwayat</h1>
<p class="mb-6 mt-1 text-slate-500">Seluruh eksperimen dan prediksi yang tersimpan di database MySQL.</p>

<x-card title="Eksperimen">
    @if($experiments->isEmpty())
        <p class="text-sm text-slate-500">Belum ada eksperimen.</p>
    @else
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
                <thead class="bg-slate-100 text-xs uppercase text-slate-500"><tr><th class="px-3 py-2">#</th><th class="px-3 py-2">Waktu</th><th class="px-3 py-2">Dataset</th><th class="px-3 py-2">c</th><th class="px-3 py-2">k</th><th class="px-3 py-2">Akurasi</th><th class="px-3 py-2">F1 baseline</th><th class="px-3 py-2">F1 gabungan</th><th class="px-3 py-2">Silhouette</th><th class="px-3 py-2"></th></tr></thead>
                <tbody>
                @foreach($experiments as $e)
                    <tr class="border-t border-slate-100">
                        <td class="px-3 py-2 font-semibold">{{ $e->id }}</td>
                        <td class="px-3 py-2 text-slate-500">{{ $e->created_at->format('d M Y H:i') }}</td>
                        <td class="px-3 py-2">{{ $e->dataset->name }}</td>
                        <td class="px-3 py-2">{{ $e->n_clusters }}</td>
                        <td class="px-3 py-2">{{ $e->k }}</td>
                        <td class="px-3 py-2">{{ number_format($e->accuracy, 3) }}</td>
                        <td class="px-3 py-2">{{ number_format($e->f1_base, 3) }}</td>
                        <td class="px-3 py-2 font-semibold">{{ number_format($e->f1_comb, 3) }}</td>
                        <td class="px-3 py-2">{{ $e->silhouette === null ? 'n/a' : number_format($e->silhouette, 3) }}</td>
                        <td class="flex justify-end gap-2 px-3 py-2">
                            <a href="{{ route('experiments.show', $e) }}" class="rounded-lg bg-blue-600 px-3 py-1 text-xs font-semibold text-white hover:bg-blue-700">Hasil</a>
                            <a href="{{ route('experiments.evaluation', $e) }}" class="rounded-lg border border-slate-300 px-3 py-1 text-xs font-semibold hover:bg-slate-50">Evaluasi</a>
                            <form method="POST" action="{{ route('experiments.destroy', $e) }}" onsubmit="return confirm('Hapus eksperimen ini beserta riwayat prediksinya?')">
                                @csrf @method('DELETE')
                                <button class="rounded-lg border border-red-200 px-3 py-1 text-xs font-semibold text-red-600 hover:bg-red-50">Hapus</button>
                            </form>
                        </td>
                    </tr>
                @endforeach
                </tbody>
            </table>
        </div>
    @endif
</x-card>

<x-card title="Prediksi">
    @if($predictions->isEmpty())
        <p class="text-sm text-slate-500">Belum ada prediksi.</p>
    @else
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
                <thead class="bg-slate-100 text-xs uppercase text-slate-500"><tr><th class="px-3 py-2">Waktu</th><th class="px-3 py-2">Model</th><th class="px-3 py-2">Tenure</th><th class="px-3 py-2">Tagihan</th><th class="px-3 py-2">Kontrak</th><th class="px-3 py-2">Cluster</th><th class="px-3 py-2">Hasil</th><th class="px-3 py-2">Baseline</th><th class="px-3 py-2">Proporsi churn</th></tr></thead>
                <tbody>
                @foreach($predictions as $h)
                    <tr class="border-t border-slate-100">
                        <td class="px-3 py-2 text-slate-500">{{ $h->created_at->format('d M Y H:i') }}</td>
                        <td class="px-3 py-2">#{{ $h->experiment_id }}</td>
                        <td class="px-3 py-2">{{ $h->input['tenure'] }}</td>
                        <td class="px-3 py-2">${{ number_format($h->input['MonthlyCharges'], 2) }}</td>
                        <td class="px-3 py-2">{{ $h->input['Contract'] }}</td>
                        <td class="px-3 py-2">Cluster {{ $h->cluster }}</td>
                        <td class="px-3 py-2"><span class="rounded-full px-2.5 py-0.5 text-xs font-semibold {{ $h->pred ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700' }}">{{ $h->pred ? 'Churn' : 'Bertahan' }}</span></td>
                        <td class="px-3 py-2 text-slate-500">{{ $h->pred_base ? 'Churn' : 'Bertahan' }}</td>
                        <td class="px-3 py-2">{{ number_format($h->proba_churn * 100) }}%</td>
                    </tr>
                @endforeach
                </tbody>
            </table>
        </div>
    @endif
</x-card>
@endsection
