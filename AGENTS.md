# roxy-sdk (Python) Agent Guide

Python SDK for RoxyAPI. Multi-domain spiritual and metaphysical intelligence API. One API key, 11 domains, sync and async support.

## Install and initialize

```bash
pip install roxy-sdk
```

```python
from roxy_sdk import create_roxy

roxy = create_roxy("your-api-key")
```

`create_roxy` sets the base URL (`https://roxyapi.com/api/v2`) and auth header automatically. Returns a `Roxy` instance with namespaced domain properties.

## Domains

Type `roxy.` to see all available namespaces:

| Namespace | What it covers |
|-----------|----------------|
| `roxy.astrology` | Western astrology: natal charts, horoscopes, synastry, moon phases, transits, compatibility |
| `roxy.vedic_astrology` | Vedic/Jyotish: birth charts, dashas, nakshatras, panchang, KP system, doshas, yogas |
| `roxy.tarot` | Rider-Waite-Smith deck: spreads, daily pulls, yes/no, Celtic Cross, custom layouts |
| `roxy.numerology` | Life path, expression, soul urge, personal year, karmic analysis, compatibility |
| `roxy.crystals` | Crystal healing properties, zodiac/chakra pairings, birthstones, search |
| `roxy.iching` | I Ching: hexagrams, trigrams, coin casting, daily readings |
| `roxy.angel_numbers` | Angel number meanings, pattern analysis, daily guidance |
| `roxy.dreams` | Dream symbol dictionary and interpretations |
| `roxy.biorhythm` | Physical, emotional, intellectual cycles, forecasts, compatibility |
| `roxy.location` | City geocoding for birth chart coordinates |
| `roxy.usage` | API usage stats and subscription info |

## Critical patterns

### Sync calls (default)

```python
horoscope = roxy.astrology.get_daily_horoscope(sign="aries")
card = roxy.tarot.draw_cards(count=3)
life_path = roxy.numerology.calculate_life_path(year=1990, month=1, day=15)
```

### Async calls (append _async)

Every sync method has an async variant with `_async` suffix:

```python
horoscope = await roxy.astrology.get_daily_horoscope_async(sign="aries")
card = await roxy.tarot.draw_cards_async(count=3)
```

### POST endpoints (charts, spreads, calculations)

Most chart and calculation endpoints require date, time, and coordinates:

```python
chart = roxy.astrology.generate_natal_chart(
    date="1990-01-15",
    time="14:30:00",
    latitude=28.6139,
    longitude=77.209,
)

vedic = roxy.vedic_astrology.generate_birth_chart(
    date="1990-01-15",
    time="14:30:00",
    latitude=28.6139,
    longitude=77.209,
)

celtic = roxy.tarot.cast_celtic_cross(question="What should I focus on?")

numerology = roxy.numerology.generate_numerology_chart(
    full_name="John Doe",
    year=1990,
    month=1,
    day=15,
)
```

### Error handling

Errors raise `RoxyAPIError` with `error` (message), `code` (machine-readable), and `status_code` attributes:

```python
from roxy_sdk import create_roxy, RoxyAPIError

try:
    result = roxy.astrology.get_daily_horoscope(sign="invalid")
except RoxyAPIError as e:
    print(e.code)         # "validation_error"
    print(e.error)        # "Invalid sign"
    print(e.status_code)  # 400
```

Error codes: `validation_error`, `api_key_required`, `invalid_api_key`, `subscription_not_found`, `subscription_inactive`, `not_found`, `rate_limit_exceeded`, `internal_error`.

## Common tasks

| Task | Code |
|------|------|
| Daily horoscope | `roxy.astrology.get_daily_horoscope(sign="aries")` |
| Birth chart (Western) | `roxy.astrology.generate_natal_chart(date, time, latitude, longitude)` |
| Birth chart (Vedic) | `roxy.vedic_astrology.generate_birth_chart(date, time, latitude, longitude)` |
| Compatibility score | `roxy.astrology.calculate_compatibility(person1, person2)` |
| Tarot daily card | `roxy.tarot.get_daily_card()` |
| Celtic Cross reading | `roxy.tarot.cast_celtic_cross(question="...")` |
| Draw tarot cards | `roxy.tarot.draw_cards(count=3)` |
| Life Path number | `roxy.numerology.calculate_life_path(year, month, day)` |
| Full numerology chart | `roxy.numerology.generate_numerology_chart(full_name=, year=, month=, day=)` |
| Crystal by zodiac | `roxy.crystals.get_crystals_by_zodiac(sign="aries")` |
| Crystal search | `roxy.crystals.search_crystals(q="amethyst")` |
| I Ching reading | `roxy.iching.cast_reading()` |
| Angel number meaning | `roxy.angel_numbers.get_angel_number(number="1111")` |
| Dream symbol lookup | `roxy.dreams.get_dream_symbol(id="flying")` |
| Daily biorhythm | `roxy.biorhythm.get_daily_biorhythm(date="1990-01-15")` |
| Biorhythm forecast | `roxy.biorhythm.get_biorhythm_forecast(date="1990-01-15", days=30)` |
| Find city coordinates | `roxy.location.search_cities(q="Mumbai")` |
| Check API usage | `roxy.usage.get_usage_stats()` |

## Location helper

Most chart endpoints need `latitude` and `longitude`. Use the location API to geocode:

```python
result = roxy.location.search_cities(q="Mumbai, India")
city = result["cities"][0]
# Use city["latitude"] and city["longitude"] in chart requests
```

## Gotchas

- **All parameters are keyword arguments.** Use `sign="aries"` not positional `"aries"`.
- **Async methods end with `_async`.** Every sync method has a matching async variant.
- **Do not expose API keys client-side.** Call Roxy from server code only.
- **Chart endpoints need coordinates.** Use `roxy.location.search_cities()` to get lat/lng.
- **Date format is `YYYY-MM-DD`, time is `HH:MM:SS`.** Both are strings.
- **Errors raise `RoxyAPIError`.** Catch it and check `e.code`, `e.error`, and `e.status_code`.
- **Switch on `code`, not `error`.** The `code` field is stable. The `error` message may change.

## Links

- Interactive API docs: https://roxyapi.com/api-reference
- Pricing and API keys: https://roxyapi.com/pricing
- MCP for AI agents: https://roxyapi.com/docs/mcp
- TypeScript SDK: https://www.npmjs.com/package/@roxyapi/sdk
