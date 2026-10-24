import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from transform import transform, validate  # noqa: E402

HOUR = 3_600_000
T0 = 1_700_000_000_000 - (1_700_000_000_000 % HOUR)


def candle(open_ms=T0, o="100", h="110", l="90", c="105", v="10"):
    return [open_ms, o, h, l, c, v, open_ms + HOUR - 1, "1000", 50, "5", "500", "0"]


def test_valid_candle_passes():
    validate(transform([candle()]), expected_count=1)


def test_high_below_low_fails():
    with pytest.raises(ValueError, match="high is lower than low"):
        validate(transform([candle(h="80", l="90")]))


def test_negative_volume_fails():
    with pytest.raises(ValueError, match="volume"):
        validate(transform([candle(v="-1")]))


def test_non_positive_price_fails():
    with pytest.raises(ValueError, match="positive"):
        validate(transform([candle(o="0", l="0")]))


def test_duplicate_open_time_fails():
    with pytest.raises(ValueError, match="Duplicate"):
        validate(transform([candle(), candle()]))


def test_bad_close_time_fails():
    bad = candle()
    bad[6] = bad[0] + HOUR  # off by 1 ms
    with pytest.raises(ValueError, match="close_time"):
        validate(transform([bad]))


def test_empty_fails():
    with pytest.raises(ValueError, match="No candles"):
        validate([])


def test_malformed_candle_fails():
    with pytest.raises(ValueError, match="Malformed"):
        transform([[1, 2, 3]])
