"""
Example FastAPI server using the roxy-sdk Python package.

Demonstrates all 10 domains with async endpoints, error handling,
connection lifecycle, and environment-based API key configuration.

Setup:
    pip install roxy-sdk fastapi uvicorn

    export ROXY_API_KEY="your-api-key"                        # get one at https://roxyapi.com/pricing
    export ROXY_BASE_URL="https://roxyapi.com/api/v2"        # optional, this is the default
    cd examples && uvicorn app:app --reload --port 8001

Test with curl:
    curl localhost:8001/horoscope/aries
    curl localhost:8001/horoscope/leo?lang=es
    curl -X POST localhost:8001/chart -H "Content-Type: application/json" \
         -d '{"date":"1990-07-15","time":"14:30:00","latitude":40.7128,"longitude":-74.006}'
    curl localhost:8001/tarot/draw/3
    curl localhost:8001/tarot/daily
    curl localhost:8001/numerology/life-path/1990/1/15
    curl localhost:8001/crystal/amethyst
    curl localhost:8001/crystals/zodiac/aries
    curl localhost:8001/iching/reading
    curl localhost:8001/dreams/symbol/water
    curl localhost:8001/angel-number/1111
    curl localhost:8001/vedic/nakshatras
    curl localhost:8001/location/search?q=Mumbai
    curl localhost:8001/usage
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from roxy_sdk import RoxyAPIError, create_roxy

# Read config from environment (never hardcode keys in production)
API_KEY = os.environ.get("ROXY_API_KEY", "")
BASE_URL = os.environ.get("ROXY_BASE_URL", "https://roxyapi.com/api/v2")

if not API_KEY:
    print("WARNING: ROXY_API_KEY not set. Get one at https://roxyapi.com/pricing")
    print("  export ROXY_API_KEY='your-key-here'")

# Create client at module level for connection reuse
roxy = create_roxy(api_key=API_KEY, base_url=BASE_URL) if API_KEY else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Clean up HTTP connections on shutdown
    if roxy:
        await roxy.aclose()


app = FastAPI(
    title="RoxyAPI Example",
    description="Example FastAPI server powered by roxy-sdk",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


@app.exception_handler(RoxyAPIError)
async def handle_roxy_error(request, exc: RoxyAPIError):
    """Forward API errors to the client with the original status code."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "code": exc.code},
    )


# ---------------------------------------------------------------------------
# Western Astrology
# ---------------------------------------------------------------------------


@app.get("/horoscope/{sign}")
async def daily_horoscope(sign: str, lang: str | None = None):
    """Daily horoscope for any zodiac sign. Supports 8 languages via ?lang= query param."""
    return await roxy.astrology.get_daily_horoscope_async(sign=sign, lang=lang)


class ChartRequest(BaseModel):
    date: str  # YYYY-MM-DD
    time: str  # HH:MM:SS
    latitude: float
    longitude: float
    timezone: float = 0.0  # UTC offset in hours (e.g., -5 for EST, 5.5 for IST)


@app.post("/chart")
async def natal_chart(req: ChartRequest):
    """Generate a natal birth chart from birth data."""
    return await roxy.astrology.generate_natal_chart_async(
        date=req.date,
        time=req.time,
        latitude=req.latitude,
        longitude=req.longitude,
        timezone=req.timezone,
    )


@app.get("/moon-phase")
async def moon_phase():
    """Current moon phase with illumination and zodiac sign."""
    return await roxy.astrology.get_current_moon_phase_async()


# ---------------------------------------------------------------------------
# Tarot
# ---------------------------------------------------------------------------


@app.get("/tarot/draw/{count}")
async def draw_cards(count: int):
    """Draw N tarot cards from the full 78-card Rider-Waite-Smith deck."""
    return await roxy.tarot.draw_cards_async(count=count)


@app.get("/tarot/daily")
async def daily_card():
    """Daily tarot card with interpretation."""
    return await roxy.tarot.get_daily_card_async()


# ---------------------------------------------------------------------------
# Numerology
# ---------------------------------------------------------------------------


@app.get("/numerology/life-path/{year}/{month}/{day}")
async def life_path(year: int, month: int, day: int):
    """Calculate Life Path number from birth date."""
    return await roxy.numerology.calculate_life_path_async(year=year, month=month, day=day)


# ---------------------------------------------------------------------------
# Crystals
# ---------------------------------------------------------------------------


@app.get("/crystal/{slug}")
async def crystal_detail(slug: str):
    """Crystal properties, healing info, and zodiac pairings by slug."""
    return await roxy.crystals.get_crystal_async(id=slug)


@app.get("/crystals/zodiac/{sign}")
async def crystals_by_zodiac(sign: str):
    """Crystals associated with a zodiac sign."""
    return await roxy.crystals.get_crystals_by_zodiac_async(sign=sign)


# ---------------------------------------------------------------------------
# I Ching
# ---------------------------------------------------------------------------


@app.get("/iching/reading")
async def iching_reading():
    """Cast an I Ching reading with coin toss simulation."""
    return await roxy.iching.cast_reading_async()


# ---------------------------------------------------------------------------
# Dreams
# ---------------------------------------------------------------------------


@app.get("/dreams/symbol/{symbol_id}")
async def dream_symbol(symbol_id: str):
    """Look up a dream symbol meaning."""
    return await roxy.dreams.get_dream_symbol_async(id=symbol_id)


# ---------------------------------------------------------------------------
# Angel Numbers
# ---------------------------------------------------------------------------


@app.get("/angel-number/{number}")
async def angel_number(number: str):
    """Angel number meaning and spiritual significance."""
    return await roxy.angel_numbers.get_angel_number_async(number=number)


# ---------------------------------------------------------------------------
# Vedic Astrology
# ---------------------------------------------------------------------------


@app.get("/vedic/nakshatras")
async def nakshatras():
    """List all 27 Vedic nakshatras (lunar mansions)."""
    return await roxy.vedic_astrology.list_nakshatras_async()


# ---------------------------------------------------------------------------
# Location (helper for chart endpoints)
# ---------------------------------------------------------------------------


@app.get("/location/search")
async def search_cities(q: str = Query(..., description="City name to search")):
    """Search cities to get coordinates for birth chart calculations."""
    return await roxy.location.search_cities_async(q=q)


# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------


@app.get("/usage")
async def usage_stats():
    """Check API usage and subscription info."""
    return await roxy.usage.get_usage_stats_async()
