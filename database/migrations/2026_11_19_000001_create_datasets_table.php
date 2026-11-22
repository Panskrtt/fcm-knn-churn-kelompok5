<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('datasets', function (Blueprint $table) {
            $table->id();
            $table->string('name');                  // nama file asli
            $table->string('path');                  // lokasi file di storage
            $table->unsignedInteger('n_rows');
            $table->unsignedSmallInteger('n_cols');
            $table->float('churn_rate');             // 0..1
            $table->longText('preview');             // 50 baris pertama (JSON)
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('datasets');
    }
};
