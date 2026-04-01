"""Live integration tests against localhost:3000."""
import os

import pytest

from roxy_sdk import create_roxy

TEST_KEY = os.environ.get(
    "ROXY_TEST_KEY",
    "c475efae-087c-47e8-a967-c59cb2ac837d.0b30d0fdcae1450d.mxs1rhIKiN_qSuSqZ9FbW198bpXiG3SyVUtXN7_zZh8",
)
BASE_URL = os.environ.get("ROXY_BASE_URL", "http://localhost:3000/api/v2")


@pytest.fixture
def roxy():
    r = create_roxy(TEST_KEY, base_url=BASE_URL)
    yield r
    r.close()


class TestAstrology:
    def test_daily_horoscope(self, roxy):
        result = roxy.astrology.get_daily_horoscope(sign="aries")
        assert result["sign"] == "Aries"
        assert "overview" in result

    @pytest.mark.asyncio
    async def test_daily_horoscope_async(self, roxy):
        result = await roxy.astrology.get_daily_horoscope_async(sign="aries")
        assert result["sign"] == "Aries"

    def test_signs(self, roxy):
        result = roxy.astrology.list_zodiac_signs()
        assert len(result) == 12

    def test_current_moon_phase(self, roxy):
        result = roxy.astrology.get_current_moon_phase()
        assert "phase" in result


class TestVedicAstrology:
    def test_nakshatras(self, roxy):
        result = roxy.vedic_astrology.list_nakshatras()
        assert len(result) == 27

    @pytest.mark.asyncio
    async def test_rashis_async(self, roxy):
        result = await roxy.vedic_astrology.list_rashis_async()
        assert len(result) == 12

    def test_kp_ayanamsa(self, roxy):
        result = roxy.vedic_astrology.get_kp_ayanamsa(date="2026-04-01")
        assert "ayanamsa" in result


class TestTarot:
    def test_draw_cards(self, roxy):
        result = roxy.tarot.draw_cards(count=3)
        assert len(result["cards"]) == 3

    @pytest.mark.asyncio
    async def test_daily_card_async(self, roxy):
        result = await roxy.tarot.get_daily_card_async()
        assert "card" in result

    def test_list_cards(self, roxy):
        result = roxy.tarot.list_cards()
        assert result["total"] == 78


class TestNumerology:
    def test_life_path(self, roxy):
        result = roxy.numerology.calculate_life_path(year=1990, month=1, day=15)
        assert "number" in result

    @pytest.mark.asyncio
    async def test_expression_async(self, roxy):
        result = await roxy.numerology.calculate_expression_async(full_name="John Smith")
        assert "number" in result

    def test_meaning(self, roxy):
        result = roxy.numerology.get_number_meaning(number="5")
        assert "title" in result or "meaning" in result


class TestIChing:
    def test_cast_reading(self, roxy):
        result = roxy.iching.cast_reading()
        assert "hexagram" in result

    @pytest.mark.asyncio
    async def test_hexagrams_async(self, roxy):
        result = await roxy.iching.list_hexagrams_async()
        assert result["total"] == 64

    def test_get_hexagram(self, roxy):
        result = roxy.iching.get_hexagram(number="1")
        assert "english" in result or "chinese" in result


class TestCrystals:
    def test_list_crystals(self, roxy):
        result = roxy.crystals.list_crystals()
        assert "crystals" in result or "items" in result

    @pytest.mark.asyncio
    async def test_search_async(self, roxy):
        result = await roxy.crystals.search_crystals_async(q="amethyst")
        assert isinstance(result, (list, dict))

    def test_by_zodiac(self, roxy):
        result = roxy.crystals.get_crystals_by_zodiac(sign="aries")
        assert isinstance(result, (list, dict))


class TestAngelNumbers:
    def test_list(self, roxy):
        result = roxy.angel_numbers.list_angel_numbers()
        assert isinstance(result, (list, dict))

    @pytest.mark.asyncio
    async def test_get_number_async(self, roxy):
        result = await roxy.angel_numbers.get_angel_number_async(number="111")
        assert isinstance(result, dict)

    def test_get_number(self, roxy):
        result = roxy.angel_numbers.get_angel_number(number="1111")
        assert isinstance(result, dict)


class TestDreams:
    def test_search_symbols(self, roxy):
        result = roxy.dreams.search_dream_symbols(q="water")
        assert isinstance(result, (list, dict))

    @pytest.mark.asyncio
    async def test_random_symbol_async(self, roxy):
        result = await roxy.dreams.get_random_symbols_async()
        assert isinstance(result, (list, dict))


class TestLocation:
    def test_search_cities(self, roxy):
        result = roxy.location.search_cities(q="London")
        assert "cities" in result

    @pytest.mark.asyncio
    async def test_countries_async(self, roxy):
        result = await roxy.location.list_countries_async()
        assert isinstance(result, (list, dict))


class TestUsage:
    def test_get_stats(self, roxy):
        result = roxy.usage.get_usage_stats()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_stats_async(self, roxy):
        result = await roxy.usage.get_usage_stats_async()
        assert isinstance(result, dict)
