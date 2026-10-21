"""The generated surface mirrors the committed spec, and the client sends what the API expects.

Offline. The HTTP layer is stubbed at Client.send and AsyncClient.send, so every request is
seen exactly as it would leave the process: base URL merged, headers merged, body encoded.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import random
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import httpx
import pytest

import roxy_sdk
from codegen import ROOT, camel_to_snake, domains, load_spec
from roxy_sdk import Roxy, RoxyAPIError, __version__, create_roxy, factory

DOMAINS = domains(load_spec())
OPERATIONS = [(domain, op) for domain in DOMAINS for op in domain.operations]


def spec_kwargs(op: dict[str, Any]) -> list[str]:
    """The keyword arguments the generator owes an operation: path params, body properties,
    query params, with `lang` last."""
    params = op["parameters"]
    names = [p["name"] for p in params if p["in"] == "path"]
    names += list(op["body_properties"])
    names += [p["name"] for p in params if p["in"] == "query" and p["name"] != "lang"]
    if any(p["name"] == "lang" for p in params):
        names.append("lang")
    return [camel_to_snake(n) for n in names]


def test_every_operation_is_a_method_on_the_namespace_of_its_path() -> None:
    assert len(OPERATIONS) > 200
    roxy = Roxy("test-key")
    assert {a for a in vars(roxy) if not a.startswith("_")} == {d.attr for d in DOMAINS}
    for domain, op in OPERATIONS:
        name = camel_to_snake(op["operationId"])
        namespace = getattr(roxy, domain.attr)
        sync = getattr(namespace, name, None)
        asynchronous = getattr(namespace, f"{name}_async", None)
        assert callable(sync) and not inspect.iscoroutinefunction(sync), f"{domain.attr}.{name}"
        assert inspect.iscoroutinefunction(asynchronous), f"{domain.attr}.{name}_async"


def test_every_method_takes_exactly_the_kwargs_of_its_operation() -> None:
    roxy = Roxy("test-key")
    for domain, op in OPERATIONS:
        name = camel_to_snake(op["operationId"])
        for suffix in ("", "_async"):
            method = getattr(getattr(roxy, domain.attr), name + suffix)
            params = inspect.signature(method).parameters.values()
            assert all(p.kind is p.KEYWORD_ONLY for p in params), f"roxy.{domain.attr}.{name}"
            assert [p.name for p in params] == spec_kwargs(op), f"roxy.{domain.attr}.{name}"


def test_version_is_one_value() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text()
    match = re.search(r'^version = "(.+?)"', pyproject, re.M)
    assert match and match.group(1) == __version__


def test_agent_guide_ships_inside_the_package() -> None:
    packaged = ROOT / "src" / "roxy_sdk" / "AGENTS.md"
    assert packaged.read_text() == (ROOT / "AGENTS.md").read_text()
    assert packaged.parent.samefile(ROOT / "src" / roxy_sdk.__name__)


@dataclass
class Recorder:
    """Stands in for the network: records every request and answers with the queued response."""

    response: httpx.Response
    requests: list[httpx.Request] = field(default_factory=list)

    def answer(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        self.response.request = request
        return self.response


@pytest.fixture
def stub(monkeypatch: pytest.MonkeyPatch) -> Callable[[httpx.Response], Recorder]:
    def install(response: httpx.Response) -> Recorder:
        recorder = Recorder(response)

        def send(self: httpx.Client, request: httpx.Request, **kw: Any) -> httpx.Response:
            return recorder.answer(request)

        async def send_async(
            self: httpx.AsyncClient, request: httpx.Request, **kw: Any
        ) -> httpx.Response:
            return recorder.answer(request)

        monkeypatch.setattr(httpx.Client, "send", send)
        monkeypatch.setattr(httpx.AsyncClient, "send", send_async)
        return recorder

    return install


def test_get_sends_the_key_and_sdk_headers_to_the_production_base_url(
    stub: Callable[[httpx.Response], Recorder],
) -> None:
    recorder = stub(httpx.Response(200, json={"sign": "Aries"}))
    with create_roxy("test-key") as roxy:
        result = roxy.astrology.get_daily_horoscope(sign="aries", lang="es")
    assert result == {"sign": "Aries"}
    (request,) = recorder.requests
    assert request.method == "GET"
    assert str(request.url) == "https://roxyapi.com/api/v2/astrology/horoscope/aries/daily?lang=es"
    assert request.headers["X-API-Key"] == "test-key"
    assert request.headers["X-SDK-Client"] == f"roxy-sdk-python/{__version__}"
    assert request.headers["Accept"] == "application/json"
    assert roxy._client.is_closed


async def test_post_sends_only_the_given_kwargs_as_json(
    stub: Callable[[httpx.Response], Recorder],
) -> None:
    recorder = stub(httpx.Response(200, json={"card": {"name": "The Fool"}}))
    async with create_roxy("test-key", base_url="http://localhost:3000/api/v2") as roxy:
        result = await roxy.tarot.get_daily_card_async(seed="user-42")
    assert result["card"]["name"] == "The Fool"
    (request,) = recorder.requests
    assert request.method == "POST"
    assert str(request.url) == "http://localhost:3000/api/v2/tarot/daily"
    assert request.headers["Content-Type"] == "application/json"
    assert request.headers["X-SDK-Client"] == f"roxy-sdk-python/{__version__}"
    assert json.loads(request.content) == {"seed": "user-42"}
    assert roxy._async_client.is_closed


def test_an_api_error_raises_with_the_stable_code(
    stub: Callable[[httpx.Response], Recorder],
) -> None:
    stub(httpx.Response(401, json={"error": "API key required", "code": "api_key_required"}))
    with pytest.raises(RoxyAPIError) as raised:
        create_roxy("test-key").usage.get_usage_stats()
    assert raised.value.status_code == 401
    assert raised.value.code == "api_key_required"
    assert raised.value.error == "API key required"
    assert "api_key_required" in str(raised.value)


def test_a_non_json_error_body_still_raises(stub: Callable[[httpx.Response], Recorder]) -> None:
    stub(httpx.Response(502, text="Bad Gateway"))
    with pytest.raises(RoxyAPIError) as raised:
        create_roxy("test-key", max_retries=0).usage.get_usage_stats()
    assert (raised.value.status_code, raised.value.code, raised.value.error) == (
        502,
        "unknown",
        "Bad Gateway",
    )


def test_an_empty_key_is_rejected_before_any_request() -> None:
    with pytest.raises(ValueError, match="API key is required"):
        create_roxy("")


def test_readme_and_agents_error_tables_list_exactly_the_spec_codes() -> None:
    spec_codes = [c["code"] for c in load_spec()["info"]["x-error-codes"]]
    for name in ("README.md", "AGENTS.md"):
        text = (ROOT / name).read_text()
        region = text.split("<!-- BEGIN:ERRORS -->")[1].split("<!-- END:ERRORS -->")[0]
        assert re.findall(r"^\| \S+ \| `([^`]+)` \|", region, re.M) == spec_codes


def test_error_exposes_doc_url_and_retry_after_from_the_response(
    stub: Callable[[httpx.Response], Recorder],
) -> None:
    body = {"error": "Slow down", "code": "rate_limit_per_minute", "doc_url": "https://x/e"}
    stub(httpx.Response(429, json=body, headers={"Retry-After": "7"}))
    with pytest.raises(RoxyAPIError) as raised:
        create_roxy("test-key", max_retries=0).usage.get_usage_stats()
    assert (raised.value.doc_url, raised.value.retry_after) == ("https://x/e", 7.0)


def test_retry_after_accepts_an_http_date() -> None:
    from datetime import datetime, timedelta, timezone
    from email.utils import format_datetime

    when = datetime.now(timezone.utc) + timedelta(seconds=60)
    parsed = factory._parse_retry_after(format_datetime(when, usegmt=True))
    assert parsed is not None and 55 <= parsed <= 60
    assert factory._parse_retry_after("garbage") is None
    assert factory._parse_retry_after(None) is None


def test_error_constructor_stays_backwards_compatible() -> None:
    err = RoxyAPIError("m", "c", 400)
    assert (err.doc_url, err.retry_after) == (None, None)


class Script:
    """Answers the queued responses in order and records the sleeps and request count."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, *responses: httpx.Response | Exception):
        self.queue = list(responses)
        self.sleeps: list[float] = []
        self.calls = 0
        self.requests: list[httpx.Request] = []

        def send(client: httpx.Client, request: httpx.Request, **kw: Any) -> httpx.Response:
            return self.next(request)

        async def send_async(
            client: httpx.AsyncClient, request: httpx.Request, **kw: Any
        ) -> httpx.Response:
            return self.next(request)

        async def sleep_async(seconds: float) -> None:
            self.sleeps.append(seconds)

        monkeypatch.setattr(httpx.Client, "send", send)
        monkeypatch.setattr(httpx.AsyncClient, "send", send_async)
        monkeypatch.setattr(time, "sleep", self.sleeps.append)
        monkeypatch.setattr(asyncio, "sleep", sleep_async)
        monkeypatch.setattr(random, "uniform", lambda lo, hi: hi)

    def next(self, request: httpx.Request) -> httpx.Response:
        self.calls += 1
        self.requests.append(request)
        item = self.queue.pop(0)
        if isinstance(item, Exception):
            raise item
        item.request = request
        return item


def limited(code: str, status: int = 429, retry_after: str | None = None) -> httpx.Response:
    headers = {"Retry-After": retry_after} if retry_after else {}
    return httpx.Response(status, json={"error": "e", "code": code}, headers=headers)


OK = {"ok": True}


def test_default_config_retries_twice(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, *[limited("compute_saturated", 503)] * 3)
    with pytest.raises(RoxyAPIError):
        create_roxy("k").usage.get_usage_stats()
    assert (script.calls, script.sleeps) == (3, [0.5, 1.0])


async def test_async_default_config_retries_twice(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, *[limited("compute_saturated", 503)] * 3)
    with pytest.raises(RoxyAPIError):
        await create_roxy("k").usage.get_usage_stats_async()
    assert (script.calls, script.sleeps) == (3, [0.5, 1.0])


def test_zero_max_retries_never_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, limited("rate_limit_per_minute", retry_after="1"))
    with pytest.raises(RoxyAPIError):
        create_roxy("k", max_retries=0).usage.get_usage_stats()
    assert (script.calls, script.sleeps) == (1, [])


async def test_async_zero_max_retries_never_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, limited("internal_error", 500))
    with pytest.raises(RoxyAPIError):
        await create_roxy("k", max_retries=0).usage.get_usage_stats_async()
    assert (script.calls, script.sleeps) == (1, [])


def test_429_with_retry_after_retries_once_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(
        monkeypatch,
        limited("rate_limit_per_minute", retry_after="1"),
        httpx.Response(200, json=OK),
    )
    assert create_roxy("k", max_retries=2).usage.get_usage_stats() == OK
    # Retry-After 1 plus uniform(0, initial_delay), pinned to its upper bound.
    assert script.calls == 2 and script.sleeps == [1.5]


async def test_async_429_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(
        monkeypatch, limited("rate_limit_per_minute", retry_after="1"), httpx.Response(200, json=OK)
    )
    assert await create_roxy("k", max_retries=2).usage.get_usage_stats_async() == OK
    assert script.calls == 2 and script.sleeps == [1.5]


def test_retry_after_beyond_max_delay_is_surfaced_not_waited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    script = Script(monkeypatch, limited("rate_limit_exceeded", retry_after="86400"))
    with pytest.raises(RoxyAPIError) as raised:
        create_roxy("k", max_retries=3).usage.get_usage_stats()
    assert (script.calls, script.sleeps) == (1, [])
    assert (raised.value.code, raised.value.retry_after) == ("rate_limit_exceeded", 86400.0)


def test_503_without_retry_after_uses_full_jitter_backoff(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(
        monkeypatch,
        limited("compute_saturated", 503),
        limited("compute_saturated", 503),
        httpx.Response(200, json=OK),
    )
    assert create_roxy("k", max_retries=3).usage.get_usage_stats() == OK
    # uniform pinned to its upper bound: min(30, 0.5 * 2**attempt)
    assert script.sleeps == [0.5, 1.0]


def test_backoff_is_capped_at_max_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, *[limited("compute_saturated", 503)] * 4)
    with pytest.raises(RoxyAPIError):
        create_roxy("k", max_retries=3, initial_delay=10, max_delay=15).usage.get_usage_stats()
    assert script.sleeps == [10, 15, 15]


def test_500_is_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, limited("internal_error", 500), httpx.Response(200, json=OK))
    assert create_roxy("k").usage.get_usage_stats() == OK
    assert (script.calls, script.sleeps) == (2, [0.5])


async def test_async_500_is_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, limited("internal_error", 500), httpx.Response(200, json=OK))
    assert await create_roxy("k").usage.get_usage_stats_async() == OK
    assert (script.calls, script.sleeps) == (2, [0.5])


def test_a_client_error_is_not_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, limited("validation_error", 400))
    with pytest.raises(RoxyAPIError):
        create_roxy("k").usage.get_usage_stats()
    assert (script.calls, script.sleeps) == (1, [])


@pytest.mark.parametrize("failure", [httpx.ConnectError("refused"), httpx.ConnectTimeout("dial")])
def test_a_never_established_connection_is_retried(
    monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    script = Script(monkeypatch, failure, httpx.Response(200, json=OK))
    assert create_roxy("k", max_retries=1).usage.get_usage_stats() == OK
    assert script.calls == 2


@pytest.mark.parametrize(
    "failure",
    [httpx.ReadTimeout("x"), httpx.WriteTimeout("x"), httpx.PoolTimeout("x")],
)
def test_timeouts_after_the_connection_are_not_retried(
    monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    script = Script(monkeypatch, failure)
    with pytest.raises(type(failure)):
        create_roxy("k", max_retries=3).usage.get_usage_stats()
    assert script.calls == 1


async def test_async_connect_timeout_is_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, httpx.ConnectTimeout("dial"), httpx.Response(200, json=OK))
    assert await create_roxy("k", max_retries=1).usage.get_usage_stats_async() == OK
    assert script.calls == 2


def test_a_retry_never_sleeps_past_the_client_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, limited("rate_limit_per_minute", retry_after="20"))
    with pytest.raises(RoxyAPIError):
        create_roxy("k", max_retries=3, timeout=5).usage.get_usage_stats()
    assert (script.calls, script.sleeps) == (1, [])


def test_a_post_body_is_replayed_on_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    script = Script(monkeypatch, limited("compute_saturated", 503), httpx.Response(200, json=OK))
    create_roxy("k", max_retries=1).tarot.get_daily_card(seed="user-42")
    first, second = script.requests
    assert first.content == second.content == b'{"seed":"user-42"}'


def test_negative_max_retries_is_rejected() -> None:
    with pytest.raises(ValueError, match="max_retries"):
        create_roxy("k", max_retries=-1)


def test_error_code_members_equal_the_spec_codes() -> None:
    spec_codes = [c["code"] for c in load_spec()["info"]["x-error-codes"]]
    assert [m.value for m in roxy_sdk.ErrorCode] == spec_codes
    assert all(m.name == m.value.upper() for m in roxy_sdk.ErrorCode)
    wire: str = "rate_limit_per_minute"
    assert roxy_sdk.ErrorCode.RATE_LIMIT_PER_MINUTE == wire
    assert str(roxy_sdk.ErrorCode.COMPUTE_SATURATED) == "compute_saturated"


def test_a_caught_error_code_compares_with_the_enum(
    stub: Callable[[httpx.Response], Recorder],
) -> None:
    stub(httpx.Response(429, json={"error": "e", "code": "rate_limit_per_minute"}))
    with pytest.raises(RoxyAPIError) as raised:
        create_roxy("k", max_retries=0).usage.get_usage_stats()
    assert raised.value.code == roxy_sdk.ErrorCode.RATE_LIMIT_PER_MINUTE


def test_validation_error_exposes_issues(stub: Callable[[httpx.Response], Recorder]) -> None:
    issues = [{"path": "time", "message": "Required", "code": "invalid_type"}]
    stub(httpx.Response(400, json={"error": "bad", "code": "validation_error", "issues": issues}))
    with pytest.raises(RoxyAPIError) as raised:
        create_roxy("k", max_retries=0).usage.get_usage_stats()
    assert raised.value.issues == issues


def test_issues_is_none_when_the_body_has_none() -> None:
    assert RoxyAPIError("m", "c", 400).issues is None
