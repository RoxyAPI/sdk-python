<p align="center">
  <a href="https://roxyapi.com">
    <img src="https://raw.githubusercontent.com/RoxyAPI/sdk-python/main/assets/hero.png" alt="Roxy Python SDK. Astrology, Vedic, tarot, numerology, and more behind one API key." width="100%">
  </a>
</p>

# roxy-sdk

[![PyPI](https://img.shields.io/pypi/v/roxy-sdk)](https://pypi.org/project/roxy-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/roxy-sdk)](https://pypi.org/project/roxy-sdk/)
[![Docs](https://img.shields.io/badge/docs-roxyapi.com-blue)](https://roxyapi.com/docs)
[![API Reference](https://img.shields.io/badge/api%20reference-roxyapi.com-blue)](https://roxyapi.com/api-reference)
[![License](https://img.shields.io/github/license/RoxyAPI/sdk-python)](https://github.com/RoxyAPI/sdk-python/blob/main/LICENSE)

Python SDK for astrology, Vedic astrology, tarot, numerology, and more.

One API key. Sync and async (every method has an `_async` suffix). Verified against NASA JPL Horizons.

The fastest way to add natal charts, daily horoscopes, synastry, Vedic kundli, tarot spreads, numerology, human design bodygraphs, and transit forecasts to FastAPI, Django, Flask, or any Python project. 18+ domains behind a single [Roxy](https://roxyapi.com) subscription, interpretations in 10+ languages.

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
result = roxy.location.search_cities(q="London, UK")
city = result["cities"][0]
lat, lng, tz = city["latitude"], city["longitude"], city["timezone"]

# Step 2: Western natal chart. `timezone` can be the IANA string ("Europe/London").
# The server resolves it to the DST-correct offset for the date of the chart.
natal = roxy.astrology.generate_natal_chart(
    date="1990-01-15",
    time="14:30:00",
    latitude=lat,
    longitude=lng,
    timezone=tz,
)

# Vedic kundli takes the same inputs (timezone optional, defaults to 5.5 IST).
kundli = roxy.vedic_astrology.generate_birth_chart(
    date="1990-01-15",
    time="14:30:00",
    latitude=lat,
    longitude=lng,
    timezone=tz,
)
```

Get your API key at [roxyapi.com/pricing](https://roxyapi.com/pricing). Free test keys available on the [interactive docs](https://roxyapi.com/api-reference).

## Domain reference

<!-- BEGIN:DOMAINS -->
| Domain | Property | Methods | What it covers |
|--------|----------|---------|----------------|
| Western Astrology | `roxy.astrology` | 39 | Western astrology API for natal birth charts, daily, weekly, monthly, and yearly horoscopes with unique content per s... |
| Vedic Astrology | `roxy.vedic_astrology` | 56 | Vedic astrology (Jyotish) and KP API for kundli generation with 15 divisional charts (D1-D60), panchang with choghadi... |
| Forecast | `roxy.forecast` | 5 | Astrology forecast API that merges upcoming transit aspects, sign ingresses, retrograde stations, new and full moons,... |
| Human Design | `roxy.human_design` | 12 | Human Design API that generates the full bodygraph from a birth moment: type, strategy, inner authority, profile, def... |
| Chinese Astrology | `roxy.chinese_astrology` | 16 | Chinese zodiac and BaZi astrology API: Four Pillars charts, Chinese zodiac signs and the Chinese lunisolar calendar f... |
| Feng Shui | `roxy.feng_shui` | 11 | Compute classical feng shui from one API: Xuan Kong flying star natal charts for any of the nine periods and 24 mount... |
| Mesoamerican Astrology | `roxy.mesoamerican_astrology` | 18 | Calculate Mayan astrology day signs, the Tzolkin sacred round, the Haab year, the full Long Count and the Aztec tonal... |
| Vastu | `roxy.vastu` | 10 | Vastu Shastra API for directional home and plot analysis: entrance padas with the classical effect of each of the 32... |
| Numerology | `roxy.numerology` | 20 | Numerology API to calculate life path, expression, soul urge, personality, and maturity numbers, with Pinnacle and Ch... |
| Kabbalah | `roxy.kabbalah` | 12 | Kabbalah API for gematria, the 72 names, the Tree of Life and the Hebrew birthday, from one key |
| Tarot | `roxy.tarot` | 10 | Tarot reading API with the complete 78-card Rider-Waite-Smith deck and card meanings for love, career, health, and sp... |
| Biorhythm | `roxy.biorhythm` | 6 | The most complete biorhythm API: 10 cycle types across 3 primary (physical, emotional, intellectual), 4 secondary (in... |
| Ayurveda | `roxy.ayurveda` | 8 | Ayurveda API for dosha profiles, the dinacharya daily routine and the ritucharya seasonal regimen, with a verse cited... |
| I Ching | `roxy.iching` | 9 | I-Ching oracle API with all 64 hexagrams, 384 changing lines, 8 trigrams, and modern interpretations for love, career... |
| Crystals | `roxy.crystals` | 12 | Crystal healing API covering the most popular and widely-searched healing crystals and gemstones, from Amethyst and R... |
| Dreams | `roxy.dreams` | 5 | Dream interpretation API with a 2,000+ symbol dream dictionary and psychological meanings covering animals, objects,... |
| Angel Numbers | `roxy.angel_numbers` | 4 | Angel numbers API with meanings for 111, 222, 333, 444, 555, 666, 777, 888, 999, 1111, and 75+ sequences covering eve... |
| Location | `roxy.location` | 3 | Timezone and location API with city search and geocoding across 235,000+ cities in 240+ countries, returning latitude... |
| Usage | `roxy.usage` | 1 | Monitor your API usage, check rate limits, and track request consumption |
| Languages | `roxy.languages` | 2 | List the response languages accepted by the `lang` query parameter on every i18n-aware endpoint |
<!-- END:DOMAINS -->

## Most-used endpoints

The highest-demand endpoints by domain, in the order you are most likely to ship them. Every example below reads the same birth through a different domain, and every coordinate comes from one location lookup at the top: one API key, one lookup, and eighteen domains that compose into a single product instead of eighteen separate ones. Full catalog in the [API reference](https://roxyapi.com/api-reference).

### Location first: one lookup feeds every chart

Every chart, horoscope, panchang, dasha, dosha, synastry and compatibility endpoint needs `latitude`, `longitude` and `timezone`. Never ask users to type coordinates. Look the city up once and reuse the result in every domain below.

```python
# One lookup feeds every chart below. `timezone` is the IANA name from the city
# record; the server resolves it to the DST-correct offset for the date of each chart.
place = roxy.location.search_cities(q="New York")
city = place["cities"][0]
latitude, longitude, timezone = city["latitude"], city["longitude"], city["timezone"]
birth = {"date": "1990-01-15", "time": "14:30:00", "latitude": latitude, "longitude": longitude, "timezone": timezone}

# A second person for the two-chart calls (synastry, Guna Milan, Human Design connection).
london = roxy.location.search_cities(q="London")
london_city = london["cities"][0]
lat2, lon2, tz2 = london_city["latitude"], london_city["longitude"], london_city["timezone"]
partner = {"date": "1992-07-22", "time": "09:00:00", "latitude": lat2, "longitude": lon2, "timezone": tz2}
```

### 1. Western astrology API (natal chart, daily horoscope, synastry)

Natal chart products, daily horoscope features, dating and compatibility apps, and lunar-cycle wellness apps start here.

```python
# Natal chart. The most requested Western call, run once at onboarding.
# `birth` carries the latitude, longitude and timezone from the location lookup above.
natal = roxy.astrology.generate_natal_chart(**birth)
# natal["planets"][n]["name"], ["sign"], ["house"], ["interpretation"]["summary"]; natal["ascendant"]["sign"]; natal["aspects"]

# Daily horoscope. The highest per-user call frequency in the catalog: daily content, streaks, push.
horoscope = roxy.astrology.get_daily_horoscope(sign="aries")
# horoscope["overview"], horoscope["love"], horoscope["career"], horoscope["column"], horoscope["events"], horoscope["luckyNumber"]

# Synastry. Full inter-aspect analysis between two charts, the relationship feature of dating apps.
synastry = roxy.astrology.calculate_synastry(person1=birth, person2=partner)
# synastry["compatibilityScore"], synastry["interAspects"], synastry["analysis"]["strengths"]

# Moon phase. A zero-setup call for wellness, cycle-tracking and meditation apps.
moon = roxy.astrology.get_current_moon_phase()
# moon["phase"], moon["illumination"], moon["sign"], moon["meaning"]["description"]
```

### 2. Vedic astrology API (kundli, panchang, dasha, Guna Milan, KP)

Kundli generators, matrimonial matching, muhurta and panchang apps, and KP practitioners. The same `birth` object, read sidereally.

```python
# Vedic kundli. The same birth read sidereally: `birth` reuses the location lookup above.
kundli = roxy.vedic_astrology.generate_birth_chart(**birth)
# kundli["meta"]["Moon"]["rashi"], kundli["meta"]["Moon"]["nakshatra"], kundli["houses"], kundli["combustion"]

# Detailed panchang. Tithi, nakshatra, yoga, karana, rahu kaal and the muhurtas for a date and place.
panchang = roxy.vedic_astrology.get_detailed_panchang(date="2026-10-01", latitude=latitude, longitude=longitude, timezone=timezone)
# panchang["tithi"], panchang["nakshatra"], panchang["rahuKaal"], panchang["abhijitMuhurta"]

# Vimshottari dasha. The mahadasha, antardasha and pratyantardasha running right now.
dasha = roxy.vedic_astrology.get_current_dasha(**birth)
# dasha["mahadasha"], dasha["antardasha"], dasha["remainingInMahadasha"]

# Mangal Dosha. The most asked matrimonial check.
dosha = roxy.vedic_astrology.check_manglik_dosha(**birth)
# dosha["present"]; dosha["severity"] and dosha["remedies"] are set only when present is true

# Guna Milan. The 36-point Ashtakoota score behind kundli matching, both people from the lookups above.
milan = roxy.vedic_astrology.calculate_gun_milan(person1=birth, person2=partner)
# milan["total"], milan["percentage"], milan["isCompatible"], milan["breakdown"]

# KP ruling planets. Horary answers at the moment of the question, for the place looked up above.
kp = roxy.vedic_astrology.get_kp_ruling_planets(latitude=latitude, longitude=longitude, timezone=timezone)
# kp["dayLord"], kp["moonSublord"], kp["rulingPlanets"]
```

### 3. Astrology forecast API (transit forecast, cross-domain timeline)

Forecast feeds, transit alerts and timing tools. One call returns a dated, significance-scored event list; the timeline variant merges Vedic dasha boundaries and biorhythm critical days into the same list, which no single-domain API can do.

```python
# Transit forecast. Transit-to-natal aspects, sign ingresses and retrograde stations over a window.
# `birth_data` is the same `birth` object: date, time, latitude, longitude, timezone.
transits = roxy.forecast.forecast_transits(birth_data=birth, start_date="2026-10-01", end_date="2026-10-31")
# transits["count"], transits["events"][n]["date"], ["type"], ["body"], ["target"], ["aspect"], ["significance"]

# Cross-domain timeline. The same window with Vedic dasha boundaries and biorhythm critical days merged in.
timeline = roxy.forecast.generate_timeline(birth_data=birth, start_date="2026-10-01", end_date="2026-10-31")
# timeline["events"][n]["domain"] ("western" | "vedic" | "biorhythm"), ["description"], ["significance"]
```

### 4. Human Design API (bodygraph, connection)

Self-discovery apps, coaching bots and compatibility products. The full bodygraph is one call, and the Design side is solved on the exact 88-degree solar arc rather than approximated as calendar days.

```python
# Bodygraph. Type, strategy, authority, profile, definition, centers, channels and all 26 gates in one call.
# Human Design needs only the birth instant, so it takes the date, time and timezone from the lookup above.
hd = roxy.human_design.generate_bodygraph(date=birth["date"], time=birth["time"], timezone=birth["timezone"])
# hd["type"], hd["strategy"], hd["authority"], hd["profile"], hd["definition"], hd["incarnationCross"]["name"], hd["centers"], hd["channels"], hd["gates"]

# Connection. Two bodygraphs combined, each of the 36 channels classified by how the pair forms it.
connection = roxy.human_design.calculate_connection(
    person_a={"date": birth["date"], "time": birth["time"], "timezone": birth["timezone"]},
    person_b={"date": partner["date"], "time": partner["time"], "timezone": partner["timezone"]},
)
# connection["totalChannels"], connection["summary"]["electromagnetic"], connection["combinedDefinition"]
```

### 5. Chinese zodiac API (BaZi four pillars, zodiac animal, almanac)

BaZi readings, zodiac content and Tong Shu date pages. The school splits that make two calculators disagree (`day_boundary`, `year_boundary`, `hour_clock`) are typed keyword arguments with named defaults.

```python
# BaZi Four Pillars. The anchor call of the domain, from the same birth instant as every chart above.
# Each response echoes the `conventions` it was computed under, so a chart can be reproduced, not guessed.
bazi = roxy.chinese_astrology.generate_bazi_chart(date=birth["date"], time=birth["time"], timezone=birth["timezone"])
# bazi["pillars"][n]["position"] ("year" | "month" | "day" | "hour"), ["stem"]["element"], ["branch"]["animal"], ["tenGod"]["name"]
# bazi["dayMaster"]["element"], bazi["zodiacAnimal"], bazi["fiveElements"], bazi["conventions"]

# Chinese zodiac animal. Defaults `year_boundary` to the Lunar New Year, the folk rule people mean
# when they ask which animal they are. Pass "li-chun" for the classical BaZi boundary.
animal = roxy.chinese_astrology.calculate_zodiac_animal(date=birth["date"])
# animal["animal"]["name"], animal["animal"]["element"], animal["element"] (the year stem element), animal["interpretation"]

# Almanac day. The Tong Shu view of a date: day officer, mansion, clash animal, favours and avoids.
almanac = roxy.chinese_astrology.get_almanac_day(date="2026-10-01")
# almanac["dayPillar"], almanac["dayOfficer"], almanac["clashAnimal"], almanac["favours"], almanac["avoids"]
```

### 6. Feng shui API (Kua number, flying star chart)

Kua numbers with the Eight Mansions map, Xuan Kong flying star charts for any of the nine periods and 24 mountains, annual and monthly star plates, and the annual afflictions.

```python
# Kua number. One birth date and a gender give the personal directions everything else reads off.
kua = roxy.feng_shui.calculate_kua_number(date=birth["date"], gender="female")
# kua["kua"], kua["group"] ("east" | "west"), kua["trigram"]["english"], kua["sectors"][n]["direction"], ["nature"], ["rank"]

# Flying star natal chart. Period plus facing gives the nine palaces with base, mountain and water stars.
# Send `facing` (a mountain id like "bing" or a compass label like "S2") or `facing_degrees`, not neither.
stars = roxy.feng_shui.generate_flying_star_chart(period=9, facing="S2")
# stars["facing"]["label"], stars["sitting"]["label"], stars["structure"]["name"], stars["palaces"][n]["palace"], ["base"], ["mountain"], ["water"], ["reading"]
```

### 7. Mayan astrology API (Tzolkin day sign, full Maya chart)

Maya day signs, the Haab and Long Count, and the Aztec tonalpohualli, every value a function of the date under a typed `correlation` convention echoed back in `conventions`.

```python
# Tzolkin day sign. The most asked Maya question, answered from a date alone.
tzolkin = roxy.mesoamerican_astrology.calculate_tzolkin(date=birth["date"])
# tzolkin["daySign"], tzolkin["daySignName"], tzolkin["number"], tzolkin["trecena"], tzolkin["reading"]

# Full Maya chart. Tzolkin, Haab, Long Count, Calendar Round, Lord of the Night, Year Bearer and the Cruz Maya.
maya = roxy.mesoamerican_astrology.generate_mayan_chart(date=birth["date"])
# maya["tzolkin"], maya["haab"], maya["longCount"], maya["calendarRound"], maya["yearBearer"], maya["cross"], maya["conventions"]["correlation"]
```

### 8. Vastu Shastra API (entrance analysis, room compliance)

Home and plot analysis from typed geometry. Every verdict carries a `source` object naming the text, chapter and verse it rests on, or a convention label where the texts are silent.

```python
# Entrance analysis. Plot, facing and door in; the pada, its devata, the classical effect and the recommended padas out.
entrance = roxy.vastu.calculate_entrance_pada(
    plot={"width": 30, "depth": 40, "unit": "feet"}, facing="North", door_position=0.4,
)
# entrance["pada"], entrance["devata"], entrance["effect"], entrance["auspiciousness"], entrance["recommendedPadas"], entrance["source"]

# Room compliance. A verdict per room with the verse or the convention it rests on, and a scored composite.
rooms = roxy.vastu.calculate_room_compliance(
    plot={"width": 30, "depth": 40, "unit": "feet"},
    facing="North",
    rooms=[
        {"type": "kitchen", "direction": "Southeast"},
        {"type": "master-bedroom", "direction": "Southwest"},
        {"type": "puja", "direction": "Northeast"},
    ],
)
# rooms["score"], rooms["rooms"][n]["type"], ["verdict"], ["idealDirections"], ["source"]
```

### 9. Numerology API (life path, full chart, personal year)

Works from the birth date and name alone, no coordinates, which makes it the easiest domain to integrate.

```python
# Life Path. The most searched numerology number, from the birth date alone.
life_path = roxy.numerology.calculate_life_path(year=1990, month=1, day=15)
# life_path["number"], life_path["type"] ("single" | "master"), life_path["meaning"]

# Full numerology chart. All six core numbers plus karmic lessons, pinnacles and the personal year in one call.
numerology = roxy.numerology.generate_numerology_chart(full_name="Jane Smith", year=1990, month=1, day=15)
# numerology["coreNumbers"]["lifePath"], ["expression"], ["soulUrge"], numerology["additionalInsights"]["personalYear"]

# Personal Year. The annual theme, the January feature of every numerology app.
personal_year = roxy.numerology.calculate_personal_year(month=1, day=15, year=2026)
# personal_year["personalYear"], personal_year["theme"], personal_year["advice"]
```

### 10. Kabbalah API (gematria, birth profile)

Gematria of a Latin name under a declared transliteration convention, the 72 names, the Tree of Life, and a Hebrew birthday computed from the same birth instant as every chart above.

```python
# Gematria. A Latin name transliterated under a declared convention, ten ciphers, each with its tradition and source.
gematria = roxy.kabbalah.calculate_gematria(text="Sarah")
# gematria["chosen"]["hebrew"], gematria["values"][n]["id"], ["name"], ["value"], ["tradition"]; gematria["matches"], gematria["conventions"]

# Birth profile. The Hebrew date and birthday, the three birth angels and the birth sephirah from the instant above.
kabbalah = roxy.kabbalah.generate_birth_profile(date=birth["date"], time=birth["time"], timezone=birth["timezone"])
# kabbalah["hebrewDate"], kabbalah["hebrewBirthday"], kabbalah["angels"], kabbalah["sephirah"]
```

### 11. Tarot API (daily card, three-card, Celtic Cross, yes or no)

The complete 78-card deck with meanings for love, career, health and spirit. Pass a `seed` per user for deterministic once-per-day draws.

```python
# Daily card. Deterministic per (seed, date), so one user sees one card per day.
card = roxy.tarot.get_daily_card(seed="user-42")
# card["card"]["name"], card["card"]["reversed"], card["card"]["imageUrl"], card["dailyMessage"]

# Three-card spread. Past, present, future: the most drawn spread on every tarot platform.
three = roxy.tarot.cast_three_card(question="My next quarter", seed="user-42")
# three["positions"][n]["name"], ["card"]["name"], ["interpretation"]; three["summary"]

# Celtic Cross. The ten-position professional reading.
celtic = roxy.tarot.cast_celtic_cross(question="What should I focus on?", seed="user-42")
# celtic["positions"][n]["name"], ["card"]["name"], ["interpretation"]; celtic["summary"]

# Yes or no. One card, one answer, with its strength.
answer = roxy.tarot.cast_yes_no(question="Should I take the offer?")
# answer["answer"] ("Yes" | "No" | "Maybe"), answer["strength"], answer["card"]["name"]
```

### 12. Biorhythm API (reading, forecast)

Ten cycle types across primary, secondary and extended cycles, for wellness, productivity, sports and couples apps.

```python
# Biorhythm reading. All ten cycles for a date, from the same birth date as every chart above.
bio = roxy.biorhythm.get_reading(birth_date=birth["date"], target_date="2026-10-01")
# bio["cycles"]["physical"]["value"], ["phase"]; bio["energyRating"], bio["overallPhase"], bio["criticalAlerts"], bio["interpretation"]

# Forecast. Every cycle for every day of a window, with the best and worst days named.
bio_forecast = roxy.biorhythm.get_forecast(birth_date=birth["date"], start_date="2026-10-01", end_date="2026-10-31")
# bio_forecast["summary"]["bestDay"], ["worstDay"], ["averageEnergy"]; bio_forecast["days"][n]["date"], ["physical"], ["emotional"], ["intellectual"], ["isCritical"]
```

### 13. Ayurveda API (dosha constitution, dinacharya)

The dosha profile read from a verified sidereal chart with the verse on each factor, a daily routine anchored on the local sunrise, and the six seasons from real solar ingresses. Every response carries `meta.disclaimer`.

```python
# Constitution. The dosha profile read from the sidereal chart of the same birth, each factor with its verse.
constitution = roxy.ayurveda.calculate_ayurvedic_constitution(**birth)
# constitution["composite"], constitution["factors"][n]["id"], ["doshas"], ["source"], constitution["meta"]["disclaimer"]

# Dinacharya. Brahma muhurta, the dosha periods and the routine for a date at the place looked up above.
dinacharya = roxy.ayurveda.get_dinacharya_schedule(date="2026-10-01", latitude=latitude, longitude=longitude, timezone=timezone)
# dinacharya["brahmaMuhurta"], dinacharya["doshaPeriods"], dinacharya["routine"]
```

### 14. I Ching API (cast a reading, hexagram catalog)

All 64 hexagrams, 384 changing lines and 8 trigrams, for meditation apps, decision tools and wisdom chatbots.

```python
# Cast a reading. Three coins six times: the primary hexagram, the changing lines and the resulting hexagram.
reading = roxy.iching.cast_reading(seed="user-42")
# reading["hexagram"]["number"], ["english"], reading["lines"], reading["changingLinePositions"], reading["resultingHexagram"]

# Hexagram catalog. Paginated, 20 per page by default; ask for all 64 once and cache them.
hexagrams = roxy.iching.list_hexagrams(limit=64)
# hexagrams["total"], hexagrams["hexagrams"][n]["number"], ["english"], ["pinyin"]; roxy.iching.get_hexagram(number=n) for the judgment and lines
```

### 15. Crystal healing API (by zodiac, by chakra, birthstone)

Crystal retail and metaphysical content: "crystals for [sign]" and "[chakra] chakra stones" pages, plus the birthstone for each month.

```python
# By zodiac. The most searched crystal query pattern.
by_sign = roxy.crystals.get_crystals_by_zodiac(sign="scorpio")
# by_sign["crystals"][n]["id"], ["name"], ["imageUrl"], ["colors"]; roxy.crystals.get_crystal(id=id) for full properties

# By chakra. Wellness and yoga content pages.
by_chakra = roxy.crystals.get_crystals_by_chakra(chakra="Heart")
# by_chakra["crystals"][n]["name"], ["colors"]

# Birthstone. Evergreen gift and jewelry pages.
birthstone = roxy.crystals.get_birthstones(month="1")
```

### 16. Dream interpretation API (symbol dictionary, search)

A 2,000+ symbol dream dictionary for journal apps, AI companions and self-discovery products.

```python
# Symbol detail. Every "what does it mean to dream about X" page lands here.
symbol = roxy.dreams.get_dream_symbol(id="flying")
# symbol["id"], symbol["name"], symbol["meaning"]

# Symbol search. Chatbots fetch the dictionary once and keep it locally.
symbols = roxy.dreams.search_dream_symbols(q="water")
# symbols["symbols"][n]["id"], ["name"]
```

### 17. Angel numbers API (1111, 222, 333 meanings plus universal lookup)

Meanings for every common sequence, and a lookup that answers any positive integer through its digit root.

```python
# By number. Every "meaning of 1111" page is backed by this. The path param is a string.
angel = roxy.angel_numbers.get_angel_number(number="1111")
# angel["title"], angel["coreMessage"], angel["meaning"]["spiritual"], angel["meaning"]["love"], angel["affirmation"]

# Universal lookup. Any positive integer, with the digit root carrying the answer when no curated entry exists.
sequence = roxy.angel_numbers.analyze_number_sequence(number="4242")
# sequence["digitRoot"], sequence["isRepeating"], sequence["knownMeaning"] (None when not curated), sequence["digitRootMeaning"]["title"]
```

## Built for AI agents (Claude Code, Cursor, Copilot, Codex, Gemini CLI)

<p align="center">
  <img src="https://raw.githubusercontent.com/RoxyAPI/sdk-python/main/assets/agents.png" alt="Built for Cursor, Claude, Copilot, Codex. AGENTS.md ships in site-packages, remote MCP, no local setup." width="100%">
</p>

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

<!-- BEGIN:LANGS -->
Interpretations and editorial text are available in 10 languages: `en`, `tr`, `de`, `es`, `hi`, `pt`, `fr`, `ru`, `zh-Hans`, `zh-Hant`. Pass `lang` as a keyword argument on any supported method. Defaults to `en`. Supported: `astrology`, `vedic_astrology`, `forecast`, `human_design`, `chinese_astrology`, `feng_shui`, `mesoamerican_astrology`, `vastu`, `numerology`, `kabbalah`, `tarot`, `biorhythm`, `ayurveda`, `iching`, `crystals`, `angel_numbers`, `languages`. English-only: `dreams`, `location`, `usage`. Languages without translations yet fall back to English.
<!-- END:LANGS -->

```python
card = roxy.tarot.get_daily_card(date="2026-04-22", lang="es")
life_path = roxy.numerology.calculate_life_path(year=1990, month=1, day=15, lang="hi")
```

The two Chinese scripts (`zh-Hans`, `zh-Hant`) currently ship on Chinese astrology and feng shui; every other domain answers those codes in English per field.

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
| 401 | `api_key_revoked` | Key was deleted from the account |
| 404 | `not_found` | Resource not found |
| 4xx | `bad_request` and other status-derived codes | A client error the endpoint itself detected, such as a date window whose `endDate` precedes `startDate` |
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
- [Templates](https://roxyapi.com/templates)
- [TypeScript SDK](https://www.npmjs.com/package/@roxyapi/sdk)
