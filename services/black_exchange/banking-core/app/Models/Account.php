<?php
/**
 * Created by PhpStorm.
 * User: satt
 * Date: 01/12/2018
 * Time: 00:09
 */

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Account extends Model
{
    protected $guarded = [];
    protected $casts = ["balance" => "float"];
}