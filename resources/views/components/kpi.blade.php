@props(['label', 'value', 'sub' => null, 'tone' => 'slate'])
@php
    $tones = ['blue' => 'text-blue-600', 'green' => 'text-green-700', 'red' => 'text-red-600', 'slate' => 'text-slate-900', 'muted' => 'text-slate-500'];
@endphp
<div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <p class="text-xs font-medium text-slate-500">{{ $label }}</p>
    <p class="mt-1 text-3xl font-bold {{ $tones[$tone] ?? $tones['slate'] }}">{{ $value }}</p>
    @if($sub)
        <p class="mt-1 text-xs text-slate-500">{{ $sub }}</p>
    @endif
</div>
