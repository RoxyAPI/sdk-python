# roxy-sdk (Python) - Agent Guide

Python SDK for RoxyAPI. Eleven domains (Western astrology, Vedic astrology, numerology, tarot, biorhythm, I Ching, crystals, dreams, angel numbers, location, usage). One API key, sync and async.

## Install and initialize

```bash
pip install roxy-sdk
```

```python
from roxy_sdk import create_roxy

roxy = create_roxy("your-api-key")
```

`create_roxy` sets the base URL (`https://roxyapi.com/api/v2`) and auth header automatically. Returns a `Roxy` instance with namespaced domain properties.

## Critical rule: geocode before any chart endpoint

Every chart, horoscope, panchang, dasha, dosha, navamsa, KP, synastry, compatibility, and natal endpoint needs `latitude`, `longitude`, and (for Western) `timezone`. **Never ask the user for coordinates.** Always call `roxy.location.search_cities` first.

```python
cities = roxy.location.search_cities(q="Mumbai")
lat, lng, tz = cities[0]["latitude"], cities[0]["longitude"], cities[0]["timezone"]
```

## Domains

Type `roxy.` to see all available namespaces. Type `roxy.{domain}.` in an IDE with a Python LSP to see every method.

| Namespace | What it covers |
|-----------|----------------|
| `roxy.astrology` | Western astrology: natal charts, daily / weekly / monthly horoscopes, synastry, compatibility score, transits, moon phases |
| `roxy.vedic_astrology` | Vedic / Jyotish: kundli, panchang, Vimshottari dasha, nakshatras, Mangal / Kaal Sarp / Sade Sati doshas, Guna Milan, navamsa, KP chart and ruling planets |
| `roxy.numerology` | Life path, expression, soul urge, personal year, full chart, compatibility, karmic lessons |
| `roxy.tarot` | Daily card, custom draws, three-card, Celtic Cross, yes / no, love spread, 78-card catalog |
| `roxy.biorhythm` | Daily check-in, multi-day forecast, critical days, couples compatibility, phases |
| `roxy.iching` | Daily hexagram, three-coin cast, 64 hexagrams, trigrams |
| `roxy.crystals` | By zodiac, by chakra, birthstone, search, daily, pairings |
| `roxy.dreams` | Dream symbol dictionary (3,000+ interpretations), daily prompt |
| `roxy.angel_numbers` | Number meanings, universal digit-root lookup, daily |
| `roxy.location` | City search with coordinates and timezone, countries |
| `roxy.usage` | API usage stats and subscription info |

## Critical patterns

### Two-step pattern for coordinate-dependent endpoints

```python
cities = roxy.location.search_cities(q="Delhi")
lat, lng, tz = cities[0]["latitude"], cities[0]["longitude"], cities[0]["timezone"]

chart = roxy.astrology.generate_natal_chart(
    date="1990-01-15", time="14:30:00",
    latitude=lat, longitude=lng, timezone=tz,
)
```

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

Most valuable endpoints are POST:

```python
natal = roxy.astrology.generate_natal_chart(
    date="1990-01-15", time="14:30:00",
    latitude=28.6139, longitude=77.209, timezone=5.5,
)

kundli = roxy.vedic_astrology.generate_birth_chart(
    date="1990-01-15", time="14:30:00",
    latitude=28.6139, longitude=77.209,
)

celtic = roxy.tarot.cast_celtic_cross(question="What should I focus on?")

numerology = roxy.numerology.generate_numerology_chart(
    full_name="John Doe", year=1990, month=1, day=15,
)
```

### Multi-language via `lang` kwarg

Eight languages: `en`, `tr`, `de`, `es`, `fr`, `hi`, `pt`, `ru`. Defaults to `en`.

```python
card = roxy.tarot.get_daily_card(date="2026-04-22", lang="es")
life_path = roxy.numerology.calculate_life_path(year=1990, month=1, day=15, lang="hi")
```

Supported: `astrology`, `vedic_astrology`, `numerology`, `tarot`, `biorhythm`, `iching`, `crystals`, `angel_numbers`. English-only: `dreams`, `location`, `usage`.

### Error handling

Errors raise `RoxyAPIError` with `error` (message), `code` (machine-readable), and `status_code`:

```python
from roxy_sdk import create_roxy, RoxyAPIError

try:
    result = roxy.astrology.get_daily_horoscope(sign="invalid")
except RoxyAPIError as e:
    print(e.code)         # "validation_error"
    print(e.error)        # "Invalid sign"
    print(e.status_code)  # 400
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

## Common tasks

Ordered by domain priority (Western, Vedic, Numerology, Tarot, Biorhythm, I Ching, Crystals, Dreams, Angel Numbers, Location, Usage).

| Task | Code |
|------|------|
| Daily horoscope | `roxy.astrology.get_daily_horoscope(sign="aries")` |
| Natal chart (Western) | `roxy.astrology.generate_natal_chart(date, time, latitude, longitude, timezone)` |
| Synastry | `roxy.astrology.calculate_synastry(person1, person2)` |
| Compatibility score | `roxy.astrology.calculate_compatibility(person1, person2)` |
| Current moon phase | `roxy.astrology.get_current_moon_phase()` |
| Transits | `roxy.astrology.calculate_transits(natal_chart=...)` |
| Kundli (Vedic birth chart) | `roxy.vedic_astrology.generate_birth_chart(date, time, latitude, longitude)` |
| Panchang (detailed) | `roxy.vedic_astrology.get_detailed_panchang(date, latitude, longitude)` |
| Choghadiya | `roxy.vedic_astrology.get_choghadiya(date, latitude, longitude)` |
| Current dasha | `roxy.vedic_astrology.get_current_dasha(date, time, latitude, longitude)` |
| Mangal Dosha | `roxy.vedic_astrology.check_manglik_dosha(date, time, latitude, longitude)` |
| Guna Milan (matching) | `roxy.vedic_astrology.calculate_gun_milan(person1, person2)` |
| Navamsa (D9) | `roxy.vedic_astrology.generate_navamsa(date, time, latitude, longitude)` |
| KP chart | `roxy.vedic_astrology.generate_kp_chart(date, time, latitude, longitude)` |
| Nakshatra detail | `roxy.vedic_astrology.get_nakshatra(id="ashwini")` |
| Life path number | `roxy.numerology.calculate_life_path(year, month, day)` |
| Full numerology chart | `roxy.numerology.generate_numerology_chart(full_name, year, month, day)` |
| Personal year | `roxy.numerology.calculate_personal_year(month, day)` |
| Daily tarot card | `roxy.tarot.get_daily_card(seed="user-123")` |
| Three-card spread | `roxy.tarot.cast_three_card(question="...")` |
| Celtic Cross | `roxy.tarot.cast_celtic_cross(question="...")` |
| Yes / no tarot | `roxy.tarot.cast_yes_no(question="...")` |
| Daily biorhythm | `roxy.biorhythm.get_daily_biorhythm(seed="user-123")` |
| Biorhythm forecast | `roxy.biorhythm.get_forecast(birth_date="1990-01-15")` |
| Biorhythm compatibility | `roxy.biorhythm.calculate_bio_compatibility(person1, person2)` |
| Daily hexagram | `roxy.iching.get_daily_hexagram(seed="user-123")` |
| Cast I Ching reading | `roxy.iching.cast_reading()` |
| Hexagram detail | `roxy.iching.get_hexagram(number=1)` |
| Crystal by zodiac | `roxy.crystals.get_crystals_by_zodiac(sign="aries")` |
| Crystal by chakra | `roxy.crystals.get_crystals_by_chakra(chakra="heart")` |
| Dream symbol lookup | `roxy.dreams.get_dream_symbol(id="flying")` |
| Angel number meaning | `roxy.angel_numbers.get_angel_number(number="1111")` |
| Universal number lookup | `roxy.angel_numbers.analyze_number_sequence(number="1234")` |
| Find city coordinates | `roxy.location.search_cities(q="Mumbai")` |
| Check API usage | `roxy.usage.get_usage_stats()` |

## Field formats that trip agents

These are the fields AI agents most often get wrong. Copy the format column exactly.

| Field | Format | Good | Bad |
|-------|--------|------|-----|
| `timezone` | Decimal hours from UTC (float) | `5.5` (India IST, GMT+5:30), `5.75` (Nepal NPT, GMT+5:45), `-5` (NY EST), `9.5` (Adelaide), `0` (UTC) | `"5:30"`, `"5:45"`, `5.45`, `"GMT-5"`, `"Asia/Kolkata"`, `"+0530"` |
| `date` | ISO date string | `"1990-01-15"` | `"Jan 15 1990"`, `datetime.now()`, `"15/01/1990"`, `"1990-1-15"` |
| `time` | 24-hour string | `"14:30:00"`, `"09:00:00"` | `"2:30 PM"`, `"14:30"` (no seconds), `"9:0:0"` (no leading zeros) |
| `latitude` | Decimal degrees (float) | `28.6139` (Delhi), `-33.8688` (Sydney), `40.7128` (NYC) | `"28°36'N"`, `"28 36 50"`, strings |
| `longitude` | Decimal degrees (float) | `77.209` (Delhi), `-74.006` (NYC), `139.6917` (Tokyo) | Same as latitude - no DMS strings |
| `sign` (horoscope kwarg) | Lowercase zodiac name | `"aries"`, `"taurus"`, `"gemini"`, ... `"pisces"` | `"Aries"`, `"♈"`, `"1"`, `"ARIES"` (case-insensitive but prefer lowercase) |
| `full_name` (numerology) | Birth-certificate name | `"John William Smith"`, `"Priya Rajesh Sharma"` | Nickname, married name, partial name - affects all letter-based calcs |
| `seed` | Any string (deterministic) | `"user-42"`, `"session-abc-123"`, email hash | Numbers, objects - must be string |
| `number` (angel numbers) | String | `"1111"`, `"777"`, `"1234"` | `1111` (int) fails path validation |
| `id` (nakshatra / dream / tarot) | Slug | `"ashwini"`, `"flying"`, `"the-fool"`, `"three-of-cups"` | Display names, uppercase, spaces |
| `house_system` | Enum string | `"placidus"` (default), `"whole-sign"`, `"equal"`, `"koch"` | `"Placidus"`, `"whole_sign"`, `"WS"` |
| `ayanamsa` (KP) | Enum string | `"kp-newcomb"` (default), `"kp-old"`, `"lahiri"`, `"custom"` | `"KP"`, `"New Comb"`, `"Lahiri"` |
| `node_type` | Enum string | `"true-node"`, `"mean-node"` | `"true"`, `"mean"`, `"True Node"` |
| `count` (tarot draw) | Integer 1 to 78 | `3`, `10`, `78` | `0`, `79`, strings, floats |
| `mahadasha` (path) | Planet name | `"Ketu"`, `"Venus"`, `"Sun"`, `"Moon"`, `"Mars"`, `"Rahu"`, `"Jupiter"`, `"Saturn"`, `"Mercury"` | `"KETU"` (works, case-insensitive), `"ke"`, `"Ke-tu"` |
| `person1` / `person2` | Dict with full birth data | `{"date": ..., "time": ..., "latitude": ..., "longitude": ..., "timezone": ...}` (Western) or same without timezone (Vedic) | Separate top-level kwargs, missing time, partial dict |
| `question` (tarot / iching) | Optional string | `"Should I accept the job offer?"`, `"What should I focus on this week?"` | Omit for general reading. More specific = better interpretation. |
| `year` / `month` / `day` (numerology) | Integer | `1990`, `1`, `15` | Zero-padded strings `"01"`, floats, full dates |

### Timezone cheat sheet (most-asked locations)

| Region | Decimal | Region | Decimal |
|--------|---------|--------|---------|
| UTC / London (winter) | `0` | Dubai | `4` |
| London (summer, BST) | `1` | Karachi | `5` |
| Berlin / Paris | `1` (winter) / `2` (summer) | Delhi / Mumbai (IST) | `5.5` |
| Istanbul | `3` | Kathmandu (NPT) | `5.75` |
| Moscow | `3` | Dhaka | `6` |
| Tehran | `3.5` (winter) / `4.5` (summer) | Bangkok | `7` |
| Adelaide | `9.5` (winter) / `10.5` (summer) | Singapore / Beijing | `8` |
| New York (EST / EDT) | `-5` / `-4` | Tokyo | `9` |
| Chicago (CST / CDT) | `-6` / `-5` | Sydney | `10` (winter) / `11` (summer) |
| Denver (MST / MDT) | `-7` / `-6` | Auckland | `12` (winter) / `13` (summer) |
| Los Angeles (PST / PDT) | `-8` / `-7` | Honolulu | `-10` |

DST matters. If the birth date falls inside a daylight-saving window, use the summer / DST offset. For Vedic endpoints this is rarely an issue (most users are in India, fixed 5.5), but Western natal charts must respect DST at the time of birth.

## MCP equivalents

Every method has a matching MCP tool. The remote MCP server per domain is at `https://roxyapi.com/mcp/{domain}-api` (Streamable HTTP, no stdio / no self-hosting). Tool names follow `{method}_{path_snake_case}`, for example:

- `POST /astrology/natal-chart` -> `post_astrology_natal_chart` on `/mcp/astrology-api`
- `GET /astrology/horoscope/{sign}/daily` -> `get_astrology_horoscope_sign_daily` on `/mcp/astrology-api`
- `POST /vedic-astrology/birth-chart` -> `post_vedic_astrology_birth_chart` on `/mcp/vedic-astrology-api`
- `POST /tarot/spreads/celtic-cross` -> `post_tarot_spreads_celtic_cross` on `/mcp/tarot-api`

Use the SDK for typed Python apps. Use MCP for AI agents (Claude Desktop, Cursor MCP, OpenAI agents) where the agent selects tools based on user intent.

## Gotchas

- **Geocode first.** Any chart, panchang, synastry, compatibility, or natal endpoint needs coordinates. Call `roxy.location.search_cities` before the chart method.
- **All parameters are keyword arguments.** Use `sign="aries"` not positional `"aries"`.
- **Async methods end with `_async`.** Every sync method has a matching async variant.
- **Do not expose API keys client-side.** Call Roxy from server code only.
- **Date format is `YYYY-MM-DD`, time is `HH:MM:SS`.** Both are strings.
- **Western `timezone` is required** (decimal hours, `-5` for EST, `5.5` for IST, `0` for UTC). Vedic endpoints accept an optional `timezone` that defaults to `5.5` (IST).
- **Errors raise `RoxyAPIError`.** Catch it and check `e.code`, `e.error`, and `e.status_code`.
- **Switch on `code`, not `error`.** Codes are stable. Messages may change.

## Links

- Interactive API docs: https://roxyapi.com/api-reference
- Pricing and API keys: https://roxyapi.com/pricing
- MCP for AI agents: https://roxyapi.com/docs/mcp
- TypeScript SDK: https://www.npmjs.com/package/@roxyapi/sdk
