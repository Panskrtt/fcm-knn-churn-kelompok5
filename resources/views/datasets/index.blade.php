@extends('layouts.app')
@section('title', 'Input Data')
@section('content')
<h1 class="text-3xl font-bold">Input Data</h1>
<p class="mb-6 mt-1 text-slate-500">Unggah dataset Telco Customer Churn (CSV). Dataset divalidasi oleh API Python lalu disimpan.</p>

<x-card title="Unggah Dataset" subtitle="Format CSV dengan kolom Telco Customer Churn (termasuk kolom Churn sebagai target). Maksimal 20 MB.">
    <form method="POST" action="{{ route('datasets.store') }}" enctype="multipart/form-data" data-loading="Memvalidasi dataset...">
        @csrf
        <div class="flex flex-wrap items-center gap-3">
            <input type="file" name="file" accept=".csv,text/csv"
                   class="block w-full max-w-md text-sm text-slate-600 file:mr-4 file:rounded-lg file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-blue-700 hover:file:bg-blue-100">
            <button class="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700">Unggah &amp; Validasi</button>
        </div>
    </form>
</x-card>

<x-card title="Dataset Tersimpan">
    @if($datasets->isEmpty())
        <p class="text-sm text-slate-500">Belum ada dataset.</p>
    @else
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
                <thead class="bg-slate-100 text-xs uppercase text-slate-500">
                <tr><th class="px-3 py-2">Nama file</th><th class="px-3 py-2">Baris</th><th class="px-3 py-2">Kolom</th><th class="px-3 py-2">Churn</th><th class="px-3 py-2">Diunggah</th><th class="px-3 py-2"></th></tr>
                </thead>
                <tbody>
                @foreach($datasets as $d)
                    <tr class="border-t border-slate-100 {{ $selected && $selected->id === $d->id ? 'bg-blue-50' : '' }}">
                        <td class="px-3 py-2 font-medium">{{ $d->name }}</td>
                        <td class="px-3 py-2">{{ number_format($d->n_rows) }}</td>
                        <td class="px-3 py-2">{{ $d->n_cols }}</td>
                        <td class="px-3 py-2">{{ number_format($d->churn_rate * 100, 1) }}%</td>
                        <td class="px-3 py-2 text-slate-500">{{ $d->created_at->format('d M Y H:i') }}</td>
                        <td class="flex justify-end gap-2 px-3 py-2">
                            <a href="{{ route('datasets.index', ['dataset' => $d->id]) }}" class="rounded-lg border border-slate-300 px-3 py-1 text-xs font-semibold hover:bg-slate-50">Pratinjau</a>
                            <a href="{{ route('experiments.create', ['dataset' => $d->id]) }}" class="rounded-lg bg-blue-600 px-3 py-1 text-xs font-semibold text-white hover:bg-blue-700">Proses</a>
                            <form method="POST" action="{{ route('datasets.destroy', $d) }}" onsubmit="return confirm('Hapus dataset beserta semua hasilnya?')">
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

@if($selected)
    <x-card :title="'Pratinjau: ' . $selected->name" subtitle="50 baris pertama.">
        <div class="max-h-96 overflow-auto rounded-lg border border-slate-200">
            <table class="min-w-full text-left text-xs">
                <thead class="sticky top-0 bg-slate-100 text-slate-600">
                <tr>@foreach($selected->preview['columns'] as $col)<th class="whitespace-nowrap px-3 py-2">{{ $col }}</th>@endforeach</tr>
                </thead>
                <tbody>
                @foreach($selected->preview['rows'] as $i => $row)
                    <tr class="{{ $i % 2 ? 'bg-slate-50' : '' }}">@foreach($row as $cell)<td class="whitespace-nowrap px-3 py-1.5">{{ $cell }}</td>@endforeach</tr>
                @endforeach
                </tbody>
            </table>
        </div>
    </x-card>
@endif

<x-card title="Penjelasan Variabel">
    <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
            <thead class="bg-slate-100 text-xs uppercase text-slate-500"><tr><th class="px-3 py-2">Variabel</th><th class="px-3 py-2">Penjelasan</th></tr></thead>
            <tbody>
            @foreach(config('fuzzy.column_descriptions') as $name => $desc)
                <tr class="border-t border-slate-100 {{ $loop->odd ? '' : 'bg-slate-50' }}">
                    <td class="px-3 py-2 font-mono text-xs font-semibold">{{ $name }}</td>
                    <td class="px-3 py-2 text-slate-600">{{ $desc }}</td>
                </tr>
            @endforeach
            </tbody>
        </table>
    </div>
</x-card>
@endsection
