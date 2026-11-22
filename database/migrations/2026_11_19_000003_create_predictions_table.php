<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('predictions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('experiment_id')->constrained()->cascadeOnDelete();
            $table->text('input');                      // data pelanggan yang diinput (JSON)
            $table->text('membership');                 // derajat keanggotaan (JSON)
            $table->unsignedTinyInteger('cluster');     // cluster dominan
            $table->boolean('pred');                    // prediksi FCM + KNN (1 = churn)
            $table->float('proba_churn');
            $table->boolean('pred_base');               // prediksi KNN baseline
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('predictions');
    }
};
