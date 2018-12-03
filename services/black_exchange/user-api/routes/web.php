<?php

$router->get('/', function () use ($router) {
    return [
        "version" => "1.0.0",
        "module" => "exchange-user-api"
    ];
});

$router->get('/placed_secrets', "SecretsController@getPlacedSecrets");
$router->get('/my_secrets', "SecretsController@getMySecrets");
$router->post('/place_secret', "SecretsController@placeSecret");
$router->post('/buy_secret', "SecretsController@buySecret");

$router->post('/free_coin', "FreeCoinController@receiveFreeCoin");

$router->post("/register", "AccountsController@register");
$router->get("/balance", "AccountsController@balance");
