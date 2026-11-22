<?php

namespace App\Http\Controllers;

use App\Models\Dataset;
use App\Models\Experiment;
use App\Models\Prediction;
use App\Services\FuzzyApi;

class HomeController extends Controller
{
    public function index(FuzzyApi $api)
    {
        return view('home', [
            'apiOk' => $api->health(),
            'nDatasets' => Dataset::count(),
            'nExperiments' => Experiment::count(),
            'nPredictions' => Prediction::count(),
            'latest' => Experiment::with('dataset')->latest()->first(),
        ]);
    }

    public function info()
    {
        return view('info');
    }
}
