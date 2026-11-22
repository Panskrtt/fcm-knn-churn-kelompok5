<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Dataset extends Model
{
    protected $guarded = [];

    protected $casts = [
        'preview' => 'array',
        'churn_rate' => 'float',
    ];

    public function experiments()
    {
        return $this->hasMany(Experiment::class);
    }
}
