<?php

function request($key=null) {
    if (is_null($key))
        return app("request");

    return app("request")->get($key, null) ?? app("request")->header("X-" . camel_case($key));
}
