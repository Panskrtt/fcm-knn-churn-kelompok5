<?php

namespace App\Services;

use App\Exceptions\FuzzyApiException;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Client\Response;
use Illuminate\Support\Facades\Http;

/**
 * Klien HTTP untuk API Python (FastAPI) yang menjalankan FCM + KNN.
 */
class FuzzyApi
{
    private function base(): string
    {
        return rtrim(config('fuzzy.api_url'), '/');
    }

    private function handle(Response $response): array
    {
        if ($response->successful()) {
            return $response->json();
        }

        $detail = $response->json('detail');
        if (is_array($detail)) { // format galat validasi FastAPI
            $detail = collect($detail)->map(function ($d) {
                $loc = $d['loc'] ?? [];
                return (count($loc) ? end($loc) . ': ' : '') . ($d['msg'] ?? '');
            })->implode('; ');
        }

        throw new FuzzyApiException($detail ?: 'API Python mengembalikan kesalahan (HTTP ' . $response->status() . ').');
    }

    private function send(callable $request): array
    {
        try {
            return $this->handle($request());
        } catch (ConnectionException $e) {
            throw new FuzzyApiException(
                'API Python tidak dapat dihubungi di ' . $this->base() . '. Pastikan uvicorn sedang berjalan.'
            );
        }
    }

    public function health(): bool
    {
        try {
            return Http::timeout(3)->get($this->base() . '/health')->successful();
        } catch (\Throwable $e) {
            return false;
        }
    }

    /** Validasi CSV + ringkasan + pratinjau. */
    public function inspect(string $path, string $name): array
    {
        return $this->send(fn () => Http::timeout(60)
            ->attach('file', file_get_contents($path), $name)
            ->post($this->base() . '/inspect'));
    }

    /** Menjalankan FCM + KNN. */
    public function train(string $path, string $name, array $params): array
    {
        return $this->send(fn () => Http::timeout(config('fuzzy.timeout'))
            ->attach('file', file_get_contents($path), $name)
            ->post($this->base() . '/train', $params));
    }

    /** Prediksi satu pelanggan memakai model yang sudah dilatih. */
    public function predict(string $modelId, array $values): array
    {
        return $this->send(fn () => Http::timeout(60)
            ->post($this->base() . '/predict', ['model_id' => $modelId, 'values' => $values]));
    }

    public function deleteModel(string $modelId): void
    {
        try {
            Http::timeout(10)->delete($this->base() . '/models/' . $modelId);
        } catch (\Throwable $e) {
            // model yatim di sisi Python tidak berbahaya; abaikan
        }
    }
}
