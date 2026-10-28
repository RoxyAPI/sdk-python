# roxy-sdk (Python) - Agent Guide

Python SDK for RoxyAPI. 18+ domains (Western astrology, Vedic astrology, forecast, human design, Chinese astrology, feng shui, Mesoamerican astrology, Vastu, numerology, Kabbalah, tarot, biorhythm, Ayurveda, I Ching, crystals, dreams, angel numbers, location) plus utility namespaces (usage, languages). One API key, sync and async.

## Install and initialize

```bash
pip install roxy-sdk
```

```python
from roxy_sdk import create_roxy

# Retries 429, 500, 502, 503 and 504 by default. Optional settings, shown with their defaults:
# create_roxy(key, timeout=30.0, max_retries=2, initial_delay=0.5, max_delay=30.0)
roxy = create_roxy("your-api-key")
```

`create_roxy` sets the base URL (`https://roxyapi.com/api/v2`) and auth header automatically. Returns a `Roxy` instance with namespaced domain properties.

## Critical rule: geocode before any chart endpoint

Every chart, horoscope, panchang, dasha, dosha, navamsa, KP, synastry, compatibility, and natal endpoint needs `latitude`, `longitude`, and (for Western) `timezone`. **Never ask the user for coordinates.** Always call `roxy.location.search_cities` first.

```python
result = roxy.location.search_cities(q="New York")
city = result["cities"][0]
lat, lng, tz = city["latitude"], city["longitude"], city["timezone"]
# `timezone` is the IANA string ("America/New_York"). Pass it directly to any chart endpoint.
# The server resolves it to the DST-correct decimal offset using the date of the chart itself,
# so a January 1990 New York chart gets EST (-5) even when you looked the city up in July.
# city["utcOffset"] is the offset in force today, not on the birth date, so pass the IANA `timezone` string.
```

`q` accepts bare city (`"Paris"`), city + country (`"Berlin Germany"`), or comma-qualified (`"Springfield, Illinois"`). Use the qualified form to disambiguate same-named cities.

## Domains

Type `roxy.` to see all available namespaces. Type `roxy.{domain}.` in an IDE with a Python LSP to see every method.

<!-- BEGIN:DOMAINS -->
| Namespace | Methods | What it covers |
|-----------|---------|----------------|
| [`roxy.astrology`](https://roxyapi.com/api-reference/western-astrology) | 39 | Western astrology API for natal birth charts, daily, weekly, monthly, and yearly horoscopes with unique content per s... |
| [`roxy.vedic_astrology`](https://roxyapi.com/api-reference/vedic-astrology) | 58 | Vedic astrology (Jyotish) and KP API for kundli generation with the sixteen Shodasavarga divisional charts (D1 to D60... |
| [`roxy.forecast`](https://roxyapi.com/api-reference/forecast) | 5 | Astrology forecast API that merges upcoming transit aspects, sign ingresses, retrograde stations, new and full moons,... |
| [`roxy.human_design`](https://roxyapi.com/api-reference/human-design) | 12 | Human Design API that generates the full bodygraph from a birth moment: type, strategy, inner authority, profile, def... |
| [`roxy.chinese_astrology`](https://roxyapi.com/api-reference/chinese-astrology) | 16 | Chinese zodiac and BaZi astrology API: Four Pillars charts, Chinese zodiac signs and the Chinese lunisolar calendar f... |
| [`roxy.feng_shui`](https://roxyapi.com/api-reference/feng-shui) | 11 | Compute classical feng shui from one API: Xuan Kong flying star natal charts for any of the nine periods and 24 mount... |
| [`roxy.mesoamerican_astrology`](https://roxyapi.com/api-reference/mesoamerican-astrology) | 18 | Calculate Mayan astrology day signs, the Tzolkin sacred round, the Haab year, the full Long Count and the Aztec tonal... |
| [`roxy.vastu`](https://roxyapi.com/api-reference/vastu) | 10 | Vastu Shastra API for directional home and plot analysis: entrance padas with the classical effect of each of the 32... |
| [`roxy.numerology`](https://roxyapi.com/api-reference/numerology) | 20 | Numerology API for life path numbers, complete numerology charts and compatibility, in both Pythagorean and Chaldean... |
| [`roxy.kabbalah`](https://roxyapi.com/api-reference/kabbalah) | 12 | Kabbalah API for gematria, the 72 names, the Tree of Life and the Hebrew birthday |
| [`roxy.tarot`](https://roxyapi.com/api-reference/tarot) | 10 | Tarot reading API with the complete 78-card Rider-Waite-Smith deck and card meanings for love, career, health, and sp... |
| [`roxy.biorhythm`](https://roxyapi.com/api-reference/biorhythm) | 6 | Biorhythm API for entertainment and reflection, with 10 model cycle types across 3 primary (physical, emotional, inte... |
| [`roxy.ayurveda`](https://roxyapi.com/api-reference/ayurveda) | 8 | Ayurveda API for dosha profiles, the dinacharya daily routine and the ritucharya seasonal regimen, with a verse cited... |
| [`roxy.iching`](https://roxyapi.com/api-reference/i-ching) | 9 | I-Ching oracle API with all 64 hexagrams, 384 changing lines, 8 trigrams, and modern interpretations for love, career... |
| [`roxy.crystals`](https://roxyapi.com/api-reference/crystals-and-healing-stones) | 12 | Crystal healing API covering the most popular and widely-searched healing crystals and gemstones, from Amethyst and R... |
| [`roxy.dreams`](https://roxyapi.com/api-reference/dreams) | 5 | Dream interpretation API with a 2,200+ symbol dream dictionary and psychological meanings covering animals, objects,... |
| [`roxy.angel_numbers`](https://roxyapi.com/api-reference/angel-numbers) | 4 | Angel numbers API with meanings for 111, 222, 333, 444, 555, 666, 777, 888, 999, 1111, and 75+ sequences covering eve... |
| [`roxy.location`](https://roxyapi.com/api-reference/location-and-timezone) | 3 | Timezone and location API with city search and geocoding across 5,180,000+ cities, towns and villages in 240+ countri... |
| [`roxy.usage`](https://roxyapi.com/api-reference/usage) | 1 | Monitor your API usage, check rate limits, and track request consumption |
| [`roxy.languages`](https://roxyapi.com/api-reference/languages) | 2 | List the response languages accepted by the `lang` query parameter on every i18n-aware endpoint |
<!-- END:DOMAINS -->

## Quality guidelines for agents

The rules to follow when writing any call with this SDK. Get these right and the generated signatures do the rest.

- **Responses are dicts.** Every method returns `dict[str, Any]`. Access fields with `result["key"]["subkey"]`, never `result.key.subkey` (Python will raise `AttributeError: 'dict' object has no attribute ...`).
- **Method names are snake_case versions of the OpenAPI operationId** (e.g. `castThreeCard` -> `cast_three_card`, `analyzeNumberSequence` -> `analyze_number_sequence`). Every sync method has an `_async` variant; use `await` with the async variants.
- **Param names are snake_case versions of the spec param names** (`fullName` -> `full_name`, `birthDate` -> `birth_date`, `houseSystem` -> `house_system`). All params are keyword-only.
- **When in doubt about a method or kwarg, read the generated signatures.** Check `roxy_sdk.factory` directly or run `python -c "from roxy_sdk import Roxy; help(Roxy)"` - the generated signatures are the contract.
- **Response field names come from the response schema of the spec.** They match it exactly. Never invent or pluralize. If a field is not in the spec, it is not in the response.
- **Look up any operation or field beyond this guide.** Query the combined OpenAPI spec at `https://roxyapi.com/api/v2/openapi.json` with the jq recipe in `https://roxyapi.com/AGENTS.md`, or search the keyless Docs MCP server at `https://roxyapi.com/mcp/docs` (one tool, `search_docs`).
- **Strings everywhere.** `date` is `"YYYY-MM-DD"`, `time` is `"HH:MM:SS"`, `timezone` is an IANA name (`"Asia/Kolkata"`, `"America/New_York"`) - the server resolves DST for the chart date. `number` (angel) is `"1111"`, `month` (birthstone) is `"1"`, `number` (hexagram) is `"1"`. Numeric kwargs are only `latitude`, `longitude`, `year`, `month` (numerology), `day`, `count` (tarot draw).
- **Nested dicts accept any value type.** Inside `person1` / `person2` dicts any value type works because the kwarg is typed `dict[str, Any]`; only the top-level `timezone` kwarg needs string form.
- **Do not hand-roll requests.** No raw HTTP calls. The SDK injects auth, the base URL and the error type; it retries 429, 500, 502, 503 and 504 up to twice by default (see Retries; `create_roxy(key, max_retries=0)` turns that off).

## Critical patterns

### Two-step pattern for coordinate-dependent endpoints

```python
result = roxy.location.search_cities(q="London")
city = result["cities"][0]

chart = roxy.astrology.generate_natal_chart(
    date="1990-01-15",
    time="14:30:00",
    latitude=city["latitude"],
    longitude=city["longitude"],
    timezone=city["timezone"],  # IANA string, server resolves DST for the date
)
```

One lookup feeds every domain. The same `birth` dict, spread with `**birth`, is the kwargs for `astrology.generate_natal_chart`, `vedic_astrology.generate_birth_chart`, `vedic_astrology.get_current_dasha`, `ayurveda.calculate_ayurvedic_constitution`, and it is the `birth_data` kwarg of `forecast.forecast_transits`; the instant alone (`date`, `time`, `timezone`) is the kwargs for `human_design.generate_bodygraph`, `chinese_astrology.generate_bazi_chart`, and `kabbalah.generate_birth_profile`. Never look the city up twice for one person.

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
    date="1990-01-15",
    time="14:30:00",
    latitude=40.7128,
    longitude=-74.006,
    timezone="America/New_York",
)

kundli = roxy.vedic_astrology.generate_birth_chart(
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

### Multi-language via `lang` kwarg

<!-- BEGIN:LANGS -->
10 languages: `en`, `tr`, `de`, `es`, `hi`, `pt`, `fr`, `ru`, `zh-Hans`, `zh-Hant`. Defaults to `en`. Supported: `astrology`, `vedic_astrology`, `forecast`, `human_design`, `chinese_astrology`, `feng_shui`, `mesoamerican_astrology`, `vastu`, `numerology`, `kabbalah`, `tarot`, `biorhythm`, `ayurveda`, `iching`, `crystals`, `angel_numbers`, `languages`. English-only: `dreams`, `location`, `usage`.
<!-- END:LANGS -->

```python
card = roxy.tarot.get_daily_card(date="2026-04-22", lang="es")
life_path = roxy.numerology.calculate_life_path(year=1990, month=1, day=15, lang="hi")
```

The two Chinese scripts (`zh-Hans`, `zh-Hant`) currently ship on Chinese astrology and feng shui; every other domain answers those codes in English per field. To list supported codes at runtime, call `roxy.languages.list_languages()`.

## Common tasks

In the catalog order (Western astrology, Vedic astrology, forecast, Human Design, Chinese astrology, feng shui, Mesoamerican astrology, Vastu, numerology, Kabbalah, tarot, biorhythm, Ayurveda, I Ching, crystals, dreams, angel numbers, location, usage, languages). `birth` is `{"date": ..., "time": ..., "latitude": ..., "longitude": ..., "timezone": ...}` from the two-step pattern above.

| Task | Code |
|------|------|
| Find city coordinates (do this first) | `roxy.location.search_cities(q="Berlin")` |
| Daily horoscope | `roxy.astrology.get_daily_horoscope(sign=sign)` |
| Natal chart (Western) | `roxy.astrology.generate_natal_chart(**birth)` |
| Synastry | `roxy.astrology.calculate_synastry(person1=person1, person2=person2)` |
| Compatibility score | `roxy.astrology.calculate_compatibility(person1=person1, person2=person2)` |
| Current moon phase | `roxy.astrology.get_current_moon_phase()` |
| Transits | `roxy.astrology.calculate_transits(natal_chart=natal_chart)` |
| Kundli (Vedic birth chart) | `roxy.vedic_astrology.generate_birth_chart(**birth)` |
| Panchang (detailed) | `roxy.vedic_astrology.get_detailed_panchang(date=date, latitude=latitude, longitude=longitude, timezone=timezone)` |
| Choghadiya | `roxy.vedic_astrology.get_choghadiya(date=date, latitude=latitude, longitude=longitude, timezone=timezone)` |
| Current dasha | `roxy.vedic_astrology.get_current_dasha(**birth)` |
| Mangal Dosha | `roxy.vedic_astrology.check_manglik_dosha(**birth)` |
| Guna Milan (matching) | `roxy.vedic_astrology.calculate_gun_milan(person1=person1, person2=person2)` |
| Navamsa (D9) | `roxy.vedic_astrology.generate_navamsa(**birth)` |
| KP chart | `roxy.vedic_astrology.generate_kp_chart(**birth)` |
| KP ruling planets | `roxy.vedic_astrology.get_kp_ruling_planets(latitude=latitude, longitude=longitude, timezone=timezone)` |
| Nakshatra detail | `roxy.vedic_astrology.get_nakshatra(id="ashwini")` |
| Transit forecast | `roxy.forecast.forecast_transits(birth_data=birth, start_date=start_date, end_date=end_date)` |
| Cross-domain timeline | `roxy.forecast.generate_timeline(birth_data=birth, start_date=start_date, end_date=end_date)` |
| Human Design bodygraph | `roxy.human_design.generate_bodygraph(date=date, time=time, timezone=timezone)` |
| Human Design connection | `roxy.human_design.calculate_connection(person_a=person_a, person_b=person_b)` |
| BaZi Four Pillars | `roxy.chinese_astrology.generate_bazi_chart(date=date, time=time, timezone=timezone)` |
| Chinese zodiac animal | `roxy.chinese_astrology.calculate_zodiac_animal(date=date)` |
| Almanac day (Tong Shu) | `roxy.chinese_astrology.get_almanac_day(date=date)` |
| Kua number | `roxy.feng_shui.calculate_kua_number(date=date, gender=gender)` |
| Flying star natal chart | `roxy.feng_shui.generate_flying_star_chart(period=period, facing=facing)` |
| Tzolkin day sign | `roxy.mesoamerican_astrology.calculate_tzolkin(date=date)` |
| Full Maya chart | `roxy.mesoamerican_astrology.generate_mayan_chart(date=date)` |
| Vastu entrance | `roxy.vastu.calculate_entrance_pada(plot=plot, facing=facing, door_position=door_position)` |
| Vastu room compliance | `roxy.vastu.calculate_room_compliance(plot=plot, facing=facing, rooms=rooms)` |
| Life path number | `roxy.numerology.calculate_life_path(year=year, month=month, day=day)` |
| Full numerology chart | `roxy.numerology.generate_numerology_chart(full_name=full_name, year=year, month=month, day=day)` |
| Personal year | `roxy.numerology.calculate_personal_year(month=month, day=day)` (`year` is optional, 100 to 2100, and defaults to the current UTC year) |
| Gematria | `roxy.kabbalah.calculate_gematria(text=text)` |
| Kabbalah birth profile | `roxy.kabbalah.generate_birth_profile(date=date, time=time, timezone=timezone)` |
| Daily tarot card | `roxy.tarot.get_daily_card(seed=seed)` |
| Three-card spread | `roxy.tarot.cast_three_card(question=question)` |
| Celtic Cross | `roxy.tarot.cast_celtic_cross(question=question)` |
| Yes / no tarot | `roxy.tarot.cast_yes_no(question=question)` |
| Biorhythm reading | `roxy.biorhythm.get_reading(birth_date=birth_date)` |
| Daily biorhythm reading | `roxy.biorhythm.get_daily_biorhythm(seed=seed)` |
| Biorhythm forecast | `roxy.biorhythm.get_forecast(birth_date=birth_date)` |
| Biorhythm compatibility | `roxy.biorhythm.calculate_bio_compatibility(person1=person1, person2=person2)` |
| Ayurvedic constitution | `roxy.ayurveda.calculate_ayurvedic_constitution(**birth)` |
| Dinacharya | `roxy.ayurveda.get_dinacharya_schedule(date=date, latitude=latitude, longitude=longitude, timezone=timezone)` |
| Daily hexagram | `roxy.iching.get_daily_hexagram(seed=seed)` |
| Cast I Ching reading | `roxy.iching.cast_reading()` |
| Hexagram detail | `roxy.iching.get_hexagram(number="1")` |
| Crystal by zodiac | `roxy.crystals.get_crystals_by_zodiac(sign=sign)` |
| Crystal by chakra | `roxy.crystals.get_crystals_by_chakra(chakra=chakra)` |
| Dream symbol lookup | `roxy.dreams.get_dream_symbol(id="flying")` |
| Angel number meaning | `roxy.angel_numbers.get_angel_number(number="1111")` |
| Universal number lookup | `roxy.angel_numbers.analyze_number_sequence(number="1234")` |
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
| `sign` (horoscope kwarg) | Lowercase zodiac name | `"aries"`, `"taurus"`, `"gemini"`, ... `"pisces"` | `"♈"`, `"1"` (the server matches case-insensitively, so `"Aries"` and `"ARIES"` work, but lowercase is canonical) |
| `full_name` (numerology) | Birth-certificate name | `"John William Smith"`, `"Priya Rajesh Sharma"` | Nickname, married name, partial name - affects all letter-based calcs |
| `seed` | Any string (deterministic) | `"user-42"`, `"session-abc-123"`, email hash | Numbers, objects - must be string |
| `number` (angel numbers) | String | `"1111"`, `"777"`, `"1234"` | `1111` (int) fails path validation |
| `id` (nakshatra / dream / tarot) | Slug | `"ashwini"`, `"flying"`, `"the-fool"`, `"three-of-cups"` | Display names, uppercase, spaces |
| `house_system` | Enum string | `"placidus"` (default), `"whole-sign"`, `"equal"`, `"koch"` | `"Placidus"`, `"whole_sign"`, `"WS"` |
| `ayanamsa` (KP) | Enum string | `"kp-newcomb"` (default), `"kp-old"`, `"lahiri"`, `"custom"` | `"KP"`, `"New Comb"`, `"Lahiri"` |
| `node_type` | Enum string | `"mean"` (smoothed node, traditional Vedic default), `"true"` (osculating node with perturbation corrections) | `"true-node"`, `"mean-node"`, `"True Node"` |
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
| Berlin / Paris | `1` (winter) / `2` (summer) | Delhi (IST) | `5.5` |
| Istanbul | `3` | Kathmandu (NPT) | `5.75` |
| Moscow | `3` | Dhaka | `6` |
| Tehran | `3.5` (winter) / `4.5` (summer) | Bangkok | `7` |
| Adelaide | `9.5` (winter) / `10.5` (summer) | Singapore / Beijing | `8` |
| New York (EST / EDT) | `-5` / `-4` | Tokyo | `9` |
| Chicago (CST / CDT) | `-6` / `-5` | Sydney | `10` (winter) / `11` (summer) |
| Denver (MST / MDT) | `-7` / `-6` | Auckland | `12` (winter) / `13` (summer) |
| Los Angeles (PST / PDT) | `-8` / `-7` | Honolulu | `-10` |

DST matters. If the birth date falls inside a daylight-saving window, use the summer / DST offset, or pass the IANA string from the location lookup and let the server resolve it. India observes no DST, so a fixed `5.5` is always right there; anywhere else, a natal chart must carry the offset in force at the time of birth.

## Astrology domain gotchas for LLMs

LLMs hallucinate confidently in this category. These are the specific traps you will hit when writing client code:

- **Ayanamsa is server-side in Vedic.** LLMs default to tropical / Western math. Vedic endpoints apply sidereal Lahiri ayanamsa server-side. KP endpoints accept `ayanamsa` of `kp-newcomb` (default), `kp-old`, `lahiri`, or `custom`. Do not try to "correct" server output by subtracting ayanamsa in client code.
- **Tithi count is 30, not 2.** 15 Shukla (waxing) plus 15 Krishna (waning). Older LLM training data conflates Purnima and Amavasya as single tithis. Our panchang response carries a `paksha` field (`"Shukla"` or `"Krishna"`) plus a tithi number, so there are 30 distinct tithis in a lunar month.
- **Rahu and Ketu are shadow points, not planets.** They do not appear in a real ephemeris. Endpoints accept `node_type` of `"mean"` (smooth mean node, traditional Vedic default) or `"true"` (osculating node with perturbation corrections) to select which calculation to use.
- **Nakshatra count is 27.** Abhijit is sometimes treated as a 28th in some schools, but this API uses the standard 27. `roxy.vedic_astrology.list_nakshatras()` returns a list of length 27.
- **Retrograde is per-planet, not global.** Natal chart planets and Vedic `meta` include `isRetrograde: bool` per planet. KP planet lists use `retrograde`. Never generate "Mercury retrograde globally" UI copy, check the specific planet in the response.
- **Tarot reversals are a product choice.** `allow_reversals=False` on a tarot draw means no reversed cards in that draw, period. It is not cosmically meaningful, it is a config flag.
- **Angel number lookup works for any positive integer.** Digit-root fallback covers non-canonical numbers. Do not generate validation logic that rejects anything other than `111` / `222` / `333`.
- **Seed-based daily endpoints are DETERMINISTIC per `(seed, date)` pair.** Same seed plus same date returns the same reading. This is by design for push-notification consistency. Do not describe it as "cached" or retry on stale responses.
- **Timezone affects Western calculations more than Vedic.** Western natal charts must respect DST at the time of birth. Vedic endpoints default to IST (`5.5`) which is DST-free. Pass the IANA `timezone` string from the location lookup (`"America/New_York"`, `"Asia/Kolkata"`) directly to chart calls and the server resolves the DST-correct offset for the chart `date`. Never pass the `utcOffset` of the city record (the offset in force today) or the clock of the user right now.

## Error handling

Errors raise `RoxyAPIError` with `error` (message), `code` (machine-readable), `status_code`, `doc_url` (documentation for the code), `retry_after` (seconds from the `Retry-After` header, or `None`) and `issues` (the failing fields of a `validation_error`, otherwise `None`). `ErrorCode` is a string enum of every code below, so `e.code == ErrorCode.RATE_LIMIT_PER_MINUTE` works:

```python
from roxy_sdk import create_roxy, ErrorCode, RoxyAPIError

try:
    result = roxy.astrology.get_daily_horoscope(sign="invalid")
except RoxyAPIError as e:
    if e.code == ErrorCode.VALIDATION_ERROR:
        for issue in e.issues or []:
            print(issue["path"], issue["message"], issue["code"])  # path is the dot-separated field, e.g. "time" or "person1.date"
    print(e.code)  # "validation_error"
    print(e.status_code)  # 400
```

<!-- BEGIN:ERRORS -->
Every error returns `{ error, code, doc_url }`. Switch on `code`; `error` is readable text and may change. Each meaning below says whether and when to retry, and `Retry-After` carries the wait when the response sends it. Every code is documented at https://roxyapi.com/docs/errors.

| Status | Code | Meaning |
|--------|------|---------|
| 400 | `validation_error` | A field is missing or invalid. The body lists every failing field at once in issues, each with its path and the expected shape. |
| 400 | `bad_request` | The request was rejected as a whole, for example a body that is not valid JSON or a date range that ends before it starts. |
| 400 | `date_out_of_range` | A date lies outside the span the planetary positions are served for. The error names the supported dates. |
| 401 | `api_key_required` | No API key was sent. |
| 401 | `invalid_api_key` | The key sent is malformed or cannot be verified. |
| 401 | `api_key_revoked` | The key was valid once and has since been revoked from the account page. |
| 401 | `subscription_not_found` | The key verifies, but the subscription behind it no longer exists. |
| 401 | `subscription_inactive` | The subscription behind the key is cancelled, expired or suspended, or a trial is past its end date. |
| 401 | `publishable_key_not_allowed_on_mcp` | A publishable key was used on a Remote MCP server, which takes a secret key. |
| 401 | `invalid_client_ip` | A keyless request could not be attributed to a caller. |
| 401 | `unauthorized` | Authentication failed with no more specific reason to give. |
| 403 | `forbidden` | The key is valid, but this request is not permitted. |
| 403 | `origin_required` | A publishable key with an origin allowlist was used with no Origin header, as from a server or a native app. |
| 403 | `origin_not_allowed` | The calling site is not on the origin allowlist of this publishable key. |
| 404 | `not_found` | Nothing is served at this path, or the identifier in it does not exist. A path miss adds suggestions, the closest real endpoints. |
| 405 | `method_not_allowed` | The path exists for a different HTTP method. The body lists the accepted methods in allow, as does the Allow header. |
| 409 | `conflict` | The request cannot be applied in the current state. |
| 410 | `gone` | The path was removed permanently. |
| 413 | `payload_too_large` | The request body is larger than the API accepts. A body far over the cap is refused before it reaches the API and returns a bare 413 with no JSON body. |
| 415 | `unsupported_media_type` | A request with a body was sent without Content-Type: application/json. |
| 422 | `unprocessable_entity` | Every field is valid, but the combination cannot be computed. |
| 429 | `rate_limit_exceeded` | The monthly request allowance is used up. Retry-After gives the seconds to the reset. |
| 429 | `rate_limit_per_minute` | The per-minute limit of the plan was reached. Retry-After gives the seconds to the next minute, and the monthly allowance is not charged. |
| 429 | `rate_limited` | A rate limit was reached, reported without the plan detail. |
| 429 | `free_tier_exhausted` | A keyless request has used up its trial allowance. |
| 500 | `internal_error` | The request failed inside our service. Retry with exponential backoff. |
| 503 | `compute_saturated` | Heavy calculations are briefly at capacity. Send the same request again after Retry-After seconds. |
| Any | `error` | A fallback for a status with no more specific code. The status and the error field carry the signal. |
<!-- END:ERRORS -->

### Retries

The client retries twice by default: HTTP 429, 500, 502, 503 and 504, plus connection failures where the request was never sent. Pass `max_retries` to change the count, or `max_retries=0` to turn retries off. Waits use the `Retry-After` header when present, otherwise jittered exponential backoff from `initial_delay` (default 0.5 seconds) up to `max_delay` (default 30 seconds). A `Retry-After` longer than `max_delay`, such as the one on `rate_limit_exceeded`, is not waited out: the error is raised with `retry_after` set. A retry never sleeps past `timeout`. Read timeouts are never retried.

```python
from roxy_sdk import create_roxy, RoxyAPIError

roxy = create_roxy("your-api-key", max_retries=4)

try:
    result = roxy.astrology.get_daily_horoscope(sign="aries")
except RoxyAPIError as e:
    print(e.code)  # "rate_limit_per_minute", "compute_saturated", "validation_error", ...
    print(e.doc_url)  # documentation page for that code
    print(e.retry_after)  # seconds the server asked you to wait, or None
```

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
- **A `validation_error` carries `issues`, each with `path` (the dot-separated field, such as `time` or `person1.date`), `message` and `code`.** Loop over them to show every failing field:
  ```python
  except RoxyAPIError as e:
      for issue in e.issues or []:
          print(issue["path"], issue["message"], issue["code"])
  ```
- **Switch on `e.code`, not `e.error`.** The message may change; the code is stable.
- **A city record has `city`, `province`, `country`, `iso2`, `latitude`, `longitude`, `timezone`, `utcOffset` and `population`.** The name is `city`, never `name`.
- **`utcOffset` on a city record is the offset in force today.** Pass the IANA `timezone` string to chart calls so the server resolves the offset for the birth date.
- **A natal chart `planets` is a list of objects.** Find a body by `name`: `next(p for p in chart["planets"] if p["name"] == "Moon")`.
- **In a Vedic chart `meta.Moon.rashi` is a string and `meta.Moon.nakshatra` is an object** (`name`, `pada`, `lord`). Display `kundli["meta"]["Moon"]["nakshatra"]["name"]`.
- **`sign` is matched case-insensitively.** Lowercase is canonical.
- **Total requests on a persistent failure = 1 + retries.** The default `max_retries` of 2 makes 3 requests; `max_retries=0` makes exactly one.
- **List endpoints return a paginated envelope**, `{"total": ..., "limit": ..., "offset": ...}` plus a named list (`cities`, `crystals`, `hexagrams`, `symbols`), never a bare list. Pass `limit=` to widen a page; `list_hexagrams` defaults to 20 of 64.

## Links

- Documentation: https://roxyapi.com/docs
- Interactive API docs: https://roxyapi.com/api-reference
- Pricing and API keys: https://roxyapi.com/pricing
- MCP for AI agents: https://roxyapi.com/docs/mcp
- Templates: https://roxyapi.com/templates
- Source and issues: https://github.com/RoxyAPI/sdk-python
- Other SDKs: TypeScript https://www.npmjs.com/package/@roxyapi/sdk, PHP https://packagist.org/packages/roxyapi/sdk, .NET https://www.nuget.org/packages/RoxyApi.Sdk, Go https://pkg.go.dev/github.com/RoxyAPI/sdk-go, Rust https://crates.io/crates/roxyapi
