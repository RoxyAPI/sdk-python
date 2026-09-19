"""The generated surface mirrors the committed spec, and the client sends what the API expects.

Offline. The HTTP layer is stubbed at Client.send and AsyncClient.send, so every request is
seen exactly as it would leave the process: base URL merged, headers merged, body encoded.
"""

from __future__ import annotations

import inspect
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import httpx
import pytest

import roxy_sdk
from codegen import ROOT, camel_to_snake, domains, load_spec
from roxy_sdk import Roxy, RoxyAPIError, __version__, create_roxy

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
        create_roxy("test-key").usage.get_usage_stats()
    assert (raised.value.status_code, raised.value.code, raised.value.error) == (
        502,
        "unknown",
        "Bad Gateway",
    )


def test_an_empty_key_is_rejected_before_any_request() -> None:
    with pytest.raises(ValueError, match="API key is required"):
        create_roxy("")
