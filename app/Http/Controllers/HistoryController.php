<?php

namespace App\Http\Controllers;

use App\Models\Experiment;
use App\Models\Prediction;

class HistoryController extends Controller
{
    public function index()
    {
        return view('history', [
            'experiments' => Experiment::with('dataset')->latest()->take(50)->get(),
            'predictions' => Prediction::with('experiment.dataset')->latest()->take(50)->get(),
        ]);
    }
}
