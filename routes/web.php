<?php

use App\Http\Controllers\DatasetController;
use App\Http\Controllers\ExperimentController;
use App\Http\Controllers\HistoryController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\PredictionController;
use Illuminate\Support\Facades\Route;

Route::get('/', [HomeController::class, 'index'])->name('home');
Route::get('/info', [HomeController::class, 'info'])->name('info');

// Input Data
Route::get('/data', [DatasetController::class, 'index'])->name('datasets.index');
Route::post('/data', [DatasetController::class, 'store'])->name('datasets.store');
Route::delete('/data/{dataset}', [DatasetController::class, 'destroy'])->name('datasets.destroy');

// Proses, Hasil, Evaluasi
Route::get('/proses', [ExperimentController::class, 'create'])->name('experiments.create');
Route::post('/proses', [ExperimentController::class, 'store'])->name('experiments.store');
Route::get('/hasil', [ExperimentController::class, 'latest'])->defaults('tab', 'hasil')->name('results.latest');
Route::get('/evaluasi', [ExperimentController::class, 'latest'])->defaults('tab', 'evaluasi')->name('evaluation.latest');
Route::get('/hasil/{experiment}', [ExperimentController::class, 'show'])->name('experiments.show');
Route::get('/evaluasi/{experiment}', [ExperimentController::class, 'evaluation'])->name('experiments.evaluation');
Route::delete('/eksperimen/{experiment}', [ExperimentController::class, 'destroy'])->name('experiments.destroy');

// Prediksi manual + riwayat
Route::get('/prediksi', [PredictionController::class, 'create'])->name('predictions.create');
Route::post('/prediksi', [PredictionController::class, 'store'])->name('predictions.store');
Route::get('/riwayat', [HistoryController::class, 'index'])->name('history');
