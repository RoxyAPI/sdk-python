# roxy-sdk

[![PyPI](https://img.shields.io/pypi/v/roxy-sdk)](https://pypi.org/project/roxy-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/roxy-sdk)](https://pypi.org/project/roxy-sdk/)
[![Docs](https://img.shields.io/badge/docs-roxyapi.com-blue)](https://roxyapi.com/docs)
[![API Reference](https://img.shields.io/badge/api%20reference-roxyapi.com-blue)](https://roxyapi.com/api-reference)
[![License](https://img.shields.io/github/license/RoxyAPI/sdk-python)](https://github.com/RoxyAPI/sdk-python/blob/main/LICENSE)

Python SDK for astrology, Vedic astrology, tarot, numerology, and more.

One API key. Sync and async (every method has an `_async` suffix). Verified against NASA JPL Horizons.

The fastest way to add natal charts, kundli matching, daily horoscopes, tarot readings, and spiritual insights to FastAPI, Django, Flask, or any Python project. Ten domains behind a single [Roxy](https://roxyapi.com) subscription, interpretations in eight languages.

## Install

```bash
pip install roxy-sdk
```

## Start with one call

Get real product value with a single typed call. No setup beyond your API key.

```python
from roxy_sdk import create_roxy

roxy = create_roxy("your-api-key")

horoscope = roxy.astrology.get_daily_horoscope(sign="aries")
print(horoscope["overview"], horoscope["love"], horoscope["luckyNumber"])
```

Then expand into charts, compatibility, tarot, numerology, and more.

## Quickstart

```python
from roxy_sdk import create_roxy

roxy = create_roxy("your-api-key")

# Step 1: geocode the birth city (required for any chart endpoint)
result = roxy.location.search_cities(q="Mumbai, India")
city = result["cities"][0]
lat, lng, tz = city["latitude"], city["longitude"], city["timezone"]

# Step 2: Vedic kundli. `timezone` can be the IANA string ("Asia/Kolkata").
# The server resolves it to the DST-correct offset for the chart's own date.
kundli = roxy.vedic_astrology.generate_birth_chart(
    date="1990-01-15",
    time="14:30:00",
    latitude=lat,
    longitude=lng,
    timezone=tz,
)

# Or Western natal chart (same timezone semantics)
natal = roxy.astrology.generate_natal_chart(
    date="1990-01-15",
    time="14:30:00",
    latitude=lat,
    longitude=lng,
    timezone=tz,
)
```

Get your API key at [roxyapi.com/pricing](https://roxyapi.com/pricing). Free test keys available on the [interactive docs](https://roxyapi.com/api-reference).

## Location first

Every chart, horoscope, panchang, dasha, dosha, navamsa, KP, synastry, compatibility, and natal endpoint needs `latitude`, `longitude`, and (for Western) `timezone`. **Never ask users to type coordinates.** Always call `roxy.location.search_cities(q=city)` first and feed the result into the chart call.

```python
result = roxy.location.search_cities(q="Tokyo")
city = result["cities"][0]
lat, lng, tz = city["latitude"], city["longitude"], city["timezone"]
# `tz` is the IANA string ("Asia/Tokyo"). Pass it straight into any chart
# endpoint and the server resolves it to the DST-correct offset for the chart's
# own date. If you prefer a decimal, city["utcOffset"] also works.
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

## Most-used endpoints

The highest-demand endpoints by domain, in the order you are most likely to ship them. Each block shows the most-searched API call in that domain so you can pick the feature that drives the most user value first. Full endpoint catalog in the [API reference](https://roxyapi.com/api-reference).

### 1. Western astrology API (natal chart, daily horoscope, synastry)

The global astrology app market is $6.27B and almost entirely Western. These endpoints power zodiac dating apps, Co-Star-style natal chart products, daily horoscope features, and lunar-cycle wellness apps.

```python
# Natal chart. The #1 Western query, called on every onboarding.
natal = roxy.astrology.generate_natal_chart(
    date="1990-01-15", time="14:30:00",
    latitude=28.6139, longitude=77.209, timezone=5.5,
)

# Daily horoscope. Highest per-user call frequency in the catalog, drives DAUs and push.
horoscope = roxy.astrology.get_daily_horoscope(sign="aries")
# horoscope["overview"], horoscope["love"], horoscope["career"], horoscope["luckyNumber"]

# Synastry. The dating-app pro-tier feature, full inter-aspect analysis.
synastry = roxy.astrology.calculate_synastry(
    person1={"date": "1990-01-15", "time": "14:30:00", "latitude": 28.61, "longitude": 77.20, "timezone": 5.5},
    person2={"date": "1992-07-22", "time": "09:00:00", "latitude": 19.07, "longitude": 72.87, "timezone": 5.5},
)
# synastry["compatibilityScore"], synastry["interAspects"], synastry["strengths"]

# Moon phase. Viral for wellness, cycle-tracking, meditation apps.
moon = roxy.astrology.get_current_moon_phase()
```

### 2. Vedic astrology API (kundli, panchang, dasha, Guna Milan, KP)

The depth moat. India astrology market: $163M in 2024, projected $1.8B by 2030 (49% CAGR). Kundli, panchang, dasha, dosha, and KP are the five Google-dominant queries for every matrimonial platform, kundli generator, and muhurat app.

```python
# Vedic kundli. Top India astrology keyword. Entry point for every Jyotish product.
kundli = roxy.vedic_astrology.generate_birth_chart(
    date="1990-01-15", time="14:30:00",
    latitude=28.6139, longitude=77.209, timezone=5.5,
)

# Panchang. Tithi, nakshatra, yoga, karana, rahu kaal, abhijit muhurta in one call.
panchang = roxy.vedic_astrology.get_detailed_panchang(
    date="2026-04-22", latitude=28.6139, longitude=77.209,
)

# Vimshottari dasha. Highest-value single-shot Vedic query.
dasha = roxy.vedic_astrology.get_current_dasha(
    date="1990-01-15", time="14:30:00",
    latitude=28.6139, longitude=77.209, timezone=5.5,
)

# Mangal Dosha. Most-asked matrimonial question in India.
dosha = roxy.vedic_astrology.check_manglik_dosha(
    date="1990-01-15", time="14:30:00",
    latitude=28.6139, longitude=77.209, timezone=5.5,
)

# Guna Milan. 36-point Ashtakoota matrimonial compatibility score.
milan = roxy.vedic_astrology.calculate_gun_milan(
    person1={"date": "1990-01-15", "time": "14:30:00", "latitude": 28.61, "longitude": 77.20},
    person2={"date": "1992-07-22", "time": "09:00:00", "latitude": 19.07, "longitude": 72.87},
)

# KP ruling planets. Horary answers for "will X happen" questions in real time.
kp = roxy.vedic_astrology.get_kp_ruling_planets(
    latitude=28.6139, longitude=77.209, timezone=5.5,
)
```

### 3. Numerology API (life path, full chart, personal year)

Commodity content with durable demand. `life path number calculator` is among the highest-volume spiritual searches globally. Works without birth time, the easiest domain to integrate.

```python
# Life Path. The #1 numerology keyword, every calculator page starts here.
lp = roxy.numerology.calculate_life_path(year=1990, month=1, day=15)
# lp["number"], lp["type"] ("single" | "master"), lp["meaning"]

# Full numerology chart. Premium one-shot: all six core numbers plus karmic, personal year.
chart = roxy.numerology.generate_numerology_chart(
    full_name="Jane Smith", year=1990, month=1, day=15,
)

# Personal Year. Annual forecast, drives January traffic spikes.
pyear = roxy.numerology.calculate_personal_year(month=1, day=15, year=2026)
```

### 4. Tarot API (daily card, Celtic Cross, three-card, yes / no)

High search volume, evergreen. The tarot card database is the highest per-endpoint call count in the catalog because apps fetch once and cache.

```python
# Daily card. Stickiest tarot feature. Seed per user for deterministic once-per-day behavior.
card = roxy.tarot.get_daily_card(seed="user-42")
# card["card"]["name"], card["card"]["imageUrl"], card["interpretation"]

# Celtic Cross. Professional-reader spread. Premium-tier, ten positions.
cc = roxy.tarot.cast_celtic_cross(question="What should I focus on?", seed="user-42")

# Three-card past-present-future. Most-drawn spread on every tarot platform.
three = roxy.tarot.cast_three_card(question="My next quarter", seed="user-42")

# Yes / No. Impulse micro-query, highest conversion-to-first-call on tarot surfaces.
answer = roxy.tarot.cast_yes_no(question="Should I take the offer?")
# answer["answer"] ("Yes" | "No" | "Maybe"), answer["strength"]
```

### 5. Biorhythm API (daily check-in, forecast, compatibility)

Zero competition domain. Steady search volume with the top Google result being a static calculator page. Pure land-grab for wellness, productivity, sports, and couples apps.

```python
# Daily biorhythm. Physical, emotional, intellectual, intuitive, plus seven extended cycles.
bio = roxy.biorhythm.get_daily_biorhythm(seed="user-1", date="2026-04-23")

# Multi-day forecast. Best-day / worst-day planner for calendar and coaching products.
forecast = roxy.biorhythm.get_forecast(
    birth_date="1990-01-15", start_date="2026-04-01", end_date="2026-04-30",
)
```

### 6. I Ching API (daily hexagram, coin cast, 64-hexagram catalog)

Meditation apps, decision-making tools, and wisdom chatbots. `i ching API` and `hexagram API` are the keywords.

```python
# Cast a reading. Active divination, primary hexagram plus changing lines and transformed hexagram.
reading = roxy.iching.cast_reading(seed="user-42")
# reading["hexagram"], reading["changingLinePositions"], reading["resultingHexagram"]

# Hexagram catalog. Cache once for all 64 hexagrams.
hexagrams = roxy.iching.list_hexagrams()
# hexagrams["hexagrams"] has 64 entries
```

### 7. Crystals API (by zodiac, by chakra, birthstone)

Crystal retail and metaphysical shops use these to build "crystals for [sign]" and "[chakra] chakra stones" pages.

```python
# By zodiac. Highest-search crystal query pattern.
by_sign = roxy.crystals.get_crystals_by_zodiac(sign="scorpio")
# by_sign["crystals"] is a list of id, name, color, chakra, properties

# By chakra. Second-highest crystal query pattern.
by_chakra = roxy.crystals.get_crystals_by_chakra(chakra="heart")

# Birthstone. Evergreen gift and jewelry SEO.
birthstone = roxy.crystals.get_birthstones(month=4)
```

### 8. Dream interpretation API (symbol dictionary, search)

Thousands of dream symbols. `dream meaning` is among the highest-volume spiritual searches on Google. Journal apps, AI therapy chatbots, and self-discovery products are the buyers.

```python
# Symbol detail. Every "what does it mean to dream about X" page lands here.
symbol = roxy.dreams.get_dream_symbol(id="flying")
# symbol["id"], symbol["name"], symbol["meaning"]

# Symbol search. Chatbots cache the dictionary locally after one call.
results = roxy.dreams.search_dream_symbols(q="flying")
# results["symbols"] is an array of matching symbols
```

### 9. Angel Numbers API (1111, 222, 333 meanings plus universal lookup)

Gen Z spiritual-tok fuel. `111 meaning`, `222 meaning`, `333 angel number` are evergreen viral queries with massive shareability.

```python
# By number. Every "meaning of 1111" page is backed by this.
angel = roxy.angel_numbers.get_angel_number(number="1111")
# angel["meaning"]["spiritual"], angel["meaning"]["love"], angel["affirmation"]

# Universal lookup. Works for any positive integer via digit-root fallback.
any_number = roxy.angel_numbers.analyze_number_sequence(number="4242")
```

## Built for AI agents (Claude Code, Cursor, Copilot, Codex, Gemini CLI)

This package ships `AGENTS.md` bundled alongside the source so AI coding agents can read the SDK patterns, common tasks, and gotchas directly from `site-packages/`.

Prefer MCP? Every domain has a [remote MCP server](https://roxyapi.com/docs/mcp) at `https://roxyapi.com/mcp/{domain}` (Streamable HTTP, no stdio, no self-hosting). One-line Claude Code setup:

```bash
claude mcp add-json --scope user roxy-astrology \
  '{"type":"http","url":"https://roxyapi.com/mcp/astrology","headers":{"X-API-Key":"YOUR_KEY"}}'
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

## Links

- [API Documentation](https://roxyapi.com/docs)
- [Interactive API Reference](https://roxyapi.com/api-reference)
- [Pricing](https://roxyapi.com/pricing)
- [MCP for AI Agents](https://roxyapi.com/docs/mcp)
- [Starter Apps](https://roxyapi.com/starters)
- [TypeScript SDK](https://www.npmjs.com/package/@roxyapi/sdk)
