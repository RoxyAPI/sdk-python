# roxy-sdk (Python) - Agent Guide

Python SDK for RoxyAPI. 18+ domains (Western astrology, Vedic astrology, forecast, human design, Chinese astrology, feng shui, Mesoamerican astrology, Vastu, numerology, Kabbalah, tarot, biorhythm, Ayurveda, I Ching, crystals, dreams, angel numbers, location) plus utility namespaces (usage, languages). One API key, sync and async.

## Install and initialize

```bash
pip install roxy-sdk
```

```python
from roxy_sdk import create_roxy

roxy = create_roxy("your-api-key")
```

`create_roxy` sets the base URL (`https://roxyapi.com/api/v2`) and auth header automatically. Returns a `Roxy` instance with namespaced domain properties.

## Quality guidelines for agents

- Every method returns `dict[str, Any]`. Access fields with `result["key"]["subkey"]`, never `result.key.subkey` (Python will raise `AttributeError: 'dict' object has no attribute ...`).
- Method names are snake_case versions of the OpenAPI operationId (e.g. `castThreeCard` -> `cast_three_card`, `analyzeNumberSequence` -> `analyze_number_sequence`). Every sync method has an `_async` variant; use `await` with the async variants.
- Param names are snake_case versions of the spec param names (`fullName` -> `full_name`, `birthDate` -> `birth_date`, `houseSystem` -> `house_system`). All params are keyword-only.
- When in doubt about a method or kwarg, check `roxy_sdk.factory` directly or run `python -c "from roxy_sdk import Roxy; help(Roxy)"` - the generated signatures are the contract.
- Response field names match the OpenAPI spec's response schema exactly. Never invent or pluralize. If a field isn't in the spec, it isn't in the response.
- Strings everywhere: `date` is `"YYYY-MM-DD"`, `time` is `"HH:MM:SS"`, `timezone` is an IANA name (`"Asia/Kolkata"`, `"America/New_York"`) - the server resolves DST for the chart date. `number` (angel) is `"1111"`, `month` (birthstone) is `"4"`, `number` (hexagram) is `"1"`. Numeric kwargs are only `latitude`, `longitude`, `year`, `month` (numerology), `day`, `count` (tarot draw).
- Inside `person1` / `person2` dicts any value type works because the kwarg is typed `dict[str, Any]`; only the top-level `timezone` kwarg needs string form.

## Critical rule: geocode before any chart endpoint

Every chart, horoscope, panchang, dasha, dosha, navamsa, KP, synastry, compatibility, and natal endpoint needs `latitude`, `longitude`, and (for Western) `timezone`. **Never ask the user for coordinates.** Always call `roxy.location.search_cities` first.

```python
result = roxy.location.search_cities(q="New York")
city = result["cities"][0]
lat, lng, tz = city["latitude"], city["longitude"], city["timezone"]
# `timezone` is the IANA string ("America/New_York"). Pass it directly to any chart endpoint.
# The server resolves it to the DST-correct decimal offset using the request's own date,
# so a January 1990 New York chart gets EST (-5) even when you looked the city up in July.
# If you prefer numbers, city["utcOffset"] (decimal: 5.5, -5, ...) also works.
```

`q` accepts bare city (`"Paris"`), city + country (`"Berlin Germany"`), or comma-qualified (`"Springfield, Illinois"`). Use the qualified form to disambiguate same-named cities.

## Domains

Type `roxy.` to see all available namespaces. Type `roxy.{domain}.` in an IDE with a Python LSP to see every method.

<!-- BEGIN:DOMAINS -->
| Namespace | Methods | What it covers |
|-----------|---------|----------------|
| `roxy.astrology` | 39 | Western astrology API for natal birth charts, daily, weekly, monthly, and yearly horoscopes with unique content per s... |
| `roxy.vedic_astrology` | 55 | Vedic astrology (Jyotish) and KP API for kundli generation with 15 divisional charts (D1-D60), Ashtakoot Gun Milan ku... |
| `roxy.forecast` | 5 | Forecast API that merges upcoming transit aspects, sign ingresses, retrograde stations, new and full moons, biorhythm... |
| `roxy.human_design` | 12 | Generate the full Human Design bodygraph from a birth moment: type, strategy, inner authority, profile, definition, i... |
| `roxy.chinese_astrology` | 16 | Calculate BaZi Four Pillars charts, Chinese zodiac signs, and the Chinese lunisolar calendar from any birth moment: y... |
| `roxy.feng_shui` | 11 | Compute classical feng shui from one API: Xuan Kong flying star natal charts for any of the nine periods and 24 mount... |
| `roxy.mesoamerican_astrology` | 18 | Calculate Mayan astrology day signs, the Tzolkin sacred round, the Haab year, the full Long Count and the Aztec tonal... |
| `roxy.vastu` | 10 | Vastu Shastra API for directional home and plot analysis: entrance padas with the classical effect of each of the 32... |
| `roxy.numerology` | 20 | Numerology API to calculate life path, expression, soul urge, personality, and maturity numbers, with Pinnacle and Ch... |
| `roxy.kabbalah` | 12 | Kabbalah API for gematria, the 72 names, the Tree of Life and the Hebrew birthday, from one key |
| `roxy.tarot` | 10 | Tarot reading API with the complete 78-card Rider-Waite-Smith deck and card meanings for love, career, health, and sp... |
| `roxy.biorhythm` | 6 | The most complete biorhythm API: 10 cycle types across 3 primary (physical, emotional, intellectual), 4 secondary (in... |
| `roxy.ayurveda` | 8 | Ayurveda API for dosha profiles, the dinacharya daily routine and the ritucharya seasonal regimen, with a verse cited... |
| `roxy.iching` | 9 | I-Ching oracle API with all 64 hexagrams, 384 changing lines, 8 trigrams, and modern interpretations for love, career... |
| `roxy.crystals` | 12 | Crystal healing API covering the most popular and widely-searched healing crystals and gemstones, from Amethyst and R... |
| `roxy.dreams` | 5 | Dream interpretation API with a 2,000+ symbol dream dictionary and psychological meanings covering animals, objects,... |
| `roxy.angel_numbers` | 4 | Angel numbers API with meanings for 111, 222, 333, 444, 555, 666, 777, 888, 999, 1111, and 75+ sequences covering eve... |
| `roxy.location` | 3 | Location and timezone API with city search and geocoding across 235,000+ cities in 240+ countries, returning latitude... |
| `roxy.usage` | 1 | Monitor your API usage, check rate limits, and track request consumption |
| `roxy.languages` | 2 | List the response languages accepted by the `lang` query parameter on every i18n-aware endpoint |
<!-- END:DOMAINS -->

## Critical patterns

### Two-step pattern for coordinate-dependent endpoints

```python
result = roxy.location.search_cities(q="London")
city = result["cities"][0]

chart = roxy.astrology.generate_natal_chart(
    date="1990-01-15", time="14:30:00",
    latitude=city["latitude"], longitude=city["longitude"],
    timezone=city["timezone"],  # IANA string, server resolves DST for the date
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
    latitude=40.7128, longitude=-74.006, timezone="America/New_York",
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

<!-- BEGIN:LANGS -->
10 languages: `en`, `tr`, `de`, `es`, `hi`, `pt`, `fr`, `ru`, `zh-Hans`, `zh-Hant`. Defaults to `en`. Supported: `astrology`, `vedic_astrology`, `forecast`, `human_design`, `chinese_astrology`, `feng_shui`, `mesoamerican_astrology`, `vastu`, `numerology`, `kabbalah`, `tarot`, `biorhythm`, `ayurveda`, `iching`, `crystals`, `angel_numbers`, `languages`. English-only: `dreams`, `location`, `usage`.
<!-- END:LANGS -->

```python
card = roxy.tarot.get_daily_card(date="2026-04-22", lang="es")
life_path = roxy.numerology.calculate_life_path(year=1990, month=1, day=15, lang="hi")
```

The two Chinese scripts (`zh-Hans`, `zh-Hant`) currently ship on Chinese astrology and feng shui; every other domain answers those codes in English per field. To list supported codes at runtime, call `roxy.languages.list_languages()`.

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

Ordered by domain priority (Western, Vedic, Forecast, Human Design, Chinese Astrology, Feng Shui, Numerology, Tarot, Biorhythm, I Ching, Crystals, Dreams, Angel Numbers, Location, Usage, Languages).

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
| Human Design bodygraph | `roxy.human_design.generate_bodygraph(date, time, timezone)` |
| Forecast timeline | `roxy.forecast.generate_timeline(birth_data=...)` |
| Daily biorhythm | `roxy.biorhythm.get_daily_biorhythm(seed="user-123")` |
| Biorhythm forecast | `roxy.biorhythm.get_forecast(birth_date="1990-01-15")` |
| Biorhythm compatibility | `roxy.biorhythm.calculate_bio_compatibility(person1, person2)` |
| Daily hexagram | `roxy.iching.get_daily_hexagram(seed="user-123")` |
| Cast I Ching reading | `roxy.iching.cast_reading()` |
| Hexagram detail | `roxy.iching.get_hexagram(number="1")` |
| Crystal by zodiac | `roxy.crystals.get_crystals_by_zodiac(sign="aries")` |
| Crystal by chakra | `roxy.crystals.get_crystals_by_chakra(chakra="heart")` |
| Dream symbol lookup | `roxy.dreams.get_dream_symbol(id="flying")` |
| Angel number meaning | `roxy.angel_numbers.get_angel_number(number="1111")` |
| Universal number lookup | `roxy.angel_numbers.analyze_number_sequence(number="1234")` |
| Find city coordinates | `roxy.location.search_cities(q="Berlin")` |
| Check API usage | `roxy.usage.get_usage_stats()` |
| List supported languages | `roxy.languages.list_languages()` |

## Field formats that trip agents

These are the fields AI agents most often get wrong. Copy the format column exactly.

| Field | Format | Good | Bad |
|-------|--------|------|-----|
| `timezone` | IANA string (typed kwarg) OR decimal number (inside a `dict[str, Any]`) | `"Asia/Kolkata"`, `"America/New_York"`, `"Europe/London"` as the top-level `timezone=` kwarg (server resolves to the DST-correct offset for the chart date). Decimal hours (`5.5`, `-5`, `0`) work as JSON numbers and are accepted only inside `person1`/`person2` dicts because the dict is typed `dict[str, Any]` - the top-level `timezone=` kwarg is typed `str`, so a quoted decimal like `"5.5"` is rejected server-side (validation_error). | `"5.5"` as `timezone=` (rejected, server expects IANA string or a JSON number), `"5:30"`, `"+0530"`, `"GMT-5"` |
| `date` | ISO date string | `"1990-01-15"` | `"Jan 15 1990"`, `datetime.now()`, `"15/01/1990"`, `"1990-1-15"` |
| `time` | 24-hour string | `"14:30:00"`, `"09:00:00"` | `"2:30 PM"`, `"14:30"` (no seconds), `"9:0:0"` (no leading zeros) |
| `latitude` | Decimal degrees (float) | `51.5074` (London), `-33.8688` (Sydney), `40.7128` (NYC) | `"28°36'N"`, `"28 36 50"`, strings |
| `longitude` | Decimal degrees (float) | `-0.1278` (London), `-74.006` (NYC), `139.6917` (Tokyo) | Same as latitude - no DMS strings |
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

Values are decimal hours. For the typed top-level `timezone=` kwarg, pass the IANA name from `roxy.location.search_cities` (`timezone="America/New_York"`) - the server resolves it to the correct DST offset for the chart date. Inside a `person1`/`person2` dict the bare decimal works because the dict is typed `dict[str, Any]`, so the JSON-number form below is accepted.


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

## Astrology domain gotchas for LLMs

LLMs hallucinate confidently in this category. These are the specific traps you will hit when writing client code:

- **Ayanamsa is server-side in Vedic.** LLMs default to tropical / Western math. Vedic endpoints apply sidereal Lahiri ayanamsa server-side. KP endpoints accept `ayanamsa` of `kp-newcomb` (default), `kp-old`, `lahiri`, or `custom`. Do not try to "correct" server output by subtracting ayanamsa in client code.
- **Tithi count is 30, not 2.** 15 Shukla (waxing) plus 15 Krishna (waning). Older LLM training data conflates Purnima and Amavasya as single tithis. Our panchang response carries a `paksha` field (`"Shukla"` or `"Krishna"`) plus a tithi number, so there are 30 distinct tithis in a lunar month.
- **Rahu and Ketu are shadow points, not planets.** They do not appear in a real ephemeris. Endpoints accept `node_type` of `true-node` or `mean-node` to select which calculation to use.
- **Nakshatra count is 27.** Abhijit is sometimes treated as a 28th in some schools, but this API uses the standard 27. `roxy.vedic_astrology.list_nakshatras()` returns a list of length 27.
- **Retrograde is per-planet, not global.** Natal chart planets and Vedic `meta` include `isRetrograde: bool` per planet. KP planet lists use `retrograde`. Never generate "Mercury retrograde globally" UI copy, check the specific planet in the response.
- **Tarot reversals are a product choice.** `allow_reversals=False` on a tarot draw means no reversed cards in that draw, period. It is not cosmically meaningful, it is a config flag.
- **Angel number lookup works for any positive integer.** Digit-root fallback covers non-canonical numbers. Do not generate validation logic that rejects anything other than `111` / `222` / `333`.
- **Seed-based daily endpoints are DETERMINISTIC per `(seed, date)` pair.** Same seed plus same date returns the same reading. This is by design for push-notification consistency. Do not describe it as "cached" or retry on stale responses.
- **Timezone affects Western calculations more than Vedic.** Western natal charts must respect DST at time of birth. Vedic endpoints default to IST (`5.5`) which is DST-free. Use `utcOffset` from the Location API response as your `timezone` kwarg, not the user's current clock.

## MCP equivalents

Every method has a matching MCP tool. The remote MCP server per domain is at `https://roxyapi.com/mcp/{domain}` (Streamable HTTP, no stdio / no self-hosting). Tool names follow `{method}_{path_snake_case}`, for example:

- `POST /astrology/natal-chart` -> `post_astrology_natal_chart` on `/mcp/astrology`
- `GET /astrology/horoscope/{sign}/daily` -> `get_astrology_horoscope_sign_daily` on `/mcp/astrology`
- `POST /vedic-astrology/birth-chart` -> `post_vedic_astrology_birth_chart` on `/mcp/vedic-astrology`
- `POST /tarot/spreads/celtic-cross` -> `post_tarot_spreads_celtic_cross` on `/mcp/tarot`

Use the SDK for typed Python apps. Use MCP for AI agents (Claude Desktop, Cursor MCP, OpenAI agents) where the agent selects tools based on user intent.

## Gotchas

- **Geocode first.** Any chart, panchang, synastry, compatibility, or natal endpoint needs coordinates. Call `roxy.location.search_cities` before the chart method.
- **All parameters are keyword arguments.** Use `sign="aries"` not positional `"aries"`.
- **Async methods end with `_async`.** Every sync method has a matching async variant.
- **Do not expose API keys client-side.** Call Roxy from server code only.
- **Date format is `YYYY-MM-DD`, time is `HH:MM:SS`.** Both are strings.
- **Western `timezone` is required** as an IANA string (`"Asia/Kolkata"`, `"America/New_York"`, `"Europe/London"`, `"UTC"`); the server resolves it to the DST-correct offset for the chart date. Vedic endpoints accept an optional `timezone` (same form) that defaults to IST when omitted. The decimal-number form (`5.5`) is also accepted by the API, but only inside `person1`/`person2` dicts - the top-level `timezone=` kwarg is typed `str`.
- **Errors raise `RoxyAPIError`.** Catch it and check `e.code`, `e.error`, and `e.status_code`.
- **Switch on `code`, not `error`.** Codes are stable. Messages may change.

## Links

- Interactive API docs: https://roxyapi.com/api-reference
- Pricing and API keys: https://roxyapi.com/pricing
- MCP for AI agents: https://roxyapi.com/docs/mcp
- TypeScript SDK: https://www.npmjs.com/package/@roxyapi/sdk
