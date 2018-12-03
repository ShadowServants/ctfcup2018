<?php

namespace App\Http\Controllers;

use App\Models\Account;

class AccountController extends Controller
{
    public function accounts() {
        return [
            "status" => "ok",
            Account::all()
        ];
    }

    public function create() {
        $this->validate(request(), [
            "account" => "string|alpha_num|min:1|max:30"
        ]);

        $account = request("account");

        if (Account::query()->where("uuid", $account)->exists())
            return [
                "status" => "bad",
                "reason" => "already_exists"
            ];

        return [
            "status" => "ok",
            "result" => Account::create([
                "uuid" => $account,
                "balance" => 0
            ])
        ];
    }

    public function balance() {
        $account = Account::query()->where("uuid", request("account"))->first();

        if(is_null($account)) {
            return [
                "status" => "bad",
                "reason" => "not_found"
            ];
        }

        return [
            "status" => "ok",
            "result" => optional($account)->balance ?? 0
        ];
    }

    public function change() {
        $account = Account::query()->where("uuid", request("account"))->first();

        if(is_null($account))
            return [
                "status" => "bad",
                "reason" => "not_found"
            ];

        $account->balance += floatval(request("change"));
        $account->save();

        return [
            "status" => "ok",
            "result" => $account->toArray()
        ];
    }
}
