<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Experiment extends Model
{
    protected $guarded = [];

    protected $casts = [
        'params' => 'array',
        'result' => 'array',
    ];

    public function dataset()
    {
        return $this->belongsTo(Dataset::class);
    }

    public function predictions()
    {
        return $this->hasMany(Prediction::class);
    }
}
