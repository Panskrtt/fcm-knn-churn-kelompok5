<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('experiments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('dataset_id')->constrained()->cascadeOnDelete();
            $table->string('model_id', 32)->index();   // id model di API Python
            $table->unsignedTinyInteger('n_clusters');
            $table->unsignedSmallInteger('k');
            $table->float('accuracy');                  // FCM + KNN
            $table->float('f1_base');
            $table->float('f1_comb');
            $table->float('silhouette')->nullable();
            $table->text('params');                     // parameter (JSON)
            $table->longText('result');                 // seluruh keluaran API (JSON)
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('experiments');
    }
};
