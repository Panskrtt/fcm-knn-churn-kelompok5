@props(['title' => null, 'subtitle' => null])
<section {{ $attributes->merge(['class' => 'mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm']) }}>
    @if($title)
        <h2 class="text-lg font-bold text-slate-900">{{ $title }}</h2>
    @endif
    @if($subtitle)
        <p class="mt-1 text-sm text-slate-500">{{ $subtitle }}</p>
    @endif
    <div class="{{ $title ? 'mt-4' : '' }}">{{ $slot }}</div>
</section>
