# roxy-sdk

Python SDK for [RoxyAPI](https://roxyapi.com). Astrology, tarot, numerology, I Ching, crystals, angel numbers, dream interpretation, and more. One API key, 10 domains, 120+ endpoints.

## Install

```bash
pip install roxy-sdk
```

## Quickstart

```python
from roxy_sdk import create_roxy

roxy = create_roxy("your-api-key")
horoscope = roxy.astrology.get_daily_horoscope(sign="aries")
print(horoscope)
```

Get your API key at [roxyapi.com/pricing](https://roxyapi.com/pricing). Free test keys available on the [interactive docs](https://roxyapi.com/api-reference).

## Recipes

### Dating app: zodiac compatibility

```python
person1 = {"date": "1990-01-15", "time": "14:30:00", "latitude": 28.61, "longitude": 77.20}
person2 = {"date": "1992-07-22", "time": "09:00:00", "latitude": 19.07, "longitude": 72.87}

score = roxy.astrology.calculate_compatibility(person1=person1, person2=person2)
print(f"Compatibility: {score}")
```

### Wellness app: daily tarot card

```python
card = roxy.tarot.get_daily_card()
print(f"Today: {card}")
```

### Journaling app: dream interpretation

```python
symbol = roxy.dreams.get_dream_symbol(id="flying")
print(f"Flying in dreams: {symbol}")
```

### Numerology calculator: life path number

```python
result = roxy.numerology.calculate_life_path(year=1990, month=1, day=15)
print(f"Life Path: {result}")

chart = roxy.numerology.generate_numerology_chart(full_name="Jane Smith", year=1990, month=1, day=15)
print(f"Full chart: {chart}")
```

### Crystal healing: zodiac crystals

```python
crystals = roxy.crystals.get_crystals_by_zodiac(sign="scorpio")
print(f"Scorpio crystals: {crystals}")
```

### I Ching: daily reading

```python
reading = roxy.iching.cast_daily_reading()
print(f"I Ching: {reading}")
```

## Domain reference

| Domain | Property | What it covers |
|--------|----------|----------------|
| Western Astrology | `roxy.astrology` | Natal charts, horoscopes, synastry, compatibility, transits, moon phases |
| Vedic Astrology | `roxy.vedic_astrology` | Birth charts, dashas, nakshatras, panchang, KP system, doshas, yogas |
| Tarot | `roxy.tarot` | Spreads, daily pulls, yes/no oracle, Celtic Cross, custom layouts |
| Numerology | `roxy.numerology` | Life path, expression, soul urge, personal year, karmic analysis |
| I Ching | `roxy.iching` | Hexagrams, trigrams, coin casting, daily readings |
| Crystals | `roxy.crystals` | Healing properties, zodiac/chakra pairings, birthstones, search |
| Angel Numbers | `roxy.angel_numbers` | Number meanings, pattern analysis, daily guidance |
| Dreams | `roxy.dreams` | Symbol dictionary, interpretations, daily guidance |
| Location | `roxy.location` | City geocoding for birth chart coordinates |
| Usage | `roxy.usage` | API usage stats and subscription info |

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

## Framework examples

The SDK is framework-agnostic. It works with Django, Flask, FastAPI, or any Python project.

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
    print(f"Error: {e.error}")
    print(f"Code: {e.code}")
    print(f"Status: {e.status_code}")
```

Error codes:

| Status | Code | When |
|--------|------|------|
| 400 | `validation_error` | Missing or invalid parameters |
| 401 | `api_key_required` | No API key provided |
| 401 | `invalid_api_key` | Key format invalid or tampered |
| 429 | `rate_limit_exceeded` | Monthly quota reached |
| 404 | `not_found` | Resource not found |
| 500 | `internal_error` | Server error |

## Environment variable

Store your API key in an environment variable for production use:

```python
import os
from roxy_sdk import create_roxy

roxy = create_roxy(os.environ["ROXY_API_KEY"])
```

## Configuration

`create_roxy` accepts optional parameters for advanced usage:

```python
roxy = create_roxy(
    api_key="your-api-key",
    base_url="https://roxyapi.com/api/v2",  # default, override for local development
    timeout=30.0,                            # request timeout in seconds (default: 30)
)
```

The client reuses HTTP connections for performance. For explicit cleanup, use the context manager:

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
