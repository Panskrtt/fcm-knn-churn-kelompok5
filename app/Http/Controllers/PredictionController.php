<?php

namespace App\Http\Controllers;

use App\Exceptions\FuzzyApiException;
use App\Models\Experiment;
use App\Models\Prediction;
use App\Services\FuzzyApi;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class PredictionController extends Controller
{
    public function create(Request $request)
    {
        $experiments = Experiment::with('dataset')->latest()->get();
        $selected = $experiments->firstWhere('id', (int) $request->query('experiment')) ?? $experiments->first();
        $history = $selected ? $selected->predictions()->latest()->take(10)->get() : collect();

        return view('predictions.create', compact('experiments', 'selected', 'history'));
    }

    public function store(Request $request, FuzzyApi $api)
    {
        $opt = config('fuzzy.options');
        $data = $request->validate([
            'experiment_id' => 'required|exists:experiments,id',
            'tenure' => 'required|integer|between:0,120',
            'MonthlyCharges' => 'required|numeric|min:0.01|max:1000',
            'TotalCharges' => 'nullable|numeric|min:0',
            'SeniorCitizen' => ['required', Rule::in($opt['SeniorCitizen'])],
            'Contract' => ['required', Rule::in($opt['Contract'])],
            'InternetService' => ['required', Rule::in($opt['InternetService'])],
            'PaymentMethod' => ['required', Rule::in($opt['PaymentMethod'])],
            'PaperlessBilling' => ['required', Rule::in($opt['PaperlessBilling'])],
            'TechSupport' => ['required', Rule::in($opt['TechSupport'])],
            'OnlineSecurity' => ['required', Rule::in($opt['OnlineSecurity'])],
        ], [
            'experiment_id.required' => 'Pilih model (eksperimen) terlebih dahulu.',
            'tenure.between' => 'Lama berlangganan harus 0-120 bulan.',
            'tenure.integer' => 'Lama berlangganan harus bilangan bulat.',
            'MonthlyCharges.min' => 'Tagihan bulanan harus lebih dari 0.',
            'MonthlyCharges.max' => 'Tagihan bulanan maksimal 1000.',
            'TotalCharges.min' => 'Total tagihan tidak boleh negatif.',
            '*.required' => 'Isian ini wajib diisi.',
            '*.numeric' => 'Harus berupa angka.',
            '*.in' => 'Pilihan tidak valid.',
        ]);

        $experiment = Experiment::findOrFail($data['experiment_id']);

        $values = collect($data)->except('experiment_id')->all();
        $values['tenure'] = (int) $values['tenure'];
        $values['MonthlyCharges'] = (float) $values['MonthlyCharges'];
        $values['TotalCharges'] = ($values['TotalCharges'] ?? '') === '' || $values['TotalCharges'] === null
            ? $values['tenure'] * $values['MonthlyCharges']
            : (float) $values['TotalCharges'];
        $values['SeniorCitizen'] = (int) $values['SeniorCitizen'];

        try {
            $out = $api->predict($experiment->model_id, $values);
        } catch (FuzzyApiException $e) {
            return back()->withInput()->withErrors(['api' => $e->getMessage()]);
        }

        Prediction::create([
            'experiment_id' => $experiment->id,
            'input' => $values,
            'membership' => $out['membership'],
            'cluster' => $out['cluster'],
            'pred' => (bool) $out['pred'],
            'proba_churn' => $out['proba_churn'],
            'pred_base' => (bool) $out['pred_base'],
        ]);

        return redirect()->route('predictions.create', ['experiment' => $experiment->id])
            ->withInput()
            ->with('result', $out);
    }
}
