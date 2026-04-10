"""Unit tests for the SDK factory wrapper."""

import inspect

import pytest

from roxy_sdk import Roxy, RoxyAPIError, create_roxy


def test_create_roxy_returns_roxy_instance():
    roxy = create_roxy("test-key")
    assert isinstance(roxy, Roxy)
    roxy.close()


def test_roxy_has_all_domains():
    roxy = create_roxy("test-key")
    for domain in [
        "astrology",
        "vedic_astrology",
        "tarot",
        "numerology",
        "iching",
        "crystals",
        "angel_numbers",
        "dreams",
        "location",
        "usage",
    ]:
        assert hasattr(roxy, domain), f"Missing domain: {domain}"
    roxy.close()


def test_sdk_header_is_set():
    roxy = create_roxy("test-key")
    headers = dict(roxy._client.headers)
    assert "x-sdk-client" in headers
    assert headers["x-sdk-client"].startswith("roxy-sdk-python/")
    roxy.close()


def test_api_key_header_is_set():
    roxy = create_roxy("my-secret-key")
    headers = dict(roxy._client.headers)
    assert headers["x-api-key"] == "my-secret-key"
    roxy.close()


def test_empty_api_key_raises():
    with pytest.raises(ValueError, match="API key is required"):
        create_roxy("")


def test_custom_base_url():
    roxy = create_roxy("test-key", base_url="http://localhost:3000/api/v2")
    assert "localhost:3000/api/v2" in str(roxy._client.base_url)
    roxy.close()


def test_context_manager():
    with create_roxy("test-key") as roxy:
        assert isinstance(roxy, Roxy)


def test_repr():
    roxy = create_roxy("test-key")
    assert "roxyapi.com" in repr(roxy)
    roxy.close()


def test_roxy_api_error_attributes():
    err = RoxyAPIError(error="Bad request", code="validation_error", status_code=400)
    assert err.error == "Bad request"
    assert err.code == "validation_error"
    assert err.status_code == 400
    assert "validation_error" in str(err)


def test_version_exported():
    import roxy_sdk

    assert hasattr(roxy_sdk, "__version__")
    assert isinstance(roxy_sdk.__version__, str)


def test_async_methods_exist():
    roxy = create_roxy("test-key")
    assert inspect.iscoroutinefunction(roxy.astrology.get_daily_horoscope_async)
    assert inspect.iscoroutinefunction(roxy.tarot.draw_cards_async)
    assert inspect.iscoroutinefunction(roxy.numerology.calculate_life_path_async)
    assert inspect.iscoroutinefunction(roxy.iching.cast_reading_async)
    assert inspect.iscoroutinefunction(roxy.crystals.list_crystals_async)
    assert inspect.iscoroutinefunction(roxy.angel_numbers.list_angel_numbers_async)
    assert inspect.iscoroutinefunction(roxy.dreams.search_dream_symbols_async)
    assert inspect.iscoroutinefunction(roxy.location.search_cities_async)
    assert inspect.iscoroutinefunction(roxy.usage.get_usage_stats_async)
    roxy.close()


def test_sync_methods_are_not_coroutines():
    roxy = create_roxy("test-key")
    assert not inspect.iscoroutinefunction(roxy.astrology.get_daily_horoscope)
    assert not inspect.iscoroutinefunction(roxy.tarot.draw_cards)
    assert not inspect.iscoroutinefunction(roxy.numerology.calculate_life_path)
    roxy.close()


def test_domain_method_count():
    roxy = create_roxy("test-key")
    mins = {
        "astrology": 20,
        "vedic_astrology": 30,
        "tarot": 8,
        "numerology": 10,
        "iching": 7,
        "crystals": 10,
        "angel_numbers": 3,
        "dreams": 4,
        "location": 2,
        "usage": 1,
    }
    for domain_name, min_count in mins.items():
        domain = getattr(roxy, domain_name)
        methods = [
            m
            for m in dir(domain)
            if not m.startswith("_") and not m.endswith("_async") and callable(getattr(domain, m))
        ]
        assert len(methods) >= min_count, (
            f"{domain_name} has {len(methods)}, expected >= {min_count}"
        )
    roxy.close()
