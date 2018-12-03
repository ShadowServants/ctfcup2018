<?php

namespace App\Models;

class Secret extends \Illuminate\Database\Eloquent\Model
{
    protected $guarded = [];

    protected $hidden = ["secret", "owner_account"];
}