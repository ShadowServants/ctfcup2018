<?php

namespace App\Http\Controllers;

use App\Models\FreeCoinDelay;
use App\Services\BankingService;
use Illuminate\Support\Facades\DB;

class FreeCoinController extends Controller
{
    public function receiveFreeCoin() {
        $service = app(BankingService::class);

        $account = request("account");

        $time_delay = request("time_delay");

        if($time_delay < 30 * 60) {
            $time_delay = 30 * 60; // Never less than thirty minutes!
        }

        $result = DB::transaction(function() use ($account, $time_delay) {
            $latest_block = FreeCoinDelay::where("account", $account)->first();
            if(is_null($latest_block)) {
                $this->provideFreeCoin($account);

                FreeCoinDelay::create([
                    "account" => $account,
                    "when_available" => intval(time() + $time_delay)
                ]);
                return true;
            } else {
                if(time() >= $latest_block->when_available) {
                    $this->provideFreeCoin($account);
                    $latest_block->when_available = intval(time() + $time_delay);
                    $latest_block->save();

                    return true;
                }

                return false;
            }
        });

        if($result) {
            return [
                "status" => "ok",
                "result" => $service->balance($account)
            ];
        }

        return [
            "status" => "bad",
            "reason" => "too_early"
        ];
    }

    private function provideFreeCoin($account) {
        $service = app(BankingService::class);
        $service->change($account, +1);
    }
}
