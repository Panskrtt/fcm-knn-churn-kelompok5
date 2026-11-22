<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Prediction extends Model
{
    protected $guarded = [];

    protected $casts = [
        'input' => 'array',
        'membership' => 'array',
        'pred' => 'boolean',
        'pred_base' => 'boolean',
        'proba_churn' => 'float',
    ];

    public function experiment()
    {
        return $this->belongsTo(Experiment::class);
    }
}
