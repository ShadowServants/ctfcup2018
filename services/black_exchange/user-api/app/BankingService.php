<?php

namespace App\Services;

class BankingService
{
    public function __construct() {
        $this->client = new \GuzzleHttp\Client();
        $this->banking_url = env("BANKING_URL");
    }

    public function register($account) {
        $res = $this->client->post($this->banking_url . "/api/accounts/create", [
            "form_params" => [
                "account" => $account
            ]
        ]);

        if(json_decode($res->getBody()->getContents(), true)["status"] != "ok")
            return false;
        return true;
    }

    public function balance($account) {
        $res = json_decode($this->client->post($this->banking_url . "/api/account/balance", [
            "form_params" => [
                "account" => $account
            ]
        ])->getBody()->getContents(), true);

        $status = $res["status"];
        if($status == "ok")
            return $res["result"];

        return false;
    }

    public function change($account, $difference) {
        // We want to prevent it from being logged by Tax Service (in files like access.log)

        $res = json_decode($this->client->post($this->banking_url . "/api/account/change", [
            "form_params" => [
                "account" => $account
            ],
            "headers" => [
                "X-Account" => $account,
                "X-Change" => $difference
            ]
        ])->getBody()->getContents(), true);

        if($res["status"] == "ok")
            return true;
        return false;
    }
}