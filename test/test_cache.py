from async_api_fetcher.cache import save_cache, load_cache, delete_cache


def test_cache_save_and_load(tmp_path, monkeypatch):

    import async_api_fetcher.cache as cache

    monkeypatch.setattr(
        cache,
        "CACHE_DIR",
        tmp_path
    )

    data = {
        "name": "Sweden",
        "region": "Europe"
    }

    save_cache(
        key="country:Sweden",
        data=data,
        ttl=3600
    )

    result = load_cache("country:Sweden")

    assert result == data


def test_cache_miss(tmp_path, monkeypatch):

    import async_api_fetcher.cache as cache

    monkeypatch.setattr(
        cache,
        "CACHE_DIR",
        tmp_path
    )

    result = load_cache("country:India")

    assert result is None

def test_expired_cache(tmp_path, monkeypatch):

    import async_api_fetcher.cache as cache

    monkeypatch.setattr(
        cache,
        "CACHE_DIR",
        tmp_path
    )

    cache.save_cache(
        key="country:Sweden",
        data={"name": "Sweden"},
        ttl=0
    )

    result = cache.load_cache("country:Sweden")

    assert result is None

def test_cache_delete(tmp_path, monkeypatch):

    monkeypatch.setattr(
        "async_api_fetcher.cache.CACHE_DIR",
        tmp_path
    )

    save_cache(
        "user:1",
        {"name": "Ervin"},
        ttl=3600
    )

    delete_cache("user:1")

    assert load_cache("user:1") is None

def test_delete_nonexistent_cache(tmp_path, monkeypatch):

    monkeypatch.setattr(
        "async_api_fetcher.cache.CACHE_DIR",
        tmp_path
    )

    delete_cache("user:999")

    assert load_cache("user:999") is None