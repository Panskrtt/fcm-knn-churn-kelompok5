<?php

namespace App\Http\Controllers;

use App\Exceptions\FuzzyApiException;
use App\Models\Dataset;
use App\Models\Experiment;
use App\Services\FuzzyApi;
use Illuminate\Http\Request;
use Illuminate\Support\Arr;
use Illuminate\Support\Facades\Storage;

class ExperimentController extends Controller
{
    public function create()
    {
        return view('experiments.create', [
            'datasets' => Dataset::latest()->get(),
            'defaults' => [
                'n_clusters' => 3, 'm' => 2.0, 'tol' => '0.00001', 'max_iter' => 300, 'k' => 5,
                'test_size' => 0.2, 'membership_weight' => 1.0, 'random_state' => 42,
            ],
        ]);
    }

    public function store(Request $request, FuzzyApi $api)
    {
        $data = $request->validate([
            'dataset_id' => 'required|exists:datasets,id',
            'n_clusters' => 'required|integer|between:2,10',
            'm' => 'required|numeric|min:1.01|max:5',
            'tol' => 'required|numeric|min:0.0000001|max:0.1',
            'max_iter' => 'required|integer|between:1,1000',
            'k' => 'required|integer|between:1,50',
            'test_size' => 'required|numeric|between:0.1,0.5',
            'membership_weight' => 'required|numeric|between:0,10',
            'random_state' => 'required|integer',
        ], [
            'dataset_id.required' => 'Pilih dataset terlebih dahulu.',
            'dataset_id.exists' => 'Dataset tidak ditemukan.',
            'n_clusters.between' => 'Jumlah cluster harus antara 2 dan 10.',
            'm.min' => 'Fuzzifier m harus lebih dari 1 (minimal 1.01).',
            'm.max' => 'Fuzzifier m maksimal 5.',
            'tol.min' => 'Toleransi terlalu kecil (minimal 0.0000001).',
            'tol.max' => 'Toleransi maksimal 0.1.',
            'max_iter.between' => 'Iterasi maksimum harus antara 1 dan 1000.',
            'k.between' => 'Nilai k harus antara 1 dan 50.',
            'test_size.between' => 'Proporsi data uji harus antara 0.1 dan 0.5.',
            'membership_weight.between' => 'Bobot membership harus antara 0 dan 10.',
            '*.required' => 'Isian ini wajib diisi.',
            '*.integer' => 'Harus berupa bilangan bulat.',
            '*.numeric' => 'Harus berupa angka.',
        ]);

        $dataset = Dataset::findOrFail($data['dataset_id']);
        $fullPath = Storage::path($dataset->path);
        if (!is_file($fullPath)) {
            return back()->withInput()->withErrors(['dataset_id' => 'File dataset tidak ditemukan di server. Unggah ulang.']);
        }

        @set_time_limit(300); // training + silhouette dapat memakan beberapa detik
        $params = Arr::except($data, ['dataset_id']);

        try {
            $res = $api->train($fullPath, $dataset->name, $params);
        } catch (FuzzyApiException $e) {
            return back()->withInput()->withErrors(['api' => $e->getMessage()]);
        }

        $experiment = Experiment::create([
            'dataset_id' => $dataset->id,
            'model_id' => $res['model_id'],
            'n_clusters' => $res['params']['n_clusters'],
            'k' => $res['params']['k'],
            'accuracy' => $res['metrics_comb']['accuracy'],
            'f1_base' => $res['metrics_base']['f1'],
            'f1_comb' => $res['metrics_comb']['f1'],
            'silhouette' => $res['validity']['silhouette'],
            'params' => $res['params'],
            'result' => $res,
        ]);

        return redirect()->route('experiments.show', $experiment)
            ->with('success', 'Proses selesai. Berikut hasil segmentasi dan prediksi.');
    }

    /** /hasil dan /evaluasi tanpa id: arahkan ke eksperimen terbaru. */
    public function latest(string $tab)
    {
        $experiment = Experiment::latest()->first();
        if (!$experiment) {
            return redirect()->route('experiments.create')
                ->with('info', 'Belum ada hasil. Jalankan proses terlebih dahulu.');
        }

        return redirect()->route($tab === 'evaluasi' ? 'experiments.evaluation' : 'experiments.show', $experiment);
    }

    public function show(Experiment $experiment)
    {
        return view('experiments.show', ['exp' => $experiment->load('dataset'), 'r' => $experiment->result]);
    }

    public function evaluation(Experiment $experiment)
    {
        return view('experiments.evaluation', ['exp' => $experiment->load('dataset'), 'r' => $experiment->result]);
    }

    public function destroy(Experiment $experiment, FuzzyApi $api)
    {
        $api->deleteModel($experiment->model_id);
        $experiment->delete(); // prediksi terkait ikut terhapus (cascade)

        return redirect()->route('history')->with('success', 'Eksperimen dihapus.');
    }
}
