<?php

namespace App\Http\Controllers;

use App\Services\BankingService;

class AccountsController extends Controller
{
    public function balance() {
        $this->validate(request(), [
            "account" => "string|required"
        ]);

        $balance = app(BankingService::class)->balance(request("account"));

        if($balance === false)
            return [
                "status" => "bad",
                "reason" => "account_not_found"
            ];

        return [
            "status" => "ok",
            "result" => $balance
        ];
    }

    public function register() {
        $this->validate(request(), [
            "account" => "string|required"
        ]);

        $result = app(BankingService::class)->register(request("account"));

        if($result === false) {
            return [
                "status" => "bad",
                "result" => "already_exists"
            ];
        }
        return [
            "status" => "ok"
        ];
    }
}
