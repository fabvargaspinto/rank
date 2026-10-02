from api.dependencies import auth, supabase


def test_auth_jwt_settings_are_cached(monkeypatch):
    auth.get_auth_jwt_settings.cache_clear()
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "secret")

    first = auth.get_auth_jwt_settings()
    second = auth.get_auth_jwt_settings()

    assert first is second
    assert first.issuer == "https://example.supabase.co/auth/v1"
    auth.get_auth_jwt_settings.cache_clear()


def test_supabase_url_is_cached(monkeypatch):
    supabase.get_supabase_url.cache_clear()
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co/")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "secret")

    first = supabase.get_supabase_url()
    second = supabase.get_supabase_url()

    assert first is second
    assert first == "https://example.supabase.co"
    supabase.get_supabase_url.cache_clear()
