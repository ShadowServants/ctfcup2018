<?php

$router->get('/', function () use ($router) {
    return [
        "version" => "1.0.0",
        "module" => "banking-core"
    ];
});

$router->post('/api/accounts', "AccountController@accounts");
$router->post('/api/accounts/create', "AccountController@create");
$router->post('/api/account/balance', "AccountController@balance");
$router->post('/api/account/change', "AccountController@change");
