from django.core.cache import cache


def cache_decorator(func, timeout=None):
    def dec(f):
        def inner(*args, **kwargs):
            cache_key = func(*args, **kwargs)
            cached_result = cache.get(cache_key, None)
            if cached_result:
                return cached_result
            else:
                result = f(*args,**kwargs)
                cache.set(cache_key,result,timeout)
                return result
        return inner
    return dec
