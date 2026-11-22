<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'FCM + KNN') | Prediksi Churn</title>
    {{-- Tailwind via CDN (tanpa npm). Perlu koneksi internet saat halaman dibuka. --}}
    <script src="https://cdn.tailwindcss.com/3.4.17"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>body { font-family: ui-sans-serif, system-ui, "Segoe UI", Roboto, Arial, sans-serif; }</style>
</head>
<body class="bg-slate-100 text-slate-900">
@php
    $nav = [
        ['home', 'Beranda', '⌂', ['home']],
        ['datasets.index', 'Input Data', '⇩', ['datasets.*']],
        ['experiments.create', 'Proses', '⚙', ['experiments.create', 'experiments.store']],
        ['results.latest', 'Hasil', '▦', ['experiments.show', 'results.latest']],
        ['evaluation.latest', 'Evaluasi', '✓', ['experiments.evaluation', 'evaluation.latest']],
        ['predictions.create', 'Prediksi', '◎', ['predictions.*']],
        ['history', 'Riwayat', '☰', ['history']],
        ['info', 'Informasi Sistem', 'ⓘ', ['info']],
    ];
@endphp

<aside class="fixed inset-y-0 left-0 hidden w-64 flex-col bg-slate-900 p-4 lg:flex">
    <div class="px-3 pb-6 pt-4">
        <p class="text-2xl font-bold text-white">FCM + KNN</p>
        <p class="text-sm text-slate-400">Prediksi Churn Pelanggan</p>
    </div>
    <nav class="space-y-1">
        @foreach($nav as [$route, $label, $glyph, $patterns])
            <a href="{{ route($route) }}"
               class="flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition {{ request()->routeIs(...$patterns) ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800' }}">
                <span class="w-5 text-center">{{ $glyph }}</span>{{ $label }}
            </a>
        @endforeach
    </nav>
    <p class="mt-auto px-3 text-xs text-slate-500">Teknologi Logika Fuzzy<br>Laravel + FastAPI + MySQL</p>
</aside>

<nav class="flex gap-2 overflow-x-auto bg-slate-900 p-3 lg:hidden">
    @foreach($nav as [$route, $label, $glyph, $patterns])
        <a href="{{ route($route) }}"
           class="whitespace-nowrap rounded-lg px-3 py-1.5 text-sm {{ request()->routeIs(...$patterns) ? 'bg-blue-600 text-white' : 'text-slate-300' }}">{{ $label }}</a>
    @endforeach
</nav>

<div class="lg:pl-64">
    <main class="mx-auto max-w-6xl p-6 lg:p-10">
        @if(session('success'))
            <div class="mb-5 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">✓ {{ session('success') }}</div>
        @endif
        @if(session('info'))
            <div class="mb-5 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">{{ session('info') }}</div>
        @endif
        @if($errors->any())
            <div class="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                <p class="font-semibold">Terjadi kesalahan:</p>
                <ul class="ml-5 mt-1 list-disc">
                    @foreach($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif

        @yield('content')
    </main>
</div>

<div id="loading" class="fixed inset-0 z-50 hidden items-center justify-center bg-slate-900/60">
    <div class="rounded-2xl bg-white px-8 py-6 text-center shadow-xl">
        <div class="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600"></div>
        <p id="loading-text" class="text-sm font-medium text-slate-700">Memproses...</p>
    </div>
</div>
<script>
    const loading = document.getElementById('loading');
    document.querySelectorAll('form[data-loading]').forEach(function (f) {
        f.addEventListener('submit', function () {
            document.getElementById('loading-text').textContent = f.dataset.loading;
            loading.classList.remove('hidden');
            loading.classList.add('flex');
        });
    });
    window.addEventListener('pageshow', function () { loading.classList.add('hidden'); loading.classList.remove('flex'); });
</script>
@stack('scripts')
</body>
</html>
