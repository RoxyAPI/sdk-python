# roxy-sdk

[![PyPI](https://img.shields.io/pypi/v/roxy-sdk)](https://pypi.org/project/roxy-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/roxy-sdk)](https://pypi.org/project/roxy-sdk/)
[![Docs](https://img.shields.io/badge/docs-roxyapi.com-blue)](https://roxyapi.com/docs)
[![API Reference](https://img.shields.io/badge/api%20reference-roxyapi.com-blue)](https://roxyapi.com/api-reference)
[![License](https://img.shields.io/github/license/RoxyAPI/sdk-python)](https://github.com/RoxyAPI/sdk-python/blob/main/LICENSE)

Python SDK for [RoxyAPI](https://roxyapi.com). Natal charts, Vedic kundli, numerology, tarot, biorhythm, I Ching, crystals, dreams, and angel numbers. Eleven domains, one API key, sync and async.

Build astrology apps, kundli matching, tarot platforms, compatibility tools, and daily-horoscope features without writing a single calculation.

## Install

```bash
pip install roxy-sdk
```

## Quickstart

```python
from roxy_sdk import create_roxy

roxy = create_roxy("your-api-key")

# Step 1: geocode the birth city (required for any chart endpoint)
cities = roxy.location.search_cities(q="Mumbai, India")
lat, lng = cities[0]["latitude"], cities[0]["longitude"]

# Step 2: Vedic kundli
kundli = roxy.vedic_astrology.generate_birth_chart(
    date="1990-01-15",
    time="14:30:00",
    latitude=lat,
    longitude=lng,
)

# Or Western natal chart (timezone required, decimal hours)
natal = roxy.astrology.generate_natal_chart(
    date="1990-01-15",
    time="14:30:00",
    latitude=lat,
    longitude=lng,
    timezone=5.5,
)
```

Get your API key at [roxyapi.com/pricing](https://roxyapi.com/pricing). Free test keys available on the [interactive docs](https://roxyapi.com/api-reference).

## Location first

Every chart, horoscope, panchang, dasha, dosha, navamsa, KP, synastry, compatibility, and natal endpoint needs `latitude`, `longitude`, and (for Western) `timezone`. **Never ask users to type coordinates.** Always call `roxy.location.search_cities(q=city)` first and feed the result into the chart call.

```python
cities = roxy.location.search_cities(q="Tokyo")
lat, lng, tz = cities[0]["latitude"], cities[0]["longitude"], cities[0]["timezone"]
```

## Domain reference

| Domain | Property | What it covers |
|--------|----------|----------------|
| Western Astrology | `roxy.astrology` | Natal charts, daily / weekly / monthly horoscopes, synastry, compatibility score, transits, moon phases |
| Vedic Astrology | `roxy.vedic_astrology` | Kundli, panchang, Vimshottari dasha, nakshatras, Mangal / Kaal Sarp / Sade Sati doshas, Guna Milan, navamsa, KP chart and ruling planets |
| Numerology | `roxy.numerology` | Life path, expression, soul urge, personal year, full chart, compatibility, karmic lessons |
| Tarot | `roxy.tarot` | Daily card, custom draws, three-card, Celtic Cross, yes / no, love spread, 78-card catalog |
| Biorhythm | `roxy.biorhythm` | Daily check-in, multi-day forecast, critical days, couples compatibility, phases |
| I Ching | `roxy.iching` | Daily hexagram, three-coin cast, 64 hexagrams, trigrams |
| Crystals | `roxy.crystals` | By zodiac, by chakra, birthstone, search, daily, pairings |
| Dreams | `roxy.dreams` | Dream symbol dictionary (3,000+ interpretations), daily prompt |
| Angel Numbers | `roxy.angel_numbers` | Number meanings, universal digit-root lookup, daily |
| Location | `roxy.location` | City search with coordinates and timezone, countries |
| Usage | `roxy.usage` | API usage stats and subscription info |

## Recipes

### Daily horoscope (wellness, news, lifestyle apps)

```python
horoscope = roxy.astrology.get_daily_horoscope(sign="aries")
# horoscope["overview"], horoscope["love"], horoscope["career"], ...
```

### Vedic kundli (India market, matrimonial, muhurat)

```python
cities = roxy.location.search_cities(q="Delhi")
lat, lng = cities[0]["latitude"], cities[0]["longitude"]

kundli = roxy.vedic_astrology.generate_birth_chart(
    date="1990-01-15", time="14:30:00", latitude=lat, longitude=lng,
)
```

### Panchang (daily almanac, ritual planner)

```python
panchang = roxy.vedic_astrology.get_detailed_panchang(
    date="2026-04-22", latitude=28.6139, longitude=77.209,
)
# panchang["tithi"], panchang["nakshatra"], panchang["rahuKaal"], ...
```

### Guna Milan (matrimonial matching)

```python
person1 = {"date": "1990-01-15", "time": "14:30:00", "latitude": 28.61, "longitude": 77.20}
person2 = {"date": "1992-07-22", "time": "09:00:00", "latitude": 19.07, "longitude": 72.87}

score = roxy.vedic_astrology.calculate_gun_milan(person1=person1, person2=person2)
# score["total"], score["maxScore"] (36), score["isCompatible"], score["breakdown"]
```

### Numerology life path (numerology calculators)

```python
result = roxy.numerology.calculate_life_path(year=1990, month=1, day=15)

chart = roxy.numerology.generate_numerology_chart(
    full_name="Jane Smith", year=1990, month=1, day=15,
)
```

### Tarot Celtic Cross (premium-tier tarot feature)

```python
reading = roxy.tarot.cast_celtic_cross(question="What should I focus on?")
# reading["positions"][10], reading["reading"]
```

### Daily biorhythm (wellness, productivity, sports apps)

```python
biorhythm = roxy.biorhythm.get_daily_biorhythm(seed="user-123")
```

### I Ching cast (decision-making, meditation)

```python
reading = roxy.iching.cast_reading()
```

### Crystal healing (retail, wellness)

```python
crystals = roxy.crystals.get_crystals_by_zodiac(sign="scorpio")
```

### Dream symbol lookup (journaling, self-discovery)

```python
symbol = roxy.dreams.get_dream_symbol(id="flying")
```

### Angel number meaning (viral content, spiritual apps)

```python
meaning = roxy.angel_numbers.get_angel_number(number="1111")
```

## Async support

Every method has an `_async` suffix variant for use with asyncio:

```python
import asyncio
from roxy_sdk import create_roxy

async def main():
    roxy = create_roxy("your-api-key")
    horoscope = await roxy.astrology.get_daily_horoscope_async(sign="aries")
    card = await roxy.tarot.get_daily_card_async()
    print(horoscope, card)

asyncio.run(main())
```

## Multi-language responses

Interpretations and editorial text are available in eight languages: English (`en`), Turkish (`tr`), German (`de`), Spanish (`es`), French (`fr`), Hindi (`hi`), Portuguese (`pt`), Russian (`ru`). Pass `lang` as a keyword argument on any supported method:

```python
card = roxy.tarot.get_daily_card(date="2026-04-22", lang="es")
life_path = roxy.numerology.calculate_life_path(year=1990, month=1, day=15, lang="hi")
```

Supported: `astrology`, `vedic_astrology`, `numerology`, `tarot`, `biorhythm`, `iching`, `crystals`, `angel_numbers`. English-only: `dreams`, `location`, `usage`. Untranslated fields fall back to English.

## Framework examples

The SDK is framework-agnostic. Works with Django, Flask, FastAPI, or any Python project.

### FastAPI

```python
from fastapi import FastAPI
from roxy_sdk import create_roxy

app = FastAPI()
roxy = create_roxy("your-api-key")

@app.get("/horoscope/{sign}")
async def horoscope(sign: str):
    return await roxy.astrology.get_daily_horoscope_async(sign=sign)
```

### Flask

```python
from flask import Flask, jsonify
from roxy_sdk import create_roxy

app = Flask(__name__)
roxy = create_roxy("your-api-key")

@app.route("/horoscope/<sign>")
def horoscope(sign):
    return jsonify(roxy.astrology.get_daily_horoscope(sign=sign))
```

### Django (views.py)

```python
from django.http import JsonResponse
from roxy_sdk import create_roxy

roxy = create_roxy("your-api-key")

def horoscope(request, sign):
    return JsonResponse(roxy.astrology.get_daily_horoscope(sign=sign))
```

## Error handling

All API errors raise `RoxyAPIError` with `error` (human-readable message), `code` (machine-readable, stable), and `status_code` attributes:

```python
from roxy_sdk import create_roxy, RoxyAPIError

roxy = create_roxy("your-api-key")

try:
    result = roxy.astrology.get_daily_horoscope(sign="invalid")
except RoxyAPIError as e:
    print(f"Code: {e.code}")
    print(f"Error: {e.error}")
    print(f"Status: {e.status_code}")
```

| Status | Code | When |
|--------|------|------|
| 400 | `validation_error` | Missing or invalid parameters |
| 401 | `api_key_required` | No API key provided |
| 401 | `invalid_api_key` | Key format invalid or tampered |
| 401 | `subscription_not_found` | Key references non-existent subscription |
| 401 | `subscription_inactive` | Subscription cancelled, expired, or suspended |
| 404 | `not_found` | Resource not found |
| 429 | `rate_limit_exceeded` | Monthly quota reached |
| 500 | `internal_error` | Server error |

Switch on `code`, not `error`. Messages may be reworded; codes are stable.

## Authentication

Store your API key in an environment variable for production:

```python
import os
from roxy_sdk import create_roxy

roxy = create_roxy(os.environ["ROXY_API_KEY"])
```

Never expose your API key client-side. Call Roxy from server code only.

## Configuration

`create_roxy` accepts optional parameters for advanced usage:

```python
roxy = create_roxy(
    api_key="your-api-key",
    base_url="https://roxyapi.com/api/v2",  # default
    timeout=30.0,                            # request timeout in seconds
)
```

The client reuses HTTP connections. For explicit cleanup, use the context manager:

```python
with create_roxy("your-api-key") as roxy:
    horoscope = roxy.astrology.get_daily_horoscope(sign="aries")
# connections closed automatically
```

## AI agents (Claude Code, Cursor, Copilot, Codex, Gemini CLI)

This package ships with `AGENTS.md` bundled alongside the source so AI coding agents can read the SDK patterns, common tasks, and gotchas directly.

Also available: [remote MCP server](https://roxyapi.com/docs/mcp) per domain at `https://roxyapi.com/mcp/{domain}-api` (Streamable HTTP, no stdio / no self-hosting) for agents that speak the Model Context Protocol.

## Links

- [API Documentation](https://roxyapi.com/docs)
- [Interactive API Reference](https://roxyapi.com/api-reference)
- [Pricing](https://roxyapi.com/pricing)
- [MCP for AI Agents](https://roxyapi.com/docs/mcp)
- [Starter Apps](https://roxyapi.com/starters)
- [TypeScript SDK](https://www.npmjs.com/package/@roxyapi/sdk)
