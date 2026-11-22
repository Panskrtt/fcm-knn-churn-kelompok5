<?php

namespace App\Http\Controllers;

use App\Exceptions\FuzzyApiException;
use App\Models\Dataset;
use App\Services\FuzzyApi;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class DatasetController extends Controller
{
    public function index(Request $request)
    {
        $datasets = Dataset::latest()->get();
        $selected = $datasets->firstWhere('id', (int) $request->query('dataset')) ?? $datasets->first();

        return view('datasets.index', compact('datasets', 'selected'));
    }

    public function store(Request $request, FuzzyApi $api)
    {
        $request->validate(
            ['file' => ['required', 'file', 'max:20480']],
            [
                'file.required' => 'Pilih file CSV terlebih dahulu.',
                'file.file' => 'Berkas tidak valid.',
                'file.max' => 'Ukuran file maksimal 20 MB.',
            ]
        );

        $file = $request->file('file');
        if (strtolower($file->getClientOriginalExtension()) !== 'csv') {
            return back()->withErrors(['file' => 'File harus berekstensi .csv']);
        }

        // Validasi isi dataset dilakukan oleh API Python (kolom wajib, kelas churn, dll.)
        try {
            $info = $api->inspect($file->getRealPath(), $file->getClientOriginalName());
        } catch (FuzzyApiException $e) {
            return back()->withErrors(['file' => $e->getMessage()]);
        }

        $path = $file->store('datasets');
        $dataset = Dataset::create([
            'name' => $file->getClientOriginalName(),
            'path' => $path,
            'n_rows' => $info['n_rows'],
            'n_cols' => $info['n_cols'],
            'churn_rate' => $info['churn_rate'],
            'preview' => ['columns' => $info['columns'], 'rows' => $info['preview']],
        ]);

        return redirect()->route('datasets.index', ['dataset' => $dataset->id])
            ->with('success', "Dataset valid: {$info['n_rows']} baris, {$info['n_cols']} kolom. Lanjut ke menu Proses.");
    }

    public function destroy(Dataset $dataset, FuzzyApi $api)
    {
        foreach ($dataset->experiments as $experiment) {
            $api->deleteModel($experiment->model_id);
        }
        Storage::delete($dataset->path);
        $dataset->delete(); // eksperimen dan prediksi ikut terhapus (cascade)

        return redirect()->route('datasets.index')->with('success', 'Dataset beserta hasilnya dihapus.');
    }
}
